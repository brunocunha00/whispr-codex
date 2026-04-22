from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import shutil
import sys
import tomllib


VALID_BACKENDS = {"auto", "vulkan", "cpu"}
VALID_COMMIT_MODES = {"stable-prefix"}
VALID_INJECT_TARGETS = {"foreground-window"}
VALID_INJECT_MODES = {"auto", "clipboard", "sendinput"}
VALID_INDICATOR_POSITIONS = {"top-right", "top-left", "bottom-right", "bottom-left"}


def _appdata_dir() -> Path:
    appdata = os.getenv("APPDATA")
    if appdata:
        return Path(appdata) / "whispr"
    return Path.home() / ".whispr"


def _portable_base_dir() -> Path | None:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return None


def _default_config_dir() -> Path:
    portable_dir = _portable_base_dir()
    if portable_dir is not None:
        return portable_dir
    return _appdata_dir()


DEFAULT_CONFIG_DIR = _default_config_dir()
DEFAULT_CONFIG_PATH = DEFAULT_CONFIG_DIR / "config.toml"
DEFAULT_MODELS_DIR = DEFAULT_CONFIG_DIR / "models"
DEFAULT_TEMP_DIR = DEFAULT_CONFIG_DIR / "tmp"


@dataclass(slots=True)
class AppConfig:
    hotkey: str = "f9"
    language: str = "pt"
    backend: str = "auto"
    model_path: str = str(DEFAULT_MODELS_DIR / "ggml-small.bin")
    whisper_cpp_path: str = ""
    step_ms: int = 1000
    window_ms: int = 6000
    sample_rate: int = 16000
    threads: int = max(1, (os.cpu_count() or 4) // 2)
    commit_mode: str = "stable-prefix"
    inject_target: str = "foreground-window"
    inject_mode: str = "auto"
    show_capture_indicator: bool = True
    capture_indicator_position: str = "top-right"
    keep_wav_artifacts: bool = False
    temp_dir: str = str(DEFAULT_TEMP_DIR)
    vad_model_path: str = ""
    _config_dir: str = ""

    def validate(self) -> "AppConfig":
        if self.backend not in VALID_BACKENDS:
            raise ValueError(f"backend invalido: {self.backend}")
        if self.commit_mode not in VALID_COMMIT_MODES:
            raise ValueError(f"commit_mode invalido: {self.commit_mode}")
        if self.inject_target not in VALID_INJECT_TARGETS:
            raise ValueError(f"inject_target invalido: {self.inject_target}")
        if self.inject_mode not in VALID_INJECT_MODES:
            raise ValueError(f"inject_mode invalido: {self.inject_mode}")
        if self.capture_indicator_position not in VALID_INDICATOR_POSITIONS:
            raise ValueError(f"capture_indicator_position invalido: {self.capture_indicator_position}")
        if self.step_ms <= 0:
            raise ValueError("step_ms deve ser maior que zero")
        if self.window_ms < self.step_ms:
            raise ValueError("window_ms deve ser maior ou igual a step_ms")
        if self.sample_rate != 16000:
            raise ValueError("sample_rate deve ser 16000 para a v1")
        if self.threads <= 0:
            raise ValueError("threads deve ser maior que zero")
        return self

    @property
    def model_file(self) -> Path:
        return self.resolve_path(self.model_path)

    @property
    def temp_directory(self) -> Path:
        return self.resolve_path(self.temp_dir)

    @property
    def vad_model_file(self) -> Path | None:
        if not self.vad_model_path:
            return None
        return self.resolve_path(self.vad_model_path)

    def resolve_path(self, value: str) -> Path:
        candidate = Path(os.path.expandvars(value)).expanduser()
        if candidate.is_absolute():
            return candidate
        if self._config_dir:
            return (Path(self._config_dir) / candidate).resolve()
        return candidate.resolve()

    def resolve_whisper_cpp_path(self) -> Path | None:
        configured = self.whisper_cpp_path.strip()
        if configured:
            candidate = self.resolve_path(configured)
            if candidate.exists():
                return candidate

        candidates = [
            shutil.which("whisper-cli.exe"),
            shutil.which("whisper-cli"),
        ]
        for item in candidates:
            if item:
                path = Path(item)
                if path.exists():
                    return path
        return None


def config_template(config: AppConfig | None = None) -> str:
    cfg = (config or AppConfig()).validate()

    def quote(value: str) -> str:
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'

    lines = [
        f"hotkey = {quote(cfg.hotkey)}",
        f"language = {quote(cfg.language)}",
        f"backend = {quote(cfg.backend)}",
        f"model_path = {quote(str(cfg.model_file))}",
        f"whisper_cpp_path = {quote(cfg.whisper_cpp_path)}",
        f"step_ms = {cfg.step_ms}",
        f"window_ms = {cfg.window_ms}",
        f"sample_rate = {cfg.sample_rate}",
        f"threads = {cfg.threads}",
        f"commit_mode = {quote(cfg.commit_mode)}",
        f"inject_target = {quote(cfg.inject_target)}",
        f"inject_mode = {quote(cfg.inject_mode)}",
        f"show_capture_indicator = {str(cfg.show_capture_indicator).lower()}",
        f"capture_indicator_position = {quote(cfg.capture_indicator_position)}",
        f"keep_wav_artifacts = {str(cfg.keep_wav_artifacts).lower()}",
        f"temp_dir = {quote(str(cfg.temp_directory))}",
        f"vad_model_path = {quote(cfg.vad_model_path)}",
        "",
    ]
    return "\n".join(lines)


def ensure_default_config(path: Path = DEFAULT_CONFIG_PATH) -> Path:
    if path.exists():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    DEFAULT_TEMP_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(config_template(), encoding="utf-8")
    return path


def load_config(path: Path | None = None) -> AppConfig:
    config_path = path or DEFAULT_CONFIG_PATH
    ensure_default_config(config_path)
    data = tomllib.loads(config_path.read_text(encoding="utf-8-sig"))
    config = AppConfig(**data)
    config._config_dir = str(config_path.parent.resolve())
    return config.validate()
