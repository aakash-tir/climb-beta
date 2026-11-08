from pathlib import Path

import pytest
from scripts import ROOT, load_script

from climb_beta.data.roboflow import RoboflowConfigError, api_key, load_source, parse_source

GOOD = {"workspace": "ws", "project": "proj", "version": 3, "class_map": {"Holds": "hold"}}


def test_parse_good() -> None:
    s = parse_source(GOOD)
    assert s.slug == "ws__proj__v3" and s.class_map == {"Holds": "hold"}


@pytest.mark.parametrize(
    ("patch", "msg"),
    [
        ({"version": None}, "not pinned"),
        ({"version": 0}, "positive int"),
        ({"version": "3"}, "positive int"),
        ({"workspace": ""}, "workspace"),
        ({"format": "yolov8"}, "coco-segmentation"),
    ],
)
def test_parse_rejects(patch: dict, msg: str) -> None:
    with pytest.raises(RoboflowConfigError, match=msg):
        parse_source({**GOOD, **patch})


def test_committed_config_is_unpinned_until_issue_12() -> None:
    with pytest.raises(RoboflowConfigError, match="not pinned"):
        load_source(ROOT / "data" / "roboflow.yaml")


def test_api_key() -> None:
    assert api_key({"ROBOFLOW_API_KEY": " abc "}) == "abc"
    with pytest.raises(RoboflowConfigError, match="free Roboflow account"):
        api_key({})


def test_cli_fails_cleanly_without_pin_or_key(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    mod = load_script("data/download_roboflow.py")
    monkeypatch.setattr(mod, "_load_dotenv", lambda: None)
    monkeypatch.delenv("ROBOFLOW_API_KEY", raising=False)
    cfg = tmp_path / "rf.yaml"
    cfg.write_text("workspace: w\nproject: p\nversion: 2\n")
    assert mod.main(["--config", str(cfg), "--dest", str(tmp_path)]) == 2
    assert "ROBOFLOW_API_KEY" in capsys.readouterr().err
    assert mod.main(["--dest", str(tmp_path)]) == 2  # committed config: not pinned
