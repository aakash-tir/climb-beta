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

from climb_beta.data.yolo import YoloInstance, write_labels
from climb_beta.masks import FloatArray, normalise

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

    def to_json(self) -> dict[str, Any]:
        d = asdict(self)
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

    return {images[i]["file_name"]: inst for i, inst in per_image.items() if i not in held}


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
) -> ConversionReport:
    """Convert every split folder under `src` that has a COCO json."""
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
        report.images_written[split] = len(safe)
        for k, v in counts.items():
            report.instances[k] = report.instances.get(k, 0) + v
        written_splits.append(split)
    write_dataset_yaml(out, classes, written_splits)
    (out / "conversion_report.json").write_text(
        json.dumps(report.to_json(), indent=2), encoding="utf-8"
    )
    return report
