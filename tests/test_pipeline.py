import json
from pathlib import Path

import pytest
from fakes import FakeClassifier, wall_scene
from scripts import load_script

from climb_beta.config import load_colour_config
from climb_beta.imageio import write_bgr
from climb_beta.pipeline import run

CFG = load_colour_config()


def test_pipeline_finds_both_routes_and_red_start() -> None:
    img, det, idx = wall_scene()
    res = run(img, det, CFG)
    assert res.colours_present() == ["red", "blue"]
    red = res.routes["red"].named_route()
    assert red is not None and red.holds == idx["red"]
    assert red.starts == [idx["red"][0]]
    blue = res.routes["blue"].named_route()
    assert blue is not None and blue.holds == idx["blue"] and blue.starts == []
    js = res.to_json()
    assert js["routes"]["red"]["named"] == 0
    assert len(js["detections"]) == 10


def test_pipeline_selected_colour_only() -> None:
    img, det, _ = wall_scene()
    res = run(img, det, CFG, colours=["blue"])
    assert list(res.routes) == ["blue"]


def test_classifier_method_overrides_rules() -> None:
    img, det, _ = wall_scene()
    res = run(img, det, CFG, method="classifier", classifier=FakeClassifier("green", CFG.names))
    assert {d.colour for d in res.detections if d.cls == "hold"} == {"green"}
    with pytest.raises(ValueError):
        run(img, det, CFG, method="classifier")


def test_find_route_cli(tmp_path: Path) -> None:
    img, det, idx = wall_scene()
    p = tmp_path / "wall.png"
    write_bgr(p, img)
    out = tmp_path / "r.json"
    mod = load_script("route/find_route.py")
    assert mod.main([str(p), "--colour", "red", "--out", str(out)], detector=det) == 0
    js = json.loads(out.read_text())
    assert js["routes"]["red"]["routes"][0]["holds"] == idx["red"]
    assert mod.main([str(p), "--colour", "teal"], detector=det) == 2
    assert mod.main([str(tmp_path / "none.png")], detector=det) == 2
