"""Push/pull data/basecamp/{raw,labels,exports} to/from a PRIVATE Hugging Face dataset.

Usage:
    uv sync --extra data
    python data/sync_hf.py push [-m "added cave walls"]
    python data/sync_hf.py pull

Needs HF_TOKEN (write access) and HF_DATASET_REPO (<user>/<name>) in .env.
Refuses to upload to a public repo.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from climb_beta.data.hf_sync import HFSyncError, pull, push, settings

BASECAMP = Path(__file__).resolve().parent / "basecamp"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("cmd", choices=["push", "pull"])
    ap.add_argument("--dir", type=Path, default=BASECAMP)
    ap.add_argument("-m", "--message", default="")
    args = ap.parse_args(argv)
    try:
        from dotenv import load_dotenv

        load_dotenv(BASECAMP.parent.parent / ".env")
    except ImportError:
        pass
    try:
        token, repo = settings()
        if args.cmd == "push":
            push(args.dir, repo, token, message=args.message)
        else:
            pull(args.dir, repo, token)
    except HFSyncError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    print(f"{args.cmd} ok: {repo}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
