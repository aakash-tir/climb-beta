# Graph Report - climb  (2026-11-08)

## Corpus Check
- 91 files · ~38,628 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 777 nodes · 1448 edges · 48 communities (36 shown, 12 thin omitted)
- Extraction: 76% EXTRACTED · 24% INFERRED · 0% AMBIGUOUS · INFERRED: 346 edges (avg confidence: 0.77)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b78fd2ef`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- parse_colour_config
- generate_diagram.py
- Design System
- climb-beta
- climb-beta — Plan
- Detection
- climb-beta — project context
- Stack, training hardware and demo hosting (researched 2026-11-08)
- climb-beta
- Datasets and labelling tools (researched 2026-11-08)
- Prior art and approach (researched 2026-11-08)
- pull_request_template.md
- Issue → PR → CI workflow (required for all development)
- Backlog (unscheduled)
- Colour step: why rules first, and how they handle chalk (2026-11-08)
- protect-main.sh
- CLAUDE.md
- progress.md
- __init__.py
- climb-beta
- chalk
- 2026-11-08.md
- masks.py
- test_masks.py
- __init__.py
- roboflow.py
- Detection
- _scene
- __init__.py
- convert_export
- sam_masks.py
- convert_ls_export
- README.md
- sam_masks.py
- Runbook: labelling Basecamp photos
- test_train_detector.py
- __init__.py
- schema.py
- _dataset
- preprocess
- main
- test_labelling_compose.py
- __init__.py
- run
- colour_detections
- group_routes
- Detection

## God Nodes (most connected - your core abstractions)
1. `Detection` - 29 edges
2. `wall()` - 27 edges
3. `2026-11-08` - 27 edges
4. `draw_hold()` - 24 edges
5. `classify_hold()` - 23 edges
6. `ColourConfig` - 23 edges
7. `group_routes()` - 19 edges
8. `load_script()` - 19 edges
9. `run()` - 18 edges
10. `convert_export()` - 17 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `colour_detections()`  [INFERRED]
  colour/classify_rules.py → src/climb_beta/colour/batch.py
- `main()` --calls--> `load_classes()`  [INFERRED]
  colour/classify_rules.py → src/climb_beta/config.py
- `main()` --calls--> `load_colour_config()`  [INFERRED]
  colour/classify_rules.py → src/climb_beta/config.py
- `main()` --calls--> `CropClassifier`  [INFERRED]
  colour/eval_colour.py → src/climb_beta/colour/classifier.py
- `main()` --calls--> `extract_crop()`  [INFERRED]
  colour/eval_colour.py → src/climb_beta/colour/crops.py

## Import Cycles
- None detected.

## Communities (48 total, 12 thin omitted)

### Community 0 - "parse_colour_config"
Cohesion: 0.08
Nodes (38): main(), Cut a white-balanced, background-masked crop of every labelled hold.  Usage:, main(), Convert a Roboflow `coco-segmentation` export to a YOLO-seg dataset.  Usage:, main(), Convert a Label Studio JSON export into data/basecamp/labels/<wall>/<photo>.{txt, main(), Regenerate labelling/label_config.xml from configs/colours.yaml and configs/clas (+30 more)

### Community 1 - "generate_diagram.py"
Cohesion: 0.18
Nodes (14): assign_columns(), endpoint(), esc(), group_chain(), layout(), main(), Node, (cx, cy, left, right, top, bottom, column) for a node OR group id. (+6 more)

### Community 2 - "Design System"
Cohesion: 0.12
Nodes (15): Architecture Diagram Skill, Auto-layout scaffold (local extension v1.2), Color Palette, Component Box Pattern, Design System, Export Toolbar (built-in), Info Card Pattern, Layout Structure (+7 more)

### Community 3 - "climb-beta"
Cohesion: 0.17
Nodes (11): Backlog (required), Before every PR merge (required), Change log (required), CI (required), climb-beta, Conventions, Don't commit secrets, Git workflow (required) (+3 more)

### Community 4 - "climb-beta — Plan"
Cohesion: 0.17
Nodes (11): Architecture, climb-beta — Plan, External dependencies, Milestones, Open questions, Phase 1 exit criteria (gate for Phase 2), Scope, Tech stack (+3 more)

### Community 5 - "Detection"
Cohesion: 0.07
Nodes (47): bool_, RleDecoder, classify_pixels(), ColourResult, _first_in_family(), hold_pixels(), HoldPixels, pixel_labels() (+39 more)

### Community 6 - "climb-beta — project context"
Cohesion: 0.29
Nodes (6): Auth / secrets, climb-beta — project context, Data model, Goal, Known gaps, Pipeline

### Community 7 - "Stack, training hardware and demo hosting (researched 2026-11-08)"
Cohesion: 0.29
Nodes (6): Demo hosting: Hugging Face Spaces (Gradio, CPU Basic), Detector: Ultralytics YOLO11-seg, Package manager: uv, Python 3.11, Sources, Stack, training hardware and demo hosting (researched 2026-11-08), Training hardware

### Community 8 - "climb-beta"
Cohesion: 0.29
Nodes (6): climb-beta, Data and licences, Layout, Phase 1 exit criteria, Quick start, The two-step design

### Community 9 - "Datasets and labelling tools (researched 2026-11-08)"
Cohesion: 0.33
Nodes (5): Datasets and labelling tools (researched 2026-11-08), Labelling: Label Studio + SAM 2 ML backend, Our data: Basecamp Climbing photos, Public data: Roboflow "Climbing Holds and Volumes", Sources

### Community 10 - "Prior art and approach (researched 2026-11-08)"
Cohesion: 0.33
Nodes (5): Lessons we're taking, Prior art and approach (researched 2026-11-08), Question, Sources, What exists

### Community 11 - "pull_request_template.md"
Cohesion: 0.33
Nodes (5): Before merge, Follow-up issues filed, How it was tested, What changed, Why

### Community 12 - "Issue → PR → CI workflow (required for all development)"
Cohesion: 0.40
Nodes (4): Invariants, Issue → PR → CI workflow (required for all development), The loop, Writing issues

### Community 13 - "Backlog (unscheduled)"
Cohesion: 0.40
Nodes (4): Backlog (unscheduled), Data, Phase 2 and beyond, Reach

### Community 14 - "Colour step: why rules first, and how they handle chalk (2026-11-08)"
Cohesion: 0.40
Nodes (4): Colour step: why rules first, and how they handle chalk (2026-11-08), Decisions, Rejected, The hard part

### Community 21 - "chalk"
Cohesion: 0.09
Nodes (49): Image, slice, classify_hold(), Colour of the hold under `mask` in a (white-balanced) BGR image.      White rule, chalk(), draw_hold(), Mask, Synthetic wall photos for tests: grey wall, coloured holds, chalk, tinted light. (+41 more)

### Community 22 - "2026-11-08.md"
Cohesion: 0.07
Nodes (27): 2026-11-08, Add Basecamp photo layout and split-by-wall (#13), Add chalk-aware per-pixel colour family voting (#4), Add COCO-segmentation to YOLO-seg converter (#9), Add colour/classify_rules.py CLI (#7), Add colour eval with per-colour confusion matrix (#22), Add detector inference wrapper returning Detection masks (#19), Add docker-compose for Label Studio + SAM 2 backend and labelling runbook (#17) (+19 more)

### Community 23 - "masks.py"
Cohesion: 0.11
Nodes (30): _bbox(), denormalise(), dilate(), distance_to(), edge_ring(), erode(), iou_matrix(), _kernel() (+22 more)

### Community 24 - "test_masks.py"
Cohesion: 0.21
Nodes (6): disk(), ndarray, test_dilate_grows_and_zero_is_copy(), test_edge_ring_is_inside_and_thin(), test_iou_matrix_matches_pairwise_and_skips_far_pairs(), test_polygon_roundtrip()

### Community 26 - "roboflow.py"
Cohesion: 0.13
Nodes (22): CaptureFixture, _load_dotenv(), main(), Download the pinned Roboflow Universe dataset (CC BY 4.0) as coco-segmentation., MonkeyPatch, api_key(), download(), load_source() (+14 more)

### Community 27 - "Detection"
Cohesion: 0.13
Nodes (31): cmd_assign(), cmd_build(), main(), Assign Basecamp walls to train/val/test and build the YOLO-seg dataset.  Usage:, Namespace, assign_walls(), build_dataset(), BuildReport (+23 more)

### Community 28 - "_scene"
Cohesion: 0.13
Nodes (15): Detector, ArrayLike, ImageBGR, Path, Run the YOLO11-seg detector and return full-resolution `Detection` masks.  Ultra, Build Detections from per-instance pixel polygons (original image coords)., A local path, or `hf://<user>/<repo>/<file>` downloaded from the HF Hub., Ultralytics YOLO11-seg wrapper (needs the `ml` extra). (+7 more)

### Community 30 - "convert_export"
Cohesion: 0.05
Nodes (65): BoxesXYXY, main(), Label each hold's colour in a photo with the rule-based colour step.  Usage:, Counter, best_polygon(), BoxOnly, ConversionReport, convert_export() (+57 more)

### Community 31 - "sam_masks.py"
Cohesion: 0.14
Nodes (22): main(), Push/pull data/basecamp/{raw,labels,exports} to/from a PRIVATE Hugging Face data, RuntimeError, _api(), ensure_private(), HFSyncError, pull(), push() (+14 more)

### Community 32 - "convert_ls_export"
Cohesion: 0.14
Nodes (13): FakeClassifier, FakeDetector, ImageBGR, Mask, Test doubles for the detector and the crop classifier., Returns fixed masks, as a perfect colour-blind detector would., A 600x800 wall: a 5-hold red route with start tape, a 4-hold blue route, warm li, wall_scene() (+5 more)

### Community 34 - "sam_masks.py"
Cohesion: 0.16
Nodes (13): _bbox(), _box_gap(), _gap(), load_route_config(), Mask, Path, Group same-colour holds into routes; tape near a hold marks it as a start.  Hold, The route the user means by a colour: the one with start tape, else the largest. (+5 more)

### Community 35 - "Runbook: labelling Basecamp photos"
Cohesion: 0.20
Nodes (9): 0. Prerequisites, 1. Put photos in place, 2. Start, 3. Create the project, 4. Label (per photo), 5. Export → training data, Runbook: labelling Basecamp photos, Stop / reset (+1 more)

### Community 36 - "test_train_detector.py"
Cohesion: 0.14
Nodes (25): load_train_config(), merge_datasets(), parse_train_config(), Any, Path, ValueError, Detector training config: load/validate, and merge several YOLO-seg datasets.  T, Write one Ultralytics data yaml that trains on every dataset's train split. (+17 more)

### Community 39 - "_dataset"
Cohesion: 0.09
Nodes (34): ModuleType, CropRecord, extract_crop(), iter_hold_crops(), iter_labelled_holds(), LabelledHold, ImageBGR, Mask (+26 more)

### Community 40 - "preprocess"
Cohesion: 0.11
Nodes (21): augment(), load_split(), main(), Any, Path, Train the hold-colour crop classifier (timm MobileNetV3-Large or ResNet18).  Usa, Flips, 90-degree rotations and mild brightness. No hue/saturation changes., build_model() (+13 more)

### Community 41 - "main"
Cohesion: 0.22
Nodes (12): _as_json(), main(), Any, Print a per-colour confusion matrix for the rules and (optionally) the classifie, _acc(), colour_report(), ColourReport, format_report() (+4 more)

### Community 44 - "run"
Cohesion: 0.15
Nodes (13): ColourMethod, main(), Find the route of a chosen colour in a wall photo (detector + colour + route)., DetectorLike, Protocol, ClassifierLike, PipelineResult, Any (+5 more)

### Community 45 - "colour_detections"
Cohesion: 0.15
Nodes (17): colour_detections(), ImageBGR, ndarray, Colour every hold in a photo: wall-referenced white balance, then the rules., Pixels outside every detection: the wall, used as the white-balance reference., Set `.colour`/`.colour_conf` on every hold detection (in place).      Returns th, wall_mask(), apply_gains() (+9 more)

### Community 46 - "group_routes"
Cohesion: 0.32
Nodes (11): group_routes(), _UnionFind, hold(), ladder(), tape(), test_named_route_prefers_the_taped_route_over_the_larger(), test_no_holds_of_colour(), test_scale_invariance() (+3 more)

### Community 47 - "Detection"
Cohesion: 0.18
Nodes (8): Detection, Core data types shared by detector, colour, route, eval and app., One detector instance: a mask and a class (hold, volume or tape)., (x, y) centroid of the mask in pixels., (x0, y0, x1, y1), inclusive-exclusive., test_detection_geometry(), test_empty_detection_is_safe(), test_imageio_roundtrip_and_missing()

## Knowledge Gaps
- **108 isolated node(s):** `climb-beta`, `Tech stack`, `Conventions`, `Git workflow (required)`, `Issues, PRs and CI (required)` (+103 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Detection` connect `Detection` to `convert_ls_export`, `sam_masks.py`, `run`, `colour_detections`, `group_routes`, `_scene`, `convert_export`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Why does `ColourConfig` connect `Detection` to `parse_colour_config`, `chalk`, `run`, `colour_detections`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Why does `load_script()` connect `_dataset` to `parse_colour_config`, `convert_ls_export`, `test_train_detector.py`, `Detection`, `chalk`, `roboflow.py`, `Detection`, `convert_export`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `Detection` (e.g. with `YoloInstance` and `Detector`) actually correct?**
  _`Detection` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `wall()` (e.g. with `wall_scene()` and `_scene()`) actually correct?**
  _`wall()` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `draw_hold()` (e.g. with `wall_scene()` and `_scene()`) actually correct?**
  _`draw_hold()` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `classify_hold()` (e.g. with `main()` and `colour_detections()`) actually correct?**
  _`classify_hold()` has 15 INFERRED edges - model-reasoned connections that need verification._