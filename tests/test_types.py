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
