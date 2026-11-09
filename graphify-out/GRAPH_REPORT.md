# Graph Report - docs-external-data  (2026-11-09)

## Corpus Check
- 106 files · ~49,423 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 917 nodes · 1735 edges · 58 communities (46 shown, 12 thin omitted)
- Extraction: 75% EXTRACTED · 25% INFERRED · 0% AMBIGUOUS · INFERRED: 427 edges (avg confidence: 0.76)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6f00b497`
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
- detect.py
- Runbook: labelling Basecamp photos
- test_train_detector.py
- __init__.py
- schema.py
- _dataset
- preprocess
- run
- test_labelling_compose.py
- __init__.py
- run
- colour_detections
- Detection
- group.py
- main
- group_routes
- group_routes
- Runbook: deploy the demo to Hugging Face Spaces
- build_space.py
- External training data: public datasets vs YouTube frames
- draw_route
- colour_detections
- match_masks
- 2026-11-09

## God Nodes (most connected - your core abstractions)
1. `Detection` - 37 edges
2. `2026-11-08` - 34 edges
3. `ColourConfig` - 27 edges
4. `wall()` - 27 edges
5. `load_script()` - 25 edges
6. `classify_hold()` - 24 edges
7. `evaluate()` - 24 edges
8. `draw_hold()` - 24 edges
9. `run()` - 21 edges
10. `group_routes()` - 19 edges

## Surprising Connections (you probably didn't know these)
- `test_pixel_labels_cover_hue_circle()` --calls--> `pixel_labels()`  [INFERRED]
  tests/test_colour_voting.py → src/climb_beta/colour/rules.py
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

## Communities (58 total, 12 thin omitted)

### Community 0 - "parse_colour_config"
Cohesion: 0.07
Nodes (40): main(), Label each hold's colour in a photo with the rule-based colour step.  Usage:, main(), Cut a white-balanced, background-masked crop of every labelled hold.  Usage:, main(), Convert a Roboflow `coco-segmentation` export to a YOLO-seg dataset.  Usage:, main(), Check every Phase 1 exit criterion on the held-out test walls. Exit 0 only if al (+32 more)

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
Cohesion: 0.25
Nodes (7): climb-beta, Data and licences, Layout, Phase 1 exit criteria, Quick start, The two-step design, Workflow: photo to exit criteria

### Community 9 - "Datasets and labelling tools (researched 2026-11-08)"
Cohesion: 0.29
Nodes (6): Datasets and labelling tools (researched 2026-11-08), Labelling: Label Studio + SAM 2 ML backend, Our data: Basecamp Climbing photos, Public data: Roboflow "Climbing Holds and Volumes", Sources, Update 2026-11-09: more outline sources, and YouTube frames

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

### Community 17 - "progress.md"
Cohesion: 0.29
Nodes (6): 2026-11-08: Phase 1 code-complete; waiting on data, 2026-11-09: first Basecamp photos; external-data plan, Blocked on the owner, New issues, Progress, Then, in order

### Community 21 - "chalk"
Cohesion: 0.06
Nodes (66): Image, slice, classify_hold(), hold_pixels(), ImageBGR, Mask, Colour of the hold under `mask` in a (white-balanced) BGR image.      White rule, apply_gains() (+58 more)

### Community 22 - "2026-11-08.md"
Cohesion: 0.06
Nodes (34): 2026-11-08, Add Basecamp photo layout and split-by-wall (#13), Add chalk-aware per-pixel colour family voting (#4), Add COCO-segmentation to YOLO-seg converter (#9), Add colour/classify_rules.py CLI (#7), Add colour eval with per-colour confusion matrix (#22), Add detection metrics: mask matching, hold recall, mask mAP50 (#26), Add detector inference wrapper returning Detection masks (#19) (+26 more)

### Community 23 - "masks.py"
Cohesion: 0.09
Nodes (32): _bbox(), denormalise(), dilate(), distance_to(), edge_ring(), erode(), iou_matrix(), _kernel() (+24 more)

### Community 24 - "test_masks.py"
Cohesion: 0.21
Nodes (6): disk(), ndarray, test_dilate_grows_and_zero_is_copy(), test_edge_ring_is_inside_and_thin(), test_iou_matrix_matches_pairwise_and_skips_far_pairs(), test_polygon_roundtrip()

### Community 26 - "roboflow.py"
Cohesion: 0.13
Nodes (22): CaptureFixture, _load_dotenv(), main(), Download the pinned Roboflow Universe dataset (CC BY 4.0) as coco-segmentation., api_key(), download(), load_source(), parse_source() (+14 more)

### Community 27 - "Detection"
Cohesion: 0.13
Nodes (31): cmd_assign(), cmd_build(), main(), Assign Basecamp walls to train/val/test and build the YOLO-seg dataset.  Usage:, Namespace, assign_walls(), build_dataset(), BuildReport (+23 more)

### Community 28 - "load_script"
Cohesion: 0.14
Nodes (15): build_ui(), Any, climb-beta demo: upload a wall photo, pick a colour, see that route highlighted., RGB, default_detector_factory(), DemoService, _downscale(), Logic behind the Gradio demo: photo + colour -> highlighted route + summary.  Ke (+7 more)

### Community 30 - "convert_export"
Cohesion: 0.05
Nodes (62): BoxesXYXY, Counter, best_polygon(), BoxOnly, ConversionReport, convert_export(), convert_split(), default_class_for() (+54 more)

### Community 31 - "sam_masks.py"
Cohesion: 0.14
Nodes (22): main(), Push/pull data/basecamp/{raw,labels,exports} to/from a PRIVATE Hugging Face data, _api(), ensure_private(), HFSyncError, pull(), push(), Any (+14 more)

### Community 32 - "convert_ls_export"
Cohesion: 0.13
Nodes (10): average_precision(), ClassStats, DetectionAccumulator, DetectionReport, ImageMatch, Detection metrics on masks: greedy IoU matching, recall, VOC all-point AP50.  Ex, Feed (predictions, ground truth) image by image; read the report at the end., Matching for one image and one class. (+2 more)

### Community 34 - "detect.py"
Cohesion: 0.15
Nodes (14): Detector, ArrayLike, Path, Run the YOLO11-seg detector and return full-resolution `Detection` masks.  Ultra, Build Detections from per-instance pixel polygons (original image coords)., A local path, or `hf://<user>/<repo>/<file>` downloaded from the HF Hub., Ultralytics YOLO11-seg wrapper (needs the `ml` extra)., resolve_weights() (+6 more)

### Community 35 - "Runbook: labelling Basecamp photos"
Cohesion: 0.20
Nodes (9): 0. Prerequisites, 1. Put photos in place, 2. Start, 3. Create the project, 4. Label (per photo), 5. Export → training data, Runbook: labelling Basecamp photos, Stop / reset (+1 more)

### Community 36 - "test_train_detector.py"
Cohesion: 0.14
Nodes (25): load_train_config(), merge_datasets(), parse_train_config(), Any, Path, ValueError, Detector training config: load/validate, and merge several YOLO-seg datasets.  T, Write one Ultralytics data yaml that trains on every dataset's train split. (+17 more)

### Community 39 - "_dataset"
Cohesion: 0.17
Nodes (14): check_no_wall_leakage(), evaluate(), ExitReport, LeakageError, load_routes_gt(), Any, ColourMethod, Mask (+6 more)

### Community 40 - "preprocess"
Cohesion: 0.11
Nodes (21): augment(), load_split(), main(), Any, Path, Train the hold-colour crop classifier (timm MobileNetV3-Large or ResNet18).  Usa, Flips, 90-degree rotations and mild brightness. No hue/saturation changes., build_model() (+13 more)

### Community 41 - "run"
Cohesion: 0.18
Nodes (12): DetectorLike, Protocol, ClassifierLike, PipelineResult, Any, ColourMethod, ImageBGR, Protocol (+4 more)

### Community 44 - "run"
Cohesion: 0.09
Nodes (28): ModuleType, FakeDetector, Mask, Returns fixed masks, as a perfect colour-blind detector would., load_script(), Load a top-level CLI script (e.g. colour/classify_rules.py) as a module for test, _crops(), Path (+20 more)

### Community 45 - "colour_detections"
Cohesion: 0.18
Nodes (17): bool_, classify_pixels(), ColourResult, _first_in_family(), HoldPixels, pixel_labels(), NDArray, Rule-based hold colour from the pixels inside a mask.  Pipeline for one hold (al (+9 more)

### Community 46 - "Detection"
Cohesion: 0.15
Nodes (9): ImageBGR, Detection, Core data types shared by detector, colour, route, eval and app., One detector instance: a mask and a class (hold, volume or tape)., (x, y) centroid of the mask in pixels., (x0, y0, x1, y1), inclusive-exclusive., test_detection_geometry(), test_empty_detection_is_safe() (+1 more)

### Community 47 - "group.py"
Cohesion: 0.17
Nodes (10): FakeClassifier, ImageBGR, Test doubles for the detector and the crop classifier., A 600x800 wall: a 5-hold red route with start tape, a 4-hold blue route, warm li, wall_scene(), Path, test_classifier_method_overrides_rules(), test_find_route_cli() (+2 more)

### Community 48 - "main"
Cohesion: 0.08
Nodes (39): _as_json(), main(), Any, Print a per-colour confusion matrix for the rules and (optionally) the classifie, main(), Find the route of a chosen colour in a wall photo (detector + colour + route)., CropRecord, extract_crop() (+31 more)

### Community 49 - "group_routes"
Cohesion: 0.15
Nodes (12): _bbox(), _box_gap(), _gap(), load_route_config(), Mask, Path, Group same-colour holds into routes; tape near a hold marks it as a start.  Hold, The route the user means by a colour: the one with start tape, else the largest. (+4 more)

### Community 50 - "group_routes"
Cohesion: 0.32
Nodes (11): group_routes(), _UnionFind, hold(), ladder(), tape(), test_named_route_prefers_the_taped_route_over_the_larger(), test_no_holds_of_colour(), test_scale_invariance() (+3 more)

### Community 51 - "Runbook: deploy the demo to Hugging Face Spaces"
Cohesion: 0.33
Nodes (5): 1. Publish the detector weights, 2. Build the Space folder, 3. Create and push the Space, Check, Runbook: deploy the demo to Hugging Face Spaces

### Community 52 - "build_space.py"
Cohesion: 0.50
Nodes (4): build(), main(), Path, Assemble a self-contained Hugging Face Space folder (Gradio, CPU Basic).  Usage:

### Community 53 - "External training data: public datasets vs YouTube frames"
Cohesion: 0.18
Nodes (10): Comparison, Dataset schema: a source manifest per built dataset, External training data: public datasets vs YouTube frames, Issues, Question, Recommendation: public datasets now, YouTube frames only as a gated pilot, Rights and privacy, Sources (+2 more)

### Community 54 - "draw_route"
Cohesion: 0.27
Nodes (8): draw_route(), hex_to_bgr(), ImageBGR, Draw a chosen route on the photo: everything else dimmed, route holds outlined,, Return a copy with the route highlighted. With no route, the whole photo is dimm, test_hex_to_bgr(), test_no_route_dims_everything(), test_route_pixels_kept_rest_dimmed_start_marked()

### Community 55 - "colour_detections"
Cohesion: 0.32
Nodes (7): colour_detections(), ImageBGR, ndarray, Colour every hold in a photo: wall-referenced white balance, then the rules., Pixels outside every detection: the wall, used as the white-balance reference., Set `.colour`/`.colour_conf` on every hold detection (in place).      Returns th, wall_mask()

### Community 56 - "match_masks"
Cohesion: 0.48
Nodes (6): match_masks(), Greedy matching: highest-scoring prediction first, to its best unmatched GT., box(), test_accumulator_recall_map_and_class_separation(), test_greedy_matching_highest_score_wins(), test_iou_threshold()

## Knowledge Gaps
- **132 isolated node(s):** `climb-beta`, `Tech stack`, `Conventions`, `Git workflow (required)`, `Issues, PRs and CI (required)` (+127 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Detection` connect `Detection` to `convert_ls_export`, `detect.py`, `run`, `run`, `group.py`, `group_routes`, `group_routes`, `draw_route`, `colour_detections`, `match_masks`, `convert_export`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Why does `evaluate()` connect `_dataset` to `parse_colour_config`, `convert_ls_export`, `run`, `run`, `colour_detections`, `main`, `chalk`, `masks.py`, `convert_export`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Why does `ColourConfig` connect `colour_detections` to `parse_colour_config`, `Detection`, `_dataset`, `run`, `chalk`, `colour_detections`, `load_script`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Are the 17 inferred relationships involving `Detection` (e.g. with `YoloInstance` and `Detector`) actually correct?**
  _`Detection` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `ColourConfig` (e.g. with `ColourResult` and `HoldPixels`) actually correct?**
  _`ColourConfig` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `wall()` (e.g. with `wall_scene()` and `_scene()`) actually correct?**
  _`wall()` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `load_script()` (e.g. with `test_cli_labels_holds_and_skips_tape()` and `test_cli_missing_image()`) actually correct?**
  _`load_script()` has 23 INFERRED edges - model-reasoned connections that need verification._