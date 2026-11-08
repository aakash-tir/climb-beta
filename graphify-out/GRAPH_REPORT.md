# Graph Report - climb  (2026-11-08)

## Corpus Check
- 35 files · ~17,280 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 280 nodes · 401 edges · 27 communities (21 shown, 6 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 56 edges (avg confidence: 0.78)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c301cdc3`
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

## God Nodes (most connected - your core abstractions)
1. `wall()` - 15 edges
2. `ColourConfig` - 14 edges
3. `classify_hold()` - 13 edges
4. `draw_hold()` - 13 edges
5. `parse_colour_config()` - 11 edges
6. `climb-beta` - 11 edges
7. `climb-beta — Plan` - 11 edges
8. `chalk()` - 10 edges
9. `Design System` - 10 edges
10. `pixel_labels()` - 9 edges

## Surprising Connections (you probably didn't know these)
- `test_pixel_labels_cover_hue_circle()` --calls--> `pixel_labels()`  [INFERRED]
  tests/test_colour_voting.py → src/climb_beta/colour/rules.py
- `test_gains_are_clipped_and_black_image_is_identity()` --calls--> `grey_world_gains()`  [INFERRED]
  tests/test_white_balance.py → src/climb_beta/colour/white_balance.py
- `test_repo_colour_config_has_the_ten_brief_colours()` --calls--> `load_colour_config()`  [INFERRED]
  tests/test_config.py → src/climb_beta/config.py
- `test_repo_classes_are_hold_volume_tape_in_order()` --calls--> `load_classes()`  [INFERRED]
  tests/test_config.py → src/climb_beta/config.py
- `test_detection_geometry()` --calls--> `Detection`  [INFERRED]
  tests/test_types.py → src/climb_beta/types.py

## Import Cycles
- None detected.

## Communities (27 total, 6 thin omitted)

### Community 0 - "parse_colour_config"
Cohesion: 0.19
Nodes (18): Path, Colour, ConfigError, load_classes(), load_colour_config(), parse_colour_config(), Any, Load and validate `configs/colours.yaml` and `configs/classes.yaml`. (+10 more)

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
Cohesion: 0.10
Nodes (22): bool_, classify_pixels(), ColourResult, _first_in_family(), HoldPixels, pixel_labels(), NDArray, Rule-based hold colour from the pixels inside a mask.  Pipeline for one hold ( (+14 more)

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
Cohesion: 0.14
Nodes (28): Image, classify_hold(), hold_pixels(), ImageBGR, Mask, Colour of the hold under `mask` in a (white-balanced) BGR image., chalk(), draw_hold() (+20 more)

### Community 22 - "2026-11-08.md"
Cohesion: 0.22
Nodes (8): 2026-11-08, Add chalk-aware per-pixel colour family voting (#4), Add grey-world white balance with wall reference (#3), Add mask utilities (#2), Expanded the plan and scaffolded climb-beta, .gitattributes and this log's first entry (#31), Initial commit and repo creation, Synthetic hold images for tests (#1)

### Community 23 - "masks.py"
Cohesion: 0.11
Nodes (30): ArrayLike, float32, FloatArray, _bbox(), denormalise(), dilate(), distance_to(), edge_ring() (+22 more)

### Community 24 - "test_masks.py"
Cohesion: 0.21
Nodes (6): disk(), ndarray, test_dilate_grows_and_zero_is_copy(), test_edge_ring_is_inside_and_thin(), test_iou_matrix_matches_pairwise_and_skips_far_pairs(), test_polygon_roundtrip()

### Community 26 - "grey_world"
Cohesion: 0.20
Nodes (16): slice, apply_gains(), grey_world(), grey_world_gains(), ImageBGR, Mask, Grey-world white balance.  The grey-world assumption says the average of a scene, Per-channel (B, G, R) gains that make the reference pixels' mean neutral.      P (+8 more)

## Knowledge Gaps
- **80 isolated node(s):** `climb-beta`, `Tech stack`, `Conventions`, `Git workflow (required)`, `Issues, PRs and CI (required)` (+75 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `classify_hold()` connect `chalk` to `Detection`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Why does `ColourConfig` connect `Detection` to `parse_colour_config`, `chalk`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `wall()` (e.g. with `test_chalked_blue_stays_blue()` and `test_fully_chalked_or_empty_is_unknown_without_white_rule()`) actually correct?**
  _`wall()` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `ColourConfig` (e.g. with `ColourResult` and `HoldPixels`) actually correct?**
  _`ColourConfig` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `classify_hold()` (e.g. with `test_chalked_blue_stays_blue()` and `test_fully_chalked_or_empty_is_unknown_without_white_rule()`) actually correct?**
  _`classify_hold()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `draw_hold()` (e.g. with `test_chalked_blue_stays_blue()` and `test_fully_chalked_or_empty_is_unknown_without_white_rule()`) actually correct?**
  _`draw_hold()` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `parse_colour_config()` (e.g. with `test_bad_hue_range_rejected()` and `test_duplicate_colour_rejected()`) actually correct?**
  _`parse_colour_config()` has 3 INFERRED edges - model-reasoned connections that need verification._