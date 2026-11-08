"""Fine-tune the colour-blind YOLO11-seg detector (hold / volume / tape) and log mAP.

Usage:
    uv sync --extra ml
    python train/train_detector.py --config train/configs/yolo11n-seg.yaml
    python train/train_detector.py --config train/configs/yolo11s-seg.yaml --epochs 50

Writes runs/detector/<name>/ (Ultralytics run), weights/detector-<name>.pt (best),
and weights/detector-<name>.metrics.json (box/mask mAP50 and mAP50-95 on the val split,
plus test if present).
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

from climb_beta.config import load_classes
from climb_beta.train_config import (
    TrainConfigError,
    load_train_config,
    merge_datasets,
    summarise_metrics,
)

ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--config", type=Path, required=True)
    ap.add_argument("--epochs", type=int, help="override config epochs")
    ap.add_argument("--device", help="override device (e.g. 0, cpu)")
    ap.add_argument("--project", type=Path, default=ROOT / "runs" / "detector")
    ap.add_argument("--weights-dir", type=Path, default=ROOT / "weights")
    args = ap.parse_args(argv)

    try:
        cfg = load_train_config(args.config)
        datasets = [ROOT / d if not Path(d).is_absolute() else Path(d) for d in cfg.datasets]
        missing = [str(d) for d in datasets if not (d / "dataset.yaml").exists()]
        if missing:
            raise TrainConfigError(f"datasets not built yet: {missing}")
        val = None if cfg.val_dataset is None else ROOT / cfg.val_dataset
        data_yaml = merge_datasets(
            datasets, val, load_classes(), args.project / f"{cfg.name}.data.yaml"
        )
    except TrainConfigError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    from ultralytics import YOLO  # lazy: ml extra

    kw: dict[str, Any] = cfg.train_kwargs()
    if args.epochs:
        kw["epochs"] = args.epochs
    if args.device is not None:
        kw["device"] = args.device
    model = YOLO(cfg.model)
    model.train(data=str(data_yaml), project=str(args.project), exist_ok=True, **kw)

    best = Path(model.trainer.best)
    args.weights_dir.mkdir(parents=True, exist_ok=True)
    out_w = args.weights_dir / f"detector-{cfg.name}.pt"
    shutil.copy2(best, out_w)

    trained = YOLO(str(out_w))
    report: dict[str, Any] = {"config": str(args.config), "weights": out_w.name}
    for split in ("val", "test"):
        try:
            m = trained.val(data=str(data_yaml), split=split, imgsz=cfg.imgsz, verbose=False)
        except Exception as e:  # no such split
            report[split] = {"error": str(e)[:200]}
            continue
        report[split] = summarise_metrics(m.results_dict)
    metrics_path = args.weights_dir / f"detector-{cfg.name}.metrics.json"
    metrics_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
