from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from whispr import __version__
from whispr.app import DictationApp
from whispr.audio import list_input_devices
from whispr.config import DEFAULT_CONFIG_PATH, DEFAULT_MODELS_DIR, AppConfig, ensure_default_config, load_config
from whispr.diagnostics import collect_doctor_checks, run_benchmark
from whispr.engine import EngineDependencyError, WhisperCppEngine
from whispr.telegram import TelegramAudioListener, TelegramDependencyError


app = typer.Typer(no_args_is_help=True, help="Ditado local Windows-first com whisper.cpp.")
console = Console()


def _load_config_with_overrides(
    config_path: Path | None,
    backend: str | None = None,
    model_path: Path | None = None,
) -> AppConfig:
    config = load_config(config_path)
    if backend is not None:
        config.backend = backend
    if model_path is not None:
        config.model_path = str(model_path)
    return config.validate()


def _validate_transcription_prerequisites(config: AppConfig) -> None:
    errors: list[str] = []
    if config.resolve_whisper_cpp_path() is None:
        errors.append("whisper-cli nao encontrado. Ajuste 'whisper_cpp_path' no config ou deixe o executavel no PATH.")
    if not config.model_file.exists():
        errors.append(f"modelo ggml nao encontrado em '{config.model_file}'.")
    if errors:
        for error in errors:
            console.print(f"[red]Erro:[/red] {error}")
        console.print("Rode `whispr doctor` para validar o ambiente antes de iniciar.")
        raise typer.Exit(code=1)


@app.command("init-config")
def init_config(
    config_path: Annotated[Path, typer.Option("--config-path", help="Caminho alternativo do config.")] = DEFAULT_CONFIG_PATH,
) -> None:
    path = ensure_default_config(config_path)
    DEFAULT_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    console.print(f"Config pronto em [bold]{path}[/bold]")


@app.command()
def doctor(
    config_path: Annotated[Path | None, typer.Option("--config-path", help="Caminho alternativo do config.")] = None,
) -> None:
    config = load_config(config_path)
    checks = collect_doctor_checks(config)

    table = Table(title="Doctor")
    table.add_column("Check")
    table.add_column("Status")
    table.add_column("Detalhe")
    for check in checks:
        table.add_row(check.name, "OK" if check.ok else "FAIL", check.detail)
    console.print(table)

    try:
        version = WhisperCppEngine(config).version_text()
    except EngineDependencyError as exc:
        version = str(exc)
    console.print(f"whisper.cpp: {version}")


@app.command()
def devices() -> None:
    device_list = list_input_devices()
    table = Table(title="Microfones")
    table.add_column("Index")
    table.add_column("Nome")
    table.add_column("Canais")
    table.add_column("Sample rate")
    for device in device_list:
        table.add_row(
            str(device["index"]),
            str(device["name"]),
            str(device["max_input_channels"]),
            str(device["default_samplerate"]),
        )
    console.print(table)


@app.command()
def benchmark(
    config_path: Annotated[Path | None, typer.Option("--config-path", help="Caminho alternativo do config.")] = None,
) -> None:
    config = load_config(config_path)
    results = run_benchmark(config)

    table = Table(title="Benchmark")
    table.add_column("Backend")
    table.add_column("Status")
    table.add_column("Tempo (s)")
    table.add_column("Detalhe")
    for result in results:
        table.add_row(result.backend, "OK" if result.ok else "FAIL", f"{result.elapsed_s:.2f}", result.detail)
    console.print(table)


@app.command()
def run(
    config_path: Annotated[Path | None, typer.Option("--config-path", help="Caminho alternativo do config.")] = None,
    backend: Annotated[str | None, typer.Option("--backend", help="Sobrescreve backend do config.")] = None,
    model_path: Annotated[Path | None, typer.Option("--model-path", help="Sobrescreve model_path do config.")] = None,
) -> None:
    config = _load_config_with_overrides(config_path, backend=backend, model_path=model_path)
    _validate_transcription_prerequisites(config)
    app_runtime = DictationApp(config)
    app_runtime.run()


@app.command("telegram-listen")
def telegram_listen(
    config_path: Annotated[Path | None, typer.Option("--config-path", help="Caminho alternativo do config.")] = None,
    backend: Annotated[str | None, typer.Option("--backend", help="Sobrescreve backend do config.")] = None,
    model_path: Annotated[Path | None, typer.Option("--model-path", help="Sobrescreve model_path do config.")] = None,
    once: Annotated[bool, typer.Option("--once", help="Executa um unico ciclo de polling e sai.")] = False,
) -> None:
    config = _load_config_with_overrides(config_path, backend=backend, model_path=model_path)
    _validate_transcription_prerequisites(config)

    errors: list[str] = []
    if not config.telegram_bot_token.strip():
        errors.append("telegram_bot_token nao configurado.")
    if not config.telegram_allowed_chat_ids:
        errors.append("telegram_allowed_chat_ids precisa ter ao menos um chat autorizado.")
    if config.resolve_ffmpeg_path() is None:
        errors.append("ffmpeg nao encontrado. Ajuste 'ffmpeg_path' no config ou deixe o executavel no PATH.")
    if errors:
        for error in errors:
            console.print(f"[red]Erro:[/red] {error}")
        raise typer.Exit(code=1)

    try:
        listener = TelegramAudioListener(
            config=config,
            engine=WhisperCppEngine(config),
            console=console,
        )
    except TelegramDependencyError as exc:
        console.print(f"[red]Erro:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    if once:
        listener.poll_once()
        return
    listener.run_forever()


@app.command()
def version() -> None:
    console.print(__version__)
