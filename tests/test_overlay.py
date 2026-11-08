import numpy as np
import pytest
from fakes import wall_scene

from climb_beta.config import load_colour_config
from climb_beta.masks import erode
from climb_beta.overlay import DIM, draw_route, hex_to_bgr
from climb_beta.pipeline import run


def test_route_pixels_kept_rest_dimmed_start_marked() -> None:
    img, det, idx = wall_scene()
    res = run(img, det, load_colour_config(), colours=["red"])
    route = res.routes["red"].named_route()
    out = draw_route(img, res.detections, route, outline_bgr=(0, 255, 255))
    assert out.shape == img.shape and out.dtype == np.uint8
    red0 = res.detections[idx["red"][0]].mask
    inner = erode(red0, 6)  # away from the outline
    assert inner.any()
    assert np.array_equal(out[inner], img[inner])  # route hold interior untouched
    blue = res.detections[idx["blue"][0]].mask
    assert out[blue].mean() < img[blue].mean() * (DIM + 0.1)  # other holds dimmed
    assert (out == (0, 255, 255)).all(axis=-1).any()  # outline drawn
    # "S" in white below the start hold
    x0, y0, x1, y1 = res.detections[idx["red"][0]].bbox()
    below = out[y1 : y1 + 40, x0 - 20 : x1 + 20]
    assert (below == 255).all(axis=-1).any()


def test_no_route_dims_everything() -> None:
    img, det, _ = wall_scene()
    out = draw_route(img, det.predict(img), None)
    assert out.max() <= 255 * DIM + 1


def test_hex_to_bgr() -> None:
    assert hex_to_bgr("#d7263d") == (0x3D, 0x26, 0xD7)
    with pytest.raises(ValueError):
        hex_to_bgr("#fff")
