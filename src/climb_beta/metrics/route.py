"""Route correctness: is the predicted route the named ground-truth route within 1 hold?

Predicted route holds are matched to GT route holds by mask IoU >= 0.5 (greedy).
missed = GT route holds with no match; extra = predicted route holds with no match.
A route is correct when missed + extra <= tolerance (1 in the exit criteria).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from climb_beta.masks import iou_matrix
from climb_beta.types import Mask

IOU_THR = 0.5


@dataclass(frozen=True)
class RouteScore:
    missed: int
    extra: int

    @property
    def error(self) -> int:
        return self.missed + self.extra

    def correct(self, tolerance: int = 1) -> bool:
        return self.error <= tolerance


def score_route(pred: Sequence[Mask], gt: Sequence[Mask], iou_thr: float = IOU_THR) -> RouteScore:
    ious = iou_matrix(list(pred), list(gt))
    pairs = sorted(
        ((float(ious[i, j]), i, j) for i in range(len(pred)) for j in range(len(gt))),
        reverse=True,
    )
    used_p: set[int] = set()
    used_g: set[int] = set()
    for iou, i, j in pairs:
        if iou < iou_thr:
            break
        if i in used_p or j in used_g:
            continue
        used_p.add(i)
        used_g.add(j)
    return RouteScore(missed=len(gt) - len(used_g), extra=len(pred) - len(used_p))
