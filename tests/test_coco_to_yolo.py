import json
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import pytest
import yaml
from scripts import load_script

from climb_beta.data.coco_to_yolo import best_polygon, convert_export, default_class_for
from climb_beta.data.yolo import read_labels

CLASSES = ("hold", "volume", "tape")


def _coco(images: list[dict[str, Any]], anns: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "images": images,
        "categories": [
            {"id": 0, "name": "climbing-holds"},  # Roboflow's superclass, unused
            {"id": 1, "name": "Hold"},
            {"id": 2, "name": "Volume"},
            {"id": 3, "name": "person"},
        ],
        "annotations": anns,
    }


def _export(tmp: Path) -> Path:
    src = tmp / "export"
    for folder, fname in (("train", "a.jpg"), ("valid", "b.jpg")):
        d = src / folder
        d.mkdir(parents=True)
        cv2.imwrite(str(d / fname), np.zeros((100, 200, 3), dtype=np.uint8))
    train = _coco(
        [{"id": 1, "file_name": "a.jpg", "width": 200, "height": 100}],
        [
            {
                "id": 1,
                "image_id": 1,
                "category_id": 1,
                "bbox": [20, 10, 20, 20],
                "segmentation": [[20, 10, 40, 10, 40, 30, 20, 30]],
            },
            {
                "id": 2,
                "image_id": 1,
                "category_id": 2,
                "bbox": [100, 50, 60, 40],
                # two parts: the larger one must be kept
                "segmentation": [[100, 50, 102, 50, 102, 52], [100, 50, 160, 50, 160, 90, 100, 90]],
            },
            {
                "id": 3,
                "image_id": 1,
                "category_id": 3,
                "bbox": [0, 0, 5, 5],
                "segmentation": [[0, 0, 5, 0, 5, 5]],
            },
        ],
    )
    valid = _coco(
        [{"id": 7, "file_name": "b.jpg", "width": 200, "height": 100}],
        [{"id": 9, "image_id": 7, "category_id": 1, "bbox": [10, 10, 10, 10], "segmentation": []}],
    )
    (src / "train" / "_annotations.coco.json").write_text(json.dumps(train))
    (src / "valid" / "_annotations.coco.json").write_text(json.dumps(valid))
    return src


def test_convert_export(tmp_path: Path) -> None:
    out = tmp_path / "yolo"
    rep = convert_export(_export(tmp_path), out, CLASSES)

    labels = read_labels(out / "labels" / "train" / "a.txt")
    assert [i.cls_id for i in labels] == [0, 1]
    assert np.allclose(labels[0].polygon[0], [0.1, 0.1])  # 20/200, 10/100
    assert labels[1].polygon.shape[0] == 4  # largest part kept
    assert rep.multi_polygon_kept_largest == 1
    assert rep.dropped_categories == {"person": 1}
    # box-only image held back, not written
    assert rep.images_written == {"train": 1, "val": 0}
    assert not (out / "images" / "val" / "b.jpg").exists()
    assert [b.file_name for b in rep.held_back_box_only] == ["b.jpg"]

    ds = yaml.safe_load((out / "dataset.yaml").read_text())
    assert ds["names"] == {0: "hold", 1: "volume", 2: "tape"}
    assert ds["train"] == "images/train" and ds["val"] == "images/val" and "test" not in ds
    assert json.loads((out / "conversion_report.json").read_text())["held_back_images"] == [
        ["val", "b.jpg"]
    ]


def test_explicit_class_map_wins(tmp_path: Path) -> None:
    rep = convert_export(_export(tmp_path), tmp_path / "o", CLASSES, {"Volume": "hold"})
    labels = read_labels(tmp_path / "o" / "labels" / "train" / "a.txt")
    assert [i.cls_id for i in labels] == [0, 0]
    assert rep.instances == {"hold": 2}


@pytest.mark.parametrize(
    ("name", "expected"),
    [("Hold", "hold"), ("climbing-volumes", "volume"), ("start tape", "tape"), ("bolt", None)],
)
def test_default_class_for(name: str, expected: str | None) -> None:
    assert default_class_for(name, CLASSES) == expected


def test_best_polygon_ignores_degenerate() -> None:
    poly, n = best_polygon([[1, 2, 3, 4]])
    assert poly is None and n == 0


def test_cli(tmp_path: Path) -> None:
    mod = load_script("data/convert_roboflow.py")
    src = _export(tmp_path)
    cfg = tmp_path / "none.yaml"
    assert mod.main([str(src), str(tmp_path / "out"), "--config", str(cfg)]) == 0
    assert mod.main([str(tmp_path / "missing"), str(tmp_path / "out")]) == 2
