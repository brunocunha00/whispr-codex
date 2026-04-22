from __future__ import annotations


class HotkeyDependencyError(RuntimeError):
    pass


def _load_keyboard():
    try:
        import keyboard  # type: ignore
    except ImportError as exc:  # pragma: no cover - exercised through doctor
        raise HotkeyDependencyError(
            "A dependencia 'keyboard' nao esta instalada. Rode 'python -m pip install -e .'"
        ) from exc
    return keyboard


def keyboard_available() -> bool:
    try:
        _load_keyboard()
    except HotkeyDependencyError:
        return False
    return True


class PushToTalkHotkey:
    def __init__(self, key_name: str, on_press, on_release):
        self.key_name = key_name
        self.on_press = on_press
        self.on_release = on_release
        self._pressed = False
        self._press_hook = None
        self._release_hook = None

    def start(self) -> None:
        keyboard = _load_keyboard()

        def handle_press(event) -> None:
            del event
            if self._pressed:
                return
            self._pressed = True
            self.on_press()

        def handle_release(event) -> None:
            del event
            if not self._pressed:
                return
            self._pressed = False
            self.on_release()

        self._press_hook = keyboard.on_press_key(self.key_name, handle_press, suppress=True)
        self._release_hook = keyboard.on_release_key(self.key_name, handle_release, suppress=True)

    def stop(self) -> None:
        if self._press_hook is None and self._release_hook is None:
            return
        try:
            if self._press_hook is not None:
                self._press_hook()
        except KeyError:
            pass
        finally:
            self._press_hook = None

        try:
            if self._release_hook is not None:
                self._release_hook()
        except KeyError:
            pass
        finally:
            self._release_hook = None
