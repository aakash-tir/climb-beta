from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from climb_beta.data.hf_sync import HFSyncError, pull, push, settings


@dataclass
class Info:
    private: bool


class FakeApi:
    def __init__(self, private: bool = True) -> None:
        self.private = private
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def create_repo(self, repo: str, **kw: Any) -> None:
        self.calls.append(("create_repo", {"repo": repo, **kw}))

    def repo_info(self, repo: str, **kw: Any) -> Info:
        return Info(self.private)

    def upload_folder(self, **kw: Any) -> None:
        self.calls.append(("upload_folder", kw))

    def snapshot_download(self, **kw: Any) -> None:
        self.calls.append(("snapshot_download", kw))


def test_push_always_creates_private_and_uploads_only_data(tmp_path: Path) -> None:
    api = FakeApi()
    push(tmp_path, "me/basecamp", "tok", api=api)
    create = dict(api.calls)["create_repo"]
    assert create["private"] is True and create["repo_type"] == "dataset"
    up = dict(api.calls)["upload_folder"]
    assert up["repo_type"] == "dataset" and "raw/**" in up["allow_patterns"]


def test_push_refuses_public_repo(tmp_path: Path) -> None:
    api = FakeApi(private=False)
    with pytest.raises(HFSyncError, match="PUBLIC"):
        push(tmp_path, "me/basecamp", "tok", api=api)
    assert "upload_folder" not in dict(api.calls)


def test_pull_refuses_public_and_downloads_private(tmp_path: Path) -> None:
    with pytest.raises(HFSyncError):
        pull(tmp_path, "me/x", "tok", api=FakeApi(private=False))
    api = FakeApi()
    pull(tmp_path, "me/x", "tok", api=api)
    assert dict(api.calls)["snapshot_download"]["repo_type"] == "dataset"


@pytest.mark.parametrize(
    "env", [{}, {"HF_TOKEN": "t"}, {"HF_TOKEN": "t", "HF_DATASET_REPO": "noslash"}]
)
def test_settings_validation(env: dict[str, str]) -> None:
    with pytest.raises(HFSyncError):
        settings(env)


def test_settings_ok() -> None:
    assert settings({"HF_TOKEN": " t ", "HF_DATASET_REPO": "me/b"}) == ("t", "me/b")
