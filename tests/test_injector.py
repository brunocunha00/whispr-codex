import unittest

from whispr.injector import AutoTextInjector, ClipboardPasteInjector, SendInputTextInjector, create_injector


class InjectorTests(unittest.TestCase):
    def test_factory_returns_auto_injector(self) -> None:
        injector = create_injector("auto")
        self.assertIsInstance(injector, AutoTextInjector)

    def test_factory_returns_clipboard_injector(self) -> None:
        injector = create_injector("clipboard")
        self.assertIsInstance(injector, ClipboardPasteInjector)

    def test_factory_returns_sendinput_injector(self) -> None:
        injector = create_injector("sendinput")
        self.assertIsInstance(injector, SendInputTextInjector)


if __name__ == "__main__":
    unittest.main()
