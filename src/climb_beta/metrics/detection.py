"""Detection metrics on masks: greedy IoU matching, recall, VOC all-point AP50.

Exit criteria: hold recall >= 95% (GT holds matched by a predicted hold at mask IoU >= 0.5)
and mask mAP50 >= 0.85 (mean over classes that have ground truth).
Matching is per class: a predicted volume never matches a GT hold.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

import numpy as np

from climb_beta.masks import iou_matrix
from climb_beta.types import Detection

IOU_THR = 0.5


@dataclass
class ImageMatch:
    """Matching for one image and one class."""

    pred_scores: list[float]
    pred_tp: list[bool]  # per prediction, in descending-score order
    gt_matched: list[int | None]  # per GT: index (in score order) of its matching prediction
    gt_ious: list[float]  # per GT: IoU of its match (0 if unmatched)

    @property
    def n_gt(self) -> int:
        return len(self.gt_matched)


def match_masks(
    preds: Sequence[Detection], gts: Sequence[Detection], iou_thr: float = IOU_THR
) -> ImageMatch:
    """Greedy matching: highest-scoring prediction first, to its best unmatched GT."""
    order = sorted(range(len(preds)), key=lambda i: -preds[i].score)
    ps = [preds[i] for i in order]
    ious = iou_matrix([p.mask for p in ps], [g.mask for g in gts])
    gt_matched: list[int | None] = [None] * len(gts)
    gt_ious = [0.0] * len(gts)
    tp = []
    for pi in range(len(ps)):
        best, best_iou = None, iou_thr
        for gi in range(len(gts)):
            if gt_matched[gi] is None and ious[pi, gi] >= best_iou:
                best, best_iou = gi, float(ious[pi, gi])
        if best is None:
            tp.append(False)
        else:
            gt_matched[best], gt_ious[best] = pi, best_iou
            tp.append(True)
    return ImageMatch([p.score for p in ps], tp, gt_matched, gt_ious)


def average_precision(scores: Sequence[float], tp: Sequence[bool], n_gt: int) -> float:
    """VOC all-point interpolated AP (area under the monotone precision-recall curve)."""
    if n_gt == 0:
        return float("nan")
    if not scores:
        return 0.0
    order = np.argsort(-np.asarray(scores), kind="stable")
    tps = np.asarray(tp, dtype=np.float64)[order]
    ctp, cfp = np.cumsum(tps), np.cumsum(1.0 - tps)
    recall = ctp / n_gt
    precision = ctp / np.maximum(ctp + cfp, 1e-12)
    mrec = np.concatenate([[0.0], recall, [1.0]])
    mpre = np.concatenate([[0.0], precision, [0.0]])
    for i in range(len(mpre) - 2, -1, -1):
        mpre[i] = max(mpre[i], mpre[i + 1])
    idx = np.where(mrec[1:] != mrec[:-1])[0]
    return float(np.sum((mrec[idx + 1] - mrec[idx]) * mpre[idx + 1]))


@dataclass
class ClassStats:
    n_gt: int = 0
    n_matched: int = 0
    scores: list[float] = field(default_factory=list)
    tp: list[bool] = field(default_factory=list)

    @property
    def recall(self) -> float:
        return self.n_matched / self.n_gt if self.n_gt else float("nan")

    @property
    def ap50(self) -> float:
        return average_precision(self.scores, self.tp, self.n_gt)


@dataclass
class DetectionReport:
    per_class: dict[str, ClassStats]

    @property
    def hold_recall(self) -> float:
        s = self.per_class.get("hold")
        return s.recall if s else float("nan")

    @property
    def map50(self) -> float:
        aps = [s.ap50 for s in self.per_class.values() if s.n_gt > 0]
        return float(np.mean(aps)) if aps else float("nan")


class DetectionAccumulator:
    """Feed (predictions, ground truth) image by image; read the report at the end."""

    def __init__(self, classes: Sequence[str], iou_thr: float = IOU_THR) -> None:
        self.classes = tuple(classes)
        self.iou_thr = iou_thr
        self.stats = {c: ClassStats() for c in self.classes}

    def add(self, preds: Sequence[Detection], gts: Sequence[Detection]) -> dict[str, ImageMatch]:
        out = {}
        for c in self.classes:
            p = [d for d in preds if d.cls == c]
            g = [d for d in gts if d.cls == c]
            m = match_masks(p, g, self.iou_thr)
            s = self.stats[c]
            s.n_gt += m.n_gt
            s.n_matched += sum(x is not None for x in m.gt_matched)
            s.scores += m.pred_scores
            s.tp += m.pred_tp
            out[c] = m
        return out

    def report(self) -> DetectionReport:
        return DetectionReport(self.stats)
