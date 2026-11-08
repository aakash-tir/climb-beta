"""Turn box-only annotations into masks by prompting SAM with each box.

Masks made this way are *pseudo-masks*: good enough to train on, never good enough
to test on. Every image that gets one is listed in `pseudo_masks.txt` at the dataset
root (one `split/file_name` per line), and pseudo-masked images are never written to
a test split.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt

from climb_beta.types import ImageBGR, Mask

PSEUDO_MASKS_FILE = "pseudo_masks.txt"
DEFAULT_SAM_WEIGHTS = "sam2.1_b.pt"

BoxesXYXY = npt.NDArray[np.float64]
BoxSegmenter = Callable[[ImageBGR, BoxesXYXY], list[Mask]]
"""(image, (K, 4) xyxy pixel boxes) -> K bool masks, same order."""


def xywh_to_xyxy(b: list[float]) -> list[float]:
    x, y, w, h = b
    return [x, y, x + w, y + h]


def box_fill_segmenter(img: ImageBGR, boxes: BoxesXYXY) -> list[Mask]:
    """Fallback 'segmenter' that fills each box. Only for tests and dry runs."""
    h, w = img.shape[:2]
    out = []
    for x0, y0, x1, y1 in boxes:
        m = np.zeros((h, w), dtype=bool)
        m[int(max(y0, 0)) : int(min(y1, h)), int(max(x0, 0)) : int(min(x1, w))] = True
        out.append(m)
    return out


def sam_segmenter(weights: str = DEFAULT_SAM_WEIGHTS, device: str | None = None) -> BoxSegmenter:
    """Ultralytics SAM (needs the `ml` extra). Weights download on first use."""
    from ultralytics import SAM  # lazy: heavy

    model: Any = SAM(weights)

    def segment(img: ImageBGR, boxes: BoxesXYXY) -> list[Mask]:
        if len(boxes) == 0:
            return []
        res = model(img, bboxes=boxes.tolist(), device=device, verbose=False)[0]
        if res.masks is None:
            return [np.zeros(img.shape[:2], dtype=bool) for _ in boxes]
        data = res.masks.data.cpu().numpy() > 0.5
        return [np.asarray(m, dtype=bool) for m in data]

    return segment


def write_pseudo_masks(dataset_dir: Path, entries: list[str]) -> None:
    p = dataset_dir / PSEUDO_MASKS_FILE
    p.write_text("".join(f"{e}\n" for e in sorted(set(entries))), encoding="utf-8")


def load_pseudo_masks(dataset_dir: Path) -> set[str]:
    """`split/file_name` entries of pseudo-masked images (empty if none)."""
    p = dataset_dir / PSEUDO_MASKS_FILE
    if not p.exists():
        return set()
    return {ln.strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()}
