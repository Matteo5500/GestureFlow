from __future__ import annotations

import subprocess

import numpy as np

from config import VolumeConfig
from core.hand_tracker import LandmarkPoint


class VolumeController:
    def __init__(self, volume_cfg: VolumeConfig):
        self._cfg = volume_cfg
        self._current_level: int | None = None

    def update(self, thumb: LandmarkPoint, middle: LandmarkPoint) -> int:
        # 1) distanza euclidea 2D tra thumb e middle
        dx = float(thumb.x) - float(middle.x)
        dy = float(thumb.y) - float(middle.y)
        dist = float((dx * dx + dy * dy) ** 0.5)

        # 2) map distanza -> [0, 100]
        target = float(
            np.interp(
                dist,
                [float(self._cfg.MIN_DISTANCE), float(self._cfg.MAX_DISTANCE)],
                [0.0, 100.0],
            )
        )
        if target < 0.0:
            target = 0.0
        elif target > 100.0:
            target = 100.0

        # 3) arrotonda al multiplo di 5 più vicino
        target_rounded = int(round(target / 5.0) * 5)
        if target_rounded < 0:
            target_rounded = 0
        elif target_rounded > 100:
            target_rounded = 100

        if self._current_level is None:
            self._current_level = target_rounded
            self._set_volume(self._current_level)
            return self._current_level

        # 4) applica solo se cambia di almeno 5; non più di 5 per frame
        diff = target_rounded - self._current_level
        if abs(diff) >= 5:
            step = 5 if diff > 0 else -5
            new_level = self._current_level + step
            if new_level < 0:
                new_level = 0
            elif new_level > 100:
                new_level = 100
            self._current_level = new_level
            self._set_volume(self._current_level)

        return self._current_level

    def _set_volume(self, level: int) -> None:
        try:
            subprocess.run(
                ["osascript", "-e", f"set volume output volume {int(level)}"],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            err = (e.stderr or "").strip()
            if not err:
                err = str(e)
            print(f"[VolumeController] AppleScript error: {err}")

    def get_current_volume(self) -> int:
        try:
            result = subprocess.run(
                ["osascript", "-e", "output volume of (get volume settings)"],
                capture_output=True,
                text=True,
                check=False,
            )
            return int((result.stdout or "").strip())
        except Exception as e:
            print(f"[VolumeController] get_current_volume error: {e}")
            return int(self._current_level or 0)

