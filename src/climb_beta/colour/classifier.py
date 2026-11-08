"""Small learned hold-colour classifier on masked crops (timm; needs the `ml` extra).

The class list is `configs/colours.yaml`'s colour order, stored in the checkpoint.
Training must not use hue/saturation augmentation, because colour is the label.
Preprocessing is plain numpy so it is identical in training, inference and tests.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt

from climb_beta.types import ImageBGR

ARCHS = ("mobilenetv3_large_100", "resnet18")
DEFAULT_ARCH = "mobilenetv3_large_100"
IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)


def preprocess(crops: Sequence[ImageBGR]) -> npt.NDArray[np.float32]:
    """BGR uint8 HxWx3 crops -> float32 NCHW, RGB, ImageNet-normalised."""
    arr = np.stack([c[..., ::-1] for c in crops]).astype(np.float32) / 255.0
    arr = (arr - IMAGENET_MEAN) / IMAGENET_STD
    return np.ascontiguousarray(arr.transpose(0, 3, 1, 2))


@dataclass(frozen=True)
class CheckpointMeta:
    arch: str
    classes: tuple[str, ...]
    size: int

    def to_dict(self) -> dict[str, Any]:
        return {"arch": self.arch, "classes": list(self.classes), "size": self.size}

    @staticmethod
    def from_dict(d: dict[str, Any]) -> CheckpointMeta:
        arch, classes, size = d.get("arch"), d.get("classes"), d.get("size")
        if arch not in ARCHS:
            raise ValueError(f"checkpoint arch {arch!r} not in {ARCHS}")
        if not classes or len(set(classes)) != len(classes):
            raise ValueError("checkpoint classes missing or duplicated")
        if not isinstance(size, int) or size < 16:
            raise ValueError(f"bad crop size {size!r}")
        return CheckpointMeta(str(arch), tuple(str(c) for c in classes), size)


def build_model(arch: str, num_classes: int, pretrained: bool = True) -> Any:
    import timm  # lazy

    if arch not in ARCHS:
        raise ValueError(f"arch must be one of {ARCHS}")
    return timm.create_model(arch, pretrained=pretrained, num_classes=num_classes)


class CropClassifier:
    """Load a checkpoint written by colour/train_classifier.py and classify crops."""

    def __init__(self, weights: str | Path, device: str | None = None) -> None:
        import torch  # lazy

        ckpt = torch.load(str(weights), map_location="cpu", weights_only=False)
        self.meta = CheckpointMeta.from_dict(ckpt["meta"])
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = build_model(self.meta.arch, len(self.meta.classes), pretrained=False)
        self.model.load_state_dict(ckpt["state_dict"])
        self.model.eval().to(self.device)

    @property
    def classes(self) -> tuple[str, ...]:
        return self.meta.classes

    def predict_proba(self, crops: Sequence[ImageBGR]) -> npt.NDArray[np.float32]:
        import torch

        if not crops:
            return np.zeros((0, len(self.classes)), dtype=np.float32)
        x = torch.from_numpy(preprocess(crops)).to(self.device)
        with torch.no_grad():
            p = torch.softmax(self.model(x), dim=1)
        return np.asarray(p.cpu().numpy(), dtype=np.float32)

    def predict(self, crops: Sequence[ImageBGR]) -> list[tuple[str, float]]:
        p = self.predict_proba(crops)
        idx = p.argmax(axis=1) if len(p) else np.zeros(0, dtype=int)
        return [(self.classes[int(i)], float(p[k, i])) for k, i in enumerate(idx)]
