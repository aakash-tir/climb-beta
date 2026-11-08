"""Roboflow Universe download config and helpers (the SDK itself is imported lazily)."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

API_KEY_ENV = "ROBOFLOW_API_KEY"


class RoboflowConfigError(ValueError):
    pass


@dataclass(frozen=True)
class RoboflowSource:
    workspace: str
    project: str
    version: int
    format: str = "coco-segmentation"
    licence: str = ""
    attribution: str = ""
    class_map: dict[str, str] = field(default_factory=dict)

    @property
    def slug(self) -> str:
        return f"{self.workspace}__{self.project}__v{self.version}"


def parse_source(raw: Mapping[str, Any]) -> RoboflowSource:
    for key in ("workspace", "project"):
        if not raw.get(key):
            raise RoboflowConfigError(f"roboflow.yaml: '{key}' is required")
    version = raw.get("version")
    if version is None:
        raise RoboflowConfigError(
            "roboflow.yaml: 'version' is not pinned yet. Confirm the project is "
            "instance segmentation + CC BY 4.0 in a browser and set it (issue #12)."
        )
    if not isinstance(version, int) or version < 1:
        raise RoboflowConfigError(
            f"roboflow.yaml: 'version' must be a positive int, got {version!r}"
        )
    fmt = str(raw.get("format", "coco-segmentation"))
    if fmt != "coco-segmentation":
        raise RoboflowConfigError("roboflow.yaml: only 'coco-segmentation' is supported")
    return RoboflowSource(
        workspace=str(raw["workspace"]),
        project=str(raw["project"]),
        version=version,
        format=fmt,
        licence=str(raw.get("licence", "")),
        attribution=str(raw.get("attribution", "")).strip(),
        class_map={str(k): str(v) for k, v in (raw.get("class_map") or {}).items()},
    )


def load_source(path: Path) -> RoboflowSource:
    return parse_source(yaml.safe_load(path.read_text(encoding="utf-8")) or {})


def api_key(env: Mapping[str, str] | None = None) -> str:
    env = os.environ if env is None else env
    key = env.get(API_KEY_ENV, "").strip()
    if not key:
        raise RoboflowConfigError(
            f"{API_KEY_ENV} is not set. Create a free Roboflow account, copy the API key "
            "into .env (see .env.example), and re-run."
        )
    return key


def download(src: RoboflowSource, key: str, dest_root: Path) -> Path:
    """Download the export with the Roboflow SDK (the `data` extra). Returns its folder."""
    from roboflow import Roboflow  # lazy

    dest = dest_root / src.slug
    rf = Roboflow(api_key=key)
    rf.workspace(src.workspace).project(src.project).version(src.version).download(
        src.format, location=str(dest), overwrite=False
    )
    if src.attribution:
        (dest / "ATTRIBUTION.txt").write_text(
            f"{src.attribution}\nLicence: {src.licence}\n", encoding="utf-8"
        )
    return dest
