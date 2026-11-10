"""Check every Phase 1 exit criterion on the held-out test walls. Exit 0 only if all pass.

Usage:
    uv sync --extra ml
    python eval/check_exit_criteria.py [--dataset data/yolo/basecamp]
        [--weights weights/detector-yolo11n-seg.pt] [--routes data/basecamp/routes.yaml]
        [--classifier weights/colour-mobilenetv3_large_100.pt] [--json report.json]

Targets: hold recall >= 95%, mask mAP50 >= 0.85, colour >= 95% overall and >= 90% on
pink-vs-red and chalked holds, named route (hold colour + grade) within 1 hold on
>= 9/10 complete test routes (start and finish both visible).
Phase 2 (animated beta) waits until this exits 0.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from climb_beta.config import load_classes, load_colour_config
from climb_beta.metrics.exit_criteria import LeakageError, evaluate, load_routes_gt
from climb_beta.route.group import load_route_config

ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None, detector: object | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dataset", type=Path, default=ROOT / "data" / "yolo" / "basecamp")
    ap.add_argument("--split", default="test")
    ap.add_argument(
        "--weights",
        default=os.environ.get("CLIMB_DETECTOR_WEIGHTS", "weights/detector-yolo11n-seg.pt"),
    )
    ap.add_argument("--routes", type=Path, default=ROOT / "data" / "basecamp" / "routes.yaml")
    ap.add_argument("--classifier", type=Path)
    ap.add_argument("--json", type=Path)
    args = ap.parse_args(argv)

    if not (args.dataset / "images" / args.split).is_dir():
        print(f"no {args.split} split in {args.dataset}: build it first", file=sys.stderr)
        return 2
    if detector is None:
        from climb_beta.detect import Detector

        detector = Detector(args.weights)
    clf = None
    if args.classifier:
        from climb_beta.colour.classifier import CropClassifier

        clf = CropClassifier(args.classifier)
    try:
        report = evaluate(
            args.dataset,
            detector,  # type: ignore[arg-type]
            load_colour_config(),
            load_classes(),
            load_route_config(),
            load_routes_gt(args.routes),
            split=args.split,
            method="classifier" if clf else "rules",
            classifier=clf,
        )
    except LeakageError as e:
        print(f"REFUSING: {e}", file=sys.stderr)
        return 2
    print(report.table())
    if args.json:
        args.json.write_text(json.dumps(report.to_json(), indent=2), encoding="utf-8")
    return 0 if report.all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
