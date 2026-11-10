# climb-beta — project context

## Goal
From a phone photo of a Basecamp Climbing wall, produce: every hold/volume/tape mask, a
colour for each hold, and the route of a chosen colour with its start holds. Phase 1 is
"done" only when `eval/check_exit_criteria.py` passes every row of the exit-criteria
table in `plan.md` on the held-out test walls.

## Pipeline
1. **White balance**: `climb_beta.colour.white_balance.grey_world(img, ref_mask)`.
   Channel gains make the mean of the reference pixels neutral. The reference is the
   wall (outside all detector masks) when available, otherwise the whole image.
2. **Detect**: `climb_beta.detect.Detector` wraps Ultralytics YOLO11-seg and returns
   `list[Detection]` with full-resolution bool masks. The classes come from
   `configs/classes.yaml`. The detector is trained with `hsv_h=0.5, hsv_s=0.9` so it's
   colour-blind.
3. **Colour** (per detection of a class in `coloured_classes` in `configs/colours.yaml`:
   `hold` and `tape`). A tape detection's colour is the route's grade: at Basecamp a
   route is hold colour + the colour of its small tape diamonds (the grade circuit).
   The crop classifier only relabels holds; tape keeps the rule colour.
   - `climb_beta.colour.rules.classify_hold(img, mask, cfg)` returns a `ColourResult`
     (name, confidence, votes, debug). Steps: drop chalk pixels, give each remaining
     pixel a family vote, pick the majority family; if redpink, split pink vs red on the
     top-saturation quantile; if the mask is mostly chalk-like, apply the white
     edge-ring rule.
   - `climb_beta.colour.classifier` (needs `ml`): a timm model on a masked square crop.
     The pipeline uses it when it's configured and loaded.
4. **Route**: `climb_beta.route.group` clusters holds of the chosen colour by
   single-linkage on mask-to-mask gap (relative to median hold size). A hold whose
   dilated mask touches tape has a diamond. In each route the highest taped hold is the
   `finish` if it has one diamond and sits in the top `finish_top_frac` of the route;
   other taped holds are `starts` (Basecamp: two diamonds at the bottom). A route is
   `complete` only with both. A route's `grade` is the majority colour of its diamonds;
   a same-colour cluster whose diamonds show 2+ grades is split around them (nearest
   taped hold). `named_route(grade=None)` prefers the largest complete route.
   Grey/black (`shared_colours` in `configs/route.yaml`) are shared holds. A taped shared
   hold becomes a start of the nearest route with a finish above it and the same grade.
   The finish must be the route's own colour, so an all-grey route still needs one
   own-colour finish. Untaped shared holds near the route's line go in `Route.shared`
   (usable, not exclusive, not in `holds`). Routes below `min_route_holds` survive only
   if complete.
5. **Output**: `climb_beta.overlay` draws the highlight for the app, and
   `climb_beta.metrics` computes the exit criteria.

## Data model
- **Detector dataset**: standard Ultralytics YOLO-seg layout: `images/{train,val,test}`,
  `labels/{train,val,test}` (one polygon per line, normalised), and `dataset.yaml`.
- **Colour sidecar**: `colours/{split}/<stem>.json`, a list aligned to the label lines:
  `{"colour": "red", "chalked": false}` (`null` for volume and tape).
- **Routes GT** (test only): `routes.yaml`, entries
  `{image, colour, holds: [label line idx], grade, start: [idx], finish: idx, complete}`
  (`grade`/`start`/`finish` optional; `complete` defaults true). `holds` = own-colour
  holds + taped grey/black starts. Only complete routes are scored, matched by colour +
  grade. The owner's notes on the first photo batch, to build it from, are in the
  gitignored `data/basecamp/labels/route_notes.yaml`.
- **Basecamp raw**: `data/basecamp/raw/<wall_id>/*.jpg` (gitignored). `data/basecamp/walls.yaml`
  is committed and records each wall's ID, angle and notes. `data/basecamp/splits.yaml`
  (committed) maps wall → split.
- **Pseudo-masks**: `pseudo_masks.txt` in a converted Roboflow dataset lists images whose
  masks came from SAM box prompts. These are never used for test metrics.

## Auth / secrets
There is no user auth (it's a public demo). Secrets live only in `.env`:
`ROBOFLOW_API_KEY`, `HF_TOKEN`, `LABEL_STUDIO_*`.

## Known gaps
- The Roboflow project and version aren't pinned yet (Universe blocks scripted reads).
  This is a `needs-decision` issue.
- Colour thresholds in `configs/colours.yaml` are first guesses, tuned on synthetic
  images. They must be re-tuned on real Basecamp crops (M5).
- The SAM 2 Label Studio backend is CUDA-only, so labelling needs the GPU laptop.
- HF Spaces free CPU quota has been unreliable since mid-2026, so the app must also run
  locally.
