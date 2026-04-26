from __future__ import annotations

try:
    import pyautogui  # type: ignore
except Exception:  # pragma: no cover
    pyautogui = None  # type: ignore

from config import ScrollConfig


class ScrollController:
    def __init__(self, scroll_cfg: ScrollConfig):
        if pyautogui is None:  # pragma: no cover
            raise RuntimeError(
                "pyautogui non disponibile. Installa le dipendenze con:\n"
                "pip install -r requirements.txt"
            )

        self._cfg = scroll_cfg
        self._anchor_y: float | None = None

    def update(self, norm_y: float) -> None:
        if self._anchor_y is None:
            # Attivazione gesto SCROLL: salva anchor
            self._anchor_y = float(norm_y)
            return

        delta = float(norm_y) - self._anchor_y

        if abs(delta) > float(self._cfg.SCROLL_THRESHOLD):
            scroll_amount = int(delta * float(self._cfg.SCROLL_SPEED) * -20)

            # Edge case: limita lo scroll per frame
            if scroll_amount > 15:
                scroll_amount = 15
            elif scroll_amount < -15:
                scroll_amount = -15

            if scroll_amount != 0:
                pyautogui.scroll(scroll_amount)

    def reset(self) -> None:
        self._anchor_y = None

