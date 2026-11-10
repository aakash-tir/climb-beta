"""Tape diamonds get a colour too: at Basecamp it's the route's grade circuit."""

import cv2
import numpy as np
import pytest
from synth import BLACK, BLUE, GREEN, HOT_PINK, ORANGE, PURPLE, RED, WHITE, YELLOW, wall

from climb_beta.colour.batch import colour_detections
from climb_beta.config import ConfigError, load_colour_config, parse_colour_config
from climb_beta.types import Detection, Mask

CFG = load_colour_config()


def _diamond(img: np.ndarray, centre: tuple[int, int], r: int, bgr: tuple[int, int, int]) -> Mask:
    cx, cy = centre
    pts = np.array([[cx, cy - r], [cx + r, cy], [cx, cy + r], [cx - r, cy]], dtype=np.int32)
    m = np.zeros(img.shape[:2], dtype=np.uint8)
    cv2.fillConvexPoly(m, pts, 255)
    mask = m > 0
    img[mask] = bgr
    return mask


# Basecamp's circuit colours, easiest to hardest.
CIRCUITS = [
    (YELLOW, "yellow"),
    (ORANGE, "orange"),
    (RED, "red"),
    (GREEN, "green"),
    (PURPLE, "purple"),
    (HOT_PINK, "pink"),
    (BLACK, "black"),
    (WHITE, "white"),
]


@pytest.mark.parametrize(("bgr", "expected"), CIRCUITS)
def test_diamond_gets_its_circuit_colour(bgr: tuple[int, int, int], expected: str) -> None:
    img = wall()
    hold = Detection(mask=_diamond(img, (80, 120), 25, BLUE), cls="hold")
    tape = Detection(mask=_diamond(img, (220, 120), 9, bgr), cls="tape")
    colour_detections(img, [hold, tape], CFG)
    assert tape.colour == expected
    assert hold.colour == "blue"


def test_volumes_stay_uncoloured() -> None:
    img = wall()
    vol = Detection(mask=_diamond(img, (160, 120), 40, (120, 120, 120)), cls="volume")
    _, results = colour_detections(img, [vol], CFG)
    assert vol.colour is None
    assert results == [None]


def test_coloured_classes_config() -> None:
    assert CFG.coloured_classes == ("hold", "tape")
    raw = {
        "colours": [
            {"name": "red", "family": "redpink"},
            {"name": "pink", "family": "redpink"},
        ],
        "families": {"redpink": {"hue": [[0, 9]]}},
        "thresholds": {},
    }
    assert parse_colour_config(raw).coloured_classes == ("hold",)  # default when absent
    with pytest.raises(ConfigError):
        parse_colour_config({**raw, "coloured_classes": []})
    with pytest.raises(ConfigError):
        parse_colour_config({**raw, "coloured_classes": ["hold", "hold"]})
