import math

import numpy as np
import pytest

from climb_beta import masks as M


def disk(h: int, w: int, cx: int, cy: int, r: int) -> np.ndarray:
    yy, xx = np.mgrid[0:h, 0:w]
    return (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r


def test_edge_ring_is_inside_and_thin() -> None:
    m = disk(100, 100, 50, 50, 20)
    ring = M.edge_ring(m, 3)
    assert not (ring & ~m).any()
    assert ring[50, 50 + 20] and not ring[50, 50]
    # roughly perimeter * width
    assert 0.6 < ring.sum() / (2 * math.pi * 20 * 3) < 1.3


def test_edge_ring_of_thin_mask_is_whole_mask() -> None:
    m = np.zeros((20, 20), dtype=bool)
    m[10, 2:18] = True
    assert np.array_equal(M.edge_ring(m, 2), m)


def test_edge_ring_counts_image_border_as_edge() -> None:
    m = np.ones((30, 30), dtype=bool)
    ring = M.edge_ring(m, 2)
    assert ring[0, 15] and not ring[15, 15]


def test_dilate_grows_and_zero_is_copy() -> None:
    m = disk(60, 60, 30, 30, 5)
    assert M.dilate(m, 3).sum() > m.sum()
    same = M.dilate(m, 0)
    assert np.array_equal(same, m) and same is not m


def test_mask_iou() -> None:
    a = np.zeros((10, 10), dtype=bool)
    b = np.zeros((10, 10), dtype=bool)
    a[0:4, 0:4] = True
    b[2:6, 0:4] = True
    assert M.mask_iou(a, b) == pytest.approx(8 / 24)
    assert M.mask_iou(a, a) == 1.0
    empty = np.zeros_like(a)
    assert M.mask_iou(empty, empty) == 0.0


def test_iou_matrix_matches_pairwise_and_skips_far_pairs() -> None:
    a = disk(80, 80, 20, 20, 8)
    b = disk(80, 80, 60, 60, 8)
    c = disk(80, 80, 22, 20, 8)
    mat = M.iou_matrix([a, b], [c, b, np.zeros_like(a)])
    assert mat.shape == (2, 3)
    assert mat[0, 0] == pytest.approx(M.mask_iou(a, c))
    assert mat[0, 1] == 0.0 and mat[1, 1] == 1.0 and mat[:, 2].sum() == 0.0


def test_min_gap() -> None:
    a = np.zeros((20, 40), dtype=bool)
    b = np.zeros((20, 40), dtype=bool)
    a[5:10, 0:5] = True
    b[5:10, 15:20] = True
    assert M.min_gap(a, b) == pytest.approx(11.0, abs=0.1)
    assert M.min_gap(a, a) == 0.0
    assert M.min_gap(a, np.zeros_like(a)) == math.inf


def test_polygon_roundtrip() -> None:
    m = disk(100, 120, 60, 50, 25)
    poly = M.mask_to_polygon(m, epsilon=0.5)
    back = M.polygon_to_mask(poly, 100, 120)
    assert M.mask_iou(m, back) > 0.95


def test_polygon_of_empty_mask() -> None:
    assert M.mask_to_polygon(np.zeros((5, 5), dtype=bool)).shape == (0, 2)
    assert not M.polygon_to_mask(np.zeros((2, 2)), 5, 5).any()


def test_normalise_roundtrip() -> None:
    poly = np.array([[10.0, 20.0], [50.0, 20.0], [30.0, 80.0]])
    n = M.normalise(poly, h=100, w=200)
    assert n.max() <= 1.0 and n[1, 0] == pytest.approx(0.25)
    assert np.allclose(M.denormalise(n, 100, 200), poly)
