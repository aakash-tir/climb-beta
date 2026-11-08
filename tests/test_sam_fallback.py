import json
from pathlib import Path

import cv2
import numpy as np
import pytest

from climb_beta.data.coco_to_yolo import convert_export
from climb_beta.data.sam_masks import (
    box_fill_segmenter,
    load_pseudo_masks,
    xywh_to_xyxy,
)
from climb_beta.data.yolo import read_labels

CLASSES = ("hold", "volume", "tape")
CATS = [{"id": 1, "name": "hold"}, {"id": 2, "name": "volume"}]


def _split(src: Path, folder: str, fname: str, anns: list[dict]) -> None:
    d = src / folder
    d.mkdir(parents=True)
    cv2.imwrite(str(d / fname), np.zeros((100, 200, 3), dtype=np.uint8))
    coco = {
        "images": [{"id": 1, "file_name": fname, "width": 200, "height": 100}],
        "categories": CATS,
        "annotations": [{"id": i, "image_id": 1, **a} for i, a in enumerate(anns)],
    }
    (d / "_annotations.coco.json").write_text(json.dumps(coco))


@pytest.fixture
def export(tmp_path: Path) -> Path:
    src = tmp_path / "export"
    poly = {
        "category_id": 1,
        "bbox": [0, 0, 10, 10],
        "segmentation": [[0, 0, 10, 0, 10, 10, 0, 10]],
    }
    box = {"category_id": 2, "bbox": [50, 20, 40, 30], "segmentation": []}
    _split(src, "train", "mixed.jpg", [poly, box])  # one polygon + one box-only
    _split(src, "valid", "clean.jpg", [poly])
    _split(src, "test", "boxonly.jpg", [box])
    return src


def test_without_segmenter_box_images_held_back(export: Path, tmp_path: Path) -> None:
    out = tmp_path / "o"
    rep = convert_export(export, out, CLASSES)
    assert rep.images_written == {"train": 0, "val": 1, "test": 0}
    assert load_pseudo_masks(out) == set()


def test_segmenter_fills_boxes_keeps_polygons_and_never_tests_on_pseudo(
    export: Path, tmp_path: Path
) -> None:
    out = tmp_path / "o"
    rep = convert_export(export, out, CLASSES, segmenter=box_fill_segmenter)
    assert rep.images_written == {"train": 1, "val": 1, "test": 0}
    labels = read_labels(out / "labels" / "train" / "mixed.txt")
    assert sorted(i.cls_id for i in labels) == [0, 1]  # original polygon + pseudo volume
    vol = next(i for i in labels if i.cls_id == 1)
    assert vol.polygon[:, 0].min() == pytest.approx(0.25, abs=0.01)  # x=50/200
    assert load_pseudo_masks(out) == {"train/mixed.jpg"}
    assert rep.pseudo_dropped_from_test == ["test/boxonly.jpg"]
    assert not (out / "images" / "test" / "boxonly.jpg").exists()
    js = json.loads((out / "conversion_report.json").read_text())
    assert js["pseudo_masked"] == ["train/mixed.jpg"]


def test_xywh_to_xyxy() -> None:
    assert xywh_to_xyxy([1, 2, 3, 4]) == [1, 2, 4, 6]


@pytest.mark.ml
def test_sam_segmenter_smoke() -> None:  # pragma: no cover - needs ml extra + weights
    from climb_beta.data.sam_masks import sam_segmenter

    img = np.full((128, 128, 3), 200, dtype=np.uint8)
    cv2.circle(img, (64, 64), 20, (0, 0, 200), -1)
    masks = sam_segmenter()(img, np.array([[40.0, 40.0, 88.0, 88.0]]))
    assert len(masks) == 1 and masks[0][64, 64]
