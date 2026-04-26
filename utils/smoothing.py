from __future__ import annotations


class EMAFilter:
    def __init__(self, alpha: float = 0.3):
        """
        alpha: peso del nuovo valore (0=ignora nuovo, 1=ignora storico)
        Un alpha di 0.3 dà fluidità alta.
        MouseConfig.SMOOTHING_FACTOR corrisponde a (1 - alpha).
        """
        self._alpha = float(alpha)
        self._prev_x: float | None = None
        self._prev_y: float | None = None

    def smooth(self, x: float, y: float) -> tuple[float, float]:
        """
        Formula EMA:
          smoothed_x = alpha * new_x + (1 - alpha) * prev_x
        Al primo frame ritorna il valore grezzo.
        """
        if self._prev_x is None or self._prev_y is None:
            self._prev_x = float(x)
            self._prev_y = float(y)
            return float(x), float(y)

        a = self._alpha
        sx = a * float(x) + (1.0 - a) * self._prev_x
        sy = a * float(y) + (1.0 - a) * self._prev_y
        self._prev_x, self._prev_y = sx, sy
        return sx, sy

    def reset(self) -> None:
        """Azzera lo stato (chiamato quando si passa a REST)."""
        self._prev_x = None
        self._prev_y = None

