import math

import numpy as np

from climb_beta.types import Detection


def test_detection_geometry() -> None:
    m = np.zeros((10, 20), dtype=bool)
    m[2:4, 5:9] = True
    d = Detection(mask=m, cls="hold")
    assert d.area == 8
    assert d.bbox() == (5, 2, 9, 4)
    assert d.centroid() == (6.5, 2.5)


def test_empty_detection_is_safe() -> None:
    d = Detection(mask=np.zeros((4, 4), dtype=bool), cls="hold")
    assert d.area == 0
    assert d.bbox() == (0, 0, 0, 0)
    assert all(math.isnan(v) for v in d.centroid())


def test_imageio_roundtrip_and_missing(tmp_path) -> None:  # type: ignore[no-untyped-def]
    from climb_beta.imageio import read_bgr, write_bgr

    img = np.zeros((4, 5, 3), dtype=np.uint8)
    img[1, 2] = (10, 20, 30)
    p = tmp_path / "sub dir é" / "x.png"
    write_bgr(p, img)
    back = read_bgr(p)
    assert back is not None and np.array_equal(back, img)
    assert read_bgr(tmp_path / "missing.png") is None
