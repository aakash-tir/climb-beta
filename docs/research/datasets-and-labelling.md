# Datasets and labelling tools (researched 2026-11-08)

## Public data: Roboflow "Climbing Holds and Volumes"
Roboflow Universe has several projects with similar names. I couldn't read their pages
directly, because Universe returns HTTP 403 to non-browser clients. From search snippets:

| Project | Annotation type | Notes |
|---|---|---|
| `blackcreed-xpgxh/climbing-holds-and-volumes` | not confirmed | "identify and classify climbing holds and climbing volumes on indoor walls" |
| `test-7uxfw/climbing-holds-and-volumes-r1iuf` | **bounding boxes** | "bounding boxes around individual climbing holds and climbing volumes" |
| `rock-climbing-9qwqx/hold-segmentation` | instance segmentation, CC BY 4.0 | holds only, no description |

**Decision (owner, 2026-11-08):** the converter takes polygons where the export has
them. When an annotation is box-only, it makes a mask by prompting SAM with the box,
and lists that image in `pseudo_masks.txt`. Pseudo-masked images are kept out of every
test split. Which exact project and version to pin is an open `needs-decision` issue,
since it needs a logged-in browser to confirm the task type and licence. Download goes
through the `roboflow` Python SDK with `ROBOFLOW_API_KEY` from `.env`, which needs a
free Roboflow account. Export format `coco-segmentation` holds both polygons and boxes,
so one converter covers both cases.

Attribution: CC BY 4.0 requires credit. The README's "Data and licences" section names
the dataset, its authors and the licence.

## Our data: Basecamp Climbing photos
- **Split by wall.** Photos of one wall share holds, angle and lighting, so a random
  photo split leaks the test set into training and inflates every metric. The wall ID is
  the folder name (`data/basecamp/raw/<wall_id>/`). `data/split_by_wall.py` assigns
  whole walls to train/val/test and refuses to write a split where a wall appears twice.
- **Storage (owner decision, 2026-11-08):** photos and labels are gitignored. They stay
  on the labelling machine and sync to a **private Hugging Face dataset repo**, because
  they show the gym's walls and setters' routes, which aren't ours to publish without
  permission. Only the folder layout, `walls.yaml` and the split manifest are committed.

## Labelling: Label Studio + SAM 2 ML backend
From the [Label Studio SAM 2 tutorial](https://labelstud.io/tutorials/segment_anything_2_image):
- The backend is the `segment_anything_2_image` example in
  `HumanSignal/label-studio-ml-backend`. It serves on port 9090, and `GET /` returns
  `{"status":"UP"}`.
- **It is CUDA-only** (`DEVICE` supports only `cuda`; CPU is "coming soon"). The owner's
  laptop has an RTX 5070 Ti with 12 GB, so labelling runs locally under Docker with the
  NVIDIA runtime.
- Env vars: `DEVICE`, `MODEL_CONFIG` (default `sam2_hiera_l.yaml`), `MODEL_CHECKPOINT`
  (default `sam2_hiera_large.pt`), `BASIC_AUTH_USER/PASS`, `LOG_LEVEL`, `WORKERS`, `THREADS`.
- Interaction: `KeyPointLabels`/`RectangleLabels` with `smart="true"` are the prompts,
  and SAM 2 answers with `BrushLabels`. Inside Docker, the Label Studio container must
  reach the backend by its compose service name, not `localhost`.
- Per-hold colour uses `<Choices perRegion="true">`, so each mask carries its own colour
  and a `chalked` flag. The eval needs that flag for its chalk subset.

## Sources
- https://universe.roboflow.com/blackcreed-xpgxh/climbing-holds-and-volumes
- https://universe.roboflow.com/test-7uxfw/climbing-holds-and-volumes-r1iuf
- https://universe.roboflow.com/rock-climbing-9qwqx/hold-segmentation
- https://labelstud.io/tutorials/segment_anything_2_image
- https://docs.humansignal.com/tutorials/segment_anything_2_image
