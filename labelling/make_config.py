"""Regenerate labelling/label_config.xml from configs/colours.yaml and configs/classes.yaml.

Usage:
    python labelling/make_config.py [--check]

--check exits 1 if the committed file is out of date (used by the tests).
Paste the XML into Label Studio: Project > Settings > Labeling Interface > Code.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from climb_beta.config import load_classes, load_colour_config
from climb_beta.labelling.make_config import build_config

OUT = Path(__file__).resolve().parent / "label_config.xml"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    xml = build_config(load_classes(), load_colour_config())
    if args.check:
        current = args.out.read_text(encoding="utf-8") if args.out.exists() else ""
        if current != xml:
            print(
                f"{args.out} is out of date; run python labelling/make_config.py", file=sys.stderr
            )
            return 1
        return 0
    args.out.write_text(xml, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
