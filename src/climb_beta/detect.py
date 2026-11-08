"""Run the YOLO11-seg detector and return full-resolution `Detection` masks.

Ultralytics' `masks.data` is at the (letterboxed) inference size. Its `masks.xy`
polygons are already in original-image pixels, so masks are rasterised from those.
That keeps `results_to_detections` a pure function, testable without ultralytics.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any, Protocol

import numpy as np
import numpy.typing as npt

from climb_beta.masks import polygon_to_mask
from climb_beta.types import Detection, ImageBGR

HF_PREFIX = "hf://"


class DetectorLike(Protocol):
    def predict(self, img: ImageBGR) -> list[Detection]: ...


def results_to_detections(
    polygons: Sequence[npt.ArrayLike],
    cls_ids: Sequence[int],
    scores: Sequence[float],
    names: Sequence[str] | dict[int, str],
    shape: tuple[int, int],
    min_area: int = 16,
) -> list[Detection]:
    """Build Detections from per-instance pixel polygons (original image coords)."""
    h, w = shape
    out = []
    for poly, c, s in zip(polygons, cls_ids, scores, strict=True):
        mask = polygon_to_mask(np.asarray(poly, dtype=np.float64), h, w)
        if mask.sum() < min_area:
            continue
        out.append(Detection(mask=mask, cls=str(names[int(c)]), score=float(s)))
    return out


def resolve_weights(spec: str) -> Path:
    """A local path, or `hf://<user>/<repo>/<file>` downloaded from the HF Hub."""
    if spec.startswith(HF_PREFIX):
        parts = spec[len(HF_PREFIX) :].split("/")
        if len(parts) < 3:
            raise ValueError(f"expected hf://<user>/<repo>/<file>, got {spec!r}")
        from huggingface_hub import hf_hub_download  # lazy

        return Path(hf_hub_download("/".join(parts[:2]), "/".join(parts[2:])))
    p = Path(spec)
    if not p.exists():
        raise FileNotFoundError(f"detector weights not found: {p}")
    return p


class Detector:
    """Ultralytics YOLO11-seg wrapper (needs the `ml` extra)."""

    def __init__(
        self,
        weights: str | Path,
        conf: float = 0.25,
        iou: float = 0.6,
        imgsz: int = 1024,
        device: str | None = None,
        max_det: int = 500,
    ) -> None:
        from ultralytics import YOLO  # lazy

        self.model: Any = YOLO(str(resolve_weights(str(weights))))
        self.conf, self.iou, self.imgsz, self.device, self.max_det = (
            conf,
            iou,
            imgsz,
            device,
            max_det,
        )

    @property
    def names(self) -> dict[int, str]:
        return dict(self.model.names)

    def predict(self, img: ImageBGR) -> list[Detection]:
        res = self.model.predict(
            img,
            conf=self.conf,
            iou=self.iou,
            imgsz=self.imgsz,
            device=self.device,
            max_det=self.max_det,
            verbose=False,
        )[0]
        if res.masks is None or res.boxes is None or len(res.boxes) == 0:
            return []
        return results_to_detections(
            list(res.masks.xy),
            res.boxes.cls.cpu().numpy().astype(int).tolist(),
            res.boxes.conf.cpu().numpy().tolist(),
            self.names,
            img.shape[:2],
        )
