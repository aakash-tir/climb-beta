"""Image read/write with the package's types (BGR uint8)."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from climb_beta.types import ImageBGR


def read_bgr(path: Path | str) -> ImageBGR | None:
    """Read an image as BGR uint8, or None if it can't be read. Handles non-ASCII paths."""
    try:
        buf = np.fromfile(str(path), dtype=np.uint8)
    except OSError:
        return None
    img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
    return None if img is None else np.asarray(img, dtype=np.uint8)


def write_bgr(path: Path | str, img: ImageBGR) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    ok, buf = cv2.imencode(p.suffix or ".png", img)
    if not ok:
        raise OSError(f"cannot encode image for {p}")
    buf.tofile(str(p))
