"""Download the pinned Roboflow Universe dataset (CC BY 4.0) as coco-segmentation.

Usage:
    uv sync --extra data
    python data/download_roboflow.py [--config data/roboflow.yaml] [--dest data/roboflow]

Reads ROBOFLOW_API_KEY from the environment or .env. Next step:
    python data/convert_roboflow.py data/roboflow/<slug> data/yolo/roboflow [--sam-fallback]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from climb_beta.data.roboflow import RoboflowConfigError, api_key, download, load_source

HERE = Path(__file__).resolve().parent


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(HERE.parent / ".env")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--config", type=Path, default=HERE / "roboflow.yaml")
    ap.add_argument("--dest", type=Path, default=HERE / "roboflow")
    args = ap.parse_args(argv)
    _load_dotenv()
    try:
        src = load_source(args.config)
        key = api_key()
    except RoboflowConfigError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    out = download(src, key, args.dest)
    print(f"downloaded {src.slug} -> {out}")
    print(f"next: python data/convert_roboflow.py {out} data/yolo/roboflow --sam-fallback")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
