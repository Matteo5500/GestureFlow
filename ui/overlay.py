from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from core.gesture_recognizer import GestureType
from core.hand_tracker import HandData

try:
    import cv2  # type: ignore
except Exception:  # pragma: no cover
    cv2 = None  # type: ignore

HAND_CONNECTIONS = [
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 4),  # pollice
    (0, 5),
    (5, 6),
    (6, 7),
    (7, 8),  # indice
    (0, 9),
    (9, 10),
    (10, 11),
    (11, 12),  # medio
    (0, 13),
    (13, 14),
    (14, 15),
    (15, 16),  # anulare
    (0, 17),
    (17, 18),
    (18, 19),
    (19, 20),  # mignolo
    (5, 9),
    (9, 13),
    (13, 17),  # nocche
]


def _hex_to_bgr(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return b, g, r


GESTURE_COLORS: dict[GestureType, tuple[int, int, int]] = {
    GestureType.REST: _hex_to_bgr("#888888"),
    GestureType.NAVIGATE: _hex_to_bgr("#00FF88"),
    GestureType.CLICK: _hex_to_bgr("#00BBFF"),
    GestureType.SCROLL: _hex_to_bgr("#AA44FF"),
    GestureType.VOLUME: _hex_to_bgr("#FF8800"),
}


@dataclass
class HandOverlay:
    def _draw_skeleton(self, frame: np.ndarray, hand: HandData, color: tuple[int, int, int]) -> None:
        h, w = frame.shape[:2]

        for start_idx, end_idx in HAND_CONNECTIONS:
            pt1 = hand.landmarks[start_idx]
            pt2 = hand.landmarks[end_idx]
            x1, y1 = int(pt1.x * w), int(pt1.y * h)
            x2, y2 = int(pt2.x * w), int(pt2.y * h)

            # Specchia X perché il frame mostrato è flippato
            x1 = w - x1
            x2 = w - x2
            cv2.line(frame, (x1, y1), (x2, y2), color, 2)

        for lm in hand.landmarks:
            x = int((1 - lm.x) * w)
            y = int(lm.y * h)
            cv2.circle(frame, (x, y), 4, color, -1)

    def _draw_center_text(self, frame: np.ndarray, text: str, color: tuple[int, int, int]) -> None:
        h, w = frame.shape[:2]
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 0.9
        thickness = 2
        (tw, th), _ = cv2.getTextSize(text, font, scale, thickness)
        x = max(0, (w - tw) // 2)
        y = max(th + 10, (h + th) // 2)
        cv2.putText(frame, text, (x, y), font, scale, color, thickness, cv2.LINE_AA)

    def _badge(self, frame: np.ndarray, label: str, color: tuple[int, int, int]) -> None:
        x0, y0 = 10, 10
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 0.7
        thickness = 2
        pad_x, pad_y = 10, 8

        (tw, th), _ = cv2.getTextSize(label, font, scale, thickness)
        x1 = x0 + pad_x * 2 + tw
        y1 = y0 + pad_y * 2 + th

        cv2.rectangle(frame, (x0, y0), (x1, y1), color, -1)
        cv2.putText(
            frame,
            label,
            (x0 + pad_x, y0 + pad_y + th),
            font,
            scale,
            (255, 255, 255),
            thickness,
            cv2.LINE_AA,
        )

    def _draw_fps(self, frame: np.ndarray, fps: float) -> None:
        h, w = frame.shape[:2]
        text = f"{fps:.1f} FPS"
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 0.55
        thickness = 1
        (tw, th), _ = cv2.getTextSize(text, font, scale, thickness)
        cv2.putText(
            frame,
            text,
            (w - tw - 10, 10 + th),
            font,
            scale,
            (255, 255, 255),
            thickness,
            cv2.LINE_AA,
        )

    def _draw_volume_bar(self, frame: np.ndarray, volume_level: int) -> None:
        h, w = frame.shape[:2]
        bar_w = 18
        pad = 12
        x0 = w - pad - bar_w
        y0 = 60
        y1 = h - 80
        cv2.rectangle(frame, (x0, y0), (x0 + bar_w, y1), (255, 255, 255), 1)

        level = 0 if volume_level < 0 else 100 if volume_level > 100 else int(volume_level)
        fill_h = int(((y1 - y0) * level) / 100)
        fy0 = y1 - fill_h
        cv2.rectangle(frame, (x0 + 2, fy0), (x0 + bar_w - 2, y1 - 2), _hex_to_bgr("#FF8800"), -1)
        cv2.putText(
            frame,
            f"{level}%",
            (x0 - 10, y0 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )

    def _draw_highlight_circle(self, frame: np.ndarray, hand: HandData, idx: int, color: tuple[int, int, int]) -> tuple[int, int]:
        h, w = frame.shape[:2]
        p = hand.landmarks[idx]
        cx = int((1.0 - float(p.x)) * w)
        cy = int(float(p.y) * h)
        cv2.circle(frame, (cx, cy), 10, color, 2, cv2.LINE_AA)
        cv2.circle(frame, (cx, cy), 3, color, -1, cv2.LINE_AA)
        return cx, cy

    def draw(
        self,
        frame: np.ndarray,
        hand: HandData | None,
        gesture: GestureType,
        fps: float,
        volume_level: int | None = None,
    ) -> np.ndarray:
        if cv2 is None:  # pragma: no cover
            raise RuntimeError(
                "opencv-python (cv2) non disponibile. Installa le dipendenze con:\n"
                "pip install -r requirements.txt"
            )
        out = frame.copy()

        if hand is None:
            self._draw_center_text(out, "Nessuna mano rilevata", _hex_to_bgr("#888888"))
            self._draw_fps(out, fps)
            return out

        # Choose skeleton/gesture color
        if not hand.is_front_facing:
            self._badge(out, "REST", _hex_to_bgr("#888888"))
            cv2.putText(
                out,
                "Modalità Riposo",
                (10, 55),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2,
                cv2.LINE_AA,
            )
            draw_color = _hex_to_bgr("#AAAAAA")
        else:
            draw_color = GESTURE_COLORS.get(gesture, _hex_to_bgr("#888888"))
            self._badge(out, gesture.name, draw_color)

        # 1) Draw skeleton manually (Tasks API has no drawing_utils)
        self._draw_skeleton(out, hand, draw_color)

        # 2) Highlight active landmarks
        if hand.is_front_facing:
            if gesture == GestureType.NAVIGATE:
                self._draw_highlight_circle(out, hand, 8, draw_color)
            elif gesture == GestureType.CLICK:
                x1, y1 = self._draw_highlight_circle(out, hand, 4, draw_color)
                x2, y2 = self._draw_highlight_circle(out, hand, 8, draw_color)
                cv2.line(out, (x1, y1), (x2, y2), draw_color, 2, cv2.LINE_AA)
            elif gesture == GestureType.SCROLL:
                self._draw_highlight_circle(out, hand, 8, draw_color)
                self._draw_highlight_circle(out, hand, 12, draw_color)
            elif gesture == GestureType.VOLUME:
                self._draw_highlight_circle(out, hand, 4, draw_color)
                self._draw_highlight_circle(out, hand, 12, draw_color)

        # 4) FPS top-right
        self._draw_fps(out, fps)

        # 5) Volume bar
        if gesture == GestureType.VOLUME and volume_level is not None:
            self._draw_volume_bar(out, int(volume_level))

        return out

