from __future__ import annotations

from dataclasses import dataclass, field
import threading
import time

from rich.console import Console

from whispr.audio import MicrophoneInput, SessionAudioBuffer
from whispr.config import AppConfig
from whispr.engine import WhisperCppEngine
from whispr.hotkey import PushToTalkHotkey
from whispr.injector import ForegroundTextInjector, InjectionError, create_injector
from whispr.overlay import CaptureIndicator, create_capture_indicator
from whispr.stabilization import StablePrefixCommitter


@dataclass(slots=True)
class DictationSession:
    audio: SessionAudioBuffer
    committer: StablePrefixCommitter = field(default_factory=StablePrefixCommitter)
    started_at: float = field(default_factory=time.monotonic)
    last_tick_at: float = 0.0


class DictationController:
    def __init__(
        self,
        config: AppConfig,
        engine: WhisperCppEngine,
        injector: ForegroundTextInjector,
        indicator: CaptureIndicator,
        console: Console,
    ):
        self.config = config
        self.engine = engine
        self.injector = injector
        self.indicator = indicator
        self.console = console
        self._lock = threading.Lock()
        self._session: DictationSession | None = None

    def on_press(self) -> None:
        with self._lock:
            if self._session is not None:
                return
            self._session = DictationSession(audio=SessionAudioBuffer(sample_rate=self.config.sample_rate))
        self.indicator.show()
        self.console.print("[cyan]Captura iniciada[/cyan]")

    def on_release(self) -> None:
        with self._lock:
            session = self._session
            self._session = None
        self.indicator.hide()
        if session is None:
            return
        pcm_data = session.audio.snapshot_all()
        if not pcm_data:
            self.console.print("[yellow]Captura encerrada sem audio[/yellow]")
            return
        self.console.print("[cyan]Processando flush final...[/cyan]")
        result = self._transcribe(pcm_data)
        if result is None:
            return
        delta = session.committer.flush(result.text)
        if delta:
            self._inject(delta)
        self.console.print(f"[green]Final:[/green] {result.text or '<sem texto>'}")

    def on_audio(self, chunk: bytes) -> None:
        with self._lock:
            session = self._session
        if session is None:
            return
        session.audio.append(chunk)

    def tick(self) -> None:
        with self._lock:
            session = self._session
        if session is None:
            return
        now = time.monotonic()
        if now - session.last_tick_at < (self.config.step_ms / 1000):
            return
        if session.audio.duration_ms() < self.config.step_ms:
            return
        session.last_tick_at = now
        partial_pcm = session.audio.snapshot_last_ms(self.config.window_ms)
        result = self._transcribe(partial_pcm)
        if result is None:
            return
        delta = session.committer.observe(result.text)
        if delta:
            self._inject(delta)
        self.console.print(f"[dim]Parcial ({result.backend}, {result.elapsed_s:.2f}s):[/dim] {result.text or '<sem texto>'}")

    def _requested_backend(self) -> str:
        return self.config.backend

    def _transcribe(self, pcm_data: bytes):
        try:
            return self.engine.transcribe_pcm(
                pcm_data,
                backend=self._requested_backend(),
                sample_rate=self.config.sample_rate,
            )
        except Exception as exc:
            self.console.print(f"[red]Falha na transcricao:[/red] {exc}")
            return None

    def _inject(self, text: str) -> None:
        try:
            self.injector.inject(text)
        except InjectionError as exc:
            self.console.print(f"[red]Falha ao injetar texto:[/red] {exc}")
            return
        self.console.print(f"[green]Enviado:[/green] {text!r}")


class DictationApp:
    def __init__(self, config: AppConfig):
        self.console = Console()
        self.config = config
        self.engine = WhisperCppEngine(config)
        self.injector = create_injector(config.inject_mode)
        self.indicator = create_capture_indicator(
            enabled=config.show_capture_indicator,
            position=config.capture_indicator_position,
        )
        self.controller = DictationController(
            config=config,
            engine=self.engine,
            injector=self.injector,
            indicator=self.indicator,
            console=self.console,
        )
        self.microphone = MicrophoneInput(sample_rate=config.sample_rate, callback=self.controller.on_audio)
        self.hotkey = PushToTalkHotkey(config.hotkey, self.controller.on_press, self.controller.on_release)

    def run(self) -> None:
        self.console.print("[bold]whispr[/bold] pronto.")
        self.console.print(
            f"Hotkey: {self.config.hotkey.upper()} | backend: {self.config.backend} | idioma: {self.config.language} | injecao: {self.config.inject_mode}"
        )
        self.console.print("Pressione Ctrl+C para encerrar.")

        try:
            self.microphone.start()
            self.hotkey.start()
            while True:
                self.controller.tick()
                time.sleep(0.05)
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Encerrando...[/yellow]")
        finally:
            self.indicator.close()
            self.hotkey.stop()
            self.microphone.stop()
