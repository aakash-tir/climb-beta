from pathlib import Path

import numpy as np
import pytest

from climb_beta.route.group import RouteConfig, group_routes, load_route_config
from climb_beta.types import Detection

H, W = 600, 800


def hold(cx: int, cy: int, colour: str, r: int = 10) -> Detection:
    yy, xx = np.mgrid[0:H, 0:W]
    return Detection(mask=(xx - cx) ** 2 + (yy - cy) ** 2 <= r * r, cls="hold", colour=colour)


def tape(x0: int, y0: int, x1: int, y1: int) -> Detection:
    m = np.zeros((H, W), dtype=bool)
    m[y0:y1, x0:x1] = True
    return Detection(mask=m, cls="tape")


def ladder(x: int, colour: str, n: int = 5, y0: int = 550, step: int = 80) -> list[Detection]:
    return [hold(x, y0 - k * step, colour) for k in range(n)]


def test_two_same_colour_routes_split_and_other_colours_ignored() -> None:
    dets = ladder(100, "red") + ladder(650, "red", n=4) + ladder(380, "blue")
    res = group_routes(dets, "red")
    assert [r.size for r in res.routes] == [5, 4]
    assert res.routes[0].holds == [0, 1, 2, 3, 4]
    assert all(dets[i].colour == "red" for r in res.routes for i in r.holds)


def test_tape_marks_start_hold_only() -> None:
    dets = ladder(100, "red")
    dets.append(tape(85, 563, 115, 570))  # just below the bottom hold (y=550, r=10)
    dets.append(hold(130, 520, "blue"))  # a blue hold near the tape is not a red start
    res = group_routes(dets, "red")
    (route,) = res.routes
    assert route.starts == [0]
    assert res.named_route() is route


def test_named_route_prefers_the_taped_route_over_the_larger() -> None:
    dets = ladder(100, "red", n=6) + ladder(650, "red", n=4)
    dets.append(tape(640, 563, 660, 570))  # tape under the smaller route's first hold
    res = group_routes(dets, "red")
    named = res.named_route()
    assert named is not None and named.size == 4 and named.starts


def test_stray_far_hold_is_not_part_of_route() -> None:
    dets = ladder(100, "red") + [hold(700, 60, "red")]
    res = group_routes(dets, "red")
    assert [r.size for r in res.routes] == [5]
    assert res.strays == [5]


def test_scale_invariance() -> None:
    small = group_routes(ladder(100, "red", step=80) + ladder(600, "red", step=80), "red")
    # bigger holds, same layout ratio -> same grouping
    big = [hold(100, 550 - k * 80, "red", r=20) for k in range(5)]
    big += [hold(600, 550 - k * 80, "red", r=20) for k in range(5)]
    assert len(group_routes(big, "red").routes) == len(small.routes) == 2


def test_no_holds_of_colour() -> None:
    res = group_routes(ladder(100, "blue"), "red")
    assert res.routes == [] and res.named_route() is None


def test_config_loading_and_validation(tmp_path) -> None:  # type: ignore[no-untyped-def]
    assert load_route_config() == RouteConfig(6.0, 0.6, 3)
    p = tmp_path / "r.yaml"
    p.write_text("link_factor: -1\n")
    with pytest.raises(ValueError):
        load_route_config(p)


def start_pair(x: int, y: int) -> list[Detection]:
    """Two diamonds just below a hold centred at (x, y)."""
    return [tape(x - 8, y + 12, x - 2, y + 18), tape(x + 2, y + 12, x + 8, y + 18)]


def finish_diamond(x: int, y: int) -> Detection:
    """One diamond just above a hold centred at (x, y)."""
    return tape(x - 3, y - 18, x + 3, y - 12)


def test_complete_route_has_start_and_finish() -> None:
    dets = ladder(100, "red")  # holds 0 (bottom, y=550) .. 4 (top, y=230)
    dets += start_pair(100, 550) + [finish_diamond(100, 230)]
    (route,) = group_routes(dets, "red").routes
    assert route.starts == [0]
    assert route.finish == 4
    assert route.complete


def test_start_only_route_is_incomplete() -> None:
    dets = ladder(100, "red") + start_pair(100, 550)
    (route,) = group_routes(dets, "red").routes
    assert route.starts == [0] and route.finish is None
    assert not route.complete


def test_finish_only_route_is_incomplete() -> None:
    dets = ladder(100, "red") + [finish_diamond(100, 230)]
    (route,) = group_routes(dets, "red").routes
    assert route.starts == [] and route.finish == 4
    assert not route.complete


def test_two_starting_holds_each_with_a_diamond() -> None:
    dets = ladder(100, "red") + [hold(140, 550, "red")]  # hold 5: second start hold
    dets += [tape(97, 562, 103, 568), tape(137, 562, 143, 568), finish_diamond(100, 230)]
    (route,) = group_routes(dets, "red").routes
    assert route.starts == [0, 5]
    assert route.finish == 4 and route.complete


def test_two_diamonds_at_the_top_are_not_a_finish() -> None:
    dets = ladder(100, "red") + start_pair(100, 230)  # a start pair, wherever it sits
    (route,) = group_routes(dets, "red").routes
    assert route.finish is None and route.starts == [4]


def test_named_route_prefers_complete_over_larger_partial() -> None:
    dets = ladder(100, "red", n=6) + start_pair(100, 550)  # 6 holds, start only
    small = ladder(650, "red", n=4)  # 4 holds, y 550..310
    dets += small + start_pair(650, 550) + [finish_diamond(650, 310)]
    res = group_routes(dets, "red")
    named = res.named_route()
    assert named is not None and named.size == 4 and named.complete


def test_finish_top_frac_validated(tmp_path: Path) -> None:
    p = tmp_path / "route.yaml"
    p.write_text("finish_top_frac: 0\n")
    with pytest.raises(ValueError):
        load_route_config(p)
