# Graph Report - climb  (2026-11-08)

## Corpus Check
- 43 files · ~19,759 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 336 nodes · 538 edges · 30 communities (23 shown, 7 thin omitted)
- Extraction: 81% EXTRACTED · 19% INFERRED · 0% AMBIGUOUS · INFERRED: 100 edges (avg confidence: 0.78)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7d8836e5`
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
- grey_world
- Detection
- _scene
- __init__.py

## God Nodes (most connected - your core abstractions)
1. `classify_hold()` - 22 edges
2. `wall()` - 19 edges
3. `ColourConfig` - 16 edges
4. `draw_hold()` - 16 edges
5. `chalk()` - 13 edges
6. `parse_colour_config()` - 11 edges
7. `Detection` - 11 edges
8. `_scene()` - 11 edges
9. `climb-beta` - 11 edges
10. `2026-11-08` - 11 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `colour_detections()`  [INFERRED]
  colour/classify_rules.py → src/climb_beta/colour/batch.py
- `main()` --calls--> `load_classes()`  [INFERRED]
  colour/classify_rules.py → src/climb_beta/config.py
- `main()` --calls--> `load_colour_config()`  [INFERRED]
  colour/classify_rules.py → src/climb_beta/config.py
- `test_pixel_labels_cover_hue_circle()` --calls--> `pixel_labels()`  [INFERRED]
  tests/test_colour_voting.py → src/climb_beta/colour/rules.py
- `test_gains_are_clipped_and_black_image_is_identity()` --calls--> `grey_world_gains()`  [INFERRED]
  tests/test_white_balance.py → src/climb_beta/colour/white_balance.py

## Import Cycles
- None detected.

## Communities (30 total, 7 thin omitted)

### Community 0 - "parse_colour_config"
Cohesion: 0.17
Nodes (19): Label each hold's colour in a photo with the rule-based colour step.  Usage:, Colour, ConfigError, load_classes(), load_colour_config(), parse_colour_config(), Any, Path (+11 more)

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
Cohesion: 0.18
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
Cohesion: 0.10
Nodes (42): Image, classify_hold(), hold_pixels(), ImageBGR, Mask, Colour of the hold under `mask` in a (white-balanced) BGR image.      White rule, chalk(), draw_hold() (+34 more)

### Community 22 - "2026-11-08.md"
Cohesion: 0.17
Nodes (11): 2026-11-08, Add chalk-aware per-pixel colour family voting (#4), Add colour/classify_rules.py CLI (#7), Add grey-world white balance with wall reference (#3), Add mask utilities (#2), Add white-hold rule using the mask's edge ring (#6), Expanded the plan and scaffolded climb-beta, .gitattributes and this log's first entry (#31) (+3 more)

### Community 23 - "masks.py"
Cohesion: 0.11
Nodes (30): ArrayLike, float32, _bbox(), denormalise(), dilate(), distance_to(), edge_ring(), erode() (+22 more)

### Community 24 - "test_masks.py"
Cohesion: 0.21
Nodes (6): disk(), ndarray, test_dilate_grows_and_zero_is_copy(), test_edge_ring_is_inside_and_thin(), test_iou_matrix_matches_pairwise_and_skips_far_pairs(), test_polygon_roundtrip()

### Community 26 - "grey_world"
Cohesion: 0.21
Nodes (15): slice, apply_gains(), grey_world(), grey_world_gains(), ImageBGR, Mask, Grey-world white balance.  The grey-world assumption says the average of a scene, Per-channel (B, G, R) gains that make the reference pixels' mean neutral.      P (+7 more)

### Community 27 - "Detection"
Cohesion: 0.13
Nodes (14): colour_detections(), ImageBGR, ndarray, Colour every hold in a photo: wall-referenced white balance, then the rules., Pixels outside every detection: the wall, used as the white-balance reference., Set `.colour`/`.colour_conf` on every hold detection (in place).      Returns th, wall_mask(), Detection (+6 more)

### Community 28 - "_scene"
Cohesion: 0.17
Nodes (20): main(), ModuleType, format_label_line(), instances_to_detections(), parse_label_line(), FloatArray, Path, Read and write Ultralytics YOLO-seg label files.  One instance per line: `<class (+12 more)

## Knowledge Gaps
- **83 isolated node(s):** `climb-beta`, `Tech stack`, `Conventions`, `Git workflow (required)`, `Issues, PRs and CI (required)` (+78 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `classify_hold()` connect `chalk` to `Detection`, `Detection`, `masks.py`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Why does `colour_detections()` connect `Detection` to `Detection`, `grey_world`, `_scene`, `chalk`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Why does `ColourConfig` connect `Detection` to `parse_colour_config`, `Detection`, `chalk`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `classify_hold()` (e.g. with `colour_detections()` and `edge_ring()`) actually correct?**
  _`classify_hold()` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `wall()` (e.g. with `_scene()` and `colour_of()`) actually correct?**
  _`wall()` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `ColourConfig` (e.g. with `ColourResult` and `HoldPixels`) actually correct?**
  _`ColourConfig` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `draw_hold()` (e.g. with `_scene()` and `colour_of()`) actually correct?**
  _`draw_hold()` has 12 INFERRED edges - model-reasoned connections that need verification._