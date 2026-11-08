"""Cut a white-balanced, background-masked crop of every labelled hold.

Usage:
    python colour/make_crops.py data/yolo/basecamp data/crops/basecamp [--size 96]

Output: an ImageFolder tree <out>/<split>/<colour>/<photo>__<idx>.png plus
<out>/index.csv (split, path, colour, chalked, source, idx) used by the colour eval.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

from climb_beta.colour.crops import write_crops
from climb_beta.config import load_classes


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("dataset", type=Path, help="YOLO-seg dataset with colours/<split>/ sidecars")
    ap.add_argument("out", type=Path)
    ap.add_argument("--size", type=int, default=96)
    args = ap.parse_args(argv)
    if not (args.dataset / "images").is_dir():
        print(f"not a YOLO dataset: {args.dataset}", file=sys.stderr)
        return 2
    recs = write_crops(args.dataset, args.out, load_classes(), args.size)
    by = Counter((r.split, r.colour) for r in recs)
    for (split, colour), n in sorted(by.items()):
        print(f"{split:5s} {colour:8s} {n}")
    print(f"{len(recs)} crops -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
