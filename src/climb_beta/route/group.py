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

A route's `grade` is the majority colour of its diamonds (the grade circuit). Two
routes can share a hold colour and differ only in grade, so a same-colour cluster whose
diamonds show two or more grades is split: each taped hold anchors its grade, and every
other hold joins the grade of the nearest anchor.

Grey and black holds (`shared_colours`) are shared: any route may use them, and a route
can be mostly, or only, shared holds plus its diamonds. Its one rule is a valid finish:
the single finish diamond sits by a hold of the route's own colour. So:

- a shared hold with diamonds joins a route as a start when that route has a finish
  above it and the diamond grades agree (the nearest such route wins);
- untaped shared holds near the line of the route (within `shared_link_factor` x hold
  size of the polyline through its holds, bottom to top) are listed in `Route.shared`:
  usable, not exclusive to the route, and not part of `holds`;
- a route smaller than `min_route_holds` is kept only when it is complete.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import yaml

from climb_beta.config import CONFIG_DIR
from climb_beta.masks import dilate, min_gap
from climb_beta.types import Detection, Mask

HOLD, TAPE = "hold", "tape"
UNKNOWN = "unknown"


@dataclass(frozen=True)
class RouteConfig:
    link_factor: float = 6.0
    tape_reach_factor: float = 0.6
    min_route_holds: int = 3
    finish_top_frac: float = 0.5
    shared_colours: tuple[str, ...] = ("grey", "black")
    shared_link_factor: float = 2.0


def load_route_config(path: Path | None = None) -> RouteConfig:
    raw = yaml.safe_load((path or CONFIG_DIR / "route.yaml").read_text(encoding="utf-8")) or {}
    cfg = RouteConfig(
        link_factor=float(raw.get("link_factor", 6.0)),
        tape_reach_factor=float(raw.get("tape_reach_factor", 0.6)),
        min_route_holds=int(raw.get("min_route_holds", 3)),
        finish_top_frac=float(raw.get("finish_top_frac", 0.5)),
        shared_colours=tuple(str(c) for c in raw.get("shared_colours", ["grey", "black"])),
        shared_link_factor=float(raw.get("shared_link_factor", 2.0)),
    )
    if (
        cfg.link_factor <= 0
        or cfg.tape_reach_factor < 0
        or cfg.min_route_holds < 1
        or not 0 < cfg.finish_top_frac <= 1
        or cfg.shared_link_factor < 0
    ):
        raise ValueError(f"bad route config: {cfg}")
    return cfg


@dataclass
class Route:
    colour: str
    holds: list[int]  # indices into the detection list
    starts: list[int] = field(default_factory=list)  # holds by the start diamonds
    finish: int | None = None  # the hold by the single finish diamond
    grade: str | None = None  # colour of the route's diamonds (its grade circuit)
    shared: list[int] = field(default_factory=list)  # usable grey/black holds near it

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

    def named_route(self, grade: str | None = None) -> Route | None:
        """The route the user means by a colour (and optionally a grade): the largest
        complete route, else the largest with any diamond tape, else the largest."""
        cands = [r for r in self.routes if grade is None or r.grade == grade]
        for pool in (
            [r for r in cands if r.complete],
            [r for r in cands if r.starts or r.finish is not None],
            cands,
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


def _tape_grade(tapes: Sequence[int], detections: Sequence[Detection]) -> str | None:
    """Majority colour of some tape pieces (None if none is coloured)."""
    votes = Counter(c for t in tapes if (c := detections[t].colour) and c != UNKNOWN)
    return votes.most_common(1)[0][0] if votes else None


def _split_by_grade(
    members: list[int], touched: dict[int, list[int]], detections: Sequence[Detection]
) -> list[tuple[str | None, list[int]]]:
    """Split one same-colour cluster into one part per diamond grade."""
    anchors = {i: g for i in members if (g := _tape_grade(touched.get(i, []), detections))}
    grades = sorted(set(anchors.values()))
    if len(grades) <= 1:
        return [(grades[0] if grades else None, members)]
    centres = {i: detections[i].centroid() for i in members}
    parts: dict[str, list[int]] = {g: [] for g in grades}
    for i in members:
        if i in anchors:
            parts[anchors[i]].append(i)
            continue
        x, y = centres[i]
        nearest = min(anchors, key=lambda a: (centres[a][0] - x) ** 2 + (centres[a][1] - y) ** 2)
        parts[anchors[nearest]].append(i)
    return [(g, parts[g]) for g in grades]


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


def _centre(boxes: dict[int, tuple[int, int, int, int]], i: int) -> tuple[float, float]:
    b = boxes[i]
    return ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)


def _seg_dist(p: tuple[float, float], a: tuple[float, float], b: tuple[float, float]) -> float:
    """Distance from point p to segment ab."""
    ax, ay = a
    dx, dy = b[0] - ax, b[1] - ay
    n = dx * dx + dy * dy
    t = 0.0 if n == 0 else max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / n))
    return float(np.hypot(p[0] - (ax + t * dx), p[1] - (ay + t * dy)))


def _touching_tapes(
    holds: list[int],
    tapes: list[int],
    detections: Sequence[Detection],
    boxes: dict[int, tuple[int, int, int, int]],
    reach: int,
) -> dict[int, list[int]]:
    """hold -> tape pieces its grown mask touches."""
    touched: dict[int, list[int]] = {}
    for i in holds:
        x0, y0, x1, y1 = boxes[i]
        grown_box = (x0 - reach, y0 - reach, x1 + reach, y1 + reach)
        grown = None
        for t in tapes:
            if _box_gap(grown_box, boxes[t]) > 0:
                continue
            if grown is None:
                grown = dilate(detections[i].mask, reach)
            if (grown & detections[t].mask).any():
                touched.setdefault(i, []).append(t)
    return touched


def _attach_shared_starts(
    routes: list[Route],
    shared: list[int],
    touched: dict[int, list[int]],
    detections: Sequence[Detection],
    boxes: dict[int, tuple[int, int, int, int]],
) -> None:
    """Give each taped shared hold to the nearest route that has a finish above it and a
    compatible grade. It becomes one of that route's holds and starts."""
    for s in shared:
        if s not in touched:
            continue
        grade = _tape_grade(touched[s], detections)
        sx, sy = _centre(boxes, s)
        fits = [
            r
            for r in routes
            if r.finish is not None
            and _centre(boxes, r.finish)[1] < sy
            and (grade is None or r.grade is None or r.grade == grade)
        ]
        if grade is not None and any(r.grade == grade for r in fits):
            fits = [r for r in fits if r.grade == grade]
        if not fits:
            continue

        def dist(r: Route, sx: float = sx, sy: float = sy) -> float:
            return min(float(np.hypot(*np.subtract(_centre(boxes, i), (sx, sy)))) for i in r.holds)

        best = min(fits, key=dist)
        best.holds = sorted([*best.holds, s])
        best.starts = sorted([*best.starts, s])


def _nearby_shared(
    route: Route, shared: list[int], boxes: dict[int, tuple[int, int, int, int]], reach: float
) -> list[int]:
    """Untaped shared holds within `reach` of the polyline through the route's holds."""
    pts = sorted((_centre(boxes, i) for i in route.holds), key=lambda c: -c[1])
    segs = list(zip(pts, pts[1:], strict=False)) or [(pts[0], pts[0])]
    out = []
    for s in shared:
        c = _centre(boxes, s)
        if min(_seg_dist(c, a, b) for a, b in segs) <= reach:
            out.append(s)
    return out


def group_routes(
    detections: Sequence[Detection], colour: str, cfg: RouteConfig | None = None
) -> RouteResult:
    cfg = cfg or RouteConfig()
    cand = [i for i, d in enumerate(detections) if d.cls == HOLD and d.colour == colour and d.area]
    shared_colours = set(cfg.shared_colours) - {colour}
    shared = [
        i
        for i, d in enumerate(detections)
        if d.cls == HOLD and d.colour in shared_colours and d.area
    ]
    tapes = [i for i, d in enumerate(detections) if d.cls == TAPE and d.area]
    holds_all = [d.area for d in detections if d.cls == HOLD and d.area]
    size = float(np.sqrt(np.median(holds_all))) if holds_all else 1.0
    if not cand:
        return RouteResult(colour, [], [], size)

    link = cfg.link_factor * size
    boxes = {i: _bbox(detections[i].mask) for i in cand + shared + tapes}
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
    touched = _touching_tapes(cand + shared, tapes, detections, boxes, reach)

    routes: list[Route] = []
    for members in clusters.values():
        for grade, part in _split_by_grade(sorted(members), touched, detections):
            diamonds = {i: len(touched.get(i, [])) for i in part}
            starts, finish = _start_and_finish(part, diamonds, boxes, cfg.finish_top_frac)
            routes.append(Route(colour, part, starts, finish, grade))
    _attach_shared_starts(routes, shared, touched, detections, boxes)

    kept: list[Route] = []
    strays: list[int] = []
    for r in routes:
        if r.size >= cfg.min_route_holds or r.complete:
            kept.append(r)
        else:
            strays.extend(i for i in r.holds if i in cand)
    untaped = [i for i in shared if i not in touched]
    for r in kept:
        r.shared = _nearby_shared(r, untaped, boxes, cfg.shared_link_factor * size)
    kept.sort(key=lambda r: (-r.size, r.holds[0]))
    return RouteResult(colour, kept, sorted(strays), size)
