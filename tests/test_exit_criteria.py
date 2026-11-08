import json
from pathlib import Path

import numpy as np
import pytest
from fakes import FakeDetector, wall_scene
from scripts import load_script

from climb_beta.data.yolo import YoloInstance, write_labels
from climb_beta.imageio import write_bgr
from climb_beta.masks import mask_to_polygon, normalise
from climb_beta.metrics.route import score_route
from climb_beta.types import Mask


def _disk(cx: int, cy: int, r: int = 10) -> Mask:
    yy, xx = np.mgrid[0:100, 0:100]
    return (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r


def test_score_route() -> None:
    gt = [_disk(10, 10), _disk(40, 40), _disk(70, 70)]
    assert score_route(gt, gt).error == 0
    s = score_route([gt[0], gt[1], _disk(90, 10)], gt)  # one missed, one extra
    assert (s.missed, s.extra) == (1, 1) and not s.correct(1)
    assert score_route(gt[:2], gt).correct(1)
    assert score_route([], gt).missed == 3


def _test_set(root: Path, chalked_colours: bool = True) -> tuple[Path, FakeDetector]:
    """One test photo (the wall_scene), GT labels, sidecars and a routes.yaml."""
    img, det, idx = wall_scene()
    h, w = img.shape[:2]
    write_bgr(root / "images" / "test" / "w__1.png", img)
    insts, side = [], []
    for i, (m, cls) in enumerate(det.items):
        insts.append(
            YoloInstance(
                ["hold", "volume", "tape"].index(cls), normalise(mask_to_polygon(m, 0.5), h, w)
            )
        )
        colour = "red" if i in idx["red"] else "blue" if i in idx["blue"] else None
        side.append({"cls": cls, "colour": colour, "chalked": i in (1, 3)})
    write_labels(root / "labels" / "test" / "w__1.txt", insts)
    (root / "colours" / "test").mkdir(parents=True)
    (root / "colours" / "test" / "w__1.json").write_text(json.dumps(side))
    routes = root / "routes.yaml"
    routes.write_text(
        f"routes:\n  - {{image: w__1.png, colour: red, holds: {idx['red']}}}\n"
        f"  - {{image: w__1.png, colour: blue, holds: {idx['blue']}}}\n"
    )
    return routes, det


def test_perfect_detector_passes_everything(tmp_path: Path) -> None:
    routes, det = _test_set(tmp_path)
    out = tmp_path / "r.json"
    mod = load_script("eval/check_exit_criteria.py")
    rc = mod.main(
        ["--dataset", str(tmp_path), "--routes", str(routes), "--json", str(out)], detector=det
    )
    rep = json.loads(out.read_text())
    assert rep["passed"] == {k: True for k in rep["passed"]}, rep["values"]
    assert rc == 0
    assert rep["counts"]["colour_chalked"] == 2 and rep["counts"]["route_within_1"] == 2


def test_detector_missing_holds_fails_recall_and_route(tmp_path: Path) -> None:
    routes, det = _test_set(tmp_path)
    weak = FakeDetector(det.items[2:])  # misses two red holds
    out = tmp_path / "r.json"
    mod = load_script("eval/check_exit_criteria.py")
    rc = mod.main(
        ["--dataset", str(tmp_path), "--routes", str(routes), "--json", str(out)], detector=weak
    )
    rep = json.loads(out.read_text())
    assert rc == 1
    assert not rep["passed"]["hold_recall"] and not rep["passed"]["route_within_1"]
    assert rep["passed"]["colour_overall"]  # colour is measured on GT masks: unaffected


def test_empty_or_missing_test_set_never_passes(tmp_path: Path) -> None:
    mod = load_script("eval/check_exit_criteria.py")
    assert mod.main(["--dataset", str(tmp_path)], detector=FakeDetector([])) == 2
    (tmp_path / "images" / "test").mkdir(parents=True)
    assert mod.main(["--dataset", str(tmp_path)], detector=FakeDetector([])) == 1


def test_wall_leakage_refused(tmp_path: Path) -> None:
    routes, det = _test_set(tmp_path)
    (tmp_path / "manifest.json").write_text(
        json.dumps(
            [
                {"image": "a", "wall": "w", "split": "train"},
                {"image": "b", "wall": "w", "split": "test"},
            ]
        )
    )
    mod = load_script("eval/check_exit_criteria.py")
    assert mod.main(["--dataset", str(tmp_path), "--routes", str(routes)], detector=det) == 2


def test_pseudo_masked_test_images_skipped(tmp_path: Path) -> None:
    from climb_beta.metrics.exit_criteria import evaluate

    routes, det = _test_set(tmp_path)
    (tmp_path / "pseudo_masks.txt").write_text("test/w__1.png\n")
    from climb_beta.config import load_classes, load_colour_config

    rep = evaluate(tmp_path, det, load_colour_config(), load_classes())
    assert rep.details["skipped_pseudo_masked"] == ["w__1.png"]
    assert rep.values["hold_recall"] is None and not rep.all_passed


def test_bad_routes_yaml(tmp_path: Path) -> None:
    from climb_beta.metrics.exit_criteria import load_routes_gt

    p = tmp_path / "r.yaml"
    p.write_text("routes:\n  - {image: a.png, colour: red}\n")
    with pytest.raises(ValueError):
        load_routes_gt(p)
    assert load_routes_gt(None) == []
