from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from whispr.config import AppConfig
from whispr.engine import WhisperCppEngine, clean_transcript_text


class EngineTests(unittest.TestCase):
    def test_clean_transcript_removes_metadata(self) -> None:
        raw = """
        whisper_model_load: loading
        main: processing
        [00:00:00.000 --> 00:00:01.000]  Ola mundo
        [00:00:01.000 --> 00:00:02.000]  teste
        """
        self.assertEqual(clean_transcript_text(raw), "Ola mundo teste")

    def test_build_command_cpu_adds_no_gpu(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            cli_path = temp_dir / "whisper-cli.exe"
            cli_path.write_text("stub", encoding="utf-8")
            model_path = temp_dir / "ggml-small.bin"
            model_path.write_text("stub", encoding="utf-8")

            config = AppConfig(whisper_cpp_path=str(cli_path), model_path=str(model_path))
            engine = WhisperCppEngine(config)
            command = engine.build_command(temp_dir / "capture.wav", temp_dir / "capture", backend="cpu")
            self.assertIn("--no-gpu", command)

    def test_auto_backend_falls_back_to_cpu(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            cli_path = temp_dir / "whisper-cli.exe"
            cli_path.write_text("stub", encoding="utf-8")
            model_path = temp_dir / "ggml-small.bin"
            model_path.write_text("stub", encoding="utf-8")

            config = AppConfig(backend="auto", whisper_cpp_path=str(cli_path), model_path=str(model_path), temp_dir=str(temp_dir))
            engine = WhisperCppEngine(config)

            attempts = []

            def fake_run_attempt(pcm_data, backend, sample_rate):
                attempts.append(backend)
                if backend == "vulkan":
                    raise RuntimeError("gpu fail")
                class Result:
                    text = "ola"
                    elapsed_s = 0.01
                    command = []
                    stdout = ""
                    stderr = ""
                    backend = "cpu"
                return Result()

            with patch.object(engine, "_run_attempt", side_effect=fake_run_attempt):
                result = engine.transcribe_pcm(b"\x00\x00" * 1600)

            self.assertEqual(attempts, ["vulkan", "cpu"])
            self.assertEqual(result.backend, "cpu")


if __name__ == "__main__":
    unittest.main()
