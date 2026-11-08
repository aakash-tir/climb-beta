import numpy as np
import pytest
from synth import CHALK, RED, chalk, draw_hold, tint, wall


def test_wall_is_deterministic_bgr_uint8() -> None:
    a, b = wall(seed=3), wall(seed=3)
    assert a.dtype == np.uint8 and a.shape == (240, 320, 3)
    assert np.array_equal(a, b)
    assert not np.array_equal(a, wall(seed=4))


def test_draw_hold_mask_area_and_colour() -> None:
    img = wall()
    m = draw_hold(img, (100, 100), 20, RED)
    assert m.dtype == np.bool_
    assert abs(m.sum() - np.pi * 20 * 20) / (np.pi * 400) < 0.05
    centre = img[100, 100].astype(int)
    assert np.abs(centre - np.array(RED)).max() < 10
    assert np.abs(img[5, 5].astype(int) - np.array([190, 192, 195])).max() < 15


@pytest.mark.parametrize("region", ["centre", "random"])
def test_chalk_fraction(region: str) -> None:
    img = wall()
    m = draw_hold(img, (150, 120), 30, RED)
    ch = chalk(img, m, 0.4, region=region)
    assert not (ch & ~m).any()
    assert abs(ch.sum() / m.sum() - 0.4) < 0.01
    assert np.abs(img[ch].mean(axis=0) - np.array(CHALK)).max() < 3


def test_centre_chalk_leaves_edges() -> None:
    img = wall()
    m = draw_hold(img, (150, 120), 30, RED)
    ch = chalk(img, m, 0.5, region="centre")
    assert ch[120, 150]  # centre chalked
    assert not ch[120, 150 + 29]  # edge untouched


def test_tint_scales_channels() -> None:
    img = np.full((2, 2, 3), 100, dtype=np.uint8)
    out = tint(img, (0.5, 1.0, 1.5))
    assert out[0, 0].tolist() == [50, 100, 150]
