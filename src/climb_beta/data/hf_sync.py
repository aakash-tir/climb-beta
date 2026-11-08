"""Sync the private Basecamp photos/labels with a **private** Hugging Face dataset repo.

Owner decision (2026-11-08): gym photos never go into git and never become public
without the gym's permission. Every push checks that the target repo is private
and refuses otherwise.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

TOKEN_ENV = "HF_TOKEN"
REPO_ENV = "HF_DATASET_REPO"
SYNC_PATTERNS = ["raw/**", "labels/**", "exports/**"]


class HFSyncError(RuntimeError):
    pass


def settings(env: Mapping[str, str] | None = None) -> tuple[str, str]:
    env = os.environ if env is None else env
    token, repo = env.get(TOKEN_ENV, "").strip(), env.get(REPO_ENV, "").strip()
    if not token or not repo:
        raise HFSyncError(f"set {TOKEN_ENV} and {REPO_ENV} in .env (see .env.example)")
    if repo.count("/") != 1:
        raise HFSyncError(f"{REPO_ENV} must look like '<user>/<name>', got {repo!r}")
    return token, repo


def _api(token: str) -> Any:
    from huggingface_hub import HfApi  # lazy: `data` extra

    return HfApi(token=token)


def ensure_private(api: Any, repo: str) -> None:
    """Create the dataset repo as private if missing; refuse if it exists and is public."""
    api.create_repo(repo, repo_type="dataset", private=True, exist_ok=True)
    info = api.repo_info(repo, repo_type="dataset")
    if not getattr(info, "private", False):
        raise HFSyncError(
            f"dataset repo {repo} is PUBLIC. Refusing to upload gym photos. "
            "Make it private on huggingface.co first."
        )


def push(local: Path, repo: str, token: str, api: Any | None = None, message: str = "") -> None:
    api = api or _api(token)
    ensure_private(api, repo)
    api.upload_folder(
        folder_path=str(local),
        repo_id=repo,
        repo_type="dataset",
        allow_patterns=SYNC_PATTERNS,
        commit_message=message or "Sync Basecamp photos and labels",
    )


def pull(local: Path, repo: str, token: str, api: Any | None = None) -> None:
    api = api or _api(token)
    info = api.repo_info(repo, repo_type="dataset")
    if not getattr(info, "private", False):
        raise HFSyncError(f"dataset repo {repo} is public; expected a private repo")
    api.snapshot_download(
        repo_id=repo, repo_type="dataset", local_dir=str(local), allow_patterns=SYNC_PATTERNS
    )
