from __future__ import annotations

from dataclasses import dataclass, field
from math import sin, tau
from pathlib import Path
import tempfile
import threading
import wave


class AudioDependencyError(RuntimeError):
    pass


def _load_sounddevice():
    try:
        import sounddevice  # type: ignore
    except ImportError as exc:  # pragma: no cover - exercised through doctor paths
        raise AudioDependencyError(
            "A dependencia 'sounddevice' nao esta instalada. Rode 'python -m pip install -e .'"
        ) from exc
    return sounddevice


def list_input_devices() -> list[dict[str, object]]:
    sounddevice = _load_sounddevice()
    devices = sounddevice.query_devices()
    results: list[dict[str, object]] = []
    for index, device in enumerate(devices):
        if int(device.get("max_input_channels", 0)) > 0:
            results.append(
                {
                    "index": index,
                    "name": device.get("name", f"device-{index}"),
                    "max_input_channels": int(device.get("max_input_channels", 0)),
                    "default_samplerate": int(device.get("default_samplerate", 0)),
                }
            )
    return results


class MicrophoneInput:
    def __init__(self, sample_rate: int, callback):
        self.sample_rate = sample_rate
        self._callback = callback
        self._stream = None

    def start(self) -> None:
        sounddevice = _load_sounddevice()
        if self._stream is not None:
            return

        def on_audio(indata, frames, time_info, status) -> None:
            del frames, time_info
            if status:
                return
            self._callback(bytes(indata))

        self._stream = sounddevice.RawInputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="int16",
            callback=on_audio,
        )
        self._stream.start()

    def stop(self) -> None:
        if self._stream is None:
            return
        self._stream.stop()
        self._stream.close()
        self._stream = None


@dataclass(slots=True)
class SessionAudioBuffer:
    sample_rate: int
    sample_width: int = 2
    channels: int = 1
    _data: bytearray = field(default_factory=bytearray)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    @property
    def bytes_per_second(self) -> int:
        return self.sample_rate * self.sample_width * self.channels

    def append(self, chunk: bytes) -> None:
        if not chunk:
            return
        with self._lock:
            self._data.extend(chunk)

    def duration_ms(self) -> int:
        with self._lock:
            if not self._data:
                return 0
            return int((len(self._data) / self.bytes_per_second) * 1000)

    def snapshot_all(self) -> bytes:
        with self._lock:
            return bytes(self._data)

    def snapshot_last_ms(self, window_ms: int) -> bytes:
        with self._lock:
            if not self._data:
                return b""
            wanted = int((window_ms / 1000) * self.bytes_per_second)
            return bytes(self._data[-wanted:])

    def clear(self) -> None:
        with self._lock:
            self._data.clear()


def write_pcm_wav(pcm_data: bytes, sample_rate: int, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(destination), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_data)
    return destination


def write_temp_pcm_wav(pcm_data: bytes, sample_rate: int, directory: Path | None = None) -> Path:
    base_dir = directory
    if base_dir is not None:
        base_dir.mkdir(parents=True, exist_ok=True)
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False, dir=base_dir)
    else:
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)

    temp_file.close()
    return write_pcm_wav(pcm_data, sample_rate, Path(temp_file.name))


def generate_benchmark_pcm(sample_rate: int, seconds: float = 2.0) -> bytes:
    total_samples = int(sample_rate * seconds)
    amplitude = 16000
    samples = bytearray()
    for index in range(total_samples):
        value = int(amplitude * sin(tau * 220 * (index / sample_rate)))
        samples.extend(int(value).to_bytes(2, byteorder="little", signed=True))
    return bytes(samples)
