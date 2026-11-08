"""Read and write Ultralytics YOLO-seg label files.

One instance per line: `<class_id> x1 y1 x2 y2 ...` with coordinates normalised to
[0, 1] by image width (x) and height (y).
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from climb_beta.masks import FloatArray, denormalise, polygon_to_mask
from climb_beta.types import Detection


@dataclass
class YoloInstance:
    cls_id: int
    polygon: FloatArray  # (N, 2) normalised


def parse_label_line(line: str) -> YoloInstance | None:
    parts = line.split()
    if not parts:
        return None
    if len(parts) < 7 or (len(parts) - 1) % 2:
        raise ValueError(f"bad YOLO-seg line (need class + >=3 xy pairs): {line[:60]!r}")
    coords = np.asarray([float(p) for p in parts[1:]], dtype=np.float64).reshape(-1, 2)
    return YoloInstance(int(parts[0]), coords)


def read_labels(path: Path) -> list[YoloInstance]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        inst = parse_label_line(line)
        if inst is not None:
            out.append(inst)
    return out


def format_label_line(cls_id: int, polygon_norm: FloatArray, decimals: int = 6) -> str:
    coords = " ".join(f"{v:.{decimals}f}" for v in np.clip(polygon_norm, 0, 1).reshape(-1))
    return f"{cls_id} {coords}"


def write_labels(path: Path, instances: Iterable[YoloInstance]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [format_label_line(i.cls_id, i.polygon) for i in instances]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def instances_to_detections(
    instances: Sequence[YoloInstance], classes: Sequence[str], h: int, w: int
) -> list[Detection]:
    """Rasterise label polygons into full-resolution Detection masks."""
    dets = []
    for idx, inst in enumerate(instances):
        if not 0 <= inst.cls_id < len(classes):
            raise ValueError(f"class id {inst.cls_id} out of range for {list(classes)}")
        mask = polygon_to_mask(denormalise(inst.polygon, h, w), h, w)
        dets.append(Detection(mask=mask, cls=classes[inst.cls_id], attrs={"label_idx": idx}))
    return dets
