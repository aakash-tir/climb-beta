from pathlib import Path

import numpy as np
import pytest
import yaml
from fakes import wall_scene
from scripts import load_script

from climb_beta.demo import DemoService


def _no_weights() -> object:
    raise RuntimeError("No detector weights configured.")


def test_handle_highlights_route_and_summarises() -> None:
    img_bgr, det, idx = wall_scene()
    svc = DemoService(detector_factory=lambda: det)
    out, msg = svc.handle(np.ascontiguousarray(img_bgr[..., ::-1]), "red")
    assert out is not None and out.shape == img_bgr.shape
    assert "**Red route (white grade):** 5 holds, 1 start hold(s)" in msg
    assert "Colours seen: red, blue" in msg
    assert svc.grades[0] == "any" and svc.grades[1:] == list(svc.colour_cfg.grades)
    _, msg = svc.handle(np.ascontiguousarray(img_bgr[..., ::-1]), "red", "white")
    assert "**Red route (white grade)" in msg
    _, msg = svc.handle(np.ascontiguousarray(img_bgr[..., ::-1]), "red", "pink")
    assert "No **red / pink-grade** route" in msg


def test_handle_without_weights_explains() -> None:
    img_bgr, _, _ = wall_scene()
    svc = DemoService(detector_factory=_no_weights)  # type: ignore[arg-type]
    out, msg = svc.handle(img_bgr[..., ::-1], "red")
    assert "Detector not available" in msg and out is not None


def test_handle_edge_cases() -> None:
    img_bgr, det, _ = wall_scene()
    svc = DemoService(detector_factory=lambda: det)
    assert svc.handle(None, "red")[0] is None
    assert "Unknown colour" in svc.handle(img_bgr[..., ::-1], "teal")[1]
    assert "No **green** route" in svc.handle(img_bgr[..., ::-1], "green")[1]


def test_default_factory_requires_env(monkeypatch: pytest.MonkeyPatch) -> None:
    from climb_beta.demo import default_detector_factory

    monkeypatch.delenv("CLIMB_DETECTOR_WEIGHTS", raising=False)
    with pytest.raises(RuntimeError, match="CLIMB_DETECTOR_WEIGHTS"):
        default_detector_factory()


def test_build_space_folder(tmp_path: Path) -> None:
    mod = load_script("app/build_space.py")
    out = tmp_path / "space"
    assert mod.main([str(out)]) == 0
    for f in (
        "app.py",
        "requirements.txt",
        "README.md",
        "LICENSE",
        "configs/colours.yaml",
        "climb_beta/pipeline.py",
    ):
        assert (out / f).exists(), f
    front = (out / "README.md").read_text(encoding="utf-8").split("---")[1]
    meta = yaml.safe_load(front)
    assert (
        meta["sdk"] == "gradio" and meta["app_file"] == "app.py" and meta["license"] == "agpl-3.0"
    )
    assert "download.pytorch.org/whl/cpu" in (out / "requirements.txt").read_text()
    assert "CLIMB_CONFIG_DIR" in (out / "app.py").read_text(encoding="utf-8")
    assert not list(out.rglob("*.pt"))


def test_ui_builds() -> None:
    pytest.importorskip("gradio")
    img_bgr, det, _ = wall_scene()
    mod = load_script("app/app.py")
    demo = mod.build_ui(DemoService(detector_factory=lambda: det))
    assert demo is not None
