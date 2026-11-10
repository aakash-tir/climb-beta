"""Load and validate `configs/colours.yaml` and `configs/classes.yaml`."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
# Overridable so a packaged copy (e.g. the HF Space) can ship configs next to the package.
CONFIG_DIR = Path(os.environ.get("CLIMB_CONFIG_DIR", str(REPO_ROOT / "configs")))
CHROMATIC_FAMILIES = ("redpink", "orange", "yellow", "green", "blue", "purple")
ACHROMATIC = "achromatic"


class ConfigError(ValueError):
    """Raised when a config file is malformed."""


@dataclass(frozen=True)
class Colour:
    name: str
    family: str
    swatch: str


@dataclass(frozen=True)
class ColourConfig:
    colours: tuple[Colour, ...]
    family_hues: dict[str, tuple[tuple[int, int], ...]]
    thresholds: dict[str, Any] = field(default_factory=dict)
    # Detector classes the colour step labels. Tape is coloured because a Basecamp
    # route's tape diamonds carry its grade colour.
    coloured_classes: tuple[str, ...] = ("hold",)
    # Grade circuits (tape diamond colours), easiest to hardest.
    grades: tuple[str, ...] = ()

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(c.name for c in self.colours)

    def by_family(self, family: str) -> tuple[Colour, ...]:
        return tuple(c for c in self.colours if c.family == family)

    def has(self, name: str) -> bool:
        return name in self.names


def _require(d: dict[str, Any], key: str, where: str) -> Any:
    if key not in d:
        raise ConfigError(f"{where}: missing key '{key}'")
    return d[key]


def parse_colour_config(raw: dict[str, Any]) -> ColourConfig:
    """Validate a parsed colours.yaml mapping."""
    colours_raw = _require(raw, "colours", "colours.yaml")
    families_raw = _require(raw, "families", "colours.yaml")
    thresholds = _require(raw, "thresholds", "colours.yaml")

    colours: list[Colour] = []
    seen: set[str] = set()
    for i, c in enumerate(colours_raw):
        name = str(_require(c, "name", f"colours[{i}]")).strip().lower()
        family = str(_require(c, "family", f"colours[{i}]"))
        if name in seen:
            raise ConfigError(f"duplicate colour '{name}'")
        if family != ACHROMATIC and family not in families_raw:
            raise ConfigError(f"colour '{name}' uses unknown family '{family}'")
        seen.add(name)
        colours.append(Colour(name=name, family=family, swatch=str(c.get("swatch", "#888888"))))

    family_hues: dict[str, tuple[tuple[int, int], ...]] = {}
    for fam, spec in families_raw.items():
        ranges = []
        for lo, hi in _require(spec, "hue", f"families.{fam}"):
            if not (0 <= lo < hi <= 180):
                raise ConfigError(f"families.{fam}: bad hue range [{lo}, {hi}]")
            ranges.append((int(lo), int(hi)))
        family_hues[str(fam)] = tuple(ranges)

    redpink = [c.name for c in colours if c.family == "redpink"]
    if redpink and set(redpink) != {"red", "pink"}:
        raise ConfigError("the redpink family must contain exactly 'red' and 'pink'")

    coloured = tuple(str(c) for c in raw.get("coloured_classes", ["hold"]))
    if not coloured or len(set(coloured)) != len(coloured):
        raise ConfigError("colours.yaml: coloured_classes must be a non-empty, unique list")

    grades = tuple(str(g).strip().lower() for g in raw.get("grades", []))
    if len(set(grades)) != len(grades):
        raise ConfigError("colours.yaml: duplicate grade")
    if bad := [g for g in grades if g not in seen]:
        raise ConfigError(f"colours.yaml: grades {bad} are not colours")

    return ColourConfig(
        colours=tuple(colours),
        family_hues=family_hues,
        thresholds=thresholds,
        coloured_classes=coloured,
        grades=grades,
    )


def load_colour_config(path: Path | None = None) -> ColourConfig:
    path = path or CONFIG_DIR / "colours.yaml"
    with path.open(encoding="utf-8") as f:
        return parse_colour_config(yaml.safe_load(f))


def load_classes(path: Path | None = None) -> tuple[str, ...]:
    path = path or CONFIG_DIR / "classes.yaml"
    with path.open(encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    classes = tuple(str(c) for c in _require(raw, "classes", "classes.yaml"))
    if len(set(classes)) != len(classes):
        raise ConfigError("classes.yaml: duplicate class names")
    return classes
