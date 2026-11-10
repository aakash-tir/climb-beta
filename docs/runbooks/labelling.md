# Runbook: labelling Basecamp photos

Label Studio with the SAM 2.1 backend: click a hold, get a mask, pick its colour.
Everything runs locally on the GPU laptop. Photos never leave the machine, except
through the private HF dataset sync.

## 0. Prerequisites
- Docker Desktop with the NVIDIA runtime (`docker info` lists `nvidia` under Runtimes).
- An NVIDIA GPU. The SAM 2 backend is CUDA-only. Our image targets CUDA 12.8 so it
  runs on RTX 50-series (sm_120). The upstream image (CUDA 12.6) does not.
- `.env` at the repo root, from `.env.example`: set `LABEL_STUDIO_USERNAME`,
  `LABEL_STUDIO_PASSWORD`, and (after step 2) `LABEL_STUDIO_API_KEY`.

## 1. Put photos in place
```
data/basecamp/raw/<wall_id>/<photo>.jpg
```
One folder per physical wall section. The wall ID is the unit of the train/val/test
split, so don't mix two walls in one folder. Add the wall to `data/basecamp/walls.yaml`.
Pull existing photos with `python data/sync_hf.py pull`.

## 2. Start
```bash
docker compose -f labelling/docker-compose.yml up -d --build   # first build: ~15 min, ~12 GB
curl http://localhost:9090/                                     # {"status":"UP"} once SAM is loaded
```
Open http://localhost:8080 and log in with the `.env` user. Then go to **Account &
Settings → Personal Access Token**, copy the token into `.env` as
`LABEL_STUDIO_API_KEY`, and restart the backend so it can fetch images:
`docker compose -f labelling/docker-compose.yml up -d sam2`.

## 3. Create the project
1. **Create Project** → name it `basecamp-holds`.
2. **Labeling Setup → Custom template → Code**: paste `labelling/label_config.xml`.
   Regenerate it first with `python labelling/make_config.py` if `configs/colours.yaml`
   changed.
3. **Settings → Cloud Storage → Add Source Storage → Local files**: absolute local path
   `/data/basecamp/raw`, file filter `.*\.(jpe?g|png)$`, and tick *Treat every bucket
   object as a source file*. **Sync**.
4. **Settings → Model → Connect Model**: URL `http://sam2:9090`, and enable
   *Interactive preannotations*.

## 4. Label (per photo)
1. Turn on **Auto-Annotation** (toolbar). Pick `hold` in the `sam_point` tool and
   click the hold. SAM 2 returns a brush mask. Use `sam_box` for long, thin holds and
   tape. Fix edges with the brush/eraser, or draw a `poly` by hand if SAM fails.
2. **Select the region**, then pick its **colour**, and tick **chalked** if chalk
   covers a visible part of the hold. Every hold needs a colour (the export warns
   about any that don't).
3. Label each small **tape diamond** as `tape` (`sam_box` works best) and give it
   its colour too: at Basecamp the diamond colour is the route's grade. Two diamonds
   at the bottom mark the start, one at the top the finish. Volumes need no colour.
4. Label **every** hold, volume and tape diamond in the photo. A missed hold becomes
   background and teaches the detector to miss it.
5. Submit.

## 5. Export → training data
1. **Export → JSON** (not JSON-MIN) → save to `data/basecamp/exports/<date>.json`.
2. Convert and build:
   ```bash
   uv sync --extra label
   python labelling/export_to_yolo.py data/basecamp/exports/<date>.json
   python data/split_by_wall.py assign     # only places new walls; never moves old ones
   python data/split_by_wall.py build      # -> data/yolo/basecamp
   python data/sync_hf.py push -m "labelled <walls>"
   ```

## Stop / reset
`docker compose -f labelling/docker-compose.yml down`. Label Studio's database is in
`labelling/.ls-data` (gitignored). Back it up before deleting it.

## Troubleshooting
- **Backend stuck / not UP**: `docker compose -f labelling/docker-compose.yml logs sam2`.
  `no kernel image is available for execution on the device` means the image wasn't
  built for your GPU arch. Check `TORCH_CUDA_ARCH_LIST` in `labelling/sam2-backend/Dockerfile`.
- **Masks never appear**: is the model connected with *interactive preannotations* on?
  Are Auto-Annotation and a `smart` tool (`sam_point` / `sam_box`) selected?
- **Backend can't load images (403/401)**: `LABEL_STUDIO_API_KEY` is missing or stale.
