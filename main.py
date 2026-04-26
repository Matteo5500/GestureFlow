from __future__ import annotations

import time

import cv2

from config import camera_cfg, gesture_cfg, mouse_cfg, scroll_cfg, tracking_cfg, volume_cfg

from controllers.mouse_controller import MouseController
from controllers.scroll_controller import ScrollController
from controllers.volume_controller import VolumeController
from core.gesture_recognizer import GestureRecognizer, GestureType
from core.gesture_state import GestureStateMachine
from core.hand_tracker import HandTracker
from ui.hud import HUDPanel
from ui.overlay import HandOverlay
from utils.screen_utils import get_screen_size


WINDOW_TITLE = "Hand Gesture Controller"


def _open_camera() -> cv2.VideoCapture:
    cap = cv2.VideoCapture(camera_cfg.CAMERA_INDEX)
    if not cap.isOpened():
        raise RuntimeError(
            "Webcam non trovata. Verifica\n"
            "l'indice in config.py → CameraConfig.CAMERA_INDEX"
        )

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, float(camera_cfg.FRAME_WIDTH))
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, float(camera_cfg.FRAME_HEIGHT))
    cap.set(cv2.CAP_PROP_FPS, float(camera_cfg.FPS_TARGET))
    return cap


def main() -> None:
    cap: cv2.VideoCapture | None = None
    try:
        cap = _open_camera()

        cv2.namedWindow(WINDOW_TITLE, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
        cv2.resizeWindow(WINDOW_TITLE, 800, 600)

        hand_tracker = HandTracker(tracking_cfg)
        recognizer = GestureRecognizer(tracking_cfg)
        state = GestureStateMachine(gesture_cfg)
        overlay = HandOverlay()
        hud = HUDPanel()

        screen_w, screen_h = get_screen_size()
        mouse_controller = MouseController(mouse_cfg, (screen_w, screen_h))
        scroll_controller = ScrollController(scroll_cfg)
        volume_controller = VolumeController(volume_cfg)

        prev_t = time.perf_counter()
        fps_smoothed = 0.0

        prev_confirmed = GestureType.REST
        click_pending = False
        volume_level: int | None = None

        while True:
            # 1) cap.read() → frame grezzo
            ok, frame = cap.read()
            if not ok or frame is None:
                break

            # 2) hand_tracker.process_frame(frame) → hand_data (frame NON specchiato)
            hand = hand_tracker.process_frame(frame)

            # 3) gesture_recognizer.recognize(hand_data) → raw_gesture
            raw_gesture = recognizer.recognize(hand)
            # 4) state_machine.update(raw_gesture) → confirmed_gesture
            confirmed = state.update(raw_gesture)

            # Reset controller of previous gesture when gesture changes
            if confirmed != prev_confirmed:
                if prev_confirmed == GestureType.SCROLL:
                    scroll_controller.reset()
                elif prev_confirmed == GestureType.NAVIGATE:
                    mouse_controller.reset_smoothing()
                elif prev_confirmed == GestureType.VOLUME:
                    volume_controller = VolumeController(volume_cfg)

            # CLICK (event-based): pending when entering CLICK, click when exiting CLICK
            if confirmed == GestureType.CLICK and prev_confirmed != GestureType.CLICK:
                click_pending = True
            if confirmed != GestureType.CLICK and prev_confirmed == GestureType.CLICK and click_pending:
                mouse_controller.click()
                click_pending = False

            # 5) Switch su confirmed_gesture
            if confirmed == GestureType.NAVIGATE:
                if hand is not None:
                    mouse_controller.move(hand.index_tip.x, hand.index_tip.y)
            elif confirmed == GestureType.SCROLL:
                if hand is not None:
                    scroll_controller.update(hand.index_tip.y)
            elif confirmed == GestureType.VOLUME:
                if hand is not None:
                    volume_level = volume_controller.update(hand.thumb_tip, hand.middle_tip)
            elif confirmed == GestureType.REST:
                mouse_controller.reset_smoothing()
                scroll_controller.reset()
                volume_controller = VolumeController(volume_cfg)
                volume_level = None
                click_pending = False
            else:
                # CLICK: handled by event logic above
                pass

            # 6) frame_display = cv2.flip(frame, 1)  # specchia per display
            frame_display = cv2.flip(frame, 1)

            # 7) overlay.draw(...)
            frame_display = overlay.draw(
                frame=frame_display,
                hand=hand,
                gesture=confirmed,
                fps=fps_smoothed,
                volume_level=volume_level if confirmed == GestureType.VOLUME else None,
            )

            # 8) hud.draw_status_bar(...)
            extra_info: dict = {}
            if confirmed == GestureType.VOLUME and volume_level is not None:
                extra_info["volume_level"] = volume_level

            frame_display = hud.draw_status_bar(
                frame=frame_display,
                gesture=confirmed,
                is_active=(confirmed != GestureType.REST),
                extra_info=extra_info,
            )

            # 9) cv2.imshow(...)
            cv2.imshow(WINDOW_TITLE, frame_display)

            # 10) Calcola e aggiorna FPS
            now_t = time.perf_counter()
            dt = now_t - prev_t
            prev_t = now_t
            fps = (1.0 / dt) if dt > 0 else 0.0
            fps_smoothed = (0.9 * fps_smoothed) + (0.1 * fps) if fps_smoothed else fps

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break

            prev_confirmed = confirmed

    except RuntimeError as e:
        print(str(e))
    finally:
        try:
            if "hand_tracker" in locals():
                hand_tracker.release()
        except Exception:
            pass
        if cap is not None:
            cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

