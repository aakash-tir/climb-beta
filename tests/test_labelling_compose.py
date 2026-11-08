"""Static checks on the labelling stack (CI can't run Docker or a GPU)."""

import yaml
from scripts import ROOT

COMPOSE = ROOT / "labelling" / "docker-compose.yml"
DOCKERFILE = ROOT / "labelling" / "sam2-backend" / "Dockerfile"


def test_compose_wires_label_studio_and_gpu_sam2() -> None:
    c = yaml.safe_load(COMPOSE.read_text())
    ls, sam = c["services"]["label-studio"], c["services"]["sam2"]
    assert ls["environment"]["LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT"] == "/data/basecamp"
    assert "../data/basecamp:/data/basecamp:ro" in ls["volumes"]  # photos read-only
    assert sam["environment"]["LABEL_STUDIO_URL"] == "http://label-studio:8080"
    assert sam["environment"]["DEVICE"] == "cuda"
    gpu = sam["deploy"]["resources"]["reservations"]["devices"][0]
    assert gpu["driver"] == "nvidia" and "gpu" in gpu["capabilities"]


def test_local_state_dirs_are_gitignored() -> None:
    ignore = (ROOT / ".gitignore").read_text()
    assert "labelling/.ls-data/" in ignore and "labelling/.sam2-models/" in ignore


def test_backend_image_targets_blackwell() -> None:
    text = DOCKERFILE.read_text()
    assert "cuda12.8" in text or "cuda13" in text
    assert "12.0" in text.split("TORCH_CUDA_ARCH_LIST=", 1)[1].splitlines()[0]
    assert "ML_BACKEND_SHA=" in text  # upstream pinned
