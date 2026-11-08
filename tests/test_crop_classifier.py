from pathlib import Path

import cv2
import numpy as np
import pytest
from scripts import load_script
from synth import BLUE, RED, draw_hold, wall

from climb_beta.colour.classifier import CheckpointMeta, preprocess
from climb_beta.colour.crops import extract_crop
from climb_beta.imageio import write_bgr


def test_preprocess_rgb_order_and_shape() -> None:
    red = np.zeros((8, 8, 3), dtype=np.uint8)
    red[..., 2] = 255  # BGR red
    x = preprocess([red, red])
    assert x.shape == (2, 3, 8, 8) and x.dtype == np.float32
    assert x[0, 0].mean() > x[0, 2].mean()  # channel 0 is R after BGR->RGB


def test_checkpoint_meta_roundtrip_and_validation() -> None:
    m = CheckpointMeta("resnet18", ("red", "pink"), 96)
    assert CheckpointMeta.from_dict(m.to_dict()) == m
    for bad in (
        {"arch": "vit", "classes": ["a"], "size": 96},
        {"arch": "resnet18", "classes": ["a", "a"], "size": 96},
        {"arch": "resnet18", "classes": ["a"], "size": 4},
    ):
        with pytest.raises(ValueError):
            CheckpointMeta.from_dict(bad)


def test_augment_never_changes_hue() -> None:
    mod = load_script("colour/train_classifier.py")
    img = np.zeros((16, 16, 3), dtype=np.uint8)
    img[:] = (40, 30, 200)
    rng = np.random.default_rng(0)
    h0 = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)[..., 0].mean()
    for _ in range(20):
        out = mod.augment(img, rng)
        h = cv2.cvtColor(np.ascontiguousarray(out), cv2.COLOR_BGR2HSV)[..., 0].mean()
        assert abs(h - h0) <= 1.0


def _crops(root: Path, n: int = 12) -> Path:
    for split in ("train", "val"):
        for colour, bgr in (("red", RED), ("blue", BLUE)):
            for i in range(n):
                img = wall(h=64, w=64, seed=i)
                m = draw_hold(img, (32, 32), 12 + i % 5, bgr, seed=i)
                write_bgr(root / split / colour / f"{i}.png", extract_crop(img, m, size=48))
    return root


def test_unknown_colour_folder_rejected(tmp_path: Path) -> None:
    mod = load_script("colour/train_classifier.py")
    (tmp_path / "train" / "teal").mkdir(parents=True)
    assert mod.main([str(tmp_path)]) == 2


@pytest.mark.ml
def test_train_and_predict_smoke(tmp_path: Path) -> None:  # pragma: no cover - ml extra
    from climb_beta.colour.classifier import CropClassifier

    mod = load_script("colour/train_classifier.py")
    out = tmp_path / "c.pt"
    args = [str(_crops(tmp_path / "crops")), "--epochs", "3", "--batch", "8", "--out", str(out)]
    assert mod.main([*args, "--arch", "resnet18", "--no-pretrained"]) == 0
    clf = CropClassifier(out)
    img = wall(h=64, w=64, seed=99)
    m = draw_hold(img, (32, 32), 14, RED)
    ((name, conf),) = clf.predict([extract_crop(img, m, size=48)])
    assert name in clf.classes and 0.0 <= conf <= 1.0
