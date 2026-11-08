"""Assemble a self-contained Hugging Face Space folder (Gradio, CPU Basic).

Usage:
    python app/build_space.py dist/space
    # then push dist/space to your Space repo (see docs/runbooks/deploy-space.md)

The folder holds app.py, the climb_beta package, configs/, a CPU-only requirements.txt
and a README.md with the Space front matter. Detector weights are NOT copied: set the
Space variable CLIMB_DETECTOR_WEIGHTS=hf://<user>/<repo>/<file>.pt instead.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FRONT_MATTER = """---
title: climb-beta
emoji: 🧗
colorFrom: red
colorTo: indigo
sdk: gradio
sdk_version: {gradio}
app_file: app.py
pinned: false
license: agpl-3.0
short_description: Find a climbing route by hold colour (Phase 1 demo)
---

# climb-beta demo

Upload a photo of a wall at Basecamp Climbing, pick a colour, and see that route's holds.
Source and licence (AGPL-3.0): see the climb-beta repository.

Set the Space variable `CLIMB_DETECTOR_WEIGHTS` to `hf://<user>/<repo>/<file>.pt`.
"""

# CPU wheels keep the image small; Spaces CPU Basic has no GPU.
REQUIREMENTS = """--extra-index-url https://download.pytorch.org/whl/cpu
torch
torchvision
ultralytics>=8.3.40
timm>=1.0
numpy
opencv-python-headless
pyyaml
pillow
huggingface_hub
"""


def build(out: Path, gradio_version: str) -> Path:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    shutil.copytree(
        ROOT / "src" / "climb_beta",
        out / "climb_beta",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    shutil.copytree(ROOT / "configs", out / "configs")
    shutil.copy2(ROOT / "app" / "app.py", out / "app.py")  # finds configs/ next to itself
    (out / "requirements.txt").write_text(REQUIREMENTS, encoding="utf-8")
    (out / "README.md").write_text(FRONT_MATTER.format(gradio=gradio_version), encoding="utf-8")
    shutil.copy2(ROOT / "LICENSE", out / "LICENSE")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("out", type=Path)
    ap.add_argument("--gradio-version", default="6.31.0")
    args = ap.parse_args(argv)
    build(args.out, args.gradio_version)
    print(f"Space folder ready: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
