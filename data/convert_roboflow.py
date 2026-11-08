"""Convert a Roboflow `coco-segmentation` export to a YOLO-seg dataset.

Usage:
    python data/convert_roboflow.py data/roboflow/<export-dir> data/yolo/roboflow

Category names are mapped to our classes (configs/classes.yaml) by `class_map` in
data/roboflow.yaml if present, else by keyword ("hold", "volume", "tape").
Images that have box-only annotations are held back and listed in
conversion_report.json, unless --sam-fallback turns their boxes into SAM masks.
Those images are listed in pseudo_masks.txt and never kept in the test split.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

from climb_beta.config import load_classes
from climb_beta.data.coco_to_yolo import convert_export
from climb_beta.data.sam_masks import DEFAULT_SAM_WEIGHTS, sam_segmenter

HERE = Path(__file__).resolve().parent


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("src", type=Path, help="Roboflow export dir (train/ valid/ test/)")
    ap.add_argument("out", type=Path, help="output YOLO-seg dataset dir")
    ap.add_argument("--config", type=Path, default=HERE / "roboflow.yaml")
    ap.add_argument(
        "--sam-fallback",
        action="store_true",
        help="mask box-only annotations with SAM (needs the ml extra); listed in pseudo_masks.txt",
    )
    ap.add_argument("--sam-weights", default=DEFAULT_SAM_WEIGHTS)
    args = ap.parse_args(argv)

    if not args.src.is_dir():
        print(f"not a directory: {args.src}", file=sys.stderr)
        return 2
    class_map = None
    if args.config.exists():
        class_map = (yaml.safe_load(args.config.read_text(encoding="utf-8")) or {}).get("class_map")
    segmenter = sam_segmenter(args.sam_weights) if args.sam_fallback else None
    report = convert_export(args.src, args.out, load_classes(), class_map, segmenter)
    print(f"images written: {report.images_written}")
    print(f"instances:      {report.instances}")
    if report.dropped_categories:
        print(f"dropped categories: {report.dropped_categories}")
    if report.pseudo_masked:
        print(f"SAM pseudo-masked {len(report.pseudo_masked)} images (pseudo_masks.txt)")
    if report.pseudo_dropped_from_test:
        print(f"dropped {len(report.pseudo_dropped_from_test)} box-only test images")
    held = {b.file_name for b in report.held_back_box_only}
    if held and not args.sam_fallback:
        print(
            f"held back {len(held)} images with box-only annotations (see conversion_report.json)"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
