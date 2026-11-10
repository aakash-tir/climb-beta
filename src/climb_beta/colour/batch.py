"""Colour holds and tape in a photo: wall-referenced white balance, then the rules.

Which detector classes are coloured is `ColourConfig.coloured_classes`. A hold's colour
is its plastic; a tape detection's colour is the route's grade diamond colour.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from climb_beta.colour.rules import ColourResult, classify_hold
from climb_beta.colour.white_balance import grey_world
from climb_beta.config import ColourConfig
from climb_beta.types import Detection, ImageBGR


def wall_mask(img: ImageBGR, detections: Sequence[Detection]) -> np.ndarray:
    """Pixels outside every detection: the wall, used as the white-balance reference."""
    m = np.ones(img.shape[:2], dtype=bool)
    for d in detections:
        m &= ~d.mask
    return m


def colour_detections(
    img: ImageBGR,
    detections: Sequence[Detection],
    cfg: ColourConfig,
    white_balance: bool = True,
) -> tuple[ImageBGR, list[ColourResult | None]]:
    """Set `.colour`/`.colour_conf` on every detection of a coloured class (in place).

    Returns the balanced image and one result per detection (None for classes that
    aren't coloured, e.g. volumes).
    """
    balanced = grey_world(img, ref_mask=wall_mask(img, detections)) if white_balance else img
    results: list[ColourResult | None] = []
    for d in detections:
        if d.cls not in cfg.coloured_classes:
            results.append(None)
            continue
        r = classify_hold(balanced, d.mask, cfg)
        d.colour, d.colour_conf = r.name, r.confidence
        results.append(r)
    return balanced, results
