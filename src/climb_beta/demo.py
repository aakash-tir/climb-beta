"""Logic behind the Gradio demo: photo + colour -> highlighted route + summary.

Kept free of Gradio so it can be tested without the `app` extra. The detector is
created lazily on the first request, so the UI starts fast and starts without weights
(it then explains what's missing instead of crashing).
"""

from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass, field

import numpy as np
import numpy.typing as npt

from climb_beta.config import ColourConfig, load_colour_config
from climb_beta.detect import DetectorLike
from climb_beta.overlay import draw_route, hex_to_bgr
from climb_beta.pipeline import run
from climb_beta.route.group import RouteConfig, load_route_config

WEIGHTS_ENV = "CLIMB_DETECTOR_WEIGHTS"
MAX_SIDE = 2048  # downscale huge phone photos: faster on CPU, same holds
RGB = npt.NDArray[np.uint8]


def default_detector_factory() -> DetectorLike:
    spec = os.environ.get(WEIGHTS_ENV, "").strip()
    if not spec:
        raise RuntimeError(
            f"No detector weights configured. Set {WEIGHTS_ENV} to a local .pt path or "
            "hf://<user>/<repo>/<file>.pt (train one with train/train_detector.py)."
        )
    from climb_beta.detect import Detector

    return Detector(spec, device="cpu")


def _downscale(img: RGB) -> RGB:
    import cv2

    h, w = img.shape[:2]
    s = MAX_SIDE / max(h, w)
    if s >= 1:
        return img
    out = cv2.resize(img, (round(w * s), round(h * s)), interpolation=cv2.INTER_AREA)
    return np.asarray(out, dtype=np.uint8)


@dataclass
class DemoService:
    detector_factory: Callable[[], DetectorLike] = default_detector_factory
    colour_cfg: ColourConfig = field(default_factory=load_colour_config)
    route_cfg: RouteConfig = field(default_factory=load_route_config)
    _detector: DetectorLike | None = None

    @property
    def colours(self) -> list[str]:
        return list(self.colour_cfg.names)

    def detector(self) -> DetectorLike:
        if self._detector is None:
            self._detector = self.detector_factory()
        return self._detector

    def handle(self, image_rgb: RGB | None, colour: str) -> tuple[RGB | None, str]:
        if image_rgb is None:
            return None, "Upload a photo of a wall first."
        if not self.colour_cfg.has(colour):
            return image_rgb, f"Unknown colour '{colour}'."
        try:
            det = self.detector()
        except RuntimeError as e:
            return image_rgb, f"**Detector not available.** {e}"
        rgb = _downscale(np.ascontiguousarray(image_rgb[..., :3]))
        bgr = np.ascontiguousarray(rgb[..., ::-1])
        res = run(bgr, det, self.colour_cfg, self.route_cfg, colours=[colour])
        rr = res.routes[colour]
        route = rr.named_route()
        swatch = next(c.swatch for c in self.colour_cfg.colours if c.name == colour)
        out = draw_route(bgr, res.detections, route, hex_to_bgr(swatch))
        n_holds = sum(d.cls == "hold" for d in res.detections)
        present = ", ".join(res.colours_present()) or "none"
        if route is None:
            msg = f"No **{colour}** route found. Hold colours seen: {present}."
        else:
            starts = (
                f"{len(route.starts)} start hold(s) marked S"
                if route.starts
                else "no start tape found"
            )
            starts += ", finish marked F" if route.finish is not None else ", no finish found"
            if not route.complete:
                starts += " (incomplete route)"
            others = len(rr.routes) - 1
            msg = (
                f"**{colour.title()} route:** {route.size} holds, {starts}."
                + (f" ({others} other {colour} route(s) on this photo.)" if others else "")
                + f"\n\nDetected {n_holds} holds in total. Colours seen: {present}."
            )
        return np.ascontiguousarray(out[..., ::-1]), msg
