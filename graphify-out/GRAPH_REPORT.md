# Graph Report - climb  (2026-11-08)

## Corpus Check
- 74 files · ~32,204 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 622 nodes · 1081 edges · 39 communities (29 shown, 10 thin omitted)
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 231 edges (avg confidence: 0.78)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6dd1770b`
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

## God Nodes (most connected - your core abstractions)
1. `classify_hold()` - 22 edges
2. `2026-11-08` - 22 edges
3. `ColourConfig` - 20 edges
4. `wall()` - 20 edges
5. `convert_export()` - 17 edges
6. `draw_hold()` - 17 edges
7. `Detection` - 16 edges
8. `YoloInstance` - 14 edges
9. `load_script()` - 13 edges
10. `_dataset()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `colour_detections()`  [INFERRED]
  colour/classify_rules.py → src/climb_beta/colour/batch.py
- `main()` --calls--> `load_classes()`  [INFERRED]
  colour/classify_rules.py → src/climb_beta/config.py
- `main()` --calls--> `load_colour_config()`  [INFERRED]
  colour/classify_rules.py → src/climb_beta/config.py
- `main()` --calls--> `convert_export()`  [INFERRED]
  data/convert_roboflow.py → src/climb_beta/data/coco_to_yolo.py
- `main()` --calls--> `sam_segmenter()`  [INFERRED]
  data/convert_roboflow.py → src/climb_beta/data/sam_masks.py

## Import Cycles
- None detected.

## Communities (39 total, 10 thin omitted)

### Community 0 - "parse_colour_config"
Cohesion: 0.08
Nodes (37): Label each hold's colour in a photo with the rule-based colour step.  Usage:, main(), Convert a Roboflow `coco-segmentation` export to a YOLO-seg dataset.  Usage:, main(), Convert a Label Studio JSON export into data/basecamp/labels/<wall>/<photo>.{txt, main(), Regenerate labelling/label_config.xml from configs/colours.yaml and configs/clas, Colour (+29 more)

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
Cohesion: 0.17
Nodes (18): bool_, classify_pixels(), ColourResult, _first_in_family(), HoldPixels, pixel_labels(), NDArray, Rule-based hold colour from the pixels inside a mask.  Pipeline for one hold (al (+10 more)

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
Nodes (61): Image, slice, classify_hold(), hold_pixels(), ImageBGR, Mask, Colour of the hold under `mask` in a (white-balanced) BGR image.      White rule, apply_gains() (+53 more)

### Community 22 - "2026-11-08.md"
Cohesion: 0.09
Nodes (22): 2026-11-08, Add Basecamp photo layout and split-by-wall (#13), Add chalk-aware per-pixel colour family voting (#4), Add COCO-segmentation to YOLO-seg converter (#9), Add colour/classify_rules.py CLI (#7), Add detector inference wrapper returning Detection masks (#19), Add docker-compose for Label Studio + SAM 2 backend and labelling runbook (#17), Add grey-world white balance with wall reference (#3) (+14 more)

### Community 23 - "masks.py"
Cohesion: 0.12
Nodes (28): float32, _bbox(), denormalise(), dilate(), distance_to(), edge_ring(), erode(), iou_matrix() (+20 more)

### Community 24 - "test_masks.py"
Cohesion: 0.21
Nodes (6): disk(), ndarray, test_dilate_grows_and_zero_is_copy(), test_edge_ring_is_inside_and_thin(), test_iou_matrix_matches_pairwise_and_skips_far_pairs(), test_polygon_roundtrip()

### Community 26 - "roboflow.py"
Cohesion: 0.13
Nodes (22): CaptureFixture, _load_dotenv(), main(), Download the pinned Roboflow Universe dataset (CC BY 4.0) as coco-segmentation., MonkeyPatch, api_key(), download(), load_source() (+14 more)

### Community 27 - "Detection"
Cohesion: 0.09
Nodes (35): cmd_assign(), cmd_build(), main(), Assign Basecamp walls to train/val/test and build the YOLO-seg dataset.  Usage:, ModuleType, Namespace, assign_walls(), build_dataset() (+27 more)

### Community 28 - "_scene"
Cohesion: 0.07
Nodes (31): Protocol, colour_detections(), ImageBGR, ndarray, Colour every hold in a photo: wall-referenced white balance, then the rules., Pixels outside every detection: the wall, used as the white-balance reference., Set `.colour`/`.colour_conf` on every hold detection (in place).      Returns th, wall_mask() (+23 more)

### Community 30 - "convert_export"
Cohesion: 0.09
Nodes (42): main(), Counter, best_polygon(), BoxOnly, ConversionReport, convert_export(), convert_split(), default_class_for() (+34 more)

### Community 31 - "sam_masks.py"
Cohesion: 0.14
Nodes (22): main(), Push/pull data/basecamp/{raw,labels,exports} to/from a PRIVATE Hugging Face data, RuntimeError, _api(), ensure_private(), HFSyncError, pull(), push() (+14 more)

### Community 32 - "convert_ls_export"
Cohesion: 0.12
Nodes (26): RleDecoder, convert_ls_export(), ExportReport, _latest_annotation(), photo_key(), Any, Mask, Path (+18 more)

### Community 34 - "sam_masks.py"
Cohesion: 0.12
Nodes (21): BoxesXYXY, box_fill_segmenter(), load_pseudo_masks(), BoxSegmenter, ImageBGR, Mask, Path, Turn box-only annotations into masks by prompting SAM with each box.  Masks made (+13 more)

### Community 35 - "Runbook: labelling Basecamp photos"
Cohesion: 0.20
Nodes (9): 0. Prerequisites, 1. Put photos in place, 2. Start, 3. Create the project, 4. Label (per photo), 5. Export → training data, Runbook: labelling Basecamp photos, Stop / reset (+1 more)

### Community 36 - "test_train_detector.py"
Cohesion: 0.10
Nodes (32): ImageBGR, Path, Image read/write with the package's types (BGR uint8)., Read an image as BGR uint8, or None if it can't be read. Handles non-ASCII paths, read_bgr(), write_bgr(), load_train_config(), merge_datasets() (+24 more)

## Knowledge Gaps
- **103 isolated node(s):** `climb-beta`, `Tech stack`, `Conventions`, `Git workflow (required)`, `Issues, PRs and CI (required)` (+98 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Detection` connect `_scene` to `convert_export`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Why does `ColourConfig` connect `Detection` to `parse_colour_config`, `convert_ls_export`, `_scene`, `chalk`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Why does `_dataset()` connect `test_train_detector.py` to `chalk`, `convert_export`, `masks.py`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `classify_hold()` (e.g. with `colour_detections()` and `edge_ring()`) actually correct?**
  _`classify_hold()` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `ColourConfig` (e.g. with `ColourResult` and `HoldPixels`) actually correct?**
  _`ColourConfig` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `wall()` (e.g. with `_scene()` and `colour_of()`) actually correct?**
  _`wall()` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `convert_export()` (e.g. with `main()` and `write_pseudo_masks()`) actually correct?**
  _`convert_export()` has 7 INFERRED edges - model-reasoned connections that need verification._