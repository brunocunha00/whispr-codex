from pathlib import Path
import tempfile
import unittest

from whispr.config import AppConfig, config_template, ensure_default_config, load_config


class ConfigTests(unittest.TestCase):
    def test_template_contains_expected_defaults(self) -> None:
        rendered = config_template(AppConfig())
        self.assertIn('hotkey = "f9"', rendered)
        self.assertIn('backend = "auto"', rendered)
        self.assertIn('telegram_allowed_chat_ids = []', rendered)

    def test_ensure_default_config_creates_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir_name:
            config_path = Path(temp_dir_name) / "config.toml"
            ensure_default_config(config_path)
            self.assertTrue(config_path.exists())
            loaded = load_config(config_path)
            self.assertEqual(loaded.language, "pt")

    def test_relative_paths_are_resolved_from_config_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir_name:
            base_dir = Path(temp_dir_name)
            (base_dir / "models").mkdir()
            (base_dir / "bin").mkdir()
            (base_dir / "tmp").mkdir()
            model_path = base_dir / "models" / "ggml-small.bin"
            cli_path = base_dir / "bin" / "whisper-cli.exe"
            ffmpeg_path = base_dir / "bin" / "ffmpeg.exe"
            model_path.write_text("stub", encoding="utf-8")
            cli_path.write_text("stub", encoding="utf-8")
            ffmpeg_path.write_text("stub", encoding="utf-8")
            config_path = base_dir / "config.toml"
            config_path.write_text(
                "\n".join(
                    [
                        'hotkey = "f9"',
                        'language = "pt"',
                        'backend = "cpu"',
                        'model_path = "models\\\\ggml-small.bin"',
                        'whisper_cpp_path = "bin\\\\whisper-cli.exe"',
                        'ffmpeg_path = "bin\\\\ffmpeg.exe"',
                        "step_ms = 1000",
                        "window_ms = 6000",
                        "sample_rate = 16000",
                        "threads = 4",
                        'commit_mode = "stable-prefix"',
                        'inject_target = "foreground-window"',
                        'inject_mode = "auto"',
                        "show_capture_indicator = true",
                        'capture_indicator_position = "top-right"',
                        "keep_wav_artifacts = false",
                        'temp_dir = "tmp"',
                        'vad_model_path = ""',
                        'telegram_bot_token = "token"',
                        "telegram_allowed_chat_ids = [1234]",
                        "telegram_poll_timeout_s = 15",
                        'telegram_api_base_url = "https://api.telegram.org"',
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            loaded = load_config(config_path)
            self.assertEqual(loaded.model_file, model_path.resolve())
            self.assertEqual(loaded.resolve_whisper_cpp_path(), cli_path.resolve())
            self.assertEqual(loaded.resolve_ffmpeg_path(), ffmpeg_path.resolve())

    def test_validation_rejects_invalid_backend(self) -> None:
        with self.assertRaises(ValueError):
            AppConfig(backend="cuda").validate()

    def test_validation_rejects_invalid_inject_mode(self) -> None:
        with self.assertRaises(ValueError):
            AppConfig(inject_mode="batata").validate()

    def test_validation_rejects_invalid_indicator_position(self) -> None:
        with self.assertRaises(ValueError):
            AppConfig(capture_indicator_position="centro").validate()

    def test_validation_rejects_non_integer_telegram_chat_ids(self) -> None:
        with self.assertRaises(ValueError):
            AppConfig(telegram_allowed_chat_ids=["abc"]).validate()


if __name__ == "__main__":
    unittest.main()
