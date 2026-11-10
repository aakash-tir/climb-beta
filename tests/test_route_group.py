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


def graded_tape(x0: int, y0: int, x1: int, y1: int, grade: str) -> Detection:
    t = tape(x0, y0, x1, y1)
    t.colour = grade
    return t


def test_route_grade_is_its_diamond_colour() -> None:
    dets = ladder(100, "red")
    dets += [graded_tape(97, 562, 103, 568, "green"), graded_tape(97, 212, 103, 218, "green")]
    (route,) = group_routes(dets, "red").routes
    assert route.grade == "green" and route.complete


def test_untaped_route_has_no_grade() -> None:
    (route,) = group_routes(ladder(100, "red"), "red").routes
    assert route.grade is None


def test_same_colour_cluster_split_by_grade() -> None:
    # Two pink routes side by side, close enough to cluster as one: the left one is
    # red-grade, the right one orange-grade, each with a start pair and a finish.
    dets = ladder(100, "pink") + ladder(180, "pink")  # holds 0..4 and 5..9
    for x, g in ((100, "red"), (180, "orange")):
        dets += [
            graded_tape(x - 8, 562, x - 2, 568, g),
            graded_tape(x + 2, 562, x + 8, 568, g),
            graded_tape(x - 3, 212, x + 3, 218, g),
        ]
    res = group_routes(dets, "pink")
    by_grade = {r.grade: r for r in res.routes}
    assert set(by_grade) == {"red", "orange"}
    assert by_grade["red"].holds == [0, 1, 2, 3, 4]
    assert by_grade["orange"].holds == [5, 6, 7, 8, 9]
    assert all(r.complete for r in res.routes)
    assert res.named_route("orange") is by_grade["orange"]
    assert res.named_route("yellow") is None


def test_unknown_tape_colour_is_ignored_for_grade() -> None:
    dets = ladder(100, "red")
    dets += [graded_tape(97, 562, 103, 568, "unknown"), graded_tape(97, 212, 103, 218, "blue")]
    (route,) = group_routes(dets, "red").routes
    assert route.grade == "blue"


def mostly_grey_route(start_grade: str, finish_grade: str) -> list[Detection]:
    """Grey start (2 diamonds) at the bottom, three grey holds, an orange finish (1 diamond)
    at the top, plus a far-away grey hold. Indices: 0 start, 1-3 middle, 4 finish, 5 far."""
    dets = [hold(300, 550, "grey")]
    dets += [hold(300, y, "grey") for y in (470, 390, 310)]
    dets += [hold(300, 230, "orange"), hold(650, 400, "grey")]
    dets += [
        graded_tape(292, 562, 298, 568, start_grade),
        graded_tape(302, 562, 308, 568, start_grade),
        graded_tape(297, 212, 303, 218, finish_grade),
    ]
    return dets


def test_route_of_shared_holds_with_own_colour_finish() -> None:
    res = group_routes(mostly_grey_route("green", "green"), "orange")
    (route,) = res.routes
    assert route.holds == [0, 4]
    assert route.starts == [0] and route.finish == 4
    assert route.complete and route.grade == "green"
    assert route.shared == [1, 2, 3]  # grey holds on the line; the far one isn't


def test_shared_start_needs_matching_grade() -> None:
    res = group_routes(mostly_grey_route("red", "green"), "orange")
    assert res.routes == []  # one orange finish, no start: incomplete and too small
    assert res.strays == [4]


def test_shared_holds_alone_never_form_a_route() -> None:
    dets = ladder(100, "grey") + ladder(300, "black")
    dets += start_pair(100, 550) + [finish_diamond(100, 230)]
    assert group_routes(dets, "red").routes == []


def test_requested_colour_is_not_shared_with_itself() -> None:
    (route,) = group_routes(ladder(100, "black"), "black").routes
    assert route.holds == [0, 1, 2, 3, 4] and route.shared == []


def test_grey_hold_between_route_holds_is_shared_by_both_neighbours() -> None:
    dets = ladder(100, "red") + ladder(160, "blue") + [hold(130, 510, "grey")]  # grey = 10
    red = group_routes(dets, "red").named_route()
    blue = group_routes(dets, "blue").named_route()
    assert red is not None and blue is not None
    assert red.shared == [10] and blue.shared == [10]
    assert 10 not in red.holds and 10 not in blue.holds


def test_shared_config_validated(tmp_path: Path) -> None:
    assert load_route_config().shared_colours == ("grey", "black")
    p = tmp_path / "route.yaml"
    p.write_text("shared_link_factor: -1\n")
    with pytest.raises(ValueError):
        load_route_config(p)
