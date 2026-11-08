import csv
import json
from pathlib import Path

import numpy as np
import pytest
from scripts import load_script
from synth import BLUE, RED, draw_hold, wall

from climb_beta.colour.crops import NEUTRAL, extract_crop, write_crops
from climb_beta.data.yolo import YoloInstance, write_labels
from climb_beta.imageio import read_bgr, write_bgr
from climb_beta.masks import mask_to_polygon, normalise

CLASSES = ("hold", "volume", "tape")


def test_crop_is_square_masked_and_centred() -> None:
    img = wall(h=200, w=300)
    other = draw_hold(img, (150, 100), 30, BLUE)  # neighbour that must not leak in
    m = draw_hold(img, (110, 100), 20, RED, seed=1)
    other &= ~m
    crop = extract_crop(img, m, size=64, pad=0.5)
    assert crop.shape == (64, 64, 3)
    assert np.abs(crop[32, 32].astype(int) - np.array(RED)).max() < 15
    assert (crop[0, 0] == NEUTRAL).all()
    # no blue pixels from the neighbouring hold
    b, r = crop[..., 0].astype(int), crop[..., 2].astype(int)
    assert not ((b > 150) & (r < 80)).any()


def test_crop_at_image_edge_and_empty() -> None:
    img = wall(h=100, w=100)
    m = draw_hold(img, (3, 50), 15, RED)
    crop = extract_crop(img, m, size=32)
    assert crop.shape == (32, 32, 3)
    assert (extract_crop(img, np.zeros_like(m)) == NEUTRAL).all()


def _dataset(root: Path, mismatch: bool = False) -> Path:
    img = wall(h=120, w=160)
    m1 = draw_hold(img, (40, 60), 18, RED, seed=1)
    m2 = draw_hold(img, (110, 60), 18, BLUE, seed=2)
    vol = np.zeros((120, 160), dtype=bool)
    vol[5:20, 5:40] = True
    write_bgr(root / "images" / "train" / "p.png", img)
    insts = [
        YoloInstance(c, normalise(mask_to_polygon(m), 120, 160))
        for c, m in ((0, m1), (0, m2), (1, vol))
    ]
    write_labels(root / "labels" / "train" / "p.txt", insts)
    side = [
        {"cls": "hold", "colour": "red", "chalked": True},
        {"cls": "hold", "colour": "blue", "chalked": False},
        {"cls": "volume", "colour": None, "chalked": None},
    ]
    if mismatch:
        side = side[:2]
    (root / "colours" / "train").mkdir(parents=True)
    (root / "colours" / "train" / "p.json").write_text(json.dumps(side))
    return root


def test_write_crops_imagefolder_and_index(tmp_path: Path) -> None:
    out = tmp_path / "crops"
    recs = write_crops(_dataset(tmp_path / "ds"), out, CLASSES, size=48)
    assert sorted(r.colour for r in recs) == ["blue", "red"]
    assert (out / "train" / "red" / "p__0.png").exists()
    assert read_bgr(out / "train" / "blue" / "p__1.png").shape == (48, 48, 3)
    rows = list(csv.DictReader((out / "index.csv").open()))
    assert {r["colour"]: r["chalked"] for r in rows} == {"red": "1", "blue": "0"}


def test_sidecar_mismatch_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="sidecar"):
        write_crops(_dataset(tmp_path / "ds", mismatch=True), tmp_path / "o", CLASSES)


def test_cli(tmp_path: Path) -> None:
    mod = load_script("colour/make_crops.py")
    assert mod.main([str(tmp_path / "nope"), str(tmp_path / "o")]) == 2
    assert mod.main([str(_dataset(tmp_path / "ds")), str(tmp_path / "o")]) == 0
