from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import re
import subprocess
import tempfile
import time

from whispr.audio import write_pcm_wav
from whispr.config import AppConfig


class EngineDependencyError(RuntimeError):
    pass


TIMESTAMP_PREFIX = re.compile(r"^\[[0-9:. ]+-->[0-9:. ]+\]\s*")


@dataclass(slots=True)
class TranscriptionResult:
    text: str
    backend: str
    elapsed_s: float
    command: list[str]
    stdout: str = ""
    stderr: str = ""


def clean_transcript_text(raw_text: str) -> str:
    lines: list[str] = []
    for raw_line in raw_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("whisper_") or line.startswith("system_info:") or line.startswith("main:"):
            continue
        line = TIMESTAMP_PREFIX.sub("", line).strip()
        if line:
            lines.append(line)
    collapsed = " ".join(lines)
    return re.sub(r"\s+", " ", collapsed).strip()


class WhisperCppEngine:
    def __init__(self, config: AppConfig):
        self.config = config

    def resolve_cli_path(self) -> Path:
        path = self.config.resolve_whisper_cpp_path()
        if path is None:
            raise EngineDependencyError(
                "whisper-cli nao encontrado. Ajuste whisper_cpp_path ou deixe o executavel no PATH."
            )
        return path

    def version_text(self) -> str:
        cli_path = self.resolve_cli_path()
        completed = subprocess.run(
            [str(cli_path), "-h"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        text = (completed.stdout or completed.stderr).strip()
        if not text:
            return "Sem resposta do whisper-cli"
        return text.splitlines()[0]

    def build_command(self, audio_path: Path, output_base: Path, backend: str | None = None) -> list[str]:
        cli_path = self.resolve_cli_path()
        selected_backend = backend or self.config.backend
        command = [
            str(cli_path),
            "-m",
            str(self.config.model_file),
            "-f",
            str(audio_path),
            "-l",
            self.config.language,
            "-t",
            str(self.config.threads),
            "--no-prints",
            "--no-timestamps",
            "--output-txt",
            "--output-file",
            str(output_base),
        ]
        vad_model = self.config.vad_model_file
        if vad_model is not None:
            command.extend(["--vad", "--vad-model", str(vad_model)])
        if selected_backend == "cpu":
            command.append("--no-gpu")
        return command

    def _backend_attempts(self, backend: str | None) -> list[str]:
        selected_backend = backend or self.config.backend
        if selected_backend == "auto":
            return ["vulkan", "cpu"]
        return [selected_backend]

    def _run_attempt(
        self,
        pcm_data: bytes,
        backend: str,
        sample_rate: int,
    ) -> TranscriptionResult:
        temp_dir = self.config.temp_directory
        temp_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temp_dir) as work_dir_name:
            work_dir = Path(work_dir_name)
            wav_path = work_dir / "capture.wav"
            output_base = work_dir / "capture"
            write_pcm_wav(pcm_data, sample_rate, wav_path)

            command = self.build_command(wav_path, output_base, backend=backend)
            started = time.perf_counter()
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
                cwd=work_dir,
            )
            elapsed = time.perf_counter() - started

            output_txt = output_base.with_suffix(".txt")
            text = ""
            if output_txt.exists():
                text = clean_transcript_text(output_txt.read_text(encoding="utf-8", errors="replace"))
            if not text:
                text = clean_transcript_text(completed.stdout)

            if completed.returncode != 0:
                detail = completed.stderr.strip() or completed.stdout.strip() or "Falha desconhecida"
                raise RuntimeError(f"whisper-cli falhou ({completed.returncode}) em {backend}: {detail}")

            resolved_backend = "cpu" if "--no-gpu" in command else backend
            return TranscriptionResult(
                text=text,
                backend=resolved_backend,
                elapsed_s=elapsed,
                command=command,
                stdout=completed.stdout,
                stderr=completed.stderr,
            )

    def transcribe_pcm(self, pcm_data: bytes, backend: str | None = None, sample_rate: int | None = None) -> TranscriptionResult:
        if not pcm_data:
            return TranscriptionResult(text="", backend=backend or self.config.backend, elapsed_s=0.0, command=[])

        self.resolve_cli_path()
        if not self.config.model_file.exists():
            raise EngineDependencyError(f"Modelo ggml nao encontrado: {self.config.model_file}")
        last_error: RuntimeError | None = None
        effective_sample_rate = sample_rate or self.config.sample_rate
        for attempt_backend in self._backend_attempts(backend):
            try:
                return self._run_attempt(pcm_data, backend=attempt_backend, sample_rate=effective_sample_rate)
            except RuntimeError as exc:
                last_error = exc
                continue
        if last_error is not None:
            raise last_error
        raise RuntimeError("Nenhuma tentativa de backend foi executada.")
