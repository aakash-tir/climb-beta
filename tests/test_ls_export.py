import json
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from scripts import load_script

from climb_beta.config import load_colour_config
from climb_beta.data.ls_export import convert_ls_export, photo_key
from climb_beta.data.yolo import read_labels

CLASSES = ("hold", "volume", "tape")
CFG = load_colour_config()
H, W = 100, 200


def fake_decode(rle: list[int], h: int, w: int) -> np.ndarray:
    # test "RLE": [x0, y0, x1, y1] box
    m = np.zeros((h, w), dtype=bool)
    x0, y0, x1, y1 = rle
    m[y0:y1, x0:x1] = True
    return m


def region(rid: str, kind: str, label: str, value: dict[str, Any]) -> dict[str, Any]:
    from_name = "mask" if kind == "brushlabels" else "poly"
    return {
        "id": rid,
        "type": kind,
        "from_name": from_name,
        "to_name": "image",
        "original_width": W,
        "original_height": H,
        "value": {**value, kind: [label]},
    }


def choice(rid: str, name: str, values: list[str]) -> dict[str, Any]:
    return {"id": rid, "type": "choices", "from_name": name, "value": {"choices": values}}


def _export(tmp: Path, colour: str = "Red") -> Path:
    result = [
        region("h1", "brushlabels", "hold", {"format": "rle", "rle": [20, 10, 60, 50]}),
        choice("h1", "colour", [colour]),
        choice("h1", "chalked", ["chalked"]),
        region("v1", "polygonlabels", "volume", {"points": [[50, 50], [90, 50], [90, 90]]}),
        region("h2", "polygonlabels", "hold", {"points": [[1, 1], [5, 1], [5, 5]]}),
        choice("h2", "colour", ["pink"]),
    ]
    tasks = [
        {
            "id": 1,
            "data": {"image": "/data/local-files/?d=raw/cave-left/IMG_0001.jpg"},
            "annotations": [
                {"was_cancelled": False, "result": []},
                {"was_cancelled": False, "result": result},
            ],
        },
        {"id": 2, "data": {"image": "/data/upload/3/abc.jpg"}, "annotations": [{"result": []}]},
        {"id": 3, "data": {"image": "/data/local-files/?d=raw/slab/x.jpg"}, "annotations": []},
    ]
    p = tmp / "export.json"
    p.write_text(json.dumps(tasks))
    return p


def test_convert(tmp_path: Path) -> None:
    out = tmp_path / "labels"
    rep = convert_ls_export(_export(tmp_path), out, CLASSES, CFG, decode=fake_decode)
    assert rep.photos == 1 and rep.regions == {"hold": 2, "volume": 1}
    labels = read_labels(out / "cave-left" / "IMG_0001.txt")
    assert [i.cls_id for i in labels] == [0, 1, 0]
    # brush box x 20..60 of 200 -> normalised 0.1..~0.3
    assert labels[0].polygon[:, 0].min() == pytest.approx(0.1, abs=0.01)
    # polygon points are percent
    assert np.allclose(labels[1].polygon[0], [0.5, 0.5])
    side = json.loads((out / "cave-left" / "IMG_0001.json").read_text())
    assert side == [
        {"cls": "hold", "colour": "red", "chalked": True},
        {"cls": "volume", "colour": None, "chalked": None},
        {"cls": "hold", "colour": "pink", "chalked": False},
    ]
    assert len(rep.skipped_tasks) == 2


def test_unknown_colour_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="teal"):
        convert_ls_export(_export(tmp_path, "teal"), tmp_path / "l", CLASSES, CFG, fake_decode)


@pytest.mark.parametrize(
    ("ref", "key"),
    [
        ("/data/local-files/?d=raw/cave/IMG_1.jpg", ("cave", "IMG_1.jpg")),
        ("/data/local-files/?d=raw%2Fcave%2FIMG%201.jpg", ("cave", "IMG 1.jpg")),
        ("C:\\x\\data\\basecamp\\raw\\prow\\a.png", ("prow", "a.png")),
        ("/data/upload/1/abc.jpg", None),
    ],
)
def test_photo_key(ref: str, key: tuple[str, str] | None) -> None:
    assert photo_key(ref) == key


def test_sdk_decoder_roundtrip() -> None:
    sdk = pytest.importorskip("label_studio_sdk.converter.brush")
    from climb_beta.data.ls_export import sdk_rle_decoder

    m = np.zeros((7, 9), dtype=np.uint8)
    m[2:5, 3:7] = 255
    back = sdk_rle_decoder(sdk.mask2rle(m), 7, 9)
    assert np.array_equal(back, m > 0)


def test_cli(tmp_path: Path) -> None:
    mod = load_script("labelling/export_to_yolo.py")
    assert mod.main([str(tmp_path / "missing.json")]) == 2
