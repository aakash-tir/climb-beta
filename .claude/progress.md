# Progress

## 2026-11-09: first Basecamp photos; external-data plan

The owner took the first ~20 Basecamp wall photos (more each session), so #62 can start.
Planned extra detector data in `docs/plans/external-training-data.md` (#67):
**public outline datasets first, YouTube frames only as a gated, private pilot.**
Val and test stay Basecamp-only, and external data is train-only and outline-only.

### New issues
- M2, ready: #68 source manifest + label scopes (do this first), #71 cross-source dedupe
- M2, after #68: #69 outline-only out of colour data + ignore regions, #70 publishing guards
- M2, needs-decision: #72 ClimbInst (the owner checks its licence)
- M4: #73 two-stage training (holdlike pretrain → Basecamp fine-tune)
- Blocked on the first detector (#63): #74 YouTube pilot go/no-go, then #75 frame
  extractor (M2) and #76 outline-only labelling config (M3)

## 2026-11-08: Phase 1 code-complete; waiting on data

All of M0–M8's code is merged through green PRs (#30–#61, plus this docs PR): colour rules, data
pipeline, labelling stack, detector training, colour classifier and eval, route grouping,
pipeline, exit-criteria check, overlay, Gradio app. 206 tests in CI (no torch), plus 4
`ml` smoke tests that pass locally on the RTX 5070 Ti (SAM 2.1, a 1-epoch YOLO11 train,
detector inference, classifier train + predict). The SAM 2 Label Studio backend image
was built and verified on the GPU (`logs/2026-11-08.md`).

**Nothing is measured yet: there is no Basecamp data.** The exit criteria are unknown.

### Blocked on the owner
- #12: pin the Roboflow project/version (check task type + licence in a browser)
- #8: confirm Basecamp's current hold colour set (`configs/colours.yaml`)
- #62: photograph and label the first walls (≥ 3 test walls, ≥ 10 test routes)

### Then, in order
- #63: train yolo11n (and s if needed), record metrics
- #36: re-tune pink/red on real crops
- #64: routes.yaml for the test walls, then run `eval/check_exit_criteria.py`

Phase 2 (animated beta) starts only when the exit check exits 0.
