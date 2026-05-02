# 🖐️ GestureFlow — Touchless Computer Control via Hand Gestures

> Control your entire computer — mouse, scroll, and volume — using only your hand and a webcam. No mouse. No keyboard. No contact.

![GestureFlow](hand-gesture-controller/img/GestureFlow.gif)
![Navigate-hand-gesture](hand-gesture-controller/img/navigate-hand-gesture.png)
![Click-hand-gesture](hand-gesture-controller/img/click-hand-gesture.png)
![Scroll-hand-gesture](hand-gesture-controller/img/scroll-hand-gesture.png)


---

## Overview

**GestureFlow** is a real-time Human-Computer Interaction (HCI) system that translates hand gestures captured via webcam into system-level commands. Built with MediaPipe's hand landmark detection and OpenCV, it runs at 30 FPS and provides live visual feedback directly on the camera feed.

This project was built as a portfolio piece to explore the intersection of computer vision, real-time signal processing, and operating system control.

---

## Demo

```
✋ Point index finger   →   Move cursor
🤏 Pinch thumb+index   →   Left click
✌️ Index + middle up   →   Scroll page
🤌 Pinch thumb+middle  →   Adjust volume
✊ Fist / palm away    →   Rest mode (no input)
```

---

## Features

- **Real-time hand tracking** at 30 FPS using MediaPipe Hand Landmarker
- **5 distinct gestures** mapped to system actions
- **Exponential smoothing** (EMA filter) for stable, jitter-free cursor movement
- **Adaptive coordinate mapping** — the hand's movement area is mapped to the full screen resolution
- **Rest mode** — commands only activate when the palm faces the camera, preventing accidental input
- **Live visual overlay** — colored skeleton, gesture badge, FPS counter, and volume bar drawn on the webcam feed
- **Event-based click detection** — click fires on pinch *release*, not on hold, for natural interaction

---

## Tech Stack

| Layer | Technology |
|---|---|
| Hand Tracking | MediaPipe Hand Landmarker (Tasks API) |
| Computer Vision | OpenCV 4.10 |
| Mouse Control | PyAutoGUI + pynput |
| Volume Control | macOS AppleScript via subprocess |
| Smoothing | Custom EMA (Exponential Moving Average) filter |
| Language | Python 3.11+ |

---

## Project Structure

```
hand-gesture-controller/
├── main.py                    # Entry point & main loop
├── config.py                  # All tunable parameters (dataclasses)
├── requirements.txt
├── models/
│   └── hand_landmarker.task   # MediaPipe model (downloaded on first run)
├── core/
│   ├── hand_tracker.py        # MediaPipe wrapper → HandData
│   ├── gesture_recognizer.py  # Gesture classification logic
│   └── gesture_state.py       # State machine (debounce & confirmation)
├── controllers/
│   ├── mouse_controller.py    # Cursor movement & click
│   ├── scroll_controller.py   # Vertical scroll
│   └── volume_controller.py   # macOS volume via AppleScript
├── ui/
│   ├── overlay.py             # Skeleton + gesture badge + FPS
│   └── hud.py                 # Status bar at bottom of frame
└── utils/
    ├── smoothing.py           # EMA filter
    └── screen_utils.py        # Coordinate mapping
```

---

## Requirements

- macOS 12 Monterey or later (Apple Silicon and Intel supported)
- Python 3.11+
- Webcam (built-in or external)
- **Accessibility permissions** for mouse control (required — see setup below)

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/gestureflow.git
cd gestureflow/hand-gesture-controller

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
python main.py
```

## macOS Accessibility Permissions (Required)

Mouse and keyboard control requires explicit system permission on macOS.

1. Open **System Settings → Privacy & Security → Accessibility**
2. Click the **+** button and add your terminal app (Terminal, iTerm2, or VS Code)
3. Make sure the toggle is **enabled**

Without this step, the cursor will not move.

---

## Gesture Reference

| Gesture | Hand Shape | Action |
|---|---|---|
| **Navigate** | Index finger extended, others closed | Move mouse cursor |
| **Click** | Pinch thumb + index (quick release) | Left mouse click |
| **Double Click** | Two quick pinches within 0.5s | Double click |
| **Scroll** | Index + middle extended, move hand up/down | Scroll page |
| **Volume** | Pinch thumb + middle, vary distance | Increase / decrease volume |
| **Rest** | Fist closed or palm facing away | No action |

---

## Configuration

All parameters are in `config.py` and can be tuned without touching the logic:

| Parameter | Default | Description |
|---|---|---|
| `PINCH_THRESHOLD` | `0.040` | Distance to trigger a pinch gesture (lower = requires tighter pinch) |
| `SMOOTHING_FACTOR` | `0.5` | Cursor smoothing (0 = raw, 1 = maximum smoothing) |
| `GESTURE_CONFIRM_FRAMES` | `1` | Frames before a gesture is confirmed (higher = more stable, less reactive) |
| `SCROLL_SPEED` | `3.0` | Scroll velocity multiplier |
| `CAMERA_INDEX` | `0` | Webcam index (change if using an external camera) |

---

## How It Works

1. Each frame from the webcam is processed by **MediaPipe Hand Landmarker**, which returns 21 3D landmarks per hand
2. The **GestureRecognizer** classifies the current hand shape into one of 5 gesture types based on finger positions and pinch distances
3. The **GestureStateMachine** debounces rapid changes, requiring N consecutive frames of the same gesture before confirming a transition
4. The confirmed gesture is dispatched to the appropriate **controller** (mouse, scroll, or volume)
5. An **EMA smoothing filter** stabilizes the cursor coordinates before applying them to the screen
6. The **overlay module** draws real-time feedback on the OpenCV window: colored skeleton, active gesture badge, FPS counter, and a volume bar

---

## Known Limitations

- macOS only (Windows/Linux support would require replacing the AppleScript volume control and testing pynput compatibility)
- Single hand tracking only
- Requires reasonable lighting conditions for reliable landmark detection
- The `is_front_facing` heuristic may occasionally misclassify hand orientation in extreme angles
