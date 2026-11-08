# Graph Report - climb  (2026-11-08)

## Corpus Check
- 99 files · ~45,088 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 860 nodes · 1650 edges · 44 communities (32 shown, 12 thin omitted)
- Extraction: 75% EXTRACTED · 25% INFERRED · 0% AMBIGUOUS · INFERRED: 407 edges (avg confidence: 0.76)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `50ecc8fe`
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
- load_script
- __init__.py
- convert_export
- sam_masks.py
- convert_ls_export
- README.md
- Runbook: labelling Basecamp photos
- test_train_detector.py
- __init__.py
- schema.py
- _dataset
- preprocess
- test_labelling_compose.py
- __init__.py
- run
- colour_detections

## God Nodes (most connected - your core abstractions)
1. `Detection` - 37 edges
2. `2026-11-08` - 32 edges
3. `wall()` - 27 edges
4. `ColourConfig` - 26 edges
5. `classify_hold()` - 24 edges
6. `evaluate()` - 24 edges
7. `draw_hold()` - 24 edges
8. `load_script()` - 23 edges
9. `run()` - 20 edges
10. `group_routes()` - 19 edges

## Surprising Connections (you probably didn't know these)
- `test_preprocess_rgb_order_and_shape()` --calls--> `preprocess()`  [INFERRED]
  tests/test_crop_classifier.py → src/climb_beta/colour/classifier.py
- `main()` --calls--> `colour_detections()`  [INFERRED]
  colour/classify_rules.py → src/climb_beta/colour/batch.py
- `main()` --calls--> `instances_to_detections()`  [INFERRED]
  colour/classify_rules.py → src/climb_beta/data/yolo.py
- `main()` --calls--> `read_labels()`  [INFERRED]
  colour/classify_rules.py → src/climb_beta/data/yolo.py
- `main()` --calls--> `CropClassifier`  [INFERRED]
  colour/eval_colour.py → src/climb_beta/colour/classifier.py

## Import Cycles
- None detected.

## Communities (44 total, 12 thin omitted)

### Community 0 - "parse_colour_config"
Cohesion: 0.05
Nodes (52): main(), Label each hold's colour in a photo with the rule-based colour step.  Usage:, _as_json(), main(), Any, Print a per-colour confusion matrix for the rules and (optionally) the classifie, main(), Cut a white-balanced, background-masked crop of every labelled hold.  Usage: (+44 more)

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
Cohesion: 0.12
Nodes (26): RleDecoder, convert_ls_export(), ExportReport, _latest_annotation(), photo_key(), Any, Mask, Path (+18 more)

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
Cohesion: 0.07
Nodes (51): Image, slice, apply_gains(), grey_world(), grey_world_gains(), ImageBGR, Mask, Grey-world white balance.  The grey-world assumption says the average of a scene (+43 more)

### Community 22 - "2026-11-08.md"
Cohesion: 0.06
Nodes (32): 2026-11-08, Add Basecamp photo layout and split-by-wall (#13), Add chalk-aware per-pixel colour family voting (#4), Add COCO-segmentation to YOLO-seg converter (#9), Add colour/classify_rules.py CLI (#7), Add colour eval with per-colour confusion matrix (#22), Add detection metrics: mask matching, hold recall, mask mAP50 (#26), Add detector inference wrapper returning Detection masks (#19) (+24 more)

### Community 23 - "masks.py"
Cohesion: 0.09
Nodes (34): instances_to_detections(), Rasterise label polygons into full-resolution Detection masks., _bbox(), denormalise(), dilate(), distance_to(), edge_ring(), erode() (+26 more)

### Community 24 - "test_masks.py"
Cohesion: 0.21
Nodes (6): disk(), ndarray, test_dilate_grows_and_zero_is_copy(), test_edge_ring_is_inside_and_thin(), test_iou_matrix_matches_pairwise_and_skips_far_pairs(), test_polygon_roundtrip()

### Community 26 - "roboflow.py"
Cohesion: 0.13
Nodes (22): CaptureFixture, _load_dotenv(), main(), Download the pinned Roboflow Universe dataset (CC BY 4.0) as coco-segmentation., MonkeyPatch, api_key(), download(), load_source() (+14 more)

### Community 27 - "Detection"
Cohesion: 0.13
Nodes (31): cmd_assign(), cmd_build(), main(), Assign Basecamp walls to train/val/test and build the YOLO-seg dataset.  Usage:, Namespace, assign_walls(), build_dataset(), BuildReport (+23 more)

### Community 28 - "load_script"
Cohesion: 0.07
Nodes (37): ModuleType, draw_route(), hex_to_bgr(), ImageBGR, Draw a chosen route on the photo: everything else dimmed, route holds outlined,, Return a copy with the route highlighted. With no route, the whole photo is dimm, FakeClassifier, FakeDetector (+29 more)

### Community 30 - "convert_export"
Cohesion: 0.06
Nodes (62): BoxesXYXY, Counter, best_polygon(), BoxOnly, ConversionReport, convert_export(), convert_split(), default_class_for() (+54 more)

### Community 31 - "sam_masks.py"
Cohesion: 0.14
Nodes (22): main(), Push/pull data/basecamp/{raw,labels,exports} to/from a PRIVATE Hugging Face data, _api(), ensure_private(), HFSyncError, pull(), push(), Any (+14 more)

### Community 32 - "convert_ls_export"
Cohesion: 0.05
Nodes (44): ImageBGR, average_precision(), ClassStats, DetectionAccumulator, DetectionReport, ImageMatch, match_masks(), Detection metrics on masks: greedy IoU matching, recall, VOC all-point AP50.  Ex (+36 more)

### Community 35 - "Runbook: labelling Basecamp photos"
Cohesion: 0.20
Nodes (9): 0. Prerequisites, 1. Put photos in place, 2. Start, 3. Create the project, 4. Label (per photo), 5. Export → training data, Runbook: labelling Basecamp photos, Stop / reset (+1 more)

### Community 36 - "test_train_detector.py"
Cohesion: 0.10
Nodes (27): load_train_config(), merge_datasets(), parse_train_config(), Any, Path, ValueError, Detector training config: load/validate, and merge several YOLO-seg datasets.  T, Write one Ultralytics data yaml that trains on every dataset's train split. (+19 more)

### Community 39 - "_dataset"
Cohesion: 0.11
Nodes (31): CropRecord, extract_crop(), iter_hold_crops(), iter_labelled_holds(), LabelledHold, ImageBGR, Mask, Path (+23 more)

### Community 40 - "preprocess"
Cohesion: 0.11
Nodes (20): augment(), load_split(), main(), Any, Path, Train the hold-colour crop classifier (timm MobileNetV3-Large or ResNet18).  Usa, Flips, 90-degree rotations and mild brightness. No hue/saturation changes., build_model() (+12 more)

### Community 44 - "run"
Cohesion: 0.06
Nodes (46): main(), Find the route of a chosen colour in a wall photo (detector + colour + route)., Detector, DetectorLike, ArrayLike, Path, Protocol, Run the YOLO11-seg detector and return full-resolution `Detection` masks.  Ultra (+38 more)

### Community 45 - "colour_detections"
Cohesion: 0.09
Nodes (37): bool_, colour_detections(), ImageBGR, ndarray, Colour every hold in a photo: wall-referenced white balance, then the rules., Pixels outside every detection: the wall, used as the white-balance reference., Set `.colour`/`.colour_conf` on every hold detection (in place).      Returns th, wall_mask() (+29 more)

## Knowledge Gaps
- **113 isolated node(s):** `climb-beta`, `Tech stack`, `Conventions`, `Git workflow (required)`, `Issues, PRs and CI (required)` (+108 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Detection` connect `convert_ls_export` to `run`, `colour_detections`, `masks.py`, `load_script`, `convert_export`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Why does `evaluate()` connect `run` to `parse_colour_config`, `convert_ls_export`, `_dataset`, `colour_detections`, `chalk`, `masks.py`, `load_script`, `convert_export`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Why does `ColourConfig` connect `colour_detections` to `parse_colour_config`, `run`, `Detection`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Are the 17 inferred relationships involving `Detection` (e.g. with `YoloInstance` and `Detector`) actually correct?**
  _`Detection` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `wall()` (e.g. with `wall_scene()` and `_scene()`) actually correct?**
  _`wall()` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `ColourConfig` (e.g. with `ColourResult` and `HoldPixels`) actually correct?**
  _`ColourConfig` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `classify_hold()` (e.g. with `main()` and `colour_detections()`) actually correct?**
  _`classify_hold()` has 16 INFERRED edges - model-reasoned connections that need verification._