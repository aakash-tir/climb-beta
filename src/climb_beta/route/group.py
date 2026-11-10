"""Group same-colour holds into routes; tape diamonds mark the start and the finish.

Holds of the chosen colour are linked when the gap between their masks is at most
`link_factor` x the median hold size. Connected components are routes. Distances
scale with the photo's own hold size, so resolution and shooting distance don't matter.
Same-colour clusters smaller than `min_route_holds` are reported as strays (often a
mis-coloured hold) rather than routes.

Basecamp marks a route with small tape diamonds: two at the bottom by the start
hold(s), one at the top by the finish hold. A hold "has" a diamond when its mask, grown
by `tape_reach_factor` x hold size, touches the tape. Within a route the highest taped
hold is the finish when it has exactly one diamond and sits in the top
`finish_top_frac` of the route's height; every other taped hold is a start. A route is
`complete` only when it has both a start and a finish.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import yaml

from climb_beta.config import CONFIG_DIR
from climb_beta.masks import dilate, min_gap
from climb_beta.types import Detection, Mask

HOLD, TAPE = "hold", "tape"


@dataclass(frozen=True)
class RouteConfig:
    link_factor: float = 6.0
    tape_reach_factor: float = 0.6
    min_route_holds: int = 3
    finish_top_frac: float = 0.5


def load_route_config(path: Path | None = None) -> RouteConfig:
    raw = yaml.safe_load((path or CONFIG_DIR / "route.yaml").read_text(encoding="utf-8")) or {}
    cfg = RouteConfig(
        link_factor=float(raw.get("link_factor", 6.0)),
        tape_reach_factor=float(raw.get("tape_reach_factor", 0.6)),
        min_route_holds=int(raw.get("min_route_holds", 3)),
        finish_top_frac=float(raw.get("finish_top_frac", 0.5)),
    )
    if (
        cfg.link_factor <= 0
        or cfg.tape_reach_factor < 0
        or cfg.min_route_holds < 1
        or not 0 < cfg.finish_top_frac <= 1
    ):
        raise ValueError(f"bad route config: {cfg}")
    return cfg


@dataclass
class Route:
    colour: str
    holds: list[int]  # indices into the detection list
    starts: list[int] = field(default_factory=list)  # holds by the start diamonds
    finish: int | None = None  # the hold by the single finish diamond

    @property
    def complete(self) -> bool:
        """A route counts only when both its start and its finish are visible."""
        return bool(self.starts) and self.finish is not None

    @property
    def size(self) -> int:
        return len(self.holds)


@dataclass
class RouteResult:
    colour: str
    routes: list[Route]  # largest first
    strays: list[int]  # same-colour holds not in any route
    hold_size_px: float

    def named_route(self) -> Route | None:
        """The route the user means by a colour: the largest complete route, else the
        largest with any diamond tape, else the largest."""
        for pool in (
            [r for r in self.routes if r.complete],
            [r for r in self.routes if r.starts or r.finish is not None],
            self.routes,
        ):
            if pool:
                return max(pool, key=lambda r: r.size)
        return None


def _bbox(m: Mask) -> tuple[int, int, int, int]:
    ys, xs = np.nonzero(m)
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def _box_gap(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> float:
    dx = max(a[0] - b[2], b[0] - a[2], 0)
    dy = max(a[1] - b[3], b[1] - a[3], 0)
    return float(np.hypot(dx, dy))


def _gap(a: Mask, b: Mask, ba: tuple[int, int, int, int], bb: tuple[int, int, int, int]) -> float:
    """Mask gap, computed on the union bbox crop (fast on 12 MP photos)."""
    x0, y0 = min(ba[0], bb[0]), min(ba[1], bb[1])
    x1, y1 = max(ba[2], bb[2]), max(ba[3], bb[3])
    return min_gap(a[y0:y1, x0:x1], b[y0:y1, x0:x1])


def _start_and_finish(
    members: list[int],
    diamonds: dict[int, int],
    boxes: dict[int, tuple[int, int, int, int]],
    finish_top_frac: float,
) -> tuple[list[int], int | None]:
    """Split a route's taped holds into start holds and the finish hold."""
    taped = [i for i in members if diamonds.get(i, 0)]
    if not taped:
        return [], None
    top = min(boxes[i][1] for i in members)
    bottom = max(boxes[i][3] for i in members)
    cut = top + finish_top_frac * (bottom - top)

    def centre_y(i: int) -> float:
        return (boxes[i][1] + boxes[i][3]) / 2

    highest = min(taped, key=centre_y)
    finish = highest if diamonds[highest] == 1 and centre_y(highest) <= cut else None
    return [i for i in taped if i != finish], finish


class _UnionFind:
    def __init__(self, n: int) -> None:
        self.p = list(range(n))

    def find(self, i: int) -> int:
        while self.p[i] != i:
            self.p[i] = self.p[self.p[i]]
            i = self.p[i]
        return i

    def union(self, i: int, j: int) -> None:
        self.p[self.find(i)] = self.find(j)


def group_routes(
    detections: Sequence[Detection], colour: str, cfg: RouteConfig | None = None
) -> RouteResult:
    cfg = cfg or RouteConfig()
    cand = [i for i, d in enumerate(detections) if d.cls == HOLD and d.colour == colour and d.area]
    tapes = [i for i, d in enumerate(detections) if d.cls == TAPE and d.area]
    holds_all = [d.area for d in detections if d.cls == HOLD and d.area]
    size = float(np.sqrt(np.median(holds_all))) if holds_all else 1.0
    if not cand:
        return RouteResult(colour, [], [], size)

    link = cfg.link_factor * size
    boxes = {i: _bbox(detections[i].mask) for i in cand + tapes}
    uf = _UnionFind(len(cand))
    for a in range(len(cand)):
        for b in range(a + 1, len(cand)):
            i, j = cand[a], cand[b]
            if _box_gap(boxes[i], boxes[j]) > link:
                continue
            if _gap(detections[i].mask, detections[j].mask, boxes[i], boxes[j]) <= link:
                uf.union(a, b)

    clusters: dict[int, list[int]] = {}
    for a, i in enumerate(cand):
        clusters.setdefault(uf.find(a), []).append(i)

    reach = max(1, int(round(cfg.tape_reach_factor * size)))
    diamonds: dict[int, int] = {}  # hold -> number of tape pieces it touches
    for i in cand:
        grown_box = (
            boxes[i][0] - reach,
            boxes[i][1] - reach,
            boxes[i][2] + reach,
            boxes[i][3] + reach,
        )
        grown = None
        for t in tapes:
            if _box_gap(grown_box, boxes[t]) > 0:
                continue
            if grown is None:
                grown = dilate(detections[i].mask, reach)
            if (grown & detections[t].mask).any():
                diamonds[i] = diamonds.get(i, 0) + 1

    routes, strays = [], []
    for members in clusters.values():
        members = sorted(members)
        if len(members) >= cfg.min_route_holds:
            starts, finish = _start_and_finish(members, diamonds, boxes, cfg.finish_top_frac)
            routes.append(Route(colour, members, starts, finish))
        else:
            strays.extend(members)
    routes.sort(key=lambda r: (-r.size, r.holds[0]))
    return RouteResult(colour, routes, sorted(strays), size)
