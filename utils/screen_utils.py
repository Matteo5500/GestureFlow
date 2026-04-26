from __future__ import annotations

# import Quartz  # NON disponibile, usa pyautogui
try:
    import pyautogui  # type: ignore
except Exception:  # pragma: no cover
    pyautogui = None  # type: ignore


def get_screen_size() -> tuple[int, int]:
    """Ritorna (width, height) della schermata principale."""
    if pyautogui is None:  # pragma: no cover
        raise RuntimeError(
            "pyautogui non disponibile. Installa le dipendenze con:\n"
            "pip install -r requirements.txt"
        )
    size = pyautogui.size()
    return int(size.width), int(size.height)


def normalize_to_screen(
    norm_x: float,
    norm_y: float,
    screen_w: int,
    screen_h: int,
    margin: int = 0,
) -> tuple[int, int]:
    """
    La webcam cattura solo la zona centrale del frame
    dove la mano si muove realisticamente.
    Definiamo una ROI (Region of Interest) più stretta
    e la mappiamo all'intero schermo.
    """

    # ROI orizzontale: la mano si muove tipicamente
    # tra 20% e 80% del frame (asse X)
    ROI_X_MIN = 0.20
    ROI_X_MAX = 0.80

    # ROI verticale: la mano si muove tipicamente
    # tra 10% e 90% del frame (asse Y)
    ROI_Y_MIN = 0.10
    ROI_Y_MAX = 0.90

    # Inverti X (frame specchiato)
    norm_x = 1.0 - norm_x

    # Mappa dalla ROI a 0.0–1.0
    mapped_x = (norm_x - ROI_X_MIN) / (ROI_X_MAX - ROI_X_MIN)
    mapped_y = (norm_y - ROI_Y_MIN) / (ROI_Y_MAX - ROI_Y_MIN)

    # Clamp a [0.0, 1.0]
    mapped_x = max(0.0, min(1.0, mapped_x))
    mapped_y = max(0.0, min(1.0, mapped_y))

    # Converti in pixel
    screen_x = int(mapped_x * screen_w)
    screen_y = int(mapped_y * screen_h)

    return screen_x, screen_y

