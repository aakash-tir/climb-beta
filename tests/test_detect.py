from pathlib import Path

import numpy as np
import pytest

from climb_beta.detect import resolve_weights, results_to_detections


def test_results_to_detections_full_resolution_masks() -> None:
    polys = [
        np.array([[10, 10], [50, 10], [50, 40], [10, 40]], dtype=np.float32),
        np.array([[100, 60], [180, 60], [180, 90]], dtype=np.float32),
        np.array([[0, 0], [1, 0], [1, 1]], dtype=np.float32),  # too small: dropped
    ]
    dets = results_to_detections(
        polys, [0, 1, 0], [0.9, 0.5, 0.3], {0: "hold", 1: "volume"}, (100, 200)
    )
    assert [d.cls for d in dets] == ["hold", "volume"]
    assert dets[0].mask.shape == (100, 200)
    assert dets[0].bbox() == (10, 10, 51, 41)
    assert dets[1].score == pytest.approx(0.5)


def test_results_to_detections_empty() -> None:
    assert results_to_detections([], [], [], ["hold"], (10, 10)) == []


def test_resolve_weights(tmp_path: Path) -> None:
    w = tmp_path / "d.pt"
    w.write_bytes(b"x")
    assert resolve_weights(str(w)) == w
    with pytest.raises(FileNotFoundError):
        resolve_weights(str(tmp_path / "missing.pt"))
    with pytest.raises(ValueError, match="hf://"):
        resolve_weights("hf://only-user")


@pytest.mark.ml
def test_detector_smoke() -> None:  # pragma: no cover - needs ml extra + downloads weights
    from climb_beta.detect import Detector

    det = Detector("yolo11n-seg.pt", imgsz=320, conf=0.01)
    out = det.predict(np.full((240, 320, 3), 128, dtype=np.uint8))
    assert isinstance(out, list)
    assert all(d.mask.shape == (240, 320) for d in out)
