"""Test doubles for the detector and the crop classifier."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from synth import BLUE, RED, chalk, draw_hold, tint, wall

from climb_beta.types import Detection, ImageBGR, Mask


class FakeDetector:
    """Returns fixed masks, as a perfect colour-blind detector would."""

    def __init__(self, items: Sequence[tuple[Mask, str]]) -> None:
        self.items = list(items)

    def predict(self, img: ImageBGR) -> list[Detection]:
        return [Detection(mask=m.copy(), cls=c, score=0.9) for m, c in self.items]


class FakeClassifier:
    def __init__(self, answer: str, classes: tuple[str, ...]) -> None:
        self.answer, self._classes = answer, classes

    @property
    def classes(self) -> tuple[str, ...]:
        return self._classes

    def predict(self, crops: Sequence[ImageBGR]) -> list[tuple[str, float]]:
        return [(self.answer, 0.99) for _ in crops]


def wall_scene() -> tuple[ImageBGR, FakeDetector, dict[str, list[int]]]:
    """A 600x800 wall: a 5-hold red route with start tape, a 4-hold blue route, warm light.

    Returns (image, detector, {"red": idx, "blue": idx, "tape": idx}).
    """
    img = wall(h=600, w=800, seed=7)
    items: list[tuple[Mask, str]] = []
    idx: dict[str, list[int]] = {"red": [], "blue": [], "tape": []}
    for k in range(5):
        m = draw_hold(img, (150 + 15 * k, 540 - 110 * k), 18, RED, seed=k)
        if k in (1, 3):
            chalk(img, m, 0.6, blend=(0.3, 1.0), seed=k)
        idx["red"].append(len(items))
        items.append((m, "hold"))
    for k in range(4):
        m = draw_hold(img, (600, 520 - 120 * k), 20, BLUE, seed=10 + k)
        idx["blue"].append(len(items))
        items.append((m, "hold"))
    t = np.zeros((600, 800), dtype=bool)
    t[562:570, 135:165] = True
    img[t] = (245, 245, 245)
    idx["tape"].append(len(items))
    items.append((t, "tape"))
    return tint(img, (0.8, 1.0, 1.15)), FakeDetector(items), idx
