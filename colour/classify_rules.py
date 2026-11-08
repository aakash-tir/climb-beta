"""Label each hold's colour in a photo with the rule-based colour step.

Usage:
    python colour/classify_rules.py IMAGE LABELS.txt [--out holds.json] [--debug debug.png]

LABELS.txt is a YOLO-seg label file for IMAGE (from the detector or from labelling).
Prints / writes one JSON record per label line.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

from climb_beta.colour.batch import colour_detections
from climb_beta.config import load_classes, load_colour_config
from climb_beta.data.yolo import instances_to_detections, read_labels


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("image", type=Path)
    ap.add_argument("labels", type=Path)
    ap.add_argument("--out", type=Path, help="write JSON here (default: stdout)")
    ap.add_argument("--debug", type=Path, help="write an annotated image here")
    ap.add_argument("--no-wb", action="store_true", help="skip white balance")
    args = ap.parse_args(argv)

    img = cv2.imread(str(args.image), cv2.IMREAD_COLOR)
    if img is None:
        print(f"cannot read image {args.image}", file=sys.stderr)
        return 2
    h, w = img.shape[:2]
    dets = instances_to_detections(read_labels(args.labels), load_classes(), h, w)
    cfg = load_colour_config()
    _, results = colour_detections(img, dets, cfg, white_balance=not args.no_wb)

    records = []
    for i, (d, r) in enumerate(zip(dets, results, strict=True)):
        cx, cy = d.centroid()
        rec: dict[str, object] = {"idx": i, "cls": d.cls, "centroid": [round(cx, 1), round(cy, 1)]}
        if r is not None:
            rec |= {
                "colour": r.name,
                "confidence": round(r.confidence, 3),
                "chalk_frac": round(r.chalk_frac, 3),
                "reason": r.reason,
            }
        records.append(rec)

    text = json.dumps(records, indent=2)
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)

    if args.debug:
        vis = img.copy()
        for d, rec in zip(dets, records, strict=True):
            contours, _ = cv2.findContours(
                d.mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            cv2.drawContours(vis, contours, -1, (255, 255, 255), 1)
            cx, cy = rec["centroid"]  # type: ignore[misc]
            label = str(rec.get("colour", d.cls))
            cv2.putText(vis, label, (int(cx), int(cy)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 2)
            cv2.putText(
                vis, label, (int(cx), int(cy)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1
            )
        cv2.imwrite(str(args.debug), vis)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
