"""Find the route of a chosen colour in a wall photo (detector + colour + route).

Usage:
    uv sync --extra ml
    python route/find_route.py IMAGE --colour red [--weights weights/detector-yolo11n-seg.pt]
        [--classifier weights/colour-mobilenetv3_large_100.pt] [--out route.json]

Without --colour, groups every colour present. Prints JSON: detections, and per colour
the routes (hold indices, start holds), which one the colour names, and strays.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from climb_beta.config import load_colour_config
from climb_beta.imageio import read_bgr
from climb_beta.pipeline import run
from climb_beta.route.group import load_route_config

DEFAULT_WEIGHTS = os.environ.get("CLIMB_DETECTOR_WEIGHTS", "weights/detector-yolo11n-seg.pt")


def main(argv: list[str] | None = None, detector: object | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("image", type=Path)
    ap.add_argument("--colour", action="append", help="repeatable; default: all colours")
    ap.add_argument("--weights", default=DEFAULT_WEIGHTS)
    ap.add_argument("--classifier", type=Path)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args(argv)

    cfg = load_colour_config()
    for c in args.colour or []:
        if not cfg.has(c):
            print(f"unknown colour {c!r}; choose from {', '.join(cfg.names)}", file=sys.stderr)
            return 2
    img = read_bgr(args.image)
    if img is None:
        print(f"cannot read image {args.image}", file=sys.stderr)
        return 2
    if detector is None:
        from climb_beta.detect import Detector

        detector = Detector(args.weights)
    clf = None
    if args.classifier:
        from climb_beta.colour.classifier import CropClassifier

        clf = CropClassifier(args.classifier)
    res = run(
        img,
        detector,  # type: ignore[arg-type]
        cfg,
        load_route_config(),
        colours=args.colour,
        method="classifier" if clf else "rules",
        classifier=clf,
    )
    text = json.dumps(res.to_json(), indent=1)
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
