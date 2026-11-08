# Runbook: deploy the demo to Hugging Face Spaces

The demo is a Gradio app that runs on **CPU Basic** (2 vCPU, 16 GB). Free CPU Basic
has been unreliable since mid-2026: forum reports of "403 cpu-basic quota limit" on
a single Space. If that happens, run it locally (`python app/app.py`). Nothing else
depends on the Space.

## 1. Publish the detector weights
Weights stay out of git. Upload the trained detector to a (public or private) HF model repo:
```bash
huggingface-cli upload <user>/climb-beta-detector weights/detector-yolo11n-seg.pt detector.pt
```
If that repo is private, the Space needs a read token (step 3).

## 2. Build the Space folder
```bash
python app/build_space.py dist/space
```
This creates `app.py`, the `climb_beta` package, `configs/`, a CPU-only
`requirements.txt`, a `README.md` with the Space front matter (sdk: gradio,
licence agpl-3.0), and `LICENSE`. `dist/` is gitignored.

## 3. Create and push the Space
1. On huggingface.co: **New Space** → SDK *Gradio* → hardware *CPU basic*.
2. **Settings → Variables**: `CLIMB_DETECTOR_WEIGHTS=hf://<user>/climb-beta-detector/detector.pt`.
   If the weights repo is private, add **Secret** `HF_TOKEN` with read access.
3. Push the folder:
   ```bash
   cd dist/space
   git init -b main && git remote add origin https://huggingface.co/spaces/<user>/climb-beta
   git add -A && git commit -m "Deploy climb-beta demo" && git push -u origin main --force
   ```

## Check
Open the Space, upload a wall photo, pick a colour. With no `CLIMB_DETECTOR_WEIGHTS`
set, the app still starts and says so. That's expected before step 1.
