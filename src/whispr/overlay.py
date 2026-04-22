from __future__ import annotations

import math
import queue
import threading
import tkinter as tk


class CaptureIndicator:
    def show(self) -> None:
        raise NotImplementedError

    def hide(self) -> None:
        raise NotImplementedError

    def close(self) -> None:
        raise NotImplementedError


class NullCaptureIndicator(CaptureIndicator):
    def show(self) -> None:
        return

    def hide(self) -> None:
        return

    def close(self) -> None:
        return


class TkCaptureIndicator(CaptureIndicator):
    def __init__(self, position: str = "top-right") -> None:
        self.position = position
        self._commands: queue.Queue[str] = queue.Queue()
        self._ready = threading.Event()
        self._visible = False
        self._thread = threading.Thread(target=self._run, name="whispr-indicator", daemon=True)
        self._thread.start()
        self._ready.wait(timeout=2)

    def show(self) -> None:
        self._commands.put("show")

    def hide(self) -> None:
        self._commands.put("hide")

    def close(self) -> None:
        self._commands.put("close")

    def _run(self) -> None:
        root = tk.Tk()
        root.withdraw()
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.attributes("-alpha", 0.92)

        background = "#111111"
        transparent = "#ff00ff"
        root.configure(bg=transparent)
        try:
            root.wm_attributes("-transparentcolor", transparent)
        except tk.TclError:
            root.configure(bg=background)

        width = 112
        height = 44
        canvas = tk.Canvas(root, width=width, height=height, bg=transparent, highlightthickness=0, bd=0)
        canvas.pack()
        self._draw_shell(canvas, width, height)
        bars = self._create_wave_bars(canvas)
        phase_state = {"value": 0.0}

        self._position_window(root, width, height)

        def animate() -> None:
            if self._visible:
                phase_state["value"] += 0.35
                self._update_wave_bars(canvas, bars, phase_state["value"])
            root.after(45, animate)

        def pump() -> None:
            while True:
                try:
                    command = self._commands.get_nowait()
                except queue.Empty:
                    break
                if command == "show":
                    self._visible = True
                    root.deiconify()
                    root.lift()
                elif command == "hide":
                    self._visible = False
                    root.withdraw()
                elif command == "close":
                    self._visible = False
                    root.destroy()
                    return
            root.after(50, pump)

        self._ready.set()
        root.after(45, animate)
        root.after(50, pump)
        root.mainloop()

    def _draw_shell(self, canvas: tk.Canvas, width: int, height: int) -> None:
        canvas.create_rectangle(2, 2, width - 2, height - 2, fill="#121417", outline="#2f343c", width=2)
        canvas.create_oval(12, 12, 24, 24, fill="#ff5a5f", outline="#ff9ea1", width=1)
        canvas.create_text(79, 22, text="REC", fill="white", font=("Segoe UI", 10, "bold"))

    def _create_wave_bars(self, canvas: tk.Canvas) -> list[int]:
        bars: list[int] = []
        x_positions = [34, 44, 54, 64]
        for x in x_positions:
            bars.append(
                canvas.create_rectangle(
                    x,
                    18,
                    x + 6,
                    28,
                    fill="#73e0a9",
                    outline="#9ef0c4",
                    width=1,
                )
            )
        return bars

    def _update_wave_bars(self, canvas: tk.Canvas, bars: list[int], phase: float) -> None:
        center_y = 22
        min_half = 4
        max_half = 11
        for index, bar in enumerate(bars):
            offset = phase + (index * 0.8)
            amplitude = (math.sin(offset) + 1) / 2
            half_height = min_half + int(amplitude * (max_half - min_half))
            x1, _, x2, _ = canvas.coords(bar)
            canvas.coords(bar, x1, center_y - half_height, x2, center_y + half_height)

    def _position_window(self, root: tk.Tk, width: int, height: int) -> None:
        root.update_idletasks()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        margin = 24

        x = margin if "left" in self.position else screen_width - width - margin
        y = margin if "top" in self.position else screen_height - height - margin
        root.geometry(f"{width}x{height}+{x}+{y}")


def create_capture_indicator(enabled: bool, position: str) -> CaptureIndicator:
    if not enabled:
        return NullCaptureIndicator()
    return TkCaptureIndicator(position=position)
