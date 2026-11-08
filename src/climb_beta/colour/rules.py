"""Rule-based hold colour from the pixels inside a mask.

Pipeline for one hold (all thresholds from `configs/colours.yaml`):
1. drop chalk pixels: HSV S < chalk_s_max and V > chalk_v_min;
2. give each remaining pixel one label: black (V < black_v_max), white/grey (S below
   achromatic_s_max, split by V), or a chromatic family by hue range;
3. take the majority label; resolve its family to a named colour.

OpenCV HSV: H in 0..179, S and V in 0..255. Lab: L* scaled to 0..255.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

import cv2
import numpy as np
import numpy.typing as npt

from climb_beta.config import ACHROMATIC, ColourConfig
from climb_beta.types import ImageBGR, Mask

UNKNOWN = "unknown"
U8 = npt.NDArray[np.uint8]


@dataclass
class ColourResult:
    name: str
    confidence: float
    family: str
    votes: dict[str, int] = field(default_factory=dict)
    chalk_frac: float = 0.0
    n_pixels: int = 0
    reason: str = ""


@dataclass
class HoldPixels:
    """HSV and Lab values of the pixels inside one mask, plus the chalk flag."""

    hsv: U8  # (N, 3)
    lab: U8  # (N, 3)
    chalk: npt.NDArray[np.bool_]  # (N,)

    @property
    def n(self) -> int:
        return int(self.hsv.shape[0])


def hold_pixels(img: ImageBGR, mask: Mask, cfg: ColourConfig) -> HoldPixels:
    t = cfg.thresholds
    hsv = np.asarray(cv2.cvtColor(img, cv2.COLOR_BGR2HSV), dtype=np.uint8)[mask]
    lab = np.asarray(cv2.cvtColor(img, cv2.COLOR_BGR2LAB), dtype=np.uint8)[mask]
    s, v = hsv[:, 1], hsv[:, 2]
    chalk = (s < t["chalk_s_max"]) & (v > t["chalk_v_min"])
    return HoldPixels(hsv=hsv, lab=lab, chalk=chalk)


def pixel_labels(hsv: U8, cfg: ColourConfig) -> npt.NDArray[np.str_]:
    """One label per pixel: a chromatic family name, or black / grey / white."""
    t = cfg.thresholds
    ach = t["achromatic"]
    h = hsv[:, 0].astype(np.int32)
    s = hsv[:, 1].astype(np.int32)
    v = hsv[:, 2].astype(np.int32)
    labels = np.full(h.shape, UNKNOWN, dtype="<U16")
    for fam, ranges in cfg.family_hues.items():
        in_fam = np.zeros(h.shape, dtype=bool)
        for lo, hi in ranges:
            in_fam |= (h >= lo) & (h < hi)
        labels[in_fam] = fam
    achromatic = s < t["achromatic_s_max"]
    labels[achromatic & (v >= ach["white_v_min"])] = "white"
    labels[achromatic & (v < ach["white_v_min"])] = "grey"
    labels[v < ach["black_v_max"]] = "black"
    return labels


def _first_in_family(
    fam: str, px: HoldPixels, keep: npt.NDArray[np.bool_], cfg: ColourConfig
) -> str:
    colours = cfg.by_family(fam)
    return colours[0].name if colours else UNKNOWN


# family -> resolver(family, pixels, voting-pixel mask, cfg) -> colour name.
# Families with one colour use the default; redpink gets its own resolver.
FAMILY_RESOLVERS: dict[
    str, Callable[[str, HoldPixels, npt.NDArray[np.bool_], ColourConfig], str]
] = {}


def split_pink_red(
    fam: str, px: HoldPixels, fam_keep: npt.NDArray[np.bool_], cfg: ColourConfig
) -> str:
    """Red vs pink from pigment saturation and lightness, not hue.

    Chalk and glare only ever lower a pixel's saturation and raise its lightness, so
    the most saturated `quantile` of the hold's red-pink pixels shows the pigment.
    Red: those pixels' median S >= red_s_min and median Lab L* <= red_l_max.
    Pink otherwise: a red tint is less saturated and lighter.
    """
    pr = cfg.thresholds["pink_red"]
    s = px.hsv[fam_keep, 1].astype(np.float64)
    lightness = px.lab[fam_keep, 0].astype(np.float64)
    if s.size == 0:
        return "red"
    top = s >= np.quantile(s, pr["quantile"])
    s_top = float(np.median(s[top]))
    l_top = float(np.median(lightness[top]))
    return "red" if s_top >= pr["red_s_min"] and l_top <= pr["red_l_max"] else "pink"


FAMILY_RESOLVERS["redpink"] = split_pink_red


def _vote(
    px: HoldPixels, keep: npt.NDArray[np.bool_], cfg: ColourConfig
) -> tuple[str, int, dict[str, int]]:
    labels = pixel_labels(px.hsv[keep], cfg)
    names, counts = np.unique(labels, return_counts=True)
    votes = {str(k): int(c) for k, c in zip(names, counts, strict=True) if k != UNKNOWN}
    if not votes:
        return UNKNOWN, 0, votes
    winner = max(votes, key=lambda k: votes[k])
    return winner, votes[winner], votes


def classify_pixels(px: HoldPixels, cfg: ColourConfig) -> ColourResult:
    """Colour of one hold from its pixels."""
    t = cfg.thresholds
    chalk_frac = float(px.chalk.mean()) if px.n else 0.0
    keep = ~px.chalk
    n_keep = int(keep.sum())
    if n_keep < t["min_pixels"]:
        return ColourResult(
            UNKNOWN, 0.0, UNKNOWN, {}, chalk_frac, n_keep, "too few non-chalk pixels"
        )

    label, n_win, votes = _vote(px, keep, cfg)
    if label == UNKNOWN:
        return ColourResult(UNKNOWN, 0.0, UNKNOWN, votes, chalk_frac, n_keep, "no votes")
    total = sum(votes.values())
    conf = n_win / total if total else 0.0

    if label in ("black", "grey", "white"):
        name = label if cfg.has(label) else UNKNOWN
        return ColourResult(
            name, conf, ACHROMATIC, votes, chalk_frac, n_keep, "achromatic majority"
        )

    # restrict the family resolver to this family's pixels
    fam_keep = keep.copy()
    fam_keep[keep] = pixel_labels(px.hsv[keep], cfg) == label
    resolver = FAMILY_RESOLVERS.get(label, _first_in_family)
    name = resolver(label, px, fam_keep, cfg)
    return ColourResult(name, conf, label, votes, chalk_frac, n_keep, f"{label} majority")


def classify_hold(img: ImageBGR, mask: Mask, cfg: ColourConfig) -> ColourResult:
    """Colour of the hold under `mask` in a (white-balanced) BGR image."""
    if not mask.any():
        return ColourResult(UNKNOWN, 0.0, UNKNOWN, reason="empty mask")
    return classify_pixels(hold_pixels(img, mask, cfg), cfg)
