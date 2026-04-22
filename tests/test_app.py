import time
import unittest

from rich.console import Console

from whispr.app import DictationController
from whispr.config import AppConfig


class FakeEngine:
    def __init__(self, outputs):
        self.outputs = list(outputs)

    def transcribe_pcm(self, pcm_data, backend=None, sample_rate=None):
        text = self.outputs.pop(0)
        class Result:
            def __init__(self, text, backend):
                self.text = text
                self.backend = backend or "cpu"
                self.elapsed_s = 0.01
        return Result(text, backend)


class FakeInjector:
    def __init__(self):
        self.sent = []

    def inject(self, text):
        self.sent.append(text)
        return len(text)


class FakeIndicator:
    def __init__(self):
        self.events = []

    def show(self):
        self.events.append("show")

    def hide(self):
        self.events.append("hide")

    def close(self):
        self.events.append("close")


class FailingEngine:
    def transcribe_pcm(self, pcm_data, backend=None, sample_rate=None):
        raise RuntimeError("falhou")


class DictationControllerTests(unittest.TestCase):
    def test_partial_and_final_commit(self) -> None:
        config = AppConfig(step_ms=100, window_ms=500)
        engine = FakeEngine(["ola mun", "ola mundo", "ola mundo bonito"])
        injector = FakeInjector()
        indicator = FakeIndicator()
        controller = DictationController(config, engine, injector, indicator, Console(file=None, quiet=True))

        controller.on_press()
        controller.on_audio(b"\x00\x00" * 1600)
        controller.tick()
        controller.on_audio(b"\x00\x00" * 1600)
        time.sleep(0.11)
        controller.tick()
        controller.on_release()

        self.assertEqual(injector.sent, ["ola ", "mundo bonito"])
        self.assertEqual(indicator.events, ["show", "hide"])

    def test_transcription_error_does_not_crash_loop(self) -> None:
        config = AppConfig(step_ms=100, window_ms=500)
        injector = FakeInjector()
        indicator = FakeIndicator()
        controller = DictationController(config, FailingEngine(), injector, indicator, Console(file=None, quiet=True))

        controller.on_press()
        controller.on_audio(b"\x00\x00" * 1600)
        controller.tick()
        controller.on_release()

        self.assertEqual(injector.sent, [])
        self.assertEqual(indicator.events, ["show", "hide"])


if __name__ == "__main__":
    unittest.main()
