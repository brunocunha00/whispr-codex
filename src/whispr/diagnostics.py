from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import platform
import time

from whispr.audio import generate_benchmark_pcm, list_input_devices
from whispr.config import AppConfig
from whispr.engine import EngineDependencyError, WhisperCppEngine
from whispr.hotkey import HotkeyDependencyError, keyboard_available
from whispr.injector import injector_supported


@dataclass(slots=True)
class DoctorCheck:
    name: str
    ok: bool
    detail: str


def collect_doctor_checks(config: AppConfig) -> list[DoctorCheck]:
    checks: list[DoctorCheck] = []
    checks.append(DoctorCheck("platform", platform.system() == "Windows", platform.platform()))

    cli_path = config.resolve_whisper_cpp_path()
    checks.append(
        DoctorCheck(
            "whisper-cli",
            cli_path is not None,
            str(cli_path) if cli_path else "Nao encontrado. Ajuste whisper_cpp_path ou PATH.",
        )
    )
    telegram_enabled = bool(config.telegram_bot_token.strip()) or bool(config.telegram_allowed_chat_ids)
    ffmpeg_path = config.resolve_ffmpeg_path()
    checks.append(
        DoctorCheck(
            "ffmpeg",
            ffmpeg_path is not None or not telegram_enabled,
            str(ffmpeg_path)
            if ffmpeg_path
            else "Nao encontrado. Necessario apenas para audio do Telegram.",
        )
    )
    checks.append(
        DoctorCheck(
            "model",
            config.model_file.exists(),
            str(config.model_file) if config.model_file.exists() else "Modelo ggml nao encontrado.",
        )
    )
    temp_dir = config.temp_directory
    temp_dir.mkdir(parents=True, exist_ok=True)
    checks.append(DoctorCheck("temp-dir", temp_dir.exists(), str(temp_dir)))

    try:
        devices = list_input_devices()
        checks.append(
            DoctorCheck(
                "microphone",
                bool(devices),
                f"{len(devices)} dispositivo(s) de entrada encontrado(s)",
            )
        )
    except Exception as exc:  # pragma: no cover - depends on local audio stack
        checks.append(DoctorCheck("microphone", False, str(exc)))

    checks.append(
        DoctorCheck(
            "hotkey",
            keyboard_available(),
            "Biblioteca keyboard carregavel" if keyboard_available() else "Dependencia keyboard indisponivel.",
        )
    )
    checks.append(
        DoctorCheck(
            "injector",
            injector_supported(),
            "SendInput disponivel" if injector_supported() else "Aplicacao foi desenhada para Windows.",
        )
    )
    checks.append(
        DoctorCheck(
            "telegram-config",
            (bool(config.telegram_bot_token.strip()) and bool(config.telegram_allowed_chat_ids))
            or not telegram_enabled,
            "Token e chats permitidos configurados"
            if config.telegram_bot_token.strip() and config.telegram_allowed_chat_ids
            else "Nao configurado. Necessario apenas para telegram-listen.",
        )
    )
    return checks


@dataclass(slots=True)
class BenchmarkResult:
    backend: str
    ok: bool
    elapsed_s: float
    detail: str


def run_benchmark(config: AppConfig) -> list[BenchmarkResult]:
    engine = WhisperCppEngine(config)
    pcm = generate_benchmark_pcm(sample_rate=config.sample_rate, seconds=2.0)
    results: list[BenchmarkResult] = []
    for backend in ("vulkan", "cpu"):
        start = time.perf_counter()
        try:
            transcription = engine.transcribe_pcm(pcm, backend=backend, sample_rate=config.sample_rate)
        except (EngineDependencyError, RuntimeError) as exc:
            elapsed = time.perf_counter() - start
            results.append(BenchmarkResult(backend=backend, ok=False, elapsed_s=elapsed, detail=str(exc)))
            continue
        elapsed = time.perf_counter() - start
        snippet = transcription.text[:60] or "<sem texto>"
        results.append(
            BenchmarkResult(
                backend=backend,
                ok=True,
                elapsed_s=elapsed,
                detail=f"{snippet} | backend_resolvido={transcription.backend}",
            )
        )
    return results
