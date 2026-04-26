from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

from config import TrackingConfig, tracking_cfg
from core.hand_tracker import HandData, LandmarkPoint


class GestureType(Enum):
    REST = auto()  # mano non attiva o non visibile
    NAVIGATE = auto()  # solo indice alzato → muovi mouse
    CLICK = auto()  # pinch pollice+indice
    SCROLL = auto()  # indice+medio alzati
    VOLUME = auto()  # pinch pollice+medio (distanza variabile)


@dataclass
class GestureRecognizer:
    config: TrackingConfig = field(default_factory=lambda: tracking_cfg)
    _config: TrackingConfig = field(init=False, repr=False)

    def __post_init__(self) -> None:
        # Alias usato per debug print richiesto
        self._config = self.config

    def _is_finger_up(self, tip: LandmarkPoint, mcp: LandmarkPoint) -> bool:
        """
        Il dito è alzato se la punta è sopra la nocca
        di almeno il 4% dell'altezza normalizzata.
        """
        return tip.y < mcp.y - 0.04

    def recognize(self, hand: HandData) -> GestureType:
        if hand is None or not hand.is_front_facing:
            return GestureType.REST

        # Calcola distanze pinch
        pinch_index = self._distance(hand.thumb_tip, hand.index_tip)
        pinch_middle = self._distance(hand.thumb_tip, hand.middle_tip)

        # Calcola quali dita sono alzate
        # Un dito è alzato se la punta è più in alto della nocca
        index_up = hand.index_tip.y < hand.index_mcp.y - 0.04
        middle_up = hand.middle_tip.y < hand.middle_mcp.y - 0.04

        # 1. CLICK: pinch pollice+indice stretto
        if pinch_index < self._config.PINCH_THRESHOLD:
            return GestureType.CLICK

        # 2. VOLUME: pinch pollice+medio stretto
        if pinch_middle < self._config.PINCH_THRESHOLD:
            return GestureType.VOLUME

        # 3. SCROLL: indice E medio alzati (nessun pinch)
        if index_up and middle_up:
            return GestureType.SCROLL

        # 4. NAVIGATE: almeno indice alzato
        if index_up:
            return GestureType.NAVIGATE

        # 5. Tutto il resto
        return GestureType.REST

    def _distance(self, a: LandmarkPoint, b: LandmarkPoint) -> float:
        # Distanza euclidea 2D (ignora z)
        dx = a.x - b.x
        dy = a.y - b.y
        return (dx * dx + dy * dy) ** 0.5

