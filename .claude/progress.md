# Progress

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
