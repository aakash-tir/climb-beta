"""Grey-world white balance.

The grey-world assumption says the average of a scene is neutral grey. A climbing
wall is close to neutral, but the holds on it are deliberately saturated. So when a
reference mask (the wall: everything outside the detector's masks) is given, the
channel gains come from those pixels only.
"""

from __future__ import annotations

import numpy as np

from climb_beta.types import ImageBGR, Mask

MIN_REF_PIXELS = 64


def grey_world_gains(
    img: ImageBGR,
    ref_mask: Mask | None = None,
    clip: tuple[float, float] = (0.5, 2.0),
    ignore_saturated: int = 250,
) -> tuple[float, float, float]:
    """Per-channel (B, G, R) gains that make the reference pixels' mean neutral.

    Pixels with any channel >= `ignore_saturated` are excluded (clipped highlights
    carry no colour information). Falls back to the whole image when the reference
    has fewer than MIN_REF_PIXELS usable pixels. Gains are clipped to `clip`.
    """
    px = img.reshape(-1, 3).astype(np.float64)
    usable = px.max(axis=1) < ignore_saturated
    if ref_mask is not None:
        ref = ref_mask.reshape(-1) & usable
        if ref.sum() < MIN_REF_PIXELS:
            ref = usable
    else:
        ref = usable
    if ref.sum() < MIN_REF_PIXELS:
        return (1.0, 1.0, 1.0)
    means = px[ref].mean(axis=0)
    if np.any(means <= 1e-6):
        return (1.0, 1.0, 1.0)
    grey = means.mean()
    gains = np.clip(grey / means, clip[0], clip[1])
    return (float(gains[0]), float(gains[1]), float(gains[2]))


def apply_gains(img: ImageBGR, gains: tuple[float, float, float]) -> ImageBGR:
    out = img.astype(np.float32) * np.asarray(gains, dtype=np.float32)[None, None, :]
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def grey_world(
    img: ImageBGR,
    ref_mask: Mask | None = None,
    clip: tuple[float, float] = (0.5, 2.0),
) -> ImageBGR:
    """White-balance `img` so the reference (default: whole image) averages to grey."""
    return apply_gains(img, grey_world_gains(img, ref_mask, clip))
