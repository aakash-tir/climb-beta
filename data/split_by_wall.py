"""Assign Basecamp walls to train/val/test and build the YOLO-seg dataset.

Usage:
    # 1) assign walls (once; re-run with --reassign only on purpose: it moves walls)
    python data/split_by_wall.py assign [--seed 0] [--ratios 0.7 0.15 0.15]
    # 2) build data/yolo/basecamp from raw photos + labels using splits.yaml
    python data/split_by_wall.py build [--out data/yolo/basecamp]

Never split photos of one wall across train and test: the wall is the unit.
New walls (not yet in splits.yaml) are added by `assign` without moving old ones.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from climb_beta.config import load_classes
from climb_beta.data.sam_masks import load_pseudo_masks
from climb_beta.data.split import (
    SPLITS,
    SplitError,
    assign_walls,
    build_dataset,
    load_splits,
    save_splits,
    scan_walls,
)

BASECAMP = Path(__file__).resolve().parent / "basecamp"


def cmd_assign(args: argparse.Namespace) -> int:
    walls = scan_walls(args.raw)
    if not walls:
        print(f"no wall folders with photos under {args.raw}", file=sys.stderr)
        return 2
    counts = {w: len(p) for w, p in walls.items()}
    if args.splits.exists() and not args.reassign:
        current = load_splits(args.splits)
        known = {w for ws in current.values() for w in ws}
        new = {w: c for w, c in counts.items() if w not in known}
        fresh = assign_walls(new, tuple(args.ratios), args.seed) if new else {}
        merged = {s: sorted(set(current[s]) | set(fresh.get(s, []))) for s in SPLITS}
    else:
        merged = assign_walls(counts, tuple(args.ratios), args.seed)
    save_splits(args.splits, merged)
    for s in SPLITS:
        n = sum(counts.get(w, 0) for w in merged[s])
        print(f"{s:5s}: {len(merged[s])} walls, {n} photos")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    splits = load_splits(args.splits)
    pseudo = load_pseudo_masks(args.labels)
    rep = build_dataset(args.raw, args.labels, splits, args.out, load_classes(), pseudo)
    print(f"images per split: {rep.images}")
    if rep.unlabelled:
        print(f"skipped {len(rep.unlabelled)} unlabelled photos")
    if rep.unassigned_walls:
        print(f"walls not in splits.yaml (run assign): {rep.unassigned_walls}")
    if rep.pseudo_skipped_from_test:
        print(f"kept {len(rep.pseudo_skipped_from_test)} pseudo-masked photos out of test")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--raw", type=Path, default=BASECAMP / "raw")
    ap.add_argument("--labels", type=Path, default=BASECAMP / "labels")
    ap.add_argument("--splits", type=Path, default=BASECAMP / "splits.yaml")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("assign")
    a.add_argument("--seed", type=int, default=0)
    a.add_argument("--ratios", type=float, nargs=3, default=[0.7, 0.15, 0.15])
    a.add_argument("--reassign", action="store_true", help="re-split all walls (moves walls!)")
    b = sub.add_parser("build")
    b.add_argument("--out", type=Path, default=BASECAMP.parent / "yolo" / "basecamp")
    args = ap.parse_args(argv)
    try:
        return cmd_assign(args) if args.cmd == "assign" else cmd_build(args)
    except SplitError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
