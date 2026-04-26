from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CameraConfig:
    CAMERA_INDEX: int = 0
    FRAME_WIDTH: int = 640
    FRAME_HEIGHT: int = 480
    FPS_TARGET: int = 30


@dataclass
class TrackingConfig:
    MAX_HANDS: int = 1
    DETECTION_CONFIDENCE: float = 0.8
    TRACKING_CONFIDENCE: float = 0.7
    # Soglia distanza per pinch (0.0–1.0, normalizzata)
    PINCH_THRESHOLD: float = 0.040
    # Minima visibilità landmark per considerarlo affidabile
    MIN_LANDMARK_VISIBILITY: float = 0.6


@dataclass
class MouseConfig:
    # Fattore di smoothing (0=nessuno, 1=massimo)
    SMOOTHING_FACTOR: float = 0.5
    # Margine in pixel dai bordi dello schermo
    SCREEN_MARGIN: int = 0
    # Velocità di mapping (moltiplicatore)
    SPEED_MULTIPLIER: float = 1.0


@dataclass
class ScrollConfig:
    SCROLL_SPEED: float = 3.0
    # Soglia minima movimento verticale per triggerare scroll
    SCROLL_THRESHOLD: float = 0.02


@dataclass
class VolumeConfig:
    # Distanza minima e massima per mapping 0%–100% volume
    MIN_DISTANCE: float = 0.03
    MAX_DISTANCE: float = 0.25


@dataclass
class GestureConfig:
    # Tempo massimo per un pinch rapido (click), in secondi
    CLICK_MAX_DURATION: float = 0.6
    # Tempo massimo tra due click per doppio click
    DOUBLE_CLICK_INTERVAL: float = 0.5
    # Frame consecutivi necessari per confermare un gesto
    GESTURE_CONFIRM_FRAMES: int = 1


camera_cfg = CameraConfig()
tracking_cfg = TrackingConfig()
mouse_cfg = MouseConfig()
scroll_cfg = ScrollConfig()
volume_cfg = VolumeConfig()
gesture_cfg = GestureConfig()

