"""Square, background-masked crops of single holds for the colour classifier.

Everything outside the hold's mask is set to neutral grey, so the classifier can only
use the hold's own pixels, never the wall or a neighbouring hold of another colour.
"""

from __future__ import annotations

import csv
import json
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from climb_beta.colour.white_balance import grey_world
from climb_beta.data.yolo import instances_to_detections, read_labels
from climb_beta.imageio import read_bgr, write_bgr
from climb_beta.types import ImageBGR, Mask

NEUTRAL = 128
IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".webp")


def extract_crop(img: ImageBGR, mask: Mask, size: int = 96, pad: float = 0.15) -> ImageBGR:
    """Square crop centred on the mask's bbox, padded by `pad`, resized to `size`."""
    ys, xs = np.nonzero(mask)
    if xs.size == 0:
        return np.full((size, size, 3), NEUTRAL, dtype=np.uint8)
    x0, x1, y0, y1 = int(xs.min()), int(xs.max()) + 1, int(ys.min()), int(ys.max()) + 1
    side = int(round(max(x1 - x0, y1 - y0) * (1 + 2 * pad)))
    side = max(side, 2)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    sx, sy = int(round(cx - side / 2)), int(round(cy - side / 2))
    canvas = np.full((side, side, 3), NEUTRAL, dtype=np.uint8)
    h, w = mask.shape
    ix0, iy0, ix1, iy1 = max(sx, 0), max(sy, 0), min(sx + side, w), min(sy + side, h)
    patch = img[iy0:iy1, ix0:ix1].copy()
    patch[~mask[iy0:iy1, ix0:ix1]] = NEUTRAL
    canvas[iy0 - sy : iy1 - sy, ix0 - sx : ix1 - sx] = patch
    interp = cv2.INTER_AREA if side > size else cv2.INTER_LINEAR
    return np.asarray(cv2.resize(canvas, (size, size), interpolation=interp), dtype=np.uint8)


@dataclass
class CropRecord:
    split: str
    path: str
    colour: str
    chalked: bool
    source: str
    idx: int


@dataclass
class LabelledHold:
    image: ImageBGR  # white-balanced photo (shared between holds of one photo)
    mask: Mask
    record: CropRecord


def iter_labelled_holds(
    dataset: Path, split: str, classes: tuple[str, ...]
) -> Iterator[LabelledHold]:
    """Every labelled hold (with a colour) in a YOLO-seg dataset split with sidecars.

    The photo is white-balanced on its wall pixels first, the same as at inference.
    """
    img_dir, lab_dir, col_dir = (dataset / k / split for k in ("images", "labels", "colours"))
    if not img_dir.is_dir():
        return
    for ip in sorted(p for p in img_dir.iterdir() if p.suffix.lower() in IMAGE_EXTS):
        lp, cp = lab_dir / f"{ip.stem}.txt", col_dir / f"{ip.stem}.json"
        if not lp.exists() or not cp.exists():
            continue
        img = read_bgr(ip)
        if img is None:
            continue
        h, w = img.shape[:2]
        dets = instances_to_detections(read_labels(lp), classes, h, w)
        side = json.loads(cp.read_text(encoding="utf-8"))
        if len(side) != len(dets):
            raise ValueError(f"{cp}: {len(side)} sidecar records for {len(dets)} label lines")
        wall = np.ones((h, w), dtype=bool)
        for d in dets:
            wall &= ~d.mask
        balanced = grey_world(img, ref_mask=wall)
        for i, (d, rec) in enumerate(zip(dets, side, strict=True)):
            if d.cls != "hold" or not rec.get("colour"):
                continue
            yield LabelledHold(
                balanced,
                d.mask,
                CropRecord(split, "", rec["colour"], bool(rec.get("chalked")), ip.name, i),
            )


def iter_hold_crops(
    dataset: Path, split: str, classes: tuple[str, ...], size: int = 96
) -> Iterator[tuple[ImageBGR, CropRecord]]:
    """Crops of every labelled hold in a YOLO-seg dataset split with colour sidecars."""
    for lh in iter_labelled_holds(dataset, split, classes):
        yield extract_crop(lh.image, lh.mask, size), lh.record


def write_crops(
    dataset: Path, out: Path, classes: tuple[str, ...], size: int = 96
) -> list[CropRecord]:
    """ImageFolder tree out/<split>/<colour>/<image>__<idx>.png plus out/index.csv."""
    records = []
    for split in ("train", "val", "test"):
        for crop, rec in iter_hold_crops(dataset, split, classes, size):
            rel = Path(split) / rec.colour / f"{Path(rec.source).stem}__{rec.idx}.png"
            write_bgr(out / rel, crop)
            rec.path = rel.as_posix()
            records.append(rec)
    out.mkdir(parents=True, exist_ok=True)
    with (out / "index.csv").open("w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["split", "path", "colour", "chalked", "source", "idx"])
        for r in records:
            wr.writerow([r.split, r.path, r.colour, int(r.chalked), r.source, r.idx])
    return records
