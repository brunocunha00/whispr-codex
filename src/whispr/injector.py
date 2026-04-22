from __future__ import annotations

import ctypes
from ctypes import wintypes
import sys
import time


if sys.platform == "win32":
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    ULONG_PTR = wintypes.WPARAM

    CF_UNICODETEXT = 13
    GMEM_MOVEABLE = 0x0002
    INPUT_KEYBOARD = 1
    VK_CONTROL = 0x11
    VK_V = 0x56
    KEYEVENTF_KEYUP = 0x0002
    KEYEVENTF_UNICODE = 0x0004

    class MOUSEINPUT(ctypes.Structure):
        _fields_ = [
            ("dx", wintypes.LONG),
            ("dy", wintypes.LONG),
            ("mouseData", wintypes.DWORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ULONG_PTR),
        ]

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [
            ("wVk", wintypes.WORD),
            ("wScan", wintypes.WORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ULONG_PTR),
        ]

    class HARDWAREINPUT(ctypes.Structure):
        _fields_ = [
            ("uMsg", wintypes.DWORD),
            ("wParamL", wintypes.WORD),
            ("wParamH", wintypes.WORD),
        ]

    class INPUT_UNION(ctypes.Union):
        _fields_ = [
            ("mi", MOUSEINPUT),
            ("ki", KEYBDINPUT),
            ("hi", HARDWAREINPUT),
        ]

    class INPUT(ctypes.Structure):
        _anonymous_ = ("u",)
        _fields_ = [("type", wintypes.DWORD), ("u", INPUT_UNION)]

    user32.OpenClipboard.argtypes = (wintypes.HWND,)
    user32.OpenClipboard.restype = wintypes.BOOL
    user32.CloseClipboard.argtypes = ()
    user32.CloseClipboard.restype = wintypes.BOOL
    user32.EmptyClipboard.argtypes = ()
    user32.EmptyClipboard.restype = wintypes.BOOL
    user32.IsClipboardFormatAvailable.argtypes = (wintypes.UINT,)
    user32.IsClipboardFormatAvailable.restype = wintypes.BOOL
    user32.GetClipboardData.argtypes = (wintypes.UINT,)
    user32.GetClipboardData.restype = wintypes.HANDLE
    user32.SetClipboardData.argtypes = (wintypes.UINT, wintypes.HANDLE)
    user32.SetClipboardData.restype = wintypes.HANDLE
    user32.SendInput.argtypes = (wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int)
    user32.SendInput.restype = wintypes.UINT

    kernel32.GlobalAlloc.argtypes = (wintypes.UINT, ctypes.c_size_t)
    kernel32.GlobalAlloc.restype = wintypes.HGLOBAL
    kernel32.GlobalLock.argtypes = (wintypes.HGLOBAL,)
    kernel32.GlobalLock.restype = wintypes.LPVOID
    kernel32.GlobalUnlock.argtypes = (wintypes.HGLOBAL,)
    kernel32.GlobalUnlock.restype = wintypes.BOOL


class InjectionError(RuntimeError):
    pass


def injector_supported() -> bool:
    return sys.platform == "win32"


class ForegroundTextInjector:
    def __init__(self) -> None:
        if not injector_supported():
            raise InjectionError("A injecao de texto so esta implementada para Windows.")

    def inject(self, text: str) -> int:
        raise NotImplementedError


class SendInputTextInjector(ForegroundTextInjector):
    def inject(self, text: str) -> int:
        if not text:
            return 0

        sent = 0
        for char in text:
            self._send_char(char)
            sent += 1
        return sent

    def _send_char(self, char: str) -> None:
        codepoint = ord(char)
        inputs = (INPUT * 2)()
        inputs[0].type = INPUT_KEYBOARD
        inputs[0].ki = KEYBDINPUT(0, codepoint, KEYEVENTF_UNICODE, 0, 0)
        inputs[1].type = INPUT_KEYBOARD
        inputs[1].ki = KEYBDINPUT(0, codepoint, KEYEVENTF_UNICODE | KEYEVENTF_KEYUP, 0, 0)
        ctypes.set_last_error(0)
        inserted = user32.SendInput(2, inputs, ctypes.sizeof(INPUT))
        if inserted != 2:
            error_code = ctypes.get_last_error()
            raise InjectionError(f"Falha ao enviar caractere {char!r} via SendInput. GetLastError={error_code}")


class ClipboardPasteInjector(ForegroundTextInjector):
    def inject(self, text: str) -> int:
        if not text:
            return 0
        self._paste_via_clipboard(text)
        return len(text)

    def _paste_via_clipboard(self, text: str) -> None:
        previous_text = self._get_clipboard_text()
        try:
            self._set_clipboard_text(text)
            self._send_ctrl_v()
            time.sleep(0.08)
        finally:
            if previous_text is not None:
                try:
                    self._set_clipboard_text(previous_text)
                except InjectionError:
                    pass

    def _send_ctrl_v(self) -> None:
        inputs = (INPUT * 4)()
        inputs[0].type = INPUT_KEYBOARD
        inputs[0].ki = KEYBDINPUT(VK_CONTROL, 0, 0, 0, 0)
        inputs[1].type = INPUT_KEYBOARD
        inputs[1].ki = KEYBDINPUT(VK_V, 0, 0, 0, 0)
        inputs[2].type = INPUT_KEYBOARD
        inputs[2].ki = KEYBDINPUT(VK_V, 0, KEYEVENTF_KEYUP, 0, 0)
        inputs[3].type = INPUT_KEYBOARD
        inputs[3].ki = KEYBDINPUT(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0, 0)
        ctypes.set_last_error(0)
        inserted = user32.SendInput(4, inputs, ctypes.sizeof(INPUT))
        if inserted != 4:
            error_code = ctypes.get_last_error()
            raise InjectionError(f"Falha ao acionar Ctrl+V. GetLastError={error_code}")

    def _get_clipboard_text(self) -> str | None:
        self._open_clipboard()
        try:
            if not user32.IsClipboardFormatAvailable(CF_UNICODETEXT):
                return None
            handle = user32.GetClipboardData(CF_UNICODETEXT)
            if not handle:
                return None
            locked = kernel32.GlobalLock(handle)
            if not locked:
                return None
            try:
                return ctypes.wstring_at(locked)
            finally:
                kernel32.GlobalUnlock(handle)
        finally:
            user32.CloseClipboard()

    def _set_clipboard_text(self, text: str) -> None:
        self._open_clipboard()
        try:
            if not user32.EmptyClipboard():
                raise InjectionError("Falha ao limpar o clipboard.")
            data = ctypes.create_unicode_buffer(text + "\0")
            size = ctypes.sizeof(data)
            handle = kernel32.GlobalAlloc(GMEM_MOVEABLE, size)
            if not handle:
                raise InjectionError("Falha ao alocar memoria para clipboard.")
            locked = kernel32.GlobalLock(handle)
            if not locked:
                raise InjectionError("Falha ao bloquear memoria do clipboard.")
            try:
                ctypes.memmove(locked, ctypes.addressof(data), size)
            finally:
                kernel32.GlobalUnlock(handle)
            if not user32.SetClipboardData(CF_UNICODETEXT, handle):
                raise InjectionError("Falha ao gravar texto no clipboard.")
        finally:
            user32.CloseClipboard()

    def _open_clipboard(self) -> None:
        for _ in range(10):
            if user32.OpenClipboard(None):
                return
            time.sleep(0.02)
        error_code = ctypes.get_last_error()
        raise InjectionError(f"Nao foi possivel abrir o clipboard. GetLastError={error_code}")


class AutoTextInjector(ForegroundTextInjector):
    def __init__(self) -> None:
        super().__init__()
        self.clipboard_injector = ClipboardPasteInjector()
        self.sendinput_injector = SendInputTextInjector()

    def inject(self, text: str) -> int:
        try:
            return self.clipboard_injector.inject(text)
        except InjectionError:
            return self.sendinput_injector.inject(text)


def create_injector(mode: str) -> ForegroundTextInjector:
    if mode == "auto":
        return AutoTextInjector()
    if mode == "clipboard":
        return ClipboardPasteInjector()
    if mode == "sendinput":
        return SendInputTextInjector()
    raise InjectionError(f"Modo de injecao invalido: {mode}")
