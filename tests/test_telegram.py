from pathlib import Path
import tempfile
import unittest

from rich.console import Console

from whispr.config import AppConfig
from whispr.engine import TranscriptionResult
from whispr.telegram import TelegramAudioListener, TelegramAudioMessage, TelegramRemoteFile, extract_audio_message


class FakeTelegramClient:
    def __init__(self, updates, file_path="voice/test.ogg", file_bytes=b"telegram-audio"):
        self.updates = list(updates)
        self.file_path = file_path
        self.file_bytes = file_bytes
        self.offsets = []
        self.downloads = []
        self.file_ids = []

    def get_updates(self, offset=None, timeout_s=0, allowed_updates=None):
        self.offsets.append((offset, timeout_s, tuple(allowed_updates or [])))
        if not self.updates:
            return []
        batch = list(self.updates)
        self.updates.clear()
        return batch

    def get_file(self, file_id):
        self.file_ids.append(file_id)
        return TelegramRemoteFile(file_id=file_id, file_path=self.file_path, file_size=len(self.file_bytes))

    def download_file(self, file_path):
        self.downloads.append(file_path)
        return self.file_bytes


class FakeAudioDecoder:
    def __init__(self):
        self.calls = []

    def decode_file(self, source_path: Path, sample_rate: int):
        self.calls.append((source_path.name, sample_rate, source_path.read_bytes()))
        return b"\x00\x00" * 1600


class FakeEngine:
    def __init__(self):
        self.calls = []

    def transcribe_pcm(self, pcm_data, backend=None, sample_rate=None):
        self.calls.append((pcm_data, backend, sample_rate))
        return TranscriptionResult(
            text="ola telegram",
            backend=backend or "cpu",
            elapsed_s=0.01,
            command=[],
        )


class FakeInjector:
    def __init__(self):
        self.sent = []

    def inject(self, text):
        self.sent.append(text)
        return len(text)


class TelegramTests(unittest.TestCase):
    def test_extract_audio_message_from_voice_update(self) -> None:
        update = {
            "update_id": 10,
            "message": {
                "chat": {"id": 42, "title": "Equipe"},
                "voice": {"file_id": "voice-1", "mime_type": "audio/ogg"},
            },
        }
        message = extract_audio_message(update)
        self.assertEqual(
            message,
            TelegramAudioMessage(
                update_id=10,
                chat_id=42,
                chat_label="Equipe",
                file_id="voice-1",
                kind="voice",
                file_name="",
                mime_type="audio/ogg",
            ),
        )

    def test_listener_processes_authorized_audio_message(self) -> None:
        update = {
            "update_id": 15,
            "message": {
                "chat": {"id": 42, "title": "Equipe"},
                "audio": {
                    "file_id": "audio-1",
                    "file_name": "gravacao.mp3",
                    "mime_type": "audio/mpeg",
                },
            },
        }
        with tempfile.TemporaryDirectory() as temp_dir_name:
            config = AppConfig(
                backend="cpu",
                temp_dir=temp_dir_name,
                telegram_bot_token="token",
                telegram_allowed_chat_ids=[42],
                telegram_poll_timeout_s=5,
            )
            client = FakeTelegramClient([update])
            audio_decoder = FakeAudioDecoder()
            engine = FakeEngine()
            injector = FakeInjector()
            listener = TelegramAudioListener(
                config=config,
                engine=engine,
                console=Console(file=None, quiet=True),
                client=client,
                audio_decoder=audio_decoder,
                injector=injector,
            )

            processed = listener.poll_once()

        self.assertEqual(processed, 1)
        self.assertEqual(client.offsets, [(None, 5, ("message",))])
        self.assertEqual(client.file_ids, ["audio-1"])
        self.assertEqual(client.downloads, ["voice/test.ogg"])
        self.assertEqual(audio_decoder.calls[0][1], 16000)
        self.assertEqual(audio_decoder.calls[0][2], b"telegram-audio")
        self.assertEqual(engine.calls[0][1], "cpu")
        self.assertEqual(engine.calls[0][2], 16000)
        self.assertEqual(injector.sent, ["ola telegram"])

    def test_listener_ignores_unauthorized_chat(self) -> None:
        update = {
            "update_id": 16,
            "message": {
                "chat": {"id": 99, "title": "Desconhecido"},
                "voice": {"file_id": "voice-2", "mime_type": "audio/ogg"},
            },
        }
        with tempfile.TemporaryDirectory() as temp_dir_name:
            config = AppConfig(
                temp_dir=temp_dir_name,
                telegram_bot_token="token",
                telegram_allowed_chat_ids=[42],
            )
            client = FakeTelegramClient([update])
            audio_decoder = FakeAudioDecoder()
            engine = FakeEngine()
            injector = FakeInjector()
            listener = TelegramAudioListener(
                config=config,
                engine=engine,
                console=Console(file=None, quiet=True),
                client=client,
                audio_decoder=audio_decoder,
                injector=injector,
            )

            processed = listener.poll_once()

        self.assertEqual(processed, 0)
        self.assertEqual(client.file_ids, [])
        self.assertEqual(audio_decoder.calls, [])
        self.assertEqual(engine.calls, [])
        self.assertEqual(injector.sent, [])


if __name__ == "__main__":
    unittest.main()
