"""Detector training config: load/validate, and merge several YOLO-seg datasets.

The detector must ignore colour, so hue/saturation augmentation is far stronger than
Ultralytics' defaults (hsv_h 0.015, hsv_s 0.7): with hsv_h=0.5 any hold can appear in
any hue during training, and the class signal has to come from shape and texture.
The loader refuses configs that weaken this.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

MIN_HSV_H = 0.3
MIN_HSV_S = 0.7
ALLOWED_MODELS = ("yolo11n-seg", "yolo11s-seg")


class TrainConfigError(ValueError):
    pass


@dataclass(frozen=True)
class TrainConfig:
    name: str
    model: str  # weights to start from: a hub name (yolo11n-seg.pt) or a path
    datasets: tuple[str, ...]  # YOLO-seg dataset dirs (each with dataset.yaml)
    val_dataset: str | None  # which dataset's val/test split to evaluate on
    epochs: int
    imgsz: int
    batch: int
    patience: int = 30
    device: str | None = None
    seed: int = 0
    augment: dict[str, float] = field(default_factory=dict)

    def train_kwargs(self) -> dict[str, Any]:
        kw: dict[str, Any] = {
            "epochs": self.epochs,
            "imgsz": self.imgsz,
            "batch": self.batch,
            "patience": self.patience,
            "seed": self.seed,
            "name": self.name,
            **self.augment,
        }
        if self.device is not None:
            kw["device"] = self.device
        return kw


def parse_train_config(raw: Mapping[str, Any]) -> TrainConfig:
    try:
        model = str(raw["model"])
        datasets = tuple(str(d) for d in raw["datasets"])
    except KeyError as e:
        raise TrainConfigError(f"missing key {e}") from None
    if not datasets:
        raise TrainConfigError("datasets: at least one dataset dir is required")
    base = Path(model).stem
    if not Path(model).suffix == ".pt":
        raise TrainConfigError(f"model must be a .pt file or hub name, got {model!r}")
    if base not in ALLOWED_MODELS and not Path(model).parent.parts:
        raise TrainConfigError(f"hub model must be one of {ALLOWED_MODELS}, got {base!r}")
    aug = {str(k): float(v) for k, v in (raw.get("augment") or {}).items()}
    if aug.get("hsv_h", 0.0) < MIN_HSV_H or aug.get("hsv_s", 0.0) < MIN_HSV_S:
        raise TrainConfigError(
            f"augment.hsv_h >= {MIN_HSV_H} and augment.hsv_s >= {MIN_HSV_S} are required: "
            "the detector must not learn hold colour"
        )
    val = raw.get("val_dataset")
    if val is not None and str(val) not in datasets:
        raise TrainConfigError("val_dataset must be one of datasets")
    cfg = TrainConfig(
        name=str(raw.get("name", base)),
        model=model,
        datasets=datasets,
        val_dataset=None if val is None else str(val),
        epochs=int(raw.get("epochs", 100)),
        imgsz=int(raw.get("imgsz", 1024)),
        batch=int(raw.get("batch", 8)),
        patience=int(raw.get("patience", 30)),
        device=None if raw.get("device") is None else str(raw["device"]),
        seed=int(raw.get("seed", 0)),
        augment=aug,
    )
    if cfg.epochs < 1 or cfg.imgsz < 32 or cfg.batch < 1:
        raise TrainConfigError("epochs, imgsz and batch must be positive")
    return cfg


def load_train_config(path: Path) -> TrainConfig:
    return parse_train_config(yaml.safe_load(path.read_text(encoding="utf-8")) or {})


def merge_datasets(
    dataset_dirs: Sequence[Path], val_dataset: Path | None, classes: Sequence[str], out: Path
) -> Path:
    """Write one Ultralytics data yaml that trains on every dataset's train split.

    val/test come from `val_dataset` (default: the last dataset, i.e. our own photos),
    so model selection and test metrics are on Basecamp walls, not public data.
    Each dataset's class names must equal `classes`.
    """
    train_dirs: list[str] = []
    for d in dataset_dirs:
        y = yaml.safe_load((d / "dataset.yaml").read_text(encoding="utf-8"))
        names = y["names"]
        names = [names[k] for k in sorted(names)] if isinstance(names, dict) else list(names)
        if list(names) != list(classes):
            raise TrainConfigError(f"{d}: classes {names} != {list(classes)}")
        if "train" in y:
            train_dirs.append(str((d / y["train"]).resolve()))
    if not train_dirs:
        raise TrainConfigError("no dataset has a train split")
    vd = val_dataset or dataset_dirs[-1]
    vy = yaml.safe_load((vd / "dataset.yaml").read_text(encoding="utf-8"))
    data: dict[str, Any] = {
        "path": str(Path.cwd()),
        "train": train_dirs,
        "names": dict(enumerate(classes)),
    }
    for split in ("val", "test"):
        if split in vy:
            data[split] = str((vd / vy[split]).resolve())
    if "val" not in data:
        raise TrainConfigError(f"{vd}: no val split to select the model on")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return out


def summarise_metrics(results_dict: Mapping[str, float]) -> dict[str, float]:
    """Pick box/mask mAP from an Ultralytics `metrics.results_dict`."""
    keys = {
        "box_map50": "metrics/mAP50(B)",
        "box_map50_95": "metrics/mAP50-95(B)",
        "mask_map50": "metrics/mAP50(M)",
        "mask_map50_95": "metrics/mAP50-95(M)",
        "mask_precision": "metrics/precision(M)",
        "mask_recall": "metrics/recall(M)",
    }
    return {k: float(results_dict[v]) for k, v in keys.items() if v in results_dict}
