"""Pink vs red: the pair the exit criteria single out (>= 90% on pink-vs-red holds)."""

import cv2
import numpy as np
import pytest
from synth import HOT_PINK, LIGHT_PINK, RED, chalk, draw_hold, tint, wall

from climb_beta.colour.rules import classify_hold
from climb_beta.colour.white_balance import grey_world
from climb_beta.config import load_colour_config

CFG = load_colour_config()


def hsv_to_bgr(h: int, s: int, v: int) -> tuple[int, int, int]:
    px = cv2.cvtColor(np.array([[[h, s, v]]], dtype=np.uint8), cv2.COLOR_HSV2BGR)[0, 0]
    return (int(px[0]), int(px[1]), int(px[2]))


def colour_of(bgr: tuple[int, int, int], **chalk_kw: object) -> str:
    img = wall()
    m = draw_hold(img, (160, 120), 32, bgr)
    if chalk_kw:
        chalk(img, m, **chalk_kw)  # type: ignore[arg-type]
    return classify_hold(img, m, CFG).name


@pytest.mark.parametrize(
    ("bgr", "expected"), [(RED, "red"), (HOT_PINK, "pink"), (LIGHT_PINK, "pink")]
)
def test_clean_holds(bgr: tuple[int, int, int], expected: str) -> None:
    assert colour_of(bgr) == expected


@pytest.mark.parametrize("frac", [0.3, 0.6, 0.8])
@pytest.mark.parametrize("region", ["centre", "random"])
def test_chalked_red_is_never_pink(frac: float, region: str) -> None:
    # solid chalk on part, thin (pinkish) chalk mixed in: the classic red->pink trap
    assert colour_of(RED, frac=frac, region=region, blend=(0.3, 1.0)) == "red"


@pytest.mark.parametrize("frac", [0.3, 0.6])
def test_chalked_pink_stays_pink(frac: float) -> None:
    assert colour_of(HOT_PINK, frac=frac, region="centre", blend=(0.3, 1.0)) == "pink"


@pytest.mark.parametrize("hue", [0, 175, 178])
def test_same_hue_split_by_saturation_and_lightness(hue: int) -> None:
    red = hsv_to_bgr(hue, 230, 200)
    pink = hsv_to_bgr(hue, 140, 255)
    assert colour_of(red) == "red"
    assert colour_of(pink) == "pink"


def test_red_under_warm_light_after_white_balance() -> None:
    img = wall(bgr=(180, 180, 180))
    m_red = draw_hold(img, (100, 120), 30, RED, seed=1)
    m_pink = draw_hold(img, (220, 120), 30, HOT_PINK, seed=2)
    warm = tint(img, (0.75, 0.95, 1.2))
    balanced = grey_world(warm, ref_mask=~(m_red | m_pink))
    assert classify_hold(balanced, m_red, CFG).name == "red"
    assert classify_hold(balanced, m_pink, CFG).name == "pink"
