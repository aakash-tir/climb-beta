from typing import Any

import pytest

from climb_beta.config import ConfigError, load_classes, load_colour_config, parse_colour_config


def test_repo_colour_config_has_the_ten_brief_colours() -> None:
    cfg = load_colour_config()
    assert set(cfg.names) == {
        "red",
        "pink",
        "orange",
        "yellow",
        "green",
        "blue",
        "purple",
        "black",
        "white",
        "grey",
    }
    assert {c.name for c in cfg.by_family("redpink")} == {"red", "pink"}


def test_repo_classes_are_hold_volume_tape_in_order() -> None:
    assert load_classes() == ("hold", "volume", "tape")


def _minimal() -> dict[str, Any]:
    return {
        "colours": [{"name": "red", "family": "redpink"}, {"name": "pink", "family": "redpink"}],
        "families": {"redpink": {"hue": [[0, 9], [150, 180]]}},
        "thresholds": {},
    }


def test_duplicate_colour_rejected() -> None:
    raw = _minimal()
    raw["colours"].append({"name": "Red", "family": "redpink"})
    with pytest.raises(ConfigError, match="duplicate"):
        parse_colour_config(raw)


def test_unknown_family_rejected() -> None:
    raw = _minimal()
    raw["colours"].append({"name": "teal", "family": "cyan"})
    with pytest.raises(ConfigError, match="unknown family"):
        parse_colour_config(raw)


def test_bad_hue_range_rejected() -> None:
    raw = _minimal()
    raw["families"]["redpink"]["hue"] = [[170, 200]]
    with pytest.raises(ConfigError, match="bad hue range"):
        parse_colour_config(raw)
