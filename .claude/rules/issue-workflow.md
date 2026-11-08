# Issue → PR → CI workflow (required for all development)

Every change to this repo, whether a feature, fix, chore, or docs, is driven by a
GitHub issue and lands through its own PR, merged only when every CI check is
green. Follow this loop in every development session. There's nothing to invoke:
these rules are how work gets done here.

## Invariants
- **One issue = one thing.** A single base, one problem or deliverable, one PR in
  size. If an issue bundles several things, split it into child issues (and close
  the parent with links) before writing code.
- **Milestones mirror `plan.md` phases** (`M0`, `M1`, …). Each holds several issues.
- **One PR per issue.** Branch `<type>/<issue#>-<slug>` (types: feat, fix, chore,
  docs, test, refactor). The PR body starts with `Closes #<n>`. Never fold a second
  issue in.
- **Never merge unless every CI check is green**, verified in-session with
  `gh pr checks <pr> --watch`. Pending, failing, cancelled, or "it passed locally"
  all mean don't merge. CI is path-filtered: only workflows whose files changed run,
  so "every check" means every check that started. A docs-only PR (`docs/`, `logs/`,
  `graphify-out/`, `*.md`) starts none and may merge once the local gate passed.
  GitHub branch protection on `main` requires a PR. CI can't be a *required* check
  because the workflow is path-filtered, so this rule is the CI gate.
- **Never commit to `main`.** Create the branch in its own command *before* any
  commit. The protect-main hook checks the branch at the moment a command starts.
- **Out-of-scope findings become new issues, not fixes.** A bug or gap that's
  unrelated to the current issue, or too big for its PR, gets
  `gh issue create` (type label, milestone if obvious, evidence, acceptance
  criteria) and a mention under "Follow-ups filed" in the PR. Keep going on the
  current issue.
- **No green, no next.** If CI can't be made green after a few honest attempts,
  or the fix needs a decision from the owner, stop: label the issue
  `needs-decision` or `blocked`, comment why, and report. Never leave a red PR
  merged.
- **No personal information** in anything committed (public repo): no names, emails,
  home-directory paths, tokens.

## The loop
1. **Sync:** `git checkout main && git pull --ff-only`. The working tree must be clean.
2. **Pick:** `gh issue list --state open --json number,title,milestone,labels`. Take
   the lowest milestone, then the lowest number, skipping `blocked` /
   `needs-decision`, unless the user named an issue or milestone. Read it fully
   with `gh issue view <n> --comments`.
3. **Branch:** `git checkout -b <type>/<n>-<slug>` (its own command).
4. **Solve: code ⇄ test** until the full local gate passes:
   `uv run ruff check . && uv run ruff format --check . && uv run mypy && uv run pytest`.
   Write tests that can fail. Add today's `logs/` entry (what / why / how), and
   update the architecture diagram if the architecture changed. Once the code is
   final, run `graphify update .` and commit `graphify-out/` **in this PR** (no
   follow-up PR: each extra PR costs a CI run).
5. **PR:** commit `<type>: <summary> (#<n>)`, `git push -u origin HEAD`,
   `gh pr create` using the PR template (`Closes #<n>` first).
6. **CI ⇄ fix:** `gh pr checks <pr> --watch`. If anything is red, run
   `gh run view <run> --log-failed`, fix on the same branch, push, and watch again.
7. **Merge on all-green only:** `gh pr merge <pr> --squash --delete-branch`, then
   `git checkout main && git pull --ff-only`, and confirm the issue closed. (The
   graph and diagram were already updated in the PR, step 4.)
8. **Next issue.** Repeat until the agreed scope (an issue, a milestone, or all
   open issues) is done, then report: issues closed (with PR links), issues
   filed, anything stopped and why.

## Writing issues
- **Title:** imperative, one thing ("Add <component> <behaviour>").
- **Body:** Context · Scope (In / Out) · Acceptance criteria (checkboxes) · Notes /
  Evidence. Use the templates in `.github/ISSUE_TEMPLATE/`.
- **Labels:** one type (`feature`, `bug`, `chore`, `docs`, `test`), plus `area:*`
  where useful, plus `needs-decision` / `blocked` when relevant.
- **Backlog vs issues:** `docs/future.md` holds only unscheduled ideas. When an
  idea is scheduled into a milestone, it becomes an issue and is removed from
  `future.md`.
