from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np

from config import TrackingConfig

import mediapipe as mp
from mediapipe.tasks import python as mp_tasks
from mediapipe.tasks.python import vision as mp_vision
from mediapipe.tasks.python.components.containers import NormalizedLandmark


# MediaPipe landmark indices (reference only; do not change)
WRIST = 0
THUMB_TIP = 4
INDEX_MCP = 5
INDEX_TIP = 8
MIDDLE_MCP = 9
MIDDLE_TIP = 12
RING_TIP = 16
PINKY_TIP = 20


@dataclass
class LandmarkPoint:
    x: float  # 0.0–1.0 normalizzato rispetto alla larghezza frame
    y: float  # 0.0–1.0 normalizzato rispetto all'altezza frame
    z: float  # profondità relativa (negativo = verso cam)
    visibility: float  # 0.0–1.0


@dataclass
class HandData:
    landmarks: list[LandmarkPoint]  # 21 punti
    handedness: str  # "Left" o "Right"
    is_front_facing: bool  # True se palmo verso camera
    wrist: LandmarkPoint  # shortcut landmarks[0]
    index_tip: LandmarkPoint  # shortcut landmarks[8]
    middle_tip: LandmarkPoint  # shortcut landmarks[12]
    ring_tip: LandmarkPoint  # shortcut landmarks[16]
    pinky_tip: LandmarkPoint  # shortcut landmarks[20]
    thumb_tip: LandmarkPoint  # shortcut landmarks[4]
    index_mcp: LandmarkPoint  # landmarks[5] (nocca indice)
    middle_mcp: LandmarkPoint  # landmarks[9]


class HandTracker:
    def __init__(self, config: TrackingConfig):
        self._config = config

        base_options = mp_tasks.BaseOptions(model_asset_path=self._get_model_path())
        options = mp_vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=config.MAX_HANDS,
            min_hand_detection_confidence=config.DETECTION_CONFIDENCE,
            min_hand_presence_confidence=config.TRACKING_CONFIDENCE,
            min_tracking_confidence=config.TRACKING_CONFIDENCE,
        )
        self._landmarker = mp_vision.HandLandmarker.create_from_options(options)
        self._last_results: Any = None

    def _get_model_path(self) -> str:
        """
        Scarica il modello se non esiste già.
        Salva in: models/hand_landmarker.task
        """
        import os
        import urllib.request

        os.makedirs("models", exist_ok=True)
        model_path = "models/hand_landmarker.task"
        if not os.path.exists(model_path):
            print("Download modello MediaPipe...")
            url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
            urllib.request.urlretrieve(url, model_path)
            print("Modello scaricato.")
        return model_path

    def process_frame(self, frame: np.ndarray) -> HandData | None:
        """
        frame è BGR (da OpenCV).
        Converti in RGB per MediaPipe.
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = self._landmarker.detect(mp_image)
        self._last_results = result

        if not result.hand_landmarks:
            return None

        # Prendi la prima mano
        landmarks_raw: list[NormalizedLandmark] = result.hand_landmarks[0]
        handedness_label = result.handedness[0][0].category_name  # "Left" o "Right"

        landmarks: list[LandmarkPoint] = []
        for lm in landmarks_raw:
            landmarks.append(
                LandmarkPoint(
                    x=float(lm.x),
                    y=float(lm.y),
                    z=float(lm.z),
                    visibility=1.0,
                )
            )

        hand = HandData(
            landmarks=landmarks,
            handedness=handedness_label,
            is_front_facing=self._compute_front_facing(landmarks, handedness_label),
            wrist=landmarks[WRIST],
            index_tip=landmarks[INDEX_TIP],
            middle_tip=landmarks[MIDDLE_TIP],
            ring_tip=landmarks[RING_TIP],
            pinky_tip=landmarks[PINKY_TIP],
            thumb_tip=landmarks[THUMB_TIP],
            index_mcp=landmarks[INDEX_MCP],
            middle_mcp=landmarks[MIDDLE_MCP],
        )

        if hand:
            print(
                f"hand={hand.handedness} "
                f"front={hand.is_front_facing} "
                f"wrist_x={hand.wrist.x:.2f} "
                f"idx_mcp_x={hand.index_mcp.x:.2f}"
            )
        return hand

    def _compute_front_facing(self, landmarks: list[LandmarkPoint], handedness: str) -> bool:
        wrist = landmarks[0]
        index_mcp = landmarks[5]
        middle_mcp = landmarks[9]
        pinky_mcp = landmarks[17]

        # Usa la larghezza della mano come riferimento
        hand_width = abs(index_mcp.x - pinky_mcp.x)

        if handedness == "Right":
            # Palmo visibile: polso a destra delle nocche
            return (wrist.x - middle_mcp.x) > -hand_width * 0.5
        # Mano sinistra: opposto
        return (middle_mcp.x - wrist.x) > -hand_width * 0.5

    def get_raw_results(self) -> Any:
        return self._last_results

    def release(self) -> None:
        self._landmarker.close()

