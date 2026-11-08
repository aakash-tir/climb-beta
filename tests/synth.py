"""Synthetic wall photos for tests: grey wall, coloured holds, chalk, tinted light.

Everything is BGR uint8 (OpenCV order) and deterministic for a given seed.
"""

from __future__ import annotations

import cv2
import numpy as np
import numpy.typing as npt

Image = npt.NDArray[np.uint8]
Mask = npt.NDArray[np.bool_]

# Reference colours (BGR) roughly matching real hold plastic.
RED = (40, 30, 200)
HOT_PINK = (180, 105, 255)
LIGHT_PINK = (203, 182, 255)
ORANGE = (0, 128, 247)
YELLOW = (30, 215, 245)
GREEN = (60, 160, 40)
BLUE = (200, 110, 30)
PURPLE = (160, 40, 120)
BLACK = (25, 25, 25)
WHITE = (238, 238, 238)
GREY = (130, 130, 130)
CHALK = (236, 238, 240)


def wall(
    h: int = 240,
    w: int = 320,
    bgr: tuple[int, int, int] = (190, 192, 195),
    noise: float = 3.0,
    seed: int = 0,
) -> Image:
    """A near-neutral textured wall."""
    rng = np.random.default_rng(seed)
    base = np.empty((h, w, 3), dtype=np.float32)
    base[:] = bgr
    base += rng.normal(0.0, noise, size=base.shape)
    return np.clip(base, 0, 255).astype(np.uint8)


def draw_hold(
    img: Image,
    centre: tuple[int, int],
    radius: int | tuple[int, int],
    bgr: tuple[int, int, int],
    shade: float = 0.15,
    seed: int = 0,
) -> Mask:
    """Draw an elliptical hold in place and return its mask.

    `shade` darkens towards the edge (brightness only, hue unchanged), like a
    rounded hold lit from the front.
    """
    h, w = img.shape[:2]
    rx, ry = (radius, radius) if isinstance(radius, int) else radius
    mask_u8 = np.zeros((h, w), dtype=np.uint8)
    cv2.ellipse(mask_u8, centre, (rx, ry), 0, 0, 360, 255, thickness=-1)
    mask = mask_u8 > 0
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt(((xx - centre[0]) / max(rx, 1)) ** 2 + ((yy - centre[1]) / max(ry, 1)) ** 2)
    factor = 1.0 - shade * np.clip(r, 0, 1) ** 2
    rng = np.random.default_rng(seed)
    colour = np.asarray(bgr, dtype=np.float32)[None, :] * factor[mask][:, None]
    colour += rng.normal(0.0, 2.0, size=colour.shape)
    img[mask] = np.clip(colour, 0, 255).astype(np.uint8)
    return mask


def chalk(img: Image, mask: Mask, frac: float, region: str = "centre", seed: int = 0) -> Mask:
    """Cover `frac` of the mask with chalk, in place. Returns the chalked-pixel mask.

    region="centre" chalks the pixels nearest the mask centroid first (hands grip the
    top/centre, edges keep their colour). region="random" scatters chalk.
    """
    rng = np.random.default_rng(seed)
    ys, xs = np.nonzero(mask)
    n = int(round(frac * xs.size))
    if n == 0:
        return np.zeros_like(mask)
    if region == "centre":
        d = (xs - xs.mean()) ** 2 + (ys - ys.mean()) ** 2
        idx = np.argsort(d, kind="stable")[:n]
    elif region == "random":
        idx = rng.choice(xs.size, size=n, replace=False)
    else:
        raise ValueError(f"unknown region {region!r}")
    chalked = np.zeros_like(mask)
    chalked[ys[idx], xs[idx]] = True
    noise = rng.normal(0.0, 4.0, size=(n, 3))
    img[chalked] = np.clip(np.asarray(CHALK, dtype=np.float32) + noise, 0, 255).astype(np.uint8)
    return chalked


def tint(img: Image, gains: tuple[float, float, float]) -> Image:
    """Return a copy lit by a coloured light: per-channel (B, G, R) gains."""
    out = img.astype(np.float32) * np.asarray(gains, dtype=np.float32)[None, None, :]
    return np.clip(out, 0, 255).astype(np.uint8)
