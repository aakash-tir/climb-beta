import json
from pathlib import Path
from typing import Any

import numpy as np
import pytest
import yaml
from scripts import ROOT, load_script
from synth import BLUE, GREEN, RED, draw_hold, wall

from climb_beta.data.coco_to_yolo import write_dataset_yaml
from climb_beta.data.yolo import YoloInstance, write_labels
from climb_beta.imageio import write_bgr
from climb_beta.masks import mask_to_polygon, normalise
from climb_beta.train_config import (
    TrainConfigError,
    load_train_config,
    merge_datasets,
    parse_train_config,
    summarise_metrics,
)

CLASSES = ("hold", "volume", "tape")
BASE: dict[str, Any] = {
    "model": "yolo11n-seg.pt",
    "datasets": ["a", "b"],
    "augment": {"hsv_h": 0.5, "hsv_s": 0.9},
}


@pytest.mark.parametrize("name", ["yolo11n-seg.yaml", "yolo11s-seg.yaml"])
def test_committed_configs_are_valid_and_colour_blind(name: str) -> None:
    cfg = load_train_config(ROOT / "train" / "configs" / name)
    assert cfg.augment["hsv_h"] >= 0.3 and cfg.augment["hsv_s"] >= 0.7
    assert cfg.val_dataset == "data/yolo/basecamp"  # model selection on our walls
    assert cfg.train_kwargs()["hsv_h"] == 0.5


@pytest.mark.parametrize(
    ("patch", "msg"),
    [
        ({"augment": {"hsv_h": 0.015, "hsv_s": 0.7}}, "must not learn hold colour"),
        ({"model": "yolov8n.pt"}, "hub model"),
        ({"model": "weights.onnx"}, ".pt"),
        ({"datasets": []}, "at least one"),
        ({"val_dataset": "c"}, "val_dataset"),
        ({"epochs": 0}, "positive"),
    ],
)
def test_bad_configs(patch: dict[str, Any], msg: str) -> None:
    with pytest.raises(TrainConfigError, match=msg):
        parse_train_config({**BASE, **patch})


def test_local_weights_path_allowed() -> None:
    cfg = parse_train_config({**BASE, "model": "runs/detector/x/weights/best.pt"})
    assert cfg.name == "best"


def _dataset(root: Path, n: int, splits: tuple[str, ...] = ("train", "val"), seed: int = 0):
    rng = np.random.default_rng(seed)
    for split in splits:
        for i in range(n):
            img = wall(h=128, w=128, seed=i)
            insts = []
            for j in range(3):
                c = (int(rng.integers(20, 108)), int(rng.integers(20, 108)))
                m = draw_hold(img, c, int(rng.integers(6, 14)), [RED, GREEN, BLUE][j], seed=j)
                insts.append(YoloInstance(0, normalise(mask_to_polygon(m), 128, 128)))
            write_bgr(root / "images" / split / f"{i}.png", img)
            write_labels(root / "labels" / split / f"{i}.txt", insts)
    write_dataset_yaml(root, CLASSES, splits)
    return root


def test_merge_datasets_trains_on_all_validates_on_last(tmp_path: Path) -> None:
    a = _dataset(tmp_path / "rf", 1)
    b = _dataset(tmp_path / "bc", 1, ("train", "val", "test"))
    out = merge_datasets([a, b], None, CLASSES, tmp_path / "m.yaml")
    y = yaml.safe_load(out.read_text())
    assert len(y["train"]) == 2
    assert y["val"].endswith(str(Path("bc") / "images" / "val"))
    assert y["test"].endswith(str(Path("bc") / "images" / "test"))


def test_merge_rejects_class_mismatch(tmp_path: Path) -> None:
    a = _dataset(tmp_path / "rf", 1)
    (a / "dataset.yaml").write_text("names: {0: hold}\ntrain: images/train\nval: images/val\n")
    with pytest.raises(TrainConfigError, match="classes"):
        merge_datasets([a], None, CLASSES, tmp_path / "m.yaml")


def test_summarise_metrics() -> None:
    s = summarise_metrics({"metrics/mAP50(M)": 0.9, "metrics/mAP50(B)": 0.8, "fitness": 1.0})
    assert s == {"mask_map50": 0.9, "box_map50": 0.8}


def test_cli_refuses_unbuilt_datasets(tmp_path: Path) -> None:
    mod = load_script("train/train_detector.py")
    cfg = ROOT / "train" / "configs" / "yolo11n-seg.yaml"
    assert mod.main(["--config", str(cfg), "--project", str(tmp_path)]) == 2


@pytest.mark.ml
def test_train_one_epoch_smoke(tmp_path: Path) -> None:  # pragma: no cover - needs ml extra
    ds = _dataset(tmp_path / "ds", 4)
    cfg = tmp_path / "c.yaml"
    cfg.write_text(
        yaml.safe_dump(
            {
                "name": "smoke",
                "model": "yolo11n-seg.pt",
                "datasets": [str(ds)],
                "epochs": 1,
                "imgsz": 128,
                "batch": 2,
                "augment": {"hsv_h": 0.5, "hsv_s": 0.9, "mosaic": 0.0},
            }
        )
    )
    mod = load_script("train/train_detector.py")
    rc = mod.main(
        [
            "--config",
            str(cfg),
            "--project",
            str(tmp_path / "runs"),
            "--weights-dir",
            str(tmp_path / "w"),
        ]
    )
    assert rc == 0
    report = json.loads((tmp_path / "w" / "detector-smoke.metrics.json").read_text())
    assert "mask_map50" in report["val"]
