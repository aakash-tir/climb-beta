# climb-beta

Phase 1 of a climbing "beta" app: **hold detection and route colour for one gym,
Basecamp Climbing (Toronto).** Upload a photo of a wall, pick a colour, and see that
route's holds highlighted, with the start holds marked by their tape.

There's no animation or 3D yet. That's Phase 2, and it waits until the Phase 1 exit
criteria below pass.

## The two-step design

```
photo → [1] Detector (YOLO11-seg)          → masks: hold | volume | tape   (colour-blind)
      → [2] Colour step (per hold mask)    → red | pink | orange | … | grey
      → Route: holds of one colour, grouped; tape near a hold marks the start
```

1. **Detector: what is a hold?** A YOLO11-seg (Ultralytics) instance-segmentation model
   with three classes: `hold`, `volume` and `tape`. It is trained with heavy hue and
   saturation augmentation, so it **ignores colour** and learns shape, texture and
   shadow. That way, a hold that matches the wall colour still gets found.
2. **Colour: what colour is it?** A separate step labels each hold from the pixels inside
   its mask:
   - grey-world white balance (computed on wall pixels);
   - per-pixel HSV/Lab voting that **drops chalk pixels** (low saturation + high brightness);
   - **pink vs red decided by saturation and lightness, not hue**: chalk only lowers
     saturation, so the most saturated pixels show the pigment;
   - a **white** rule that also checks the hold's **edge ring**, so that white holds
     aren't thrown away as chalk;
   - then a small crop classifier (timm MobileNetV3 / ResNet18) trained on labelled crops.

Keeping the two apart means each can be measured and fixed on its own. A colour error
never costs a detection, and the detector never has to learn the gym's colour palette.
Rationale and rejected alternatives: [`docs/research/`](docs/research/).

## Phase 1 exit criteria

All are measured on **held-out test walls** by `eval/check_exit_criteria.py`. Photos are
split **by wall**, so no wall appears in both train and test.

| Criterion | Target |
|---|---|
| Hold recall (mask IoU ≥ 0.5) | ≥ 95% |
| Mask mAP50 | ≥ 0.85 |
| Colour accuracy, overall | ≥ 95% |
| Colour accuracy, pink vs red holds | ≥ 90% |
| Colour accuracy, chalked holds | ≥ 90% |
| Named route correct within 1 hold | 9/10 test routes |

**Phase 2 (animated beta) does not start until every row passes.**

## Layout

| Path | What |
|---|---|
| `src/climb_beta/` | the library: types, config, colour, route, data, metrics, detector wrapper, pipeline |
| `configs/` | `colours.yaml` (colour list + rule thresholds; edit here to add a colour), `classes.yaml` |
| `data/` | Roboflow download + YOLO-seg conversion; Basecamp photo layout and split by wall |
| `labelling/` | Label Studio + SAM 2 ML backend (docker-compose), labelling config |
| `train/` | `train_detector.py` and detector configs |
| `colour/` | rule-based colouring CLI, crop classifier training, per-colour confusion matrix |
| `route/` | route grouping CLI |
| `eval/` | exit-criteria check |
| `app/` | Gradio demo for Hugging Face Spaces (CPU) |
| `tests/` | pytest suite (synthetic images, no GPU needed) |

## Quick start

```bash
uv sync                          # core + dev tools (numpy, OpenCV); enough for the tests
uv run pytest                    # the test suite
uv sync --extra ml --extra data  # + torch (CUDA 12.8), ultralytics, timm, roboflow
```

## Workflow: photo to exit criteria

```bash
uv sync --extra ml --extra data --extra label --extra app

# 1. Public data (needs ROBOFLOW_API_KEY in .env, and the version pinned in data/roboflow.yaml)
python data/download_roboflow.py
python data/convert_roboflow.py data/roboflow/<slug> data/yolo/roboflow --sam-fallback

# 2. Our photos: data/basecamp/raw/<wall_id>/*.jpg, then label (docs/runbooks/labelling.md)
docker compose -f labelling/docker-compose.yml up -d --build
python labelling/export_to_yolo.py data/basecamp/exports/<export>.json
python data/split_by_wall.py assign     # whole walls -> train/val/test (never moves old walls)
python data/split_by_wall.py build      # -> data/yolo/basecamp
python data/sync_hf.py push             # private HF dataset

# 3. Detector (colour-blind)
python train/train_detector.py --config train/configs/yolo11n-seg.yaml

# 4. Colour: rules vs classifier on val walls
python colour/make_crops.py data/yolo/basecamp data/crops/basecamp
python colour/train_classifier.py data/crops/basecamp
python colour/eval_colour.py data/yolo/basecamp --split val \
    --classifier weights/colour-mobilenetv3_large_100.pt

# 5. Exit criteria on the held-out test walls (exit code 0 = Phase 2 may start)
python eval/check_exit_criteria.py --weights weights/detector-yolo11n-seg.pt

# 6. Try it
python route/find_route.py wall.jpg --colour red
CLIMB_DETECTOR_WEIGHTS=weights/detector-yolo11n-seg.pt python app/app.py
python app/build_space.py dist/space    # HF Space folder (docs/runbooks/deploy-space.md)
```

Debug the colour rules on one photo and its labels with
`python colour/classify_rules.py photo.jpg labels.txt --debug out.png`.

The full local gate (CI runs the same on every code PR):

```bash
uv run ruff check . && uv run ruff format --check . && uv run mypy && uv run pytest
```

Secrets go in `.env` (copy `.env.example`), which is gitignored.

## Data and licences

- Code: **AGPL-3.0-or-later** (see `LICENSE`). Ultralytics YOLO is AGPL-3.0.
- Public pretraining data: Roboflow Universe "Climbing Holds and Volumes", **CC BY 4.0**.
  Credit goes to the dataset's authors on Roboflow Universe. The exact project and
  version used are recorded in `data/roboflow.yaml`.
- Basecamp photos are **not** in this repo. They're kept privately until the gym agrees
  to publication.
