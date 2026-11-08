import json
from pathlib import Path

import numpy as np
import pytest
from scripts import load_script
from synth import BLUE, HOT_PINK, RED, chalk, draw_hold, wall

from climb_beta.data.yolo import YoloInstance, write_labels
from climb_beta.imageio import write_bgr
from climb_beta.masks import mask_to_polygon, normalise
from climb_beta.metrics.colour import colour_report, format_report

LABELS = ("red", "pink", "blue")


def test_report_numbers() -> None:
    truth = ["red", "red", "pink", "pink", "blue", "blue"]
    pred = ["red", "pink", "pink", "pink", "blue", "unknown"]
    chalked = [True, True, False, False, True, False]
    r = colour_report(truth, pred, chalked, LABELS)
    assert r.overall == pytest.approx(4 / 6)
    assert r.pink_red == pytest.approx(3 / 4) and r.pink_red_n == 4
    assert r.chalked == pytest.approx(2 / 3) and r.chalked_n == 3
    assert r.per_colour == {"red": 0.5, "pink": 1.0, "blue": 0.5}
    assert r.matrix.tolist() == [[1, 1, 0, 0], [0, 2, 0, 0], [0, 0, 1, 1]]
    text = format_report(r)
    assert "unknown" in text and "pink vs red  75.0%" in text


def test_unknown_prediction_label_is_wrong_and_bad_truth_raises() -> None:
    r = colour_report(["red"], ["teal"], [False], LABELS)
    assert r.overall == 0.0 and r.matrix[0, -1] == 1
    with pytest.raises(ValueError):
        colour_report(["teal"], ["red"], [False], LABELS)
    with pytest.raises(ValueError):
        colour_report(["red"], [], [], LABELS)


def test_empty_subsets_are_none() -> None:
    r = colour_report(["blue"], ["blue"], [False], LABELS)
    assert r.pink_red is None and r.chalked is None


def test_cli_end_to_end(tmp_path: Path) -> None:
    ds = tmp_path / "ds"
    img = wall(h=120, w=240)
    holds = [
        (draw_hold(img, (40, 60), 22, RED, seed=1), "red", True),
        (draw_hold(img, (120, 60), 22, HOT_PINK, seed=2), "pink", False),
        (draw_hold(img, (200, 60), 22, BLUE, seed=3), "blue", False),
    ]
    chalk(img, holds[0][0], 0.6, blend=(0.3, 1.0))
    write_bgr(ds / "images" / "val" / "p.png", img)
    write_labels(
        ds / "labels" / "val" / "p.txt",
        [YoloInstance(0, normalise(mask_to_polygon(m), 120, 240)) for m, _, _ in holds],
    )
    (ds / "colours" / "val").mkdir(parents=True)
    side = [{"cls": "hold", "colour": c, "chalked": ch} for _, c, ch in holds]
    (ds / "colours" / "val" / "p.json").write_text(json.dumps(side))
    out = tmp_path / "r.json"
    mod = load_script("colour/eval_colour.py")
    assert mod.main([str(ds), "--json", str(out)]) == 0
    rep = json.loads(out.read_text())["rules"]
    assert rep["overall"] == 1.0 and rep["chalked_n"] == 1
    assert np.array(rep["matrix"]).sum() == 3
    assert mod.main([str(tmp_path / "empty")]) == 2
