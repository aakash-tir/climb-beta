"""Mask maths shared by colour, route, data and eval. Masks are bool HxW arrays."""

from __future__ import annotations

from collections.abc import Sequence

import cv2
import numpy as np
import numpy.typing as npt

from climb_beta.types import Mask

FloatArray = npt.NDArray[np.float64]


def _kernel(px: int) -> npt.NDArray[np.uint8]:
    k = 2 * px + 1
    return np.asarray(cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)), dtype=np.uint8)


def erode(mask: Mask, px: int) -> Mask:
    """Erode by `px` pixels. The image border counts as outside the mask."""
    if px <= 0:
        return mask.copy()
    out = cv2.erode(
        mask.astype(np.uint8),
        _kernel(px),
        borderType=cv2.BORDER_CONSTANT,
        borderValue=0,
    )
    return out.astype(bool)


def dilate(mask: Mask, px: int) -> Mask:
    """Dilate by `px` pixels."""
    if px <= 0:
        return mask.copy()
    return cv2.dilate(mask.astype(np.uint8), _kernel(px)).astype(bool)


def edge_ring(mask: Mask, width: int) -> Mask:
    """The ring of mask pixels within `width` px of the mask boundary.

    For a hold this is its sides, which hands rarely touch, so it keeps the
    pigment colour under chalk. A mask thinner than 2*width is all ring.
    """
    return mask & ~erode(mask, width)


def mask_iou(a: Mask, b: Mask) -> float:
    union = int(np.logical_or(a, b).sum())
    if union == 0:
        return 0.0
    return float(np.logical_and(a, b).sum()) / union


def _bbox(m: Mask) -> tuple[int, int, int, int] | None:
    rows = np.flatnonzero(m.any(axis=1))
    if rows.size == 0:
        return None
    cols = np.flatnonzero(m.any(axis=0))
    return int(rows[0]), int(rows[-1]), int(cols[0]), int(cols[-1])


def iou_matrix(preds: Sequence[Mask], gts: Sequence[Mask]) -> FloatArray:
    """IoU for every (pred, gt) pair; shape (len(preds), len(gts))."""
    out = np.zeros((len(preds), len(gts)), dtype=np.float64)
    pb = [_bbox(p) for p in preds]
    gb = [_bbox(g) for g in gts]
    for i, (p, bp) in enumerate(zip(preds, pb, strict=True)):
        if bp is None:
            continue
        for j, (g, bg) in enumerate(zip(gts, gb, strict=True)):
            if bg is None:
                continue
            # skip pairs whose boxes don't overlap
            if bp[1] < bg[0] or bg[1] < bp[0] or bp[3] < bg[2] or bg[3] < bp[2]:
                continue
            out[i, j] = mask_iou(p, g)
    return out


def distance_to(mask: Mask) -> npt.NDArray[np.float32]:
    """Per-pixel Euclidean distance to the nearest mask pixel (0 inside the mask)."""
    if not mask.any():
        return np.full(mask.shape, np.inf, dtype=np.float32)
    src = np.where(mask, 0, 255).astype(np.uint8)
    return np.asarray(cv2.distanceTransform(src, cv2.DIST_L2, 5), dtype=np.float32)


def min_gap(a: Mask, b: Mask, dist_a: npt.NDArray[np.float32] | None = None) -> float:
    """Smallest pixel distance between two masks (0 if they touch or overlap)."""
    if not a.any() or not b.any():
        return float("inf")
    d = distance_to(a) if dist_a is None else dist_a
    return float(d[b].min())


def polygon_to_mask(poly: npt.ArrayLike, h: int, w: int) -> Mask:
    """Rasterise an (N, 2) polygon in pixel coords (x, y)."""
    pts = np.asarray(poly, dtype=np.float64).reshape(-1, 2)
    m = np.zeros((h, w), dtype=np.uint8)
    if pts.shape[0] >= 3:
        cv2.fillPoly(m, [np.round(pts).astype(np.int32)], 1)
    return m.astype(bool)


def mask_to_polygon(mask: Mask, epsilon: float = 1.0) -> FloatArray:
    """Outer contour of the largest component as an (N, 2) pixel polygon (x, y).

    `epsilon` is the Douglas-Peucker tolerance in pixels. Empty mask -> (0, 2).
    """
    contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        return np.zeros((0, 2), dtype=np.float64)
    c = max(contours, key=cv2.contourArea)
    if epsilon > 0:
        c = cv2.approxPolyDP(c, epsilon, True)
    return c.reshape(-1, 2).astype(np.float64)


def normalise(poly: FloatArray, h: int, w: int) -> FloatArray:
    """Pixel polygon -> YOLO normalised [0, 1] coords."""
    out = poly.astype(np.float64).copy()
    out[:, 0] /= w
    out[:, 1] /= h
    return np.clip(out, 0.0, 1.0)


def denormalise(poly: FloatArray, h: int, w: int) -> FloatArray:
    """YOLO normalised coords -> pixel polygon."""
    out = poly.astype(np.float64).copy()
    out[:, 0] *= w
    out[:, 1] *= h
    return out
