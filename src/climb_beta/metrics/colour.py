"""Colour accuracy: overall, per colour, and the two subsets the exit criteria name.

Exit criteria: overall >= 95%; >= 90% on holds whose ground truth is pink or red; >= 90%
on chalked holds. A prediction of "unknown" counts as wrong.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

import numpy as np
import numpy.typing as npt

UNKNOWN = "unknown"
PINK_RED = ("pink", "red")


@dataclass
class ColourReport:
    labels: tuple[str, ...]  # rows = truth, cols = predicted (labels + "unknown")
    matrix: npt.NDArray[np.int64]
    n: int
    overall: float
    pink_red: float | None
    pink_red_n: int
    chalked: float | None
    chalked_n: int
    per_colour: dict[str, float] = field(default_factory=dict)


def _acc(t: Sequence[str], p: Sequence[str], keep: Sequence[bool]) -> tuple[float | None, int]:
    idx = [i for i, k in enumerate(keep) if k]
    if not idx:
        return None, 0
    return sum(t[i] == p[i] for i in idx) / len(idx), len(idx)


def colour_report(
    truth: Sequence[str],
    pred: Sequence[str],
    chalked: Sequence[bool],
    labels: Sequence[str],
) -> ColourReport:
    if not (len(truth) == len(pred) == len(chalked)):
        raise ValueError("truth, pred and chalked must have the same length")
    cols = (*labels, UNKNOWN)
    col_idx = {c: i for i, c in enumerate(cols)}
    m = np.zeros((len(labels), len(cols)), dtype=np.int64)
    for t, p in zip(truth, pred, strict=True):
        if t not in col_idx or t == UNKNOWN:
            raise ValueError(f"ground-truth colour {t!r} not in {list(labels)}")
        m[col_idx[t], col_idx.get(p, col_idx[UNKNOWN])] += 1
    n = len(truth)
    overall = float(np.trace(m[:, : len(labels)]) / n) if n else 0.0
    pr, pr_n = _acc(truth, pred, [t in PINK_RED for t in truth])
    ch, ch_n = _acc(truth, pred, list(chalked))
    per = {c: float(m[i, i] / m[i].sum()) for i, c in enumerate(labels) if m[i].sum() > 0}
    return ColourReport(tuple(labels), m, n, overall, pr, pr_n, ch, ch_n, per)


def format_report(r: ColourReport, title: str = "") -> str:
    cols = (*r.labels, UNKNOWN)
    w = max(7, *(len(c) for c in cols)) + 1
    lines = [title] if title else []
    lines.append("truth \\ pred".ljust(w) + "".join(c[: w - 1].rjust(w) for c in cols) + "   acc")
    for i, t in enumerate(r.labels):
        if r.matrix[i].sum() == 0:
            continue
        row = "".join(str(int(v)).rjust(w) for v in r.matrix[i])
        lines.append(t.ljust(w) + row + f"  {r.per_colour[t]:.1%}")

    def pct(v: float | None) -> str:
        return "n/a" if v is None else f"{v:.1%}"

    lines.append("")
    lines.append(f"overall      {pct(r.overall)}  (n={r.n})")
    lines.append(f"pink vs red  {pct(r.pink_red)}  (n={r.pink_red_n})")
    lines.append(f"chalked      {pct(r.chalked)}  (n={r.chalked_n})")
    return "\n".join(lines)
