import json
from pathlib import Path

import pytest
import yaml
from scripts import load_script

from climb_beta.data.split import (
    SplitError,
    assign_walls,
    build_dataset,
    load_splits,
    save_splits,
    validate_splits,
)

CLASSES = ("hold", "volume", "tape")


@pytest.mark.parametrize("seed", range(25))
def test_assignment_never_puts_a_wall_in_two_splits(seed: int) -> None:
    counts = {f"w{i}": (i * 7) % 11 + 1 for i in range(12)}
    s = assign_walls(counts, seed=seed)
    flat = [w for ws in s.values() for w in ws]
    assert sorted(flat) == sorted(counts)  # every wall exactly once
    assert len(flat) == len(set(flat))
    assert s["test"] and s["val"] and s["train"]


def test_assignment_deterministic_and_roughly_on_ratio() -> None:
    counts = {f"w{i}": 10 for i in range(20)}
    a, b = assign_walls(counts, seed=3), assign_walls(counts, seed=3)
    assert a == b
    assert len(a["train"]) == 14 and len(a["val"]) == 3 and len(a["test"]) == 3
    assert assign_walls(counts, seed=4) != a


def test_bad_ratios() -> None:
    with pytest.raises(SplitError):
        assign_walls({"a": 1}, ratios=(0.5, 0.5, 0.5))


def test_hand_written_overlap_rejected(tmp_path: Path) -> None:
    with pytest.raises(SplitError, match="both"):
        validate_splits({"train": ["cave", "slab"], "test": ["slab"]})
    p = tmp_path / "splits.yaml"
    p.write_text("train: [a]\ntest: [a]\n")
    with pytest.raises(SplitError):
        load_splits(p)
    with pytest.raises(SplitError, match="unknown"):
        validate_splits({"holdout": ["a"]})


def _photos(root: Path, walls: dict[str, int], labelled: bool = True) -> tuple[Path, Path]:
    raw, labels = root / "raw", root / "labels"
    for w, n in walls.items():
        (raw / w).mkdir(parents=True)
        (labels / w).mkdir(parents=True)
        for i in range(n):
            (raw / w / f"IMG_{i}.jpg").write_bytes(b"jpg")
            if labelled:
                (labels / w / f"IMG_{i}.txt").write_text("0 0.1 0.1 0.2 0.1 0.2 0.2\n")
                (labels / w / f"IMG_{i}.json").write_text('[{"colour": "red"}]')
    return raw, labels


def test_build_dataset_by_wall(tmp_path: Path) -> None:
    raw, labels = _photos(tmp_path, {"cave": 2, "slab": 1, "prow": 1})
    (labels / "slab" / "IMG_0.txt").unlink()  # one unlabelled photo
    splits = {"train": ["cave"], "val": ["slab"], "test": ["prow"]}
    out = tmp_path / "yolo"
    rep = build_dataset(raw, labels, splits, out, CLASSES, pseudo={"prow/IMG_0.jpg"})
    assert rep.images == {"train": 2, "val": 0, "test": 0}
    assert rep.unlabelled == ["slab/IMG_0.jpg"]
    assert rep.pseudo_skipped_from_test == ["prow/IMG_0.jpg"]
    assert (out / "images" / "train" / "cave__IMG_1.jpg").exists()
    assert (out / "colours" / "train" / "cave__IMG_1.json").exists()
    manifest = json.loads((out / "manifest.json").read_text())
    assert {r["wall"] for r in manifest} == {"cave"}
    assert yaml.safe_load((out / "dataset.yaml").read_text())["train"] == "images/train"


def test_unassigned_wall_reported(tmp_path: Path) -> None:
    raw, labels = _photos(tmp_path, {"cave": 1, "new": 1})
    rep = build_dataset(raw, labels, {"train": ["cave"]}, tmp_path / "o", CLASSES)
    assert rep.unassigned_walls == ["new"]


def test_cli_assign_is_stable_when_walls_are_added(tmp_path: Path) -> None:
    raw, labels = _photos(tmp_path, {f"w{i}": 3 for i in range(6)})
    splits = tmp_path / "splits.yaml"
    mod = load_script("data/split_by_wall.py")
    base = ["--raw", str(raw), "--labels", str(labels), "--splits", str(splits)]
    assert mod.main([*base, "assign"]) == 0
    before = load_splits(splits)
    _photos(tmp_path / "more", {"w9": 3})
    (raw / "w9").mkdir()
    (raw / "w9" / "a.jpg").write_bytes(b"x")
    assert mod.main([*base, "assign"]) == 0
    after = load_splits(splits)
    for s, ws in before.items():
        assert set(ws) <= set(after[s])  # old walls never move
    assert sum("w9" in ws for ws in after.values()) == 1
    assert mod.main([*base, "build", "--out", str(tmp_path / "ds")]) == 0


def test_cli_rejects_overlapping_splits_file(tmp_path: Path) -> None:
    raw, labels = _photos(tmp_path, {"a": 1})
    splits = tmp_path / "splits.yaml"
    splits.write_text("train: [a]\ntest: [a]\n")
    mod = load_script("data/split_by_wall.py")
    args = ["--raw", str(raw), "--labels", str(labels), "--splits", str(splits), "build"]
    assert mod.main(args) == 2


def test_save_splits_roundtrip(tmp_path: Path) -> None:
    p = tmp_path / "s.yaml"
    save_splits(p, {"train": ["a"], "val": ["b"], "test": []})
    assert load_splits(p) == {"train": ["a"], "val": ["b"], "test": []}
