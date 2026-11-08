# climb-beta

Phase 1 of a climbing beta app for one gym (Basecamp Climbing, Toronto). A colour-blind
YOLO11-seg detector finds `hold`/`volume`/`tape` masks. A separate colour step labels
each hold's colour from its mask (rules first, then a timm crop classifier), and a route
step groups same-colour holds and marks tape-adjacent holds as starts. There's no
animation or 3D: Phase 2 waits until the exit criteria in `plan.md` pass.

See `@.claude/project-context.md` for the full architecture and known gaps, and
`plan.md` for scope, stack decisions and milestones.

## Tech stack
- Python 3.11, **uv** (lockfile `uv.lock`); package `climb_beta` in `src/`
- Core deps: numpy, opencv-python-headless, pyyaml, pillow (the only ones CI installs)
- Extras: `ml` (torch + torchvision from the **cu128** index, ultralytics, timm), `data`
  (roboflow, python-dotenv), `label` (label-studio-sdk), `app` (gradio)
- Detector: Ultralytics YOLO11-seg (`yolo11n-seg` default, `yolo11s-seg` option)
- Labelling: Label Studio + SAM 2 ML backend under Docker (CUDA-only; local RTX 5070 Ti)
- Demo: Gradio, packaged for Hugging Face Spaces CPU Basic
- Licence: AGPL-3.0-or-later (follows Ultralytics). **The repo is public.**

## Conventions
- **Logic lives in `src/climb_beta/`.** The top-level `data/`, `labelling/`, `train/`,
  `colour/`, `route/`, `eval/`, `app/` folders hold thin CLIs (argparse, `main()`),
  configs and docs that call into the package. Never put logic only in a script.
- **The colour list and every threshold** live in `configs/colours.yaml`; classes in
  `configs/classes.yaml`. No hard-coded colour names or thresholds in code.
- Images are **BGR uint8** (OpenCV) inside the package. Masks are **bool HxW**. Use
  `climb_beta.types.Detection`.
- Heavy imports (`torch`, `ultralytics`, `timm`, `gradio`, `roboflow`) are **lazy**,
  inside functions, so the core package and the tests import without the extras.
- **Testing:** pytest under `tests/`. Tests that need the `ml` extra are marked
  `@pytest.mark.ml` and skipped by default (run them with `uv run pytest -m ml`).
  Use synthetic images for colour and route tests.
- **Full local gate** (CI runs the same):
  `uv run ruff check . && uv run ruff format --check . && uv run mypy && uv run pytest`
- mypy is strict on `src/`. Line length is 100.
- **Splits are by wall.** Never write code that could put photos of one wall in two splits.
- **No personal information in committed files:** no names, emails, home paths
  (`C:\Users\...`), or tokens. The repo is public. Use `.env` for secrets, and refer to
  people by role ("the owner").
- Git identity for this repo is the GitHub noreply address (set in local git config).

## Git workflow (required)
This repo has a GitHub remote, so `main` is protected:
- **Never commit directly to `main`** and never merge into it locally. All changes
  land on a branch and reach `main` only through a GitHub pull request.
- Enforced locally by `.claude/hooks/protect-main.sh` (wired as a PreToolUse hook in
  `.claude/settings.json`), which denies `git commit`/`git merge`/`git push` against
  `main`. Server side, GitHub branch protection requires a PR (see
  `.claude/rules/issue-workflow.md` for its status).
- Workflow: branch → commit → push the branch → open a PR → merge the PR → pull `main`.

## Issues, PRs and CI (required)
- **One issue = one thing:** a single base, one PR in size. Milestones (`M0`…`M8`)
  mirror the `plan.md` milestones and each holds several issues.
- **One PR per issue.** Branch `<type>/<issue#>-<slug>`, PR body starts `Closes #n`.
- **Never merge unless every CI check is green**, verified with
  `gh pr checks <pr> --watch`. Merge with `gh pr merge <pr> --squash --delete-branch`.
- Out-of-scope bugs found mid-branch become **new issues**, not fixes in the branch.
- The work loop is in `.claude/rules/issue-workflow.md` and is followed in every dev session.
- `docs/future.md` holds only *unscheduled* ideas. Once scheduled into a milestone,
  an item becomes an issue and leaves `future.md`.

## CI (required)
CI is lean on GitHub Actions minutes: workflows run on pull requests only (nothing on
the merge to `main`), each only when its own files change, and docs-only PRs (`docs/`,
`logs/`, `graphify-out/`, `*.md`) run none. Never merge a PR with a red or pending
check; a docs-only PR with no checks may merge. Don't add a `push: main` trigger or a
separate follow-up PR for docs or the graph: each costs a CI run.

## Before every PR merge (required)
Two artifacts must be kept current, together, **in the same PR**:
1. **Knowledge graph** — once the code is final, run `graphify update .` and commit
   the refreshed `graphify-out/` to the PR. This is the only refresh: there are no
   graphify git hooks.
2. **Architecture diagram** — update `docs/architecture/architecture-diagram.html`
   whenever the merged PR changed the architecture: components, stages,
   data stores/collections, external services, flows, schedules, or
   retention rules. Use the `architecture-diagram` skill's MANUAL
   workflow (hand-placed layout per its design system) and verify the
   render with a headless-browser screenshot before committing —
   auto-generated output is a draft scaffold only. Docs-only or purely
   cosmetic merges don't need a diagram update, but say so in the
   changelog entry.

Both artifacts may be empty or absent on a brand-new project. The first merge that
introduces real structure is the one that creates them.

## Backlog (required)
All future work — bugs, known gaps, feature ideas, scaling items — is recorded in
`docs/future.md` (dated bullet under the matching section). When you find or defer an
issue, add it there; when one is COMPLETE, remove it — `logs/` and the PR history are
the record of finished work (no Done section).

## Where things belong (required)
- `.claude/` — everything Claude reads: `CLAUDE.md`, `project-context.md`,
  `progress.md`, `rules/`, project agents and skills, settings and hooks.
- `docs/` — everything a person reads: `architecture/`, `future.md`, `plans/`,
  `research/`, `runbooks/`, `history/`.
- `logs/` — the dated record (below).
- The repo root stays clean: only `CLAUDE.md`, `README.md`, `plan.md`, and the
  language's required root files.

If Claude must load it to work correctly it goes in `.claude/`; if a person reads it to
understand or operate the project it goes in `docs/`. When both are true, the full
version lives in `docs/` and `.claude/CLAUDE.md` points at it.

## Change log (required)
Every day that content is added, there is exactly **one** log file: `logs/YYYY-MM-DD.md`.
Check whether today's file exists; create it if missing, append to it otherwise. Never a
file per change, never one growing log. A day with no changes has no file.

Each entry is a `##` heading naming what was done, followed by:
**What we did** · **The reason** (root cause, for fixes) · **How it was solved**.

Write the reasoning, not the diff — git already has the code. For a fix, include the
evidence that identified the root cause (traceback, version pin, timeline). Say
explicitly when a change was docs-only or cosmetic and needed no diagram update.

## Don't commit secrets
Keep `.env`, credentials, and tokens gitignored. Never hardcode API keys in source.
