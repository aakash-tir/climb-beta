"""Draw a chosen route on the photo: everything else dimmed, route holds outlined,
start holds marked "S" and the finish hold "F". Shared grey/black holds the route may use
are kept in colour with a thin outline."""

from __future__ import annotations

from collections.abc import Sequence

import cv2
import numpy as np

from climb_beta.route.group import Route
from climb_beta.types import Detection, ImageBGR

DIM = 0.35  # brightness kept outside the route
START_COLOUR = (255, 255, 255)


def hex_to_bgr(hex_colour: str) -> tuple[int, int, int]:
    h = hex_colour.lstrip("#")
    if len(h) != 6:
        raise ValueError(f"bad hex colour {hex_colour!r}")
    r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
    return (b, g, r)


def draw_route(
    img: ImageBGR,
    detections: Sequence[Detection],
    route: Route | None,
    outline_bgr: tuple[int, int, int] = (0, 255, 255),
    thickness: int | None = None,
) -> ImageBGR:
    """Return a copy with the route highlighted. With no route, the whole photo is dimmed."""
    h, w = img.shape[:2]
    keep = np.zeros((h, w), dtype=bool)
    holds = route.holds if route else []
    shared = route.shared if route else []
    for i in [*holds, *shared]:
        keep |= detections[i].mask
    grey = cv2.cvtColor(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
    out = (grey.astype(np.float32) * DIM).astype(np.uint8)
    out[keep] = img[keep]
    t = thickness or max(2, round(min(h, w) / 300))
    for i in holds:
        contours, _ = cv2.findContours(
            detections[i].mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        cv2.drawContours(out, contours, -1, outline_bgr, t, lineType=cv2.LINE_AA)
    for i in shared:
        contours, _ = cv2.findContours(
            detections[i].mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        cv2.drawContours(out, contours, -1, outline_bgr, max(1, t // 2), lineType=cv2.LINE_AA)
    marks = [(i, "S") for i in route.starts] if route else []
    if route and route.finish is not None:
        marks.append((route.finish, "F"))
    for i, label in marks:
        x0, y0, x1, y1 = detections[i].bbox()
        cx, cy = (x0 + x1) // 2, y1 + 4 * t
        scale = max(0.5, t / 2)
        org = (cx - 4 * t, cy + 6 * t)
        cv2.putText(out, label, org, cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), t + 2)
        cv2.putText(out, label, org, cv2.FONT_HERSHEY_SIMPLEX, scale, START_COLOUR, t)
    return np.asarray(out, dtype=np.uint8)
