import numpy as np
import pytest
from synth import BLACK, BLUE, GREEN, GREY, ORANGE, PURPLE, YELLOW, chalk, draw_hold, wall

from climb_beta.colour.rules import UNKNOWN, classify_hold, pixel_labels
from climb_beta.config import load_colour_config

CFG = load_colour_config()


@pytest.mark.parametrize(
    ("bgr", "expected"),
    [
        (GREEN, "green"),
        (BLUE, "blue"),
        (ORANGE, "orange"),
        (YELLOW, "yellow"),
        (PURPLE, "purple"),
        (BLACK, "black"),
        (GREY, "grey"),
    ],
)
def test_plain_holds(bgr: tuple[int, int, int], expected: str) -> None:
    img = wall()
    m = draw_hold(img, (160, 120), 30, bgr)
    r = classify_hold(img, m, CFG)
    assert r.name == expected, r
    assert r.confidence > 0.8


@pytest.mark.parametrize("frac", [0.3, 0.6, 0.8])
def test_chalked_blue_stays_blue(frac: float) -> None:
    img = wall()
    m = draw_hold(img, (160, 120), 30, BLUE)
    chalk(img, m, frac, region="centre")
    r = classify_hold(img, m, CFG)
    assert r.name == "blue", r
    assert r.chalk_frac == pytest.approx(frac, abs=0.02)


def test_scattered_chalk_on_green() -> None:
    img = wall()
    m = draw_hold(img, (160, 120), 30, GREEN)
    chalk(img, m, 0.5, region="random", seed=2)
    assert classify_hold(img, m, CFG).name == "green"


def test_empty_mask_is_unknown() -> None:
    img = wall()
    assert classify_hold(img, np.zeros(img.shape[:2], dtype=bool), CFG).name == UNKNOWN


def test_pixel_labels_cover_hue_circle() -> None:
    hsv = np.array([[h, 200, 200] for h in range(180)], dtype=np.uint8)
    labels = pixel_labels(hsv, CFG)
    assert UNKNOWN not in set(labels.tolist())
    assert labels[0] == labels[179] == "redpink"
    dark = pixel_labels(np.array([[60, 200, 30]], dtype=np.uint8), CFG)
    assert dark[0] == "black"


def test_votes_and_reason_reported() -> None:
    img = wall()
    m = draw_hold(img, (160, 120), 30, GREEN)
    r = classify_hold(img, m, CFG)
    assert r.family == "green" and r.votes["green"] == max(r.votes.values())
    assert r.n_pixels == int(m.sum())
