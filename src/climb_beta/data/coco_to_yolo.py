"""Convert a COCO-segmentation export (e.g. Roboflow's) to Ultralytics YOLO-seg.

Roboflow's `coco-segmentation` export has one folder per split (`train/`, `valid/`,
`test/`), each with images and `_annotations.coco.json`. Output layout:

    OUT/images/{train,val,test}/<file>
    OUT/labels/{train,val,test}/<stem>.txt
    OUT/dataset.yaml
    OUT/conversion_report.json

Annotations with polygons are converted directly. Box-only annotations (empty
`segmentation`) can't become masks here. Their images are held back and listed in
the report, so the SAM fallback (`climb_beta.data.sam_masks`) can mask them, or they
can be dropped. Writing those images without the boxed holds would teach the
detector that real holds are background.
"""

from __future__ import annotations

import json
import shutil
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from climb_beta.data.sam_masks import BoxSegmenter, write_pseudo_masks, xywh_to_xyxy
from climb_beta.data.yolo import YoloInstance, write_labels
from climb_beta.imageio import read_bgr
from climb_beta.masks import FloatArray, mask_to_polygon, normalise

SPLIT_ALIASES = {"train": "train", "valid": "val", "val": "val", "test": "test"}
COCO_JSON = "_annotations.coco.json"


@dataclass
class BoxOnly:
    split: str
    file_name: str
    width: int
    height: int
    cls_id: int
    bbox_xywh: list[float]


@dataclass
class ConversionReport:
    images_written: dict[str, int] = field(default_factory=dict)
    instances: dict[str, int] = field(default_factory=dict)
    dropped_categories: dict[str, int] = field(default_factory=dict)
    multi_polygon_kept_largest: int = 0
    rle_skipped: int = 0
    held_back_box_only: list[BoxOnly] = field(default_factory=list)
    # polygon instances of held-back images, keyed "split/file_name" (not serialised)
    held_back_polygons: dict[str, list[YoloInstance]] = field(default_factory=dict, repr=False)
    pseudo_masked: list[str] = field(default_factory=list)
    pseudo_dropped_from_test: list[str] = field(default_factory=list)

    def to_json(self) -> dict[str, Any]:
        d = asdict(self)
        d.pop("held_back_polygons")
        d["held_back_images"] = sorted({(b.split, b.file_name) for b in self.held_back_box_only})
        return d


def default_class_for(category_name: str, classes: Sequence[str]) -> str | None:
    """Map a source category name to one of our classes by keyword, or None."""
    n = category_name.lower()
    for c in sorted(classes, key=len, reverse=True):
        if c in n:
            return c
    return None


def polygon_area(poly: FloatArray) -> float:
    x, y = poly[:, 0], poly[:, 1]
    return 0.5 * float(abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1))))


def best_polygon(segmentation: Sequence[Sequence[float]]) -> tuple[FloatArray | None, int]:
    """Largest polygon of a COCO polygon list, and how many polygons there were."""
    polys = [np.asarray(p, dtype=np.float64).reshape(-1, 2) for p in segmentation if len(p) >= 6]
    if not polys:
        return None, 0
    return max(polys, key=polygon_area), len(polys)


def convert_split(
    coco: Mapping[str, Any],
    split: str,
    classes: Sequence[str],
    class_map: Mapping[str, str] | None,
    report: ConversionReport,
) -> dict[str, list[YoloInstance]]:
    """Return {file_name: instances} for images that are safe to write."""
    cats = {c["id"]: c["name"] for c in coco.get("categories", [])}
    cls_index = {c: i for i, c in enumerate(classes)}
    images = {im["id"]: im for im in coco.get("images", [])}
    per_image: dict[int, list[YoloInstance]] = {i: [] for i in images}
    held: set[int] = set()

    for ann in coco.get("annotations", []):
        im = images.get(ann["image_id"])
        if im is None:
            continue
        name = cats.get(ann["category_id"], "?")
        target = (class_map or {}).get(name) or default_class_for(name, classes)
        if target is None or target not in cls_index:
            report.dropped_categories[name] = report.dropped_categories.get(name, 0) + 1
            continue
        seg = ann.get("segmentation")
        if isinstance(seg, dict):  # RLE (crowd) - not expected in Roboflow exports
            report.rle_skipped += 1
            continue
        poly, n_polys = best_polygon(seg or [])
        if poly is None:
            report.held_back_box_only.append(
                BoxOnly(
                    split,
                    im["file_name"],
                    im["width"],
                    im["height"],
                    cls_index[target],
                    [float(v) for v in ann["bbox"]],
                )
            )
            held.add(im["id"])
            continue
        if n_polys > 1:
            report.multi_polygon_kept_largest += 1
        per_image[im["id"]].append(
            YoloInstance(cls_index[target], normalise(poly, im["height"], im["width"]))
        )

    for i in held:
        report.held_back_polygons[f"{split}/{images[i]['file_name']}"] = per_image[i]
    return {images[i]["file_name"]: inst for i, inst in per_image.items() if i not in held}


def _pseudo_mask_split(
    d: Path,
    out: Path,
    split: str,
    classes: Sequence[str],
    report: ConversionReport,
    segmenter: BoxSegmenter,
    counts: Counter[str],
) -> int:
    by_image: dict[str, list[BoxOnly]] = {}
    for b in report.held_back_box_only:
        if b.split == split:
            by_image.setdefault(b.file_name, []).append(b)
    written = 0
    for file_name, boxes in sorted(by_image.items()):
        key = f"{split}/{file_name}"
        if split == "test":
            report.pseudo_dropped_from_test.append(key)
            continue
        img = read_bgr(d / file_name)
        if img is None:
            continue
        xyxy = np.asarray([xywh_to_xyxy(b.bbox_xywh) for b in boxes], dtype=np.float64)
        instances = list(report.held_back_polygons.get(key, []))
        for b, m in zip(boxes, segmenter(img, xyxy), strict=True):
            poly = mask_to_polygon(m, epsilon=1.0)
            if poly.shape[0] >= 3:
                instances.append(YoloInstance(b.cls_id, normalise(poly, b.height, b.width)))
        shutil.copy2(d / file_name, out / "images" / split / file_name)
        write_labels(out / "labels" / split / (Path(file_name).stem + ".txt"), instances)
        counts.update(classes[i.cls_id] for i in instances)
        report.pseudo_masked.append(key)
        written += 1
    return written


def write_dataset_yaml(out: Path, classes: Sequence[str], splits: Sequence[str]) -> Path:
    data: dict[str, Any] = {"path": ".", "names": {i: c for i, c in enumerate(classes)}}
    for s in ("train", "val", "test"):
        if s in splits:
            data[s] = f"images/{s}"
    p = out / "dataset.yaml"
    p.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return p


def convert_export(
    src: Path,
    out: Path,
    classes: Sequence[str],
    class_map: Mapping[str, str] | None = None,
    segmenter: BoxSegmenter | None = None,
) -> ConversionReport:
    """Convert every split folder under `src` that has a COCO json.

    With a `segmenter`, held-back images get SAM pseudo-masks for their box-only
    annotations and are written to train/val, and listed in pseudo_masks.txt.
    Held-back *test* images are dropped instead: pseudo-masks are never tested on.
    """
    report = ConversionReport()
    written_splits = []
    for d in sorted(p for p in src.iterdir() if p.is_dir()):
        split = SPLIT_ALIASES.get(d.name)
        js = d / COCO_JSON
        if split is None or not js.exists():
            continue
        coco = json.loads(js.read_text(encoding="utf-8"))
        safe = convert_split(coco, split, classes, class_map, report)
        (out / "images" / split).mkdir(parents=True, exist_ok=True)
        counts: Counter[str] = Counter()
        for file_name, instances in safe.items():
            shutil.copy2(d / file_name, out / "images" / split / file_name)
            write_labels(out / "labels" / split / (Path(file_name).stem + ".txt"), instances)
            counts.update(classes[i.cls_id] for i in instances)
        if segmenter is not None:
            n_pseudo = _pseudo_mask_split(d, out, split, classes, report, segmenter, counts)
        else:
            n_pseudo = 0
        report.images_written[split] = len(safe) + n_pseudo
        for k, v in counts.items():
            report.instances[k] = report.instances.get(k, 0) + v
        written_splits.append(split)
    if segmenter is not None:
        write_pseudo_masks(out, report.pseudo_masked)
    write_dataset_yaml(out, classes, written_splits)
    (out / "conversion_report.json").write_text(
        json.dumps(report.to_json(), indent=2), encoding="utf-8"
    )
    return report
