"""Print a per-colour confusion matrix for the rules and (optionally) the classifier.

Usage:
    python colour/eval_colour.py data/yolo/basecamp [--split val] [--json out.json]
        [--classifier weights/colour-mobilenetv3_large_100.pt]

Uses ground-truth masks (labelled holds), so it measures the colour step alone,
separately from the detector. Reports overall, pink-vs-red and chalked accuracy
(exit criteria: 95% / 90% / 90%).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from climb_beta.colour.crops import extract_crop, iter_labelled_holds
from climb_beta.colour.rules import classify_hold
from climb_beta.config import load_classes, load_colour_config
from climb_beta.metrics.colour import ColourReport, colour_report, format_report


def _as_json(r: ColourReport) -> dict[str, Any]:
    return {
        "n": r.n,
        "overall": r.overall,
        "pink_red": r.pink_red,
        "pink_red_n": r.pink_red_n,
        "chalked": r.chalked,
        "chalked_n": r.chalked_n,
        "per_colour": r.per_colour,
        "labels": list(r.labels),
        "matrix": r.matrix.tolist(),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("dataset", type=Path)
    ap.add_argument("--split", default="val", choices=["train", "val", "test"])
    ap.add_argument("--classifier", type=Path, help="crop classifier checkpoint (ml extra)")
    ap.add_argument("--json", type=Path)
    args = ap.parse_args(argv)

    cfg = load_colour_config()
    holds = list(iter_labelled_holds(args.dataset, args.split, load_classes()))
    if not holds:
        print(f"no labelled holds in {args.dataset} [{args.split}]", file=sys.stderr)
        return 2
    truth = [h.record.colour for h in holds]
    chalked = [h.record.chalked for h in holds]
    rules = [classify_hold(h.image, h.mask, cfg).name for h in holds]
    reports = {"rules": colour_report(truth, rules, chalked, cfg.names)}

    if args.classifier:
        from climb_beta.colour.classifier import CropClassifier

        clf = CropClassifier(args.classifier)
        crops = [extract_crop(h.image, h.mask, clf.meta.size) for h in holds]
        pred = [name for name, _ in clf.predict(crops)]
        reports["classifier"] = colour_report(truth, pred, chalked, cfg.names)

    for name, r in reports.items():
        print(format_report(r, f"== {name} [{args.split}]"))
        print()
    if args.json:
        args.json.write_text(json.dumps({k: _as_json(v) for k, v in reports.items()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
