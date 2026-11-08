# Graph Report - climb  (2026-11-08)

## Corpus Check
- 25 files · ~13,155 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 161 nodes · 179 edges · 21 communities (16 shown, 5 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 10 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

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

## God Nodes (most connected - your core abstractions)
1. `parse_colour_config()` - 11 edges
2. `climb-beta` - 11 edges
3. `climb-beta — Plan` - 11 edges
4. `Design System` - 10 edges
5. `ConfigError` - 9 edges
6. `Detection` - 7 edges
7. `Node` - 6 edges
8. `layout()` - 6 edges
9. `ColourConfig` - 6 edges
10. `climb-beta — project context` - 6 edges

## Surprising Connections (you probably didn't know these)
- `test_repo_colour_config_has_the_ten_brief_colours()` --calls--> `load_colour_config()`  [INFERRED]
  tests/test_config.py → src/climb_beta/config.py
- `test_repo_classes_are_hold_volume_tape_in_order()` --calls--> `load_classes()`  [INFERRED]
  tests/test_config.py → src/climb_beta/config.py
- `test_detection_geometry()` --calls--> `Detection`  [INFERRED]
  tests/test_types.py → src/climb_beta/types.py
- `test_empty_detection_is_safe()` --calls--> `Detection`  [INFERRED]
  tests/test_types.py → src/climb_beta/types.py
- `test_bad_hue_range_rejected()` --indirect_call--> `ConfigError`  [INFERRED]
  tests/test_config.py → src/climb_beta/config.py

## Import Cycles
- None detected.

## Communities (21 total, 5 thin omitted)

### Community 0 - "parse_colour_config"
Cohesion: 0.16
Nodes (20): Path, Colour, ColourConfig, ConfigError, load_classes(), load_colour_config(), parse_colour_config(), Any (+12 more)

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
Cohesion: 0.20
Nodes (7): Detection, Core data types shared by detector, colour, route, eval and app., One detector instance: a mask and a class (hold, volume or tape)., (x, y) centroid of the mask in pixels., (x0, y0, x1, y1), inclusive-exclusive., test_detection_geometry(), test_empty_detection_is_safe()

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

## Knowledge Gaps
- **73 isolated node(s):** `climb-beta`, `Tech stack`, `Conventions`, `Git workflow (required)`, `Issues, PRs and CI (required)` (+68 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Are the 3 inferred relationships involving `parse_colour_config()` (e.g. with `test_bad_hue_range_rejected()` and `test_duplicate_colour_rejected()`) actually correct?**
  _`parse_colour_config()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `ConfigError` (e.g. with `test_bad_hue_range_rejected()` and `test_duplicate_colour_rejected()`) actually correct?**
  _`ConfigError` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `climb-beta`, `Tech stack`, `Conventions` to the rest of the system?**
  _73 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Design System` be split into smaller, more focused modules?**
  _Cohesion score 0.125 - nodes in this community are weakly interconnected._