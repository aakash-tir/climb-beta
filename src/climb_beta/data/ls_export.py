"""Convert a Label Studio JSON export into per-wall YOLO-seg labels + colour sidecars.

For each task (photo) it writes, under labels_root/<wall_id>/:
    <photo>.txt   YOLO-seg, one line per region (hold / volume / tape)
    <photo>.json  sidecar aligned to the label lines:
                  [{"cls": "hold", "colour": "red", "chalked": false}, ...]

Regions are BrushLabels (SAM 2 / painted, RLE) or PolygonLabels (points in percent).
Per-region Choices (`colour`, `chalked`) share the region's `id`. Photo identity comes
from the image path, which must contain `raw/<wall_id>/<photo>` (Label Studio
local-files serving rooted at data/basecamp).
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import unquote

import numpy as np

from climb_beta.config import ColourConfig
from climb_beta.data.yolo import YoloInstance, write_labels
from climb_beta.labelling import schema
from climb_beta.masks import mask_to_polygon, normalise
from climb_beta.types import Mask

RleDecoder = Callable[[list[int], int, int], Mask]
_RAW_RE = re.compile(r"raw/([^/]+)/([^/?#]+)$")


def sdk_rle_decoder(rle: list[int], h: int, w: int) -> Mask:
    """Decode Label Studio brush RLE (needs the `label` extra)."""
    from label_studio_sdk.converter.brush import decode_rle  # lazy

    flat = np.asarray(decode_rle(rle), dtype=np.uint8)
    return flat.reshape(h, w, 4)[:, :, 3] > 0


@dataclass
class ExportReport:
    photos: int = 0
    regions: dict[str, int] = field(default_factory=dict)
    holds_without_colour: list[str] = field(default_factory=list)
    skipped_tasks: list[str] = field(default_factory=list)
    empty_masks: int = 0


def photo_key(image_ref: str) -> tuple[str, str] | None:
    """('wall_id', 'photo.jpg') from a Label Studio image URL/path, or None."""
    path = unquote(image_ref.replace("\\", "/"))
    if "?d=" in path:
        path = path.split("?d=", 1)[1]
    m = _RAW_RE.search(path)
    return (m.group(1), m.group(2)) if m else None


def _latest_annotation(task: dict[str, Any]) -> dict[str, Any] | None:
    anns = [a for a in task.get("annotations", []) if not a.get("was_cancelled")]
    return anns[-1] if anns else None


def task_regions(
    result: Sequence[dict[str, Any]],
    classes: Sequence[str],
    cfg: ColourConfig,
    decode: RleDecoder,
    report: ExportReport,
    where: str,
) -> list[tuple[YoloInstance, dict[str, Any]]]:
    """Regions of one annotation in result order, as (instance, sidecar record)."""
    cls_index = {c: i for i, c in enumerate(classes)}
    colours: dict[str, str] = {}
    chalked: set[str] = set()
    for r in result:
        if r.get("type") != "choices":
            continue
        choices = r.get("value", {}).get("choices", [])
        if r.get("from_name") == schema.COLOUR and choices:
            name = str(choices[0]).lower()
            if not cfg.has(name):
                raise ValueError(f"{where}: colour '{name}' is not in configs/colours.yaml")
            colours[r["id"]] = name
        elif r.get("from_name") == schema.CHALKED and schema.CHALKED_VALUE in choices:
            chalked.add(r["id"])

    out = []
    for r in result:
        rtype, value = r.get("type"), r.get("value", {})
        if rtype not in ("brushlabels", "polygonlabels"):
            continue
        labels = value.get(rtype, [])
        if not labels or labels[0] not in cls_index:
            continue
        cls = labels[0]
        h, w = int(r["original_height"]), int(r["original_width"])
        if rtype == "brushlabels":
            mask = decode(value["rle"], h, w)
            poly = mask_to_polygon(mask, epsilon=1.0)
        else:
            pts = np.asarray(value["points"], dtype=np.float64).reshape(-1, 2)
            poly = pts / 100.0 * np.array([w, h])
        if poly.shape[0] < 3:
            report.empty_masks += 1
            continue
        rid = r["id"]
        rec: dict[str, Any] = {"cls": cls, "colour": None, "chalked": None}
        if cls == "hold":
            rec["colour"] = colours.get(rid)
            rec["chalked"] = rid in chalked
            if rec["colour"] is None:
                report.holds_without_colour.append(f"{where}#{rid}")
        out.append((YoloInstance(cls_index[cls], normalise(poly, h, w)), rec))
        report.regions[cls] = report.regions.get(cls, 0) + 1
    return out


def convert_ls_export(
    export_json: Path,
    labels_root: Path,
    classes: Sequence[str],
    cfg: ColourConfig,
    decode: RleDecoder = sdk_rle_decoder,
) -> ExportReport:
    tasks = json.loads(export_json.read_text(encoding="utf-8"))
    report = ExportReport()
    for task in tasks:
        ref = str(task.get("data", {}).get(schema.IMAGE, ""))
        key = photo_key(ref)
        ann = _latest_annotation(task)
        if key is None or ann is None:
            report.skipped_tasks.append(ref or f"task {task.get('id')}")
            continue
        wall, photo = key
        where = f"{wall}/{photo}"
        regions = task_regions(ann.get("result", []), classes, cfg, decode, report, where)
        stem = Path(photo).stem
        write_labels(labels_root / wall / f"{stem}.txt", [inst for inst, _ in regions])
        (labels_root / wall / f"{stem}.json").write_text(
            json.dumps([rec for _, rec in regions], indent=1), encoding="utf-8"
        )
        report.photos += 1
    return report
