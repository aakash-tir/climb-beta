"""Core data types shared by detector, colour, route, eval and app."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import numpy.typing as npt

Mask = npt.NDArray[np.bool_]
"""Boolean HxW mask, True inside the instance."""

ImageBGR = npt.NDArray[np.uint8]
"""HxWx3 uint8 image in OpenCV BGR order."""


@dataclass
class Detection:
    """One detector instance: a mask and a class (hold, volume or tape)."""

    mask: Mask
    cls: str
    score: float = 1.0
    colour: str | None = None
    colour_conf: float = 0.0
    attrs: dict[str, object] = field(default_factory=dict)

    @property
    def area(self) -> int:
        return int(self.mask.sum())

    def centroid(self) -> tuple[float, float]:
        """(x, y) centroid of the mask in pixels."""
        ys, xs = np.nonzero(self.mask)
        if xs.size == 0:
            return (float("nan"), float("nan"))
        return (float(xs.mean()), float(ys.mean()))

    def bbox(self) -> tuple[int, int, int, int]:
        """(x0, y0, x1, y1), inclusive-exclusive."""
        ys, xs = np.nonzero(self.mask)
        if xs.size == 0:
            return (0, 0, 0, 0)
        return (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
