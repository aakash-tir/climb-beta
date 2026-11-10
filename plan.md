# climb-beta — Plan

## What this is
Phase 1 of a climbing "beta" app: from a phone photo of a wall at **Basecamp Climbing
(Toronto)**, find every hold, volume and start-tape, label each hold's colour, and
highlight the route of a chosen colour. It's open source (AGPL-3.0, required by
Ultralytics). The design has two steps on purpose. A colour-blind YOLO11-seg model finds
the holds. A separate colour step reads each hold's colour from its mask, using
explainable rules first and a small crop classifier second. **No animation or 3D in this
phase.** Phase 2 (animated beta) starts only once every exit criterion below passes.

## Scope
**v1 (building now):**
- `data/`: Roboflow "Climbing Holds and Volumes" download (CC BY 4.0) and conversion to
  YOLO-seg (polygons, or a SAM mask from a box when only boxes exist); a Basecamp photo
  layout split **by wall**.
- `labelling/`: Label Studio + SAM 2 ML backend under docker-compose, with a labelling
  config for hold/volume/tape masks and a per-hold colour and chalked flag, generated
  from `configs/colours.yaml`.
- `train/`: `train_detector.py` fine-tunes `yolo11n-seg`/`yolo11s-seg` and logs mAP, plus
  its config files.
- `colour/` (logic in `src/climb_beta/colour/`): grey-world white balance, per-pixel
  Lab/HSV voting that drops chalk, pink vs red by saturation and lightness, the
  white-hold edge-ring rule, a timm crop classifier, and a per-colour confusion-matrix
  eval.
- `route/`: groups holds of the chosen colour into routes and finds tape near holds to
  mark the start.
- `app/`: Gradio demo (upload a photo, pick a colour, see that route highlighted),
  CPU-only and ready for Hugging Face Spaces.
- `eval/`: one script that checks every exit criterion on the held-out test walls.
- pytest suite, including the colour rules on synthetic images (chalked red, pink, white).

**Deferred** (also in `docs/future.md`): Phase 2 animated beta and 3D; gyms other than
Basecamp; video and live camera; on-device mobile app; route grade estimation.

**Non-goals:** animation or pose estimation in Phase 1; detecting holds by colour;
publishing Basecamp photos without the gym's permission.

## Phase 1 exit criteria (gate for Phase 2)
Measured by `eval/check_exit_criteria.py` on held-out **test walls** only. No
pseudo-masked images, and no wall that appears in train or val.

| Criterion | Target |
|---|---|
| Hold recall (GT holds matched at mask IoU ≥ 0.5) | **≥ 95%** |
| Mask mAP50 (hold/volume/tape) | **≥ 0.85** |
| Colour accuracy, all holds | **≥ 95%** |
| Colour accuracy, holds whose GT is pink or red | **≥ 90%** |
| Colour accuracy, holds flagged chalked | **≥ 90%** |
| Named route (hold colour + grade) correct within 1 hold (missed + extra ≤ 1), complete routes only | **≥ 9/10 test routes** |

## Tech stack
| Layer | Choice | Why | Rejected |
|---|---|---|---|
| Language / env | Python 3.11, uv | set by the plan; uv gives a lockfile and fast CI | pip + venv (no lockfile), conda (slow, heavy) |
| Detector | Ultralytics YOLO11-seg (n default, s option) | instance masks, fast on CPU, easy fine-tuning; AGPL fits our licence | Mask R-CNN/Detectron2 (heavy, Windows pain); SAM 2 alone (no classes, too slow on CPU) |
| Colour (rules) | OpenCV HSV + Lab, numpy | explainable, works with zero labels, tunable in YAML | per-image k-means (doesn't match the gym's named colours, chalk forms its own cluster); hue-only thresholds (fail on pink vs red) |
| Colour (learned) | timm MobileNetV3-Large (ResNet18 alt) on mask crops | tiny, CPU-fast, pretrained | large ViT (overkill, slow on Spaces) |
| Labelling | Label Studio + SAM 2 ML backend (Docker, local GPU) | click-to-mask; per-region colour choices | CVAT (heavier stack); Roboflow annotate (would upload gym photos to a third party) |
| Gym data storage | gitignored locally + private HF dataset repo | photos aren't ours to publish yet | committing them (public repo) |
| Tests / lint / types | pytest, ruff, mypy | idiomatic, and fast without torch | unittest |
| Demo | Gradio on HF Spaces CPU Basic | free CPU hosting, one-file app | Streamlit (no Spaces advantage); own server (cost) |
| CI | GitHub Actions, one PR-only path-filtered workflow | lean minutes | push-to-main runs |

## Architecture
```
photo ──► white balance (grey-world on wall pixels)
      ──► Detector (YOLO11-seg, colour-blind): masks + class {hold, volume, tape}
      ──► Colour step, per hold mask:
            rules: drop chalk px → per-pixel family vote → pink/red split → white edge-ring
            classifier (optional): timm on the masked crop, used when it beats rules on val
      ──► Route step: holds of chosen colour → spatial clusters → tape within reach ⇒ start
      ──► Overlay (app) / metrics (eval)
```
Code lives in the `src/climb_beta/` package (`types`, `config`, `colour/`, `route/`,
`data/`, `metrics/`, `detect.py`, `pipeline.py`, `overlay.py`). The top-level folders the
plan names (`data/`, `labelling/`, `train/`, `colour/`, `route/`, `app/`, `eval/`) hold
the runnable scripts, configs and docs, and each script is a thin CLI over the package.
Shared config: `configs/colours.yaml` (colour list and thresholds) and
`configs/classes.yaml` (detector classes).

## The hard part
**Colour under chalk, and pink vs red.** Chalk turns a red hold's grip surface white,
and averaging that gives pink. The approach (details in `docs/research/colour-rules.md`):
drop chalk pixels, decide pink vs red on the *most saturated* quantile (chalk only lowers
saturation), and catch white holds with an edge-ring check so the chalk filter doesn't
delete them. The eval reports chalked holds and pink/red holds separately, so a good
overall number can't hide this. The second hard part is **leakage**: photos of the same
wall share holds, so splits are made by wall and the split script refuses any overlap.

## External dependencies
| Service | Needed for | Cost / limits | Account |
|---|---|---|---|
| Roboflow Universe | public pretraining data | free account + API key; dataset CC BY 4.0 (attribution required) | needed, `ROBOFLOW_API_KEY` in `.env` |
| Hugging Face Hub | private dataset for gym photos; Space for the demo | free; CPU Basic Space is 2 vCPU/16 GB, but free-tier quota 403s have been reported since mid-2026 | needed, `HF_TOKEN` in `.env` |
| Ultralytics weights | `yolo11n-seg.pt`, `yolo11s-seg.pt`, `sam2.1_b.pt` | free download (AGPL) | none |
| Label Studio + ML backend | labelling | free, self-hosted, CUDA-only backend (local RTX 5070 Ti) | local admin user only |

## Testing strategy
- **Unit (CI, no torch):** colour rules on synthetic images (chalked red → red, pink →
  pink, white → white, red is never pink), grey-world, the wall split's disjointness,
  COCO→YOLO-seg conversion, LS export conversion, route grouping and tape-start, metric
  maths (mask IoU, AP50, recall, route tolerance), Label Studio config generation.
- **Smoke (local, `-m ml`):** detector, classifier and app wiring with tiny inputs, only
  when the `ml` extra is installed. These are skipped in CI.
- **Gate:** `uv run ruff check . && uv run ruff format --check . && uv run mypy && uv run pytest`.
  CI runs the same on every PR that touches code. The exit criteria are a separate,
  data-driven gate run with `eval/check_exit_criteria.py`.

## Milestones
- **M0 Scaffold:** package, configs, CI, rules, first tests. *Runnable:* `uv run pytest`.
- **M1 Colour rules:** white balance, chalk-aware voting, pink/red, white ring, synthetic
  tests. *Runnable:* `python colour/classify_rules.py img.jpg masks/`.
- **M2 Data pipeline:** Roboflow download and conversion, Basecamp layout, split by wall,
  LS export → YOLO-seg + colour sidecar. *Runnable:* a YOLO-seg `dataset.yaml`.
- **M3 Labelling:** docker-compose for Label Studio + SAM 2, generated labelling config,
  runbook. *Runnable:* `docker compose up` and click-to-mask.
- **M4 Detector:** `train_detector.py` + n/s configs, mAP logging, inference wrapper.
  *Runnable:* trained weights + metrics JSON.
- **M5 Colour classifier + colour eval:** crop extraction, timm training, confusion
  matrix. *Runnable:* `colour/eval_colour.py` prints the matrix.
- **M6 Route:** grouping and tape start. *Runnable:* route JSON for a photo.
- **M7 Exit-criteria eval:** one script, PASS/FAIL per criterion.
- **M8 Demo:** Gradio app + Spaces packaging. *Runnable:* `python app/app.py`.

## Open questions
- **Which Roboflow project/version to pin?** The name matches several projects, one of
  them box-only, and Roboflow blocks scripted page reads. The owner should confirm in a
  browser. Tracked as a `needs-decision` issue; the converter handles either.
- **Basecamp permission** to publish photos or a public dataset (owner to ask the gym).
  Until then, photos stay private.
- **Which colours Basecamp uses right now.** `configs/colours.yaml` starts with the 10 in
  the brief. The owner checks against the current set.
