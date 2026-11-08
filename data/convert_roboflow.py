"""Convert a Roboflow `coco-segmentation` export to a YOLO-seg dataset.

Usage:
    python data/convert_roboflow.py data/roboflow/<export-dir> data/yolo/roboflow

Category names are mapped to our classes (configs/classes.yaml) by `class_map` in
data/roboflow.yaml if present, else by keyword ("hold", "volume", "tape").
Images that have box-only annotations are held back and listed in
conversion_report.json (see the SAM fallback for turning them into masks).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

from climb_beta.config import load_classes
from climb_beta.data.coco_to_yolo import convert_export

HERE = Path(__file__).resolve().parent


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("src", type=Path, help="Roboflow export dir (train/ valid/ test/)")
    ap.add_argument("out", type=Path, help="output YOLO-seg dataset dir")
    ap.add_argument("--config", type=Path, default=HERE / "roboflow.yaml")
    args = ap.parse_args(argv)

    if not args.src.is_dir():
        print(f"not a directory: {args.src}", file=sys.stderr)
        return 2
    class_map = None
    if args.config.exists():
        class_map = (yaml.safe_load(args.config.read_text(encoding="utf-8")) or {}).get("class_map")
    report = convert_export(args.src, args.out, load_classes(), class_map)
    print(f"images written: {report.images_written}")
    print(f"instances:      {report.instances}")
    if report.dropped_categories:
        print(f"dropped categories: {report.dropped_categories}")
    held = {b.file_name for b in report.held_back_box_only}
    if held:
        print(
            f"held back {len(held)} images with box-only annotations (see conversion_report.json)"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
