"""Convert a Label Studio JSON export into data/basecamp/labels/<wall>/<photo>.{txt,json}.

Usage:
    uv sync --extra label
    python labelling/export_to_yolo.py data/basecamp/exports/project-1.json

Then: python data/split_by_wall.py build
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from climb_beta.config import load_classes, load_colour_config
from climb_beta.data.ls_export import convert_ls_export

BASECAMP = Path(__file__).resolve().parents[1] / "data" / "basecamp"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("export", type=Path, help="Label Studio export (JSON)")
    ap.add_argument("--labels", type=Path, default=BASECAMP / "labels")
    args = ap.parse_args(argv)
    if not args.export.exists():
        print(f"no such export: {args.export}", file=sys.stderr)
        return 2
    try:
        rep = convert_ls_export(args.export, args.labels, load_classes(), load_colour_config())
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    print(f"photos: {rep.photos}  regions: {rep.regions}")
    if rep.holds_without_colour:
        print(f"WARNING {len(rep.holds_without_colour)} holds have no colour choice:")
        for h in rep.holds_without_colour[:20]:
            print(f"  {h}")
    if rep.skipped_tasks:
        print(f"skipped {len(rep.skipped_tasks)} tasks (no annotation, or path not raw/<wall>/)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
