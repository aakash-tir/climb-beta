"""Photo -> detections -> hold colours -> routes, in one call.

detector (colour-blind) -> wall-referenced white balance -> colour per hold
(rules, or the crop classifier) -> group the chosen colour's holds into routes
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, Literal, Protocol

from climb_beta.colour.batch import colour_detections
from climb_beta.colour.crops import extract_crop
from climb_beta.colour.rules import ColourResult
from climb_beta.config import ColourConfig
from climb_beta.detect import DetectorLike
from climb_beta.route.group import RouteConfig, RouteResult, group_routes
from climb_beta.types import Detection, ImageBGR

ColourMethod = Literal["rules", "classifier"]


class ClassifierLike(Protocol):
    @property
    def classes(self) -> tuple[str, ...]: ...

    def predict(self, crops: Sequence[ImageBGR]) -> list[tuple[str, float]]: ...


@dataclass
class PipelineResult:
    detections: list[Detection]
    balanced: ImageBGR
    colour_results: list[ColourResult | None]
    routes: dict[str, RouteResult] = field(default_factory=dict)

    def colours_present(self) -> list[str]:
        seen: dict[str, int] = {}
        for d in self.detections:
            if d.cls == "hold" and d.colour and d.colour != "unknown":
                seen[d.colour] = seen.get(d.colour, 0) + 1
        return sorted(seen, key=lambda c: -seen[c])

    def to_json(self) -> dict[str, Any]:
        holds = []
        for i, d in enumerate(self.detections):
            x0, y0, x1, y1 = d.bbox()
            holds.append(
                {
                    "idx": i,
                    "cls": d.cls,
                    "score": round(d.score, 3),
                    "colour": d.colour,
                    "colour_conf": round(d.colour_conf, 3),
                    "bbox": [x0, y0, x1, y1],
                }
            )
        routes: dict[str, Any] = {}
        for c, rr in self.routes.items():
            named = rr.named_route()
            routes[c] = {
                "routes": [{"holds": r.holds, "starts": r.starts} for r in rr.routes],
                "named": None if named is None else rr.routes.index(named),
                "strays": rr.strays,
            }
        return {"detections": holds, "routes": routes}


def run(
    img: ImageBGR,
    detector: DetectorLike,
    colour_cfg: ColourConfig,
    route_cfg: RouteConfig | None = None,
    colours: Sequence[str] | None = None,
    method: ColourMethod = "rules",
    classifier: ClassifierLike | None = None,
) -> PipelineResult:
    """Run the whole Phase 1 pipeline on one photo.

    `colours`: which colours to group into routes (default: every colour present).
    `method="classifier"` replaces the rule colour with the crop classifier's.
    """
    dets = detector.predict(img)
    balanced, results = colour_detections(img, dets, colour_cfg)
    if method == "classifier":
        if classifier is None:
            raise ValueError("method='classifier' needs a classifier")
        holds = [d for d in dets if d.cls == "hold"]
        crops = [extract_crop(balanced, d.mask) for d in holds]
        for d, (name, conf) in zip(holds, classifier.predict(crops), strict=True):
            d.colour, d.colour_conf = name, conf
    res = PipelineResult(dets, balanced, results)
    for c in colours if colours is not None else res.colours_present():
        res.routes[c] = group_routes(dets, c, route_cfg)
    return res
