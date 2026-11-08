import json
from pathlib import Path

import cv2
import numpy as np
import pytest
from scripts import load_script
from synth import BLUE, HOT_PINK, RED, WHITE, chalk, draw_hold, tint, wall

from climb_beta.data.yolo import (
    YoloInstance,
    format_label_line,
    parse_label_line,
    read_labels,
    write_labels,
)
from climb_beta.masks import mask_to_polygon, normalise


def _scene(tmp_path: Path) -> tuple[Path, Path]:
    img = wall(h=240, w=320)
    holds = [
        draw_hold(img, (60, 70), 26, RED, seed=1),
        draw_hold(img, (160, 70), 26, HOT_PINK, seed=2),
        draw_hold(img, (260, 70), 26, WHITE, seed=3),
        draw_hold(img, (110, 170), 26, BLUE, seed=4),
    ]
    chalk(img, holds[0], 0.6, region="centre", blend=(0.3, 1.0))
    tape = np.zeros(img.shape[:2], dtype=bool)
    tape[200:210, 230:280] = True
    img[tape] = (250, 250, 250)
    img = tint(img, (0.8, 1.0, 1.15))
    instances = [YoloInstance(0, normalise(mask_to_polygon(m), 240, 320)) for m in holds]
    instances.append(YoloInstance(2, normalise(mask_to_polygon(tape), 240, 320)))
    ip, lp = tmp_path / "wall.png", tmp_path / "wall.txt"
    cv2.imwrite(str(ip), img)
    write_labels(lp, instances)
    return ip, lp


def test_cli_labels_holds_and_skips_tape(tmp_path: Path) -> None:
    ip, lp = _scene(tmp_path)
    out, dbg = tmp_path / "holds.json", tmp_path / "debug.png"
    mod = load_script("colour/classify_rules.py")
    assert mod.main([str(ip), str(lp), "--out", str(out), "--debug", str(dbg)]) == 0
    recs = json.loads(out.read_text())
    assert [r.get("colour") for r in recs] == ["red", "pink", "white", "blue", None]
    assert recs[4]["cls"] == "tape"
    assert dbg.exists()


def test_cli_missing_image(tmp_path: Path) -> None:
    mod = load_script("colour/classify_rules.py")
    assert mod.main([str(tmp_path / "nope.png"), str(tmp_path / "x.txt")]) == 2


def test_label_line_roundtrip_and_validation(tmp_path: Path) -> None:
    poly = np.array([[0.1, 0.2], [0.3, 0.2], [0.2, 0.4]])
    line = format_label_line(1, poly)
    inst = parse_label_line(line)
    assert inst is not None and inst.cls_id == 1 and np.allclose(inst.polygon, poly)
    assert parse_label_line("   ") is None
    with pytest.raises(ValueError):
        parse_label_line("0 0.1 0.2 0.3")
    p = tmp_path / "l.txt"
    write_labels(p, [inst, inst])
    assert len(read_labels(p)) == 2
