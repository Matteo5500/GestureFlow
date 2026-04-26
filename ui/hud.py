from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from core.gesture_recognizer import GestureType
from ui.overlay import GESTURE_COLORS, _hex_to_bgr

try:
    import cv2  # type: ignore
except Exception:  # pragma: no cover
    cv2 = None  # type: ignore


@dataclass
class HUDPanel:
    """
    Pannello informativo aggiuntivo disegnato
    in basso nel frame OpenCV.
    """

    _frame_count: int = field(default=0, init=False)

    def draw_status_bar(
        self,
        frame: np.ndarray,
        gesture: GestureType,
        is_active: bool,
        extra_info: dict,
    ) -> np.ndarray:
        if cv2 is None:  # pragma: no cover
            raise RuntimeError(
                "opencv-python (cv2) non disponibile. Installa le dipendenze con:\n"
                "pip install -r requirements.txt"
            )
        out = frame.copy()
        h, w = out.shape[:2]

        bar_h = 60
        y0 = max(0, h - bar_h)

        # Semi-transparent black background
        overlay = out.copy()
        cv2.rectangle(overlay, (0, y0), (w, h), (0, 0, 0), -1)
        out = cv2.addWeighted(overlay, 0.45, out, 0.55, 0)

        color = GESTURE_COLORS.get(gesture, _hex_to_bgr("#888888"))

        # Left: colored circle + gesture name
        cx, cy = 22, y0 + bar_h // 2
        cv2.circle(out, (cx, cy), 8, color, -1, cv2.LINE_AA)
        cv2.putText(
            out,
            gesture.name,
            (cx + 16, cy + 6),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        # Middle: active/rest label
        state_text = "ATTIVO" if is_active else "RIPOSO"
        state_color = (0, 255, 0) if is_active else _hex_to_bgr("#888888")
        cv2.putText(
            out,
            state_text,
            (180, cy + 6),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            state_color,
            2,
            cv2.LINE_AA,
        )

        # Right side extras
        if gesture == GestureType.VOLUME and "volume_level" in extra_info:
            vol = int(extra_info.get("volume_level") or 0)
            text = f"VOL: {vol}%"
            (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.65, 2)
            cv2.putText(
                out,
                text,
                (w - tw - 16, cy + 6),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

        if gesture == GestureType.SCROLL:
            # Animated arrow (blink every 10 frames)
            self._frame_count += 1
            show = (self._frame_count // 10) % 2 == 0

            direction = str(extra_info.get("scroll_direction") or "")
            arrow = ""
            if direction.lower().startswith("up"):
                arrow = "▲"
            elif direction.lower().startswith("down"):
                arrow = "▼"
            else:
                # Default: alternate up/down to show activity
                arrow = "▲" if (self._frame_count // 10) % 2 == 0 else "▼"

            if show:
                (tw, th), _ = cv2.getTextSize(arrow, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
                cv2.putText(
                    out,
                    arrow,
                    (w - tw - 24, cy + 12),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

        return out

