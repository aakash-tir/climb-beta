"""White holds vs chalk: the chalk filter must not delete white holds."""

import pytest
from synth import BLUE, GREY, RED, WHITE, chalk, draw_hold, wall

from climb_beta.colour.rules import classify_hold
from climb_beta.config import load_colour_config

CFG = load_colour_config()


def _hold(bgr: tuple[int, int, int], r: int = 30) -> tuple:
    img = wall()
    m = draw_hold(img, (160, 120), r, bgr)
    return img, m


@pytest.mark.parametrize("radius", [12, 30, 50])
def test_white_hold_is_white(radius: int) -> None:
    img, m = _hold(WHITE, radius)
    r = classify_hold(img, m, CFG)
    assert r.name == "white", r
    assert "edge ring" in r.reason


def test_chalked_white_hold_is_white() -> None:
    img, m = _hold(WHITE)
    chalk(img, m, 0.7)
    assert classify_hold(img, m, CFG).name == "white"


@pytest.mark.parametrize(("bgr", "expected"), [(RED, "red"), (BLUE, "blue")])
@pytest.mark.parametrize("frac", [0.85, 0.92])
def test_heavily_chalked_colour_hold_votes_on_ring(
    bgr: tuple[int, int, int], expected: str, frac: float
) -> None:
    img, m = _hold(bgr)
    chalk(img, m, frac, region="centre")
    r = classify_hold(img, m, CFG)
    assert r.name == expected, r
    assert r.reason.startswith("chalked")


def test_grey_hold_stays_grey() -> None:
    img, m = _hold(GREY)
    assert classify_hold(img, m, CFG).name == "grey"


def test_light_grey_chalk_like_body_but_dim_ring_is_grey() -> None:
    img, m = _hold((176, 176, 176))  # bright enough to look like chalk in the middle
    r = classify_hold(img, m, CFG)
    assert r.name == "grey", r
