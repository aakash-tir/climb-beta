"""Check every Phase 1 exit criterion on the held-out test walls.

| criterion                         | target  | measured on                               |
|-----------------------------------|---------|-------------------------------------------|
| hold recall (mask IoU >= 0.5)     | >= 0.95 | detector output vs GT holds               |
| mask mAP50                        | >= 0.85 | detector output, classes with GT          |
| colour accuracy, overall          | >= 0.95 | colour step on GT hold masks              |
| colour accuracy, pink vs red      | >= 0.90 | GT pink/red holds                         |
| colour accuracy, chalked          | >= 0.90 | GT holds flagged chalked                  |
| named route within 1 hold         | >= 0.90 | routes.yaml, complete routes (9/10)       |

Colour is measured on ground-truth masks, so a detector miss is counted once (recall),
not twice. Pseudo-masked images are skipped. The test walls must not appear in train
or val (checked against the dataset manifest when it exists). A criterion with nothing
to measure FAILS: an empty test set never passes.

Routes are Basecamp routes: hold colour + grade (tape diamond colour), with a start and
a finish. Only `complete` ground-truth routes (start and finish both in the photo) are
scored. The predicted route is the named route for that colour and grade. GT `holds`
are the route's own holds plus any taped grey/black start holds; untaped shared holds
the route may use are not scored.
"""

from __future__ import annotations

import json
import math
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from climb_beta.colour.crops import IMAGE_EXTS, extract_crop
from climb_beta.colour.rules import classify_hold
from climb_beta.colour.white_balance import grey_world
from climb_beta.config import ColourConfig
from climb_beta.data.sam_masks import load_pseudo_masks
from climb_beta.data.yolo import instances_to_detections, read_labels
from climb_beta.detect import DetectorLike
from climb_beta.imageio import read_bgr
from climb_beta.metrics.colour import colour_report
from climb_beta.metrics.detection import DetectionAccumulator
from climb_beta.metrics.route import score_route
from climb_beta.pipeline import ClassifierLike, ColourMethod, run
from climb_beta.route.group import RouteConfig
from climb_beta.types import Mask

TARGETS: dict[str, float] = {
    "hold_recall": 0.95,
    "mask_map50": 0.85,
    "colour_overall": 0.95,
    "colour_pink_red": 0.90,
    "colour_chalked": 0.90,
    "route_within_1": 0.90,
}
LABELS = {
    "hold_recall": "Hold recall (IoU>=0.5)",
    "mask_map50": "Mask mAP50",
    "colour_overall": "Colour accuracy, overall",
    "colour_pink_red": "Colour accuracy, pink vs red",
    "colour_chalked": "Colour accuracy, chalked",
    "route_within_1": "Named route within 1 hold",
}


class LeakageError(RuntimeError):
    pass


@dataclass
class ExitReport:
    values: dict[str, float | None]
    counts: dict[str, int]
    details: dict[str, Any] = field(default_factory=dict)

    def passed(self, key: str) -> bool:
        v = self.values.get(key)
        return v is not None and not math.isnan(v) and v >= TARGETS[key]

    @property
    def all_passed(self) -> bool:
        return all(self.passed(k) for k in TARGETS)

    def table(self) -> str:
        rows = [f"{'criterion':34s} {'value':>8s} {'target':>8s} {'n':>6s}  result"]
        for k, target in TARGETS.items():
            v = self.values.get(k)
            shown = "n/a" if v is None or math.isnan(v) else f"{v:.3f}"
            res = "PASS" if self.passed(k) else "FAIL"
            rows.append(
                f"{LABELS[k]:34s} {shown:>8s} {target:>8.2f} {self.counts.get(k, 0):>6d}  {res}"
            )
        rows.append("")
        rows.append(
            "ALL PASS: Phase 2 may start." if self.all_passed else "NOT PASSED: Phase 2 waits."
        )
        return "\n".join(rows)

    def to_json(self) -> dict[str, Any]:
        return {
            "values": self.values,
            "counts": self.counts,
            "targets": TARGETS,
            "passed": {k: self.passed(k) for k in TARGETS},
            "all_passed": self.all_passed,
            "details": self.details,
        }


def check_no_wall_leakage(dataset: Path, split: str) -> None:
    """Raise if a wall in `split` also appears in another split of the manifest."""
    mf = dataset / "manifest.json"
    if not mf.exists():
        return
    walls: dict[str, set[str]] = {}
    for row in json.loads(mf.read_text(encoding="utf-8")):
        walls.setdefault(row["wall"], set()).add(row["split"])
    leaked = sorted(w for w, s in walls.items() if split in s and len(s) > 1)
    if leaked:
        raise LeakageError(f"test walls also in train/val: {leaked}")


def load_routes_gt(path: Path | None) -> list[dict[str, Any]]:
    """Load and validate routes.yaml.

    Entries: {image: <file name in the test split>, colour: red, holds: [line idx],
    grade: green, start: [line idx], finish: <line idx>, complete: true}. `grade`,
    `start` and `finish` are optional; `complete` defaults to true. `start`/`finish` must
    be among `holds`.
    """
    if path is None or not path.exists():
        return []
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    routes = raw.get("routes", []) if isinstance(raw, dict) else raw
    for r in routes:
        if not {"image", "colour", "holds"} <= set(r):
            raise ValueError(f"routes.yaml entry needs image, colour, holds: {r}")
        holds = {int(i) for i in r["holds"]}
        if not {int(i) for i in r.get("start", [])} <= holds:
            raise ValueError(f"routes.yaml start holds must be in holds: {r}")
        if r.get("finish") is not None and int(r["finish"]) not in holds:
            raise ValueError(f"routes.yaml finish must be in holds: {r}")
        if not isinstance(r.get("complete", True), bool):
            raise ValueError(f"routes.yaml complete must be true/false: {r}")
        if r.get("grade") is not None and not isinstance(r["grade"], str):
            raise ValueError(f"routes.yaml grade must be a colour name: {r}")
    return list(routes)


def evaluate(
    dataset: Path,
    detector: DetectorLike,
    colour_cfg: ColourConfig,
    classes: Sequence[str],
    route_cfg: RouteConfig | None = None,
    routes_gt: Sequence[dict[str, Any]] = (),
    split: str = "test",
    method: ColourMethod = "rules",
    classifier: ClassifierLike | None = None,
) -> ExitReport:
    check_no_wall_leakage(dataset, split)
    pseudo = load_pseudo_masks(dataset)
    img_dir, lab_dir, col_dir = (dataset / k / split for k in ("images", "labels", "colours"))
    images = (
        sorted(p for p in img_dir.iterdir() if p.suffix.lower() in IMAGE_EXTS)
        if img_dir.is_dir()
        else []
    )
    routes_by_image: dict[str, list[dict[str, Any]]] = {}
    incomplete: list[dict[str, Any]] = []
    for r in routes_gt:
        if r.get("complete", True):
            routes_by_image.setdefault(str(r["image"]), []).append(r)
        else:
            incomplete.append({k: r.get(k) for k in ("image", "colour", "grade")})

    acc = DetectionAccumulator(classes)
    truth: list[str] = []
    pred_col: list[str] = []
    chalked: list[bool] = []
    route_rows: list[dict[str, Any]] = []
    skipped = []
    for ip in images:
        if f"{split}/{ip.name}" in pseudo:
            skipped.append(ip.name)
            continue
        lp, cp = lab_dir / f"{ip.stem}.txt", col_dir / f"{ip.stem}.json"
        img = read_bgr(ip)
        if img is None or not lp.exists():
            continue
        h, w = img.shape[:2]
        gts = instances_to_detections(read_labels(lp), classes, h, w)
        side = json.loads(cp.read_text(encoding="utf-8")) if cp.exists() else []

        wanted = sorted({str(r["colour"]) for r in routes_by_image.get(ip.name, [])})
        res = run(img, detector, colour_cfg, route_cfg, wanted, method, classifier)
        acc.add(res.detections, gts)

        # colour step on GT masks
        if side:
            wall = ~sum_masks([g.mask for g in gts], (h, w))
            balanced = grey_world(img, ref_mask=wall)
            holds = [
                (g, s)
                for g, s in zip(gts, side, strict=True)
                if g.cls == "hold" and s.get("colour")
            ]
            if method == "classifier" and classifier is not None:
                crops = [extract_crop(balanced, g.mask) for g, _ in holds]
                names = [n for n, _ in classifier.predict(crops)]
            else:
                names = [classify_hold(balanced, g.mask, colour_cfg).name for g, _ in holds]
            for (_, s), n in zip(holds, names, strict=True):
                truth.append(str(s["colour"]))
                pred_col.append(n)
                chalked.append(bool(s.get("chalked")))

        for r in routes_by_image.get(ip.name, []):
            grade = r.get("grade")
            named = res.routes[str(r["colour"])].named_route(grade)
            pred_masks = [res.detections[i].mask for i in named.holds] if named else []
            gt_masks = [gts[int(i)].mask for i in r["holds"]]
            sc = score_route(pred_masks, gt_masks)
            route_rows.append(
                {
                    "image": ip.name,
                    "colour": r["colour"],
                    "grade": grade,
                    "missed": sc.missed,
                    "extra": sc.extra,
                    "correct": sc.correct(1),
                    "pred_complete": bool(named and named.complete),
                }
            )

    det = acc.report()
    cr = colour_report(truth, pred_col, chalked, colour_cfg.names) if truth else None
    n_routes = len(route_rows)
    values: dict[str, float | None] = {
        "hold_recall": None if det.per_class["hold"].n_gt == 0 else det.hold_recall,
        "mask_map50": None if math.isnan(det.map50) else det.map50,
        "colour_overall": cr.overall if cr else None,
        "colour_pink_red": cr.pink_red if cr else None,
        "colour_chalked": cr.chalked if cr else None,
        "route_within_1": sum(r["correct"] for r in route_rows) / n_routes if n_routes else None,
    }
    counts = {
        "hold_recall": det.per_class["hold"].n_gt,
        "mask_map50": sum(s.n_gt for s in det.per_class.values()),
        "colour_overall": cr.n if cr else 0,
        "colour_pink_red": cr.pink_red_n if cr else 0,
        "colour_chalked": cr.chalked_n if cr else 0,
        "route_within_1": n_routes,
    }
    details: dict[str, Any] = {
        "split": split,
        "images": len(images) - len(skipped),
        "skipped_pseudo_masked": skipped,
        "ap50_per_class": {c: s.ap50 for c, s in det.per_class.items() if s.n_gt},
        "routes": route_rows,
        "routes_skipped_incomplete": incomplete,
        "colour_method": method,
    }
    if cr:
        details["colour_per_class"] = cr.per_colour
    return ExitReport(values, counts, details)


def sum_masks(masks: Sequence[Mask], shape: tuple[int, int]) -> Mask:
    out = np.zeros(shape, dtype=bool)
    for m in masks:
        out |= m
    return out
