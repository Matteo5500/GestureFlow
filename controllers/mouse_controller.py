# PERMESSI RICHIESTI: System Preferences → Privacy & Security
# → Accessibility → aggiungi Terminal (o il tuo IDE)
# Senza questi permessi, il mouse non si muoverà.

from __future__ import annotations

import time

try:
    import pyautogui  # type: ignore
except Exception:  # pragma: no cover
    pyautogui = None  # type: ignore

try:
    from pynput.mouse import Button, Controller as MouseCtrl  # type: ignore
except Exception:  # pragma: no cover
    Button = None  # type: ignore
    MouseCtrl = None  # type: ignore

from config import MouseConfig, gesture_cfg
from utils.screen_utils import normalize_to_screen
from utils.smoothing import EMAFilter


if pyautogui is not None:
    pyautogui.FAILSAFE = False  # Disabilita il failsafe corner
    pyautogui.PAUSE = 0  # Nessun delay tra comandi


class MouseController:
    def __init__(self, mouse_cfg: MouseConfig, screen_size: tuple):
        if pyautogui is None or MouseCtrl is None or Button is None:  # pragma: no cover
            raise RuntimeError(
                "Dipendenze mouse non disponibili. Installa con:\n"
                "pip install -r requirements.txt"
            )
        self._cfg = mouse_cfg
        self._screen_w = int(screen_size[0])
        self._screen_h = int(screen_size[1])

        smoothing_factor = float(self._cfg.SMOOTHING_FACTOR)
        smoothing_factor = 0.0 if smoothing_factor < 0.0 else 1.0 if smoothing_factor > 1.0 else smoothing_factor
        alpha = 1.0 - smoothing_factor
        self._ema = EMAFilter(alpha=alpha)

        self._pynput_mouse = MouseCtrl()
        self._last_click_time = 0.0

    def move(self, norm_x: float, norm_y: float) -> None:
        sx, sy = self._ema.smooth(float(norm_x), float(norm_y))
        x, y = normalize_to_screen(
            norm_x=sx,
            norm_y=sy,
            screen_w=self._screen_w,
            screen_h=self._screen_h,
            margin=int(self._cfg.SCREEN_MARGIN),
        )
        pyautogui.moveTo(x, y, duration=0)

    def click(self) -> None:
        """Esegui click sinistro con pynput."""
        now = time.time()
        self._pynput_mouse.press(Button.left)
        time.sleep(0.05)  # 50ms — necessario su macOS
        self._pynput_mouse.release(Button.left)
        self._last_click_time = now

    def double_click(self) -> None:
        self.click()
        time.sleep(0.08)
        self.click()

    def reset_smoothing(self) -> None:
        self._ema.reset()

