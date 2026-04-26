from __future__ import annotations

from dataclasses import dataclass, field

from config import GestureConfig, gesture_cfg
from core.gesture_recognizer import GestureType


@dataclass
class GestureStateMachine:
    config: GestureConfig = field(default_factory=lambda: gesture_cfg)
    current_gesture: GestureType = GestureType.REST

    _candidate: GestureType = field(default=GestureType.REST, init=False)
    _candidate_count: int = field(default=0, init=False)
    _confirm_threshold: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        self._confirm_threshold = int(self.config.GESTURE_CONFIRM_FRAMES)

    def update(self, new_gesture: GestureType) -> GestureType:
        """
        Ritorna il gesto confermato solo dopo
        GESTURE_CONFIRM_FRAMES frame consecutivi con lo stesso gesto.
        REST bypassa il contatore (transizione immediata).
        """

        if new_gesture == GestureType.REST:
            self.current_gesture = GestureType.REST
            self._candidate = GestureType.REST
            self._candidate_count = 0
            return self.current_gesture

        if new_gesture == self.current_gesture:
            self._candidate = new_gesture
            self._candidate_count = 0
            return self.current_gesture

        if new_gesture != self._candidate:
            self._candidate = new_gesture
            self._candidate_count = 1
        else:
            self._candidate_count += 1

        if self._candidate_count >= self._confirm_threshold:
            self.current_gesture = self._candidate
            self._candidate_count = 0

        return self.current_gesture

