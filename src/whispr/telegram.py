from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import mimetypes
import subprocess
import tempfile
import urllib.error
import urllib.parse
import urllib.request

from rich.console import Console

from whispr.config import AppConfig
from whispr.engine import WhisperCppEngine
from whispr.injector import ForegroundTextInjector, InjectionError, create_injector


SUPPORTED_AUDIO_EXTENSIONS = {
    ".aac",
    ".flac",
    ".m4a",
    ".mp3",
    ".mp4",
    ".oga",
    ".ogg",
    ".opus",
    ".wav",
}


class TelegramDependencyError(RuntimeError):
    pass


class TelegramApiError(RuntimeError):
    pass


class AudioConversionError(RuntimeError):
    pass


@dataclass(slots=True)
class TelegramRemoteFile:
    file_id: str
    file_path: str
    file_size: int | None = None


@dataclass(slots=True)
class TelegramAudioMessage:
    update_id: int
    chat_id: int
    chat_label: str
    file_id: str
    kind: str
    file_name: str = ""
    mime_type: str = ""

    def suggested_suffix(self) -> str:
        if self.file_name:
            suffix = Path(self.file_name).suffix.lower()
            if suffix:
                return suffix
        guessed = mimetypes.guess_extension(self.mime_type) if self.mime_type else None
        return guessed or ".bin"


def _chat_label(chat: dict[str, object], chat_id: int) -> str:
    title = chat.get("title")
    if isinstance(title, str) and title:
        return title
    username = chat.get("username")
    if isinstance(username, str) and username:
        return username
    first_name = chat.get("first_name")
    last_name = chat.get("last_name")
    parts = [part for part in (first_name, last_name) if isinstance(part, str) and part]
    if parts:
        return " ".join(parts)
    return str(chat_id)


def _supported_document(file_name: str, mime_type: str) -> bool:
    if mime_type.startswith("audio/"):
        return True
    return Path(file_name).suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS


def extract_audio_message(update: dict[str, object]) -> TelegramAudioMessage | None:
    update_id = update.get("update_id")
    if not isinstance(update_id, int):
        return None

    message = update.get("message")
    if not isinstance(message, dict):
        return None
    chat = message.get("chat")
    if not isinstance(chat, dict):
        return None
    chat_id = chat.get("id")
    if not isinstance(chat_id, int):
        return None

    for kind in ("voice", "audio", "document"):
        payload = message.get(kind)
        if not isinstance(payload, dict):
            continue
        file_id = payload.get("file_id")
        if not isinstance(file_id, str) or not file_id:
            continue
        file_name = payload.get("file_name")
        mime_type = payload.get("mime_type")
        safe_file_name = file_name if isinstance(file_name, str) else ""
        safe_mime_type = mime_type if isinstance(mime_type, str) else ""
        if kind == "document" and not _supported_document(safe_file_name, safe_mime_type):
            continue
        return TelegramAudioMessage(
            update_id=update_id,
            chat_id=chat_id,
            chat_label=_chat_label(chat, chat_id),
            file_id=file_id,
            kind=kind,
            file_name=safe_file_name,
            mime_type=safe_mime_type,
        )
    return None


class TelegramBotClient:
    def __init__(
        self,
        token: str,
        api_base_url: str = "https://api.telegram.org",
        request_timeout_s: int = 40,
    ):
        if not token.strip():
            raise TelegramDependencyError("telegram_bot_token nao configurado.")
        self.token = token.strip()
        self.api_base_url = api_base_url.rstrip("/")
        self.request_timeout_s = request_timeout_s

    def _api_url(self, method: str, params: dict[str, object] | None = None) -> str:
        url = f"{self.api_base_url}/bot{self.token}/{method}"
        if not params:
            return url
        filtered = {key: value for key, value in params.items() if value is not None}
        query = urllib.parse.urlencode(filtered)
        return f"{url}?{query}"

    def _read_json(self, url: str, timeout_s: int) -> object:
        request = urllib.request.Request(url, headers={"User-Agent": "whispr-codex"})
        try:
            with urllib.request.urlopen(request, timeout=timeout_s) as response:
                payload = response.read().decode("utf-8")
        except urllib.error.URLError as exc:
            raise TelegramApiError(f"falha na chamada Telegram: {exc}") from exc
        try:
            return json.loads(payload)
        except json.JSONDecodeError as exc:
            raise TelegramApiError("resposta invalida da API do Telegram.") from exc

    def _request_result(self, method: str, params: dict[str, object] | None = None, timeout_s: int | None = None) -> object:
        payload = self._read_json(self._api_url(method, params), timeout_s or self.request_timeout_s)
        if not isinstance(payload, dict):
            raise TelegramApiError("resposta da API sem objeto raiz.")
        if not payload.get("ok"):
            description = payload.get("description", "erro desconhecido")
            raise TelegramApiError(str(description))
        return payload.get("result")

    def get_updates(self, offset: int | None, timeout_s: int, allowed_updates: list[str] | None = None) -> list[dict[str, object]]:
        params: dict[str, object] = {
            "offset": offset,
            "timeout": timeout_s,
        }
        if allowed_updates is not None:
            params["allowed_updates"] = json.dumps(allowed_updates)
        result = self._request_result("getUpdates", params=params, timeout_s=timeout_s + 10)
        if not isinstance(result, list):
            raise TelegramApiError("getUpdates nao retornou lista.")
        return [item for item in result if isinstance(item, dict)]

    def get_file(self, file_id: str) -> TelegramRemoteFile:
        result = self._request_result("getFile", params={"file_id": file_id})
        if not isinstance(result, dict):
            raise TelegramApiError("getFile nao retornou objeto.")
        file_path = result.get("file_path")
        if not isinstance(file_path, str) or not file_path:
            raise TelegramApiError("arquivo do Telegram sem file_path.")
        file_size = result.get("file_size")
        safe_file_size = file_size if isinstance(file_size, int) else None
        return TelegramRemoteFile(file_id=file_id, file_path=file_path, file_size=safe_file_size)

    def download_file(self, file_path: str) -> bytes:
        encoded_path = urllib.parse.quote(file_path, safe="/")
        url = f"{self.api_base_url}/file/bot{self.token}/{encoded_path}"
        request = urllib.request.Request(url, headers={"User-Agent": "whispr-codex"})
        try:
            with urllib.request.urlopen(request, timeout=self.request_timeout_s) as response:
                return response.read()
        except urllib.error.URLError as exc:
            raise TelegramApiError(f"falha ao baixar arquivo do Telegram: {exc}") from exc


class FfmpegAudioDecoder:
    def __init__(self, ffmpeg_path: Path):
        self.ffmpeg_path = ffmpeg_path

    def decode_file(self, source_path: Path, sample_rate: int) -> bytes:
        command = [
            str(self.ffmpeg_path),
            "-nostdin",
            "-v",
            "error",
            "-i",
            str(source_path),
            "-f",
            "s16le",
            "-acodec",
            "pcm_s16le",
            "-ac",
            "1",
            "-ar",
            str(sample_rate),
            "-",
        ]
        completed = subprocess.run(
            command,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            detail = completed.stderr.decode("utf-8", errors="replace").strip() or "falha desconhecida"
            raise AudioConversionError(f"ffmpeg falhou: {detail}")
        if not completed.stdout:
            raise AudioConversionError("ffmpeg nao retornou audio PCM.")
        return completed.stdout


class TelegramAudioListener:
    def __init__(
        self,
        config: AppConfig,
        engine: WhisperCppEngine,
        console: Console | None = None,
        client: TelegramBotClient | None = None,
        audio_decoder: FfmpegAudioDecoder | None = None,
        injector: ForegroundTextInjector | None = None,
    ):
        self.config = config
        self.engine = engine
        self.console = console or Console()
        self.client = client or TelegramBotClient(
            token=config.telegram_bot_token,
            api_base_url=config.telegram_api_base_url,
            request_timeout_s=config.telegram_poll_timeout_s + 10,
        )
        if audio_decoder is None:
            ffmpeg_path = config.resolve_ffmpeg_path()
            if ffmpeg_path is None:
                raise TelegramDependencyError("ffmpeg nao encontrado. Ajuste 'ffmpeg_path' ou deixe o executavel no PATH.")
            audio_decoder = FfmpegAudioDecoder(ffmpeg_path)
        self.audio_decoder = audio_decoder
        self.injector = injector or create_injector(config.inject_mode)
        self.allowed_chat_ids = set(config.telegram_allowed_chat_ids)
        self._next_update_offset: int | None = None

    def poll_once(self) -> int:
        updates = self.client.get_updates(
            offset=self._next_update_offset,
            timeout_s=self.config.telegram_poll_timeout_s,
            allowed_updates=["message"],
        )
        processed = 0
        for update in updates:
            update_id = update.get("update_id")
            if isinstance(update_id, int):
                candidate_offset = update_id + 1
                if self._next_update_offset is None or candidate_offset > self._next_update_offset:
                    self._next_update_offset = candidate_offset

            message = extract_audio_message(update)
            if message is None:
                continue
            if message.chat_id not in self.allowed_chat_ids:
                self.console.print(f"[yellow]Ignorado chat nao autorizado:[/yellow] {message.chat_id}")
                continue
            try:
                result = self._process_message(message)
            except Exception as exc:
                self.console.print(
                    f"[red]Falha ao processar update {message.update_id} ({message.chat_label}):[/red] {exc}"
                )
                continue
            processed += 1
            injected = self._inject_transcript(result.text)
            self.console.print(f"[green]Telegram {message.chat_label}:[/green] {result.text or '<sem texto>'}")
            if injected:
                self.console.print(f"[green]Enviado:[/green] {result.text!r}")
        return processed

    def run_forever(self) -> None:
        self.console.print("[bold]Telegram listener pronto.[/bold]")
        self.console.print(
            f"Escutando chats: {', '.join(str(chat_id) for chat_id in sorted(self.allowed_chat_ids))} "
            f"| poll timeout: {self.config.telegram_poll_timeout_s}s"
        )
        self.console.print("Pressione Ctrl+C para encerrar.")
        try:
            while True:
                self.poll_once()
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Encerrando listener Telegram...[/yellow]")

    def _process_message(self, message: TelegramAudioMessage):
        remote_file = self.client.get_file(message.file_id)
        if remote_file.file_size is not None and remote_file.file_size > (20 * 1024 * 1024):
            raise TelegramApiError("arquivo excede o limite de 20 MB suportado pelo Bot API.")

        temp_dir = self.config.temp_directory
        temp_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temp_dir) as work_dir_name:
            work_dir = Path(work_dir_name)
            source_path = work_dir / f"telegram-input{message.suggested_suffix()}"
            source_path.write_bytes(self.client.download_file(remote_file.file_path))
            pcm_data = self.audio_decoder.decode_file(source_path, sample_rate=self.config.sample_rate)
            return self.engine.transcribe_pcm(
                pcm_data,
                backend=self.config.backend,
                sample_rate=self.config.sample_rate,
            )

    def _inject_transcript(self, text: str) -> bool:
        if not text:
            return False
        try:
            self.injector.inject(text)
        except InjectionError as exc:
            self.console.print(f"[red]Falha ao injetar texto do Telegram:[/red] {exc}")
            return False
        return True
