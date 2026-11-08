import math

import numpy as np
import pytest

from climb_beta.metrics.detection import (
    DetectionAccumulator,
    average_precision,
    match_masks,
)
from climb_beta.types import Detection


def box(x0: int, y0: int, x1: int, y1: int, cls: str = "hold", score: float = 1.0) -> Detection:
    m = np.zeros((100, 100), dtype=bool)
    m[y0:y1, x0:x1] = True
    return Detection(mask=m, cls=cls, score=score)


def test_greedy_matching_highest_score_wins() -> None:
    gt = [box(0, 0, 10, 10)]
    preds = [box(0, 0, 10, 9, score=0.4), box(0, 0, 10, 10, score=0.9)]
    m = match_masks(preds, gt)
    assert m.pred_scores == [0.9, 0.4]
    assert m.pred_tp == [True, False]  # duplicate is a false positive
    assert m.gt_matched == [0] and m.gt_ious[0] == 1.0


def test_iou_threshold() -> None:
    gt = [box(0, 0, 10, 10)]
    assert match_masks([box(0, 0, 10, 5)], gt).pred_tp == [True]  # IoU 0.5
    assert match_masks([box(0, 0, 10, 4)], gt).pred_tp == [False]  # IoU 0.4


def test_ap_hand_computed() -> None:
    # 3 GT; predictions by score: TP, FP, TP  -> P/R points (1,1/3) (.5,1/3) (2/3,2/3)
    # all-point interpolated AP = 1/3*1 + 1/3*(2/3) = 0.5556
    assert average_precision([0.9, 0.8, 0.7], [True, False, True], 3) == pytest.approx(5 / 9)
    assert average_precision([0.9], [True], 1) == 1.0
    assert average_precision([], [], 2) == 0.0
    assert math.isnan(average_precision([0.5], [False], 0))


def test_accumulator_recall_map_and_class_separation() -> None:
    acc = DetectionAccumulator(("hold", "volume", "tape"))
    # image 1: 2 GT holds, one found; a volume predicted where a hold is (wrong class)
    acc.add(
        [box(0, 0, 10, 10, score=0.9), box(50, 50, 70, 70, "volume", score=0.8)],
        [box(0, 0, 10, 10), box(50, 50, 70, 70)],
    )
    # image 2: 1 GT hold found, 1 GT volume found
    acc.add(
        [box(20, 20, 30, 30, score=0.7), box(60, 0, 90, 30, "volume", score=0.6)],
        [box(20, 20, 30, 30), box(60, 0, 90, 30, "volume")],
    )
    r = acc.report()
    assert r.hold_recall == pytest.approx(2 / 3)
    assert r.per_class["volume"].n_gt == 1
    assert r.per_class["volume"].ap50 == pytest.approx(0.5)  # FP scored above the TP
    assert r.per_class["hold"].ap50 == pytest.approx(2 / 3)
    assert r.map50 == pytest.approx((2 / 3 + 0.5) / 2)  # tape has no GT: excluded
