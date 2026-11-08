"""Train the hold-colour crop classifier (timm MobileNetV3-Large or ResNet18).

Usage:
    uv sync --extra ml
    python colour/make_crops.py data/yolo/basecamp data/crops/basecamp
    python colour/train_classifier.py data/crops/basecamp [--arch resnet18] [--epochs 30]

Classes are the colours in configs/colours.yaml (in that order); crop folders for
colours not in the config are an error. Augmentation is geometric + mild brightness
only: never hue or saturation, because colour is the label. Saves the best val-accuracy
checkpoint to weights/colour-<arch>.pt.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

from climb_beta.colour.classifier import (
    ARCHS,
    DEFAULT_ARCH,
    CheckpointMeta,
    build_model,
    preprocess,
)
from climb_beta.config import load_colour_config
from climb_beta.imageio import read_bgr

ROOT = Path(__file__).resolve().parents[1]


def load_split(crops: Path, split: str, classes: tuple[str, ...]) -> tuple[list[Any], list[int]]:
    xs, ys = [], []
    d = crops / split
    if not d.is_dir():
        return xs, ys
    for cdir in sorted(p for p in d.iterdir() if p.is_dir()):
        if cdir.name not in classes:
            raise ValueError(f"crop folder '{cdir.name}' is not a colour in configs/colours.yaml")
        for p in sorted(cdir.glob("*.png")):
            img = read_bgr(p)
            if img is not None:
                xs.append(img)
                ys.append(classes.index(cdir.name))
    return xs, ys


def augment(img: Any, rng: np.random.Generator) -> Any:
    """Flips, 90-degree rotations and mild brightness. No hue/saturation changes."""
    if rng.random() < 0.5:
        img = img[:, ::-1]
    img = np.rot90(img, int(rng.integers(0, 4)))
    gain = float(rng.uniform(0.85, 1.15))  # same gain on all channels: hue unchanged
    return np.clip(img.astype(np.float32) * gain, 0, 255).astype(np.uint8)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("crops", type=Path)
    ap.add_argument("--arch", choices=ARCHS, default=DEFAULT_ARCH)
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--no-pretrained", action="store_true")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args(argv)

    classes = load_colour_config().names
    try:
        xtr, ytr = load_split(args.crops, "train", classes)
        xva, yva = load_split(args.crops, "val", classes)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if not xtr or not xva:
        print("need crops in both train/ and val/", file=sys.stderr)
        return 2
    size = int(xtr[0].shape[0])

    import torch  # lazy

    torch.manual_seed(args.seed)
    rng = np.random.default_rng(args.seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = build_model(args.arch, len(classes), pretrained=not args.no_pretrained).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=args.epochs)
    # class-balanced loss: rare colours count as much as common ones
    counts = np.bincount(ytr, minlength=len(classes)).astype(np.float32)
    weights = np.where(counts > 0, counts.sum() / np.maximum(counts, 1) / len(classes), 0.0)
    loss_fn = torch.nn.CrossEntropyLoss(
        weight=torch.tensor(weights, dtype=torch.float32).to(device)
    )
    xva_t = torch.from_numpy(preprocess(xva)).to(device)
    yva_t = torch.tensor(yva).to(device)

    meta = CheckpointMeta(args.arch, classes, size)
    out = args.out or ROOT / "weights" / f"colour-{args.arch}.pt"
    out.parent.mkdir(parents=True, exist_ok=True)
    best, history = -1.0, []
    for epoch in range(args.epochs):
        model.train()
        order = rng.permutation(len(xtr))
        for i in range(0, len(order), args.batch):
            idx = order[i : i + args.batch]
            xb = torch.from_numpy(preprocess([augment(xtr[j], rng) for j in idx])).to(device)
            yb = torch.tensor([ytr[j] for j in idx]).to(device)
            opt.zero_grad()
            loss = loss_fn(model(xb), yb)
            loss.backward()
            opt.step()
        sched.step()
        model.eval()
        with torch.no_grad():
            acc = float((model(xva_t).argmax(1) == yva_t).float().mean())
        history.append({"epoch": epoch + 1, "loss": float(loss), "val_acc": acc})
        print(f"epoch {epoch + 1:3d}  loss {float(loss):.4f}  val_acc {acc:.4f}")
        if acc > best:
            best = acc
            torch.save({"meta": meta.to_dict(), "state_dict": model.state_dict()}, out)
    out.with_suffix(".history.json").write_text(json.dumps(history, indent=1), encoding="utf-8")
    print(f"best val_acc {best:.4f} -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
