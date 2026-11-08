# Basecamp photos (private)

Photos and labels in this folder are **gitignored** and synced to a private Hugging
Face dataset (`data/sync_hf.py`). They show the gym's walls and setters' routes, which
aren't ours to publish without the gym's permission. Only `walls.yaml`, `splits.yaml`
and this README are committed.

```
raw/<wall_id>/<photo>.jpg       phone photos, one folder per wall
labels/<wall_id>/<photo>.txt    YOLO-seg labels (from labelling/export_to_yolo.py)
labels/<wall_id>/<photo>.json   colour sidecar, aligned to the label lines
walls.yaml                      wall metadata (committed)
splits.yaml                     wall -> split (committed, made by split_by_wall.py assign)
```

**Split by wall, never by photo.** Photos of one wall share holds and lighting, so a
photo split leaks test into train. `python data/split_by_wall.py assign` assigns
whole walls. Re-running it only adds new walls and never moves existing ones (unless
you pass `--reassign`). `build` writes `data/yolo/basecamp/`.
