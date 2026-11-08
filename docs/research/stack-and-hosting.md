# Stack, training hardware and demo hosting (researched 2026-11-08)

## Detector: Ultralytics YOLO11-seg
- The plan fixes YOLO11-seg. Ultralytics is **AGPL-3.0**, which is why this repo is
  AGPL-3.0 too: any model or service built on it has to be AGPL-compatible unless you
  hold an Ultralytics enterprise licence.
- `yolo11n-seg` (2.9M params) is the CPU and Spaces default. `yolo11s-seg` (10M params)
  is the accuracy option. Both configs are committed, and eval picks whichever meets the
  exit criteria at an acceptable CPU latency.
- **Colour invariance:** train with `hsv_h=0.5, hsv_s=0.9`, so the hue of a hold carries
  no class signal. Classes are `hold`, `volume`, `tape`.
- Rejected: **Mask R-CNN / Detectron2** (heavier, slower on CPU, and the Windows install
  is painful); **SAM 2 alone as the detector** (it has no class head, its automatic
  mask generation is far too slow on CPU, and it over-segments bolt holes and wall
  texture).

## Training hardware
- The owner's laptop has an **RTX 5070 Ti, 12 GB (Blackwell, sm_120)**. Blackwell needs
  PyTorch wheels built for **CUDA 12.8 or newer**, so the `ml` extra pulls `torch` from
  the `pytorch-cu128` index on Windows and Linux.
- CI never installs torch. Everything under test (colour rules, route grouping, dataset
  conversion, wall split, metrics) is numpy + OpenCV, which keeps CI near a minute.

## Package manager: uv, Python 3.11
Set by the plan. Optional extras keep heavy dependencies out of the default install:
`ml` (ultralytics, timm, torch), `data` (roboflow), `app` (gradio), `dev` (pytest, ruff,
mypy).

## Demo hosting: Hugging Face Spaces (Gradio, CPU Basic)
- CPU Basic is described as **2 vCPU, 16 GB RAM, 50 GB non-persistent disk** and is
  listed as free ([HF forum](https://discuss.huggingface.co/t/question-about-the-cpu-basic-quota-limit/176628)).
- **Risk:** since about mid-2026, forum threads report free accounts getting
  "403 cpu-basic quota limit" on their only Space, with staff suggesting PRO or credits
  ([thread](https://discuss.huggingface.co/t/403-cpu-basic-quota-limit-on-my-first-and-only-space/178658)).
  The demo is built so that `python app/app.py` runs it locally just the same, and the
  Space is a convenience, not a dependency.
- `yolo11n-seg` at 640 px runs in roughly 100–300 ms per image on 2 vCPUs (Ultralytics'
  published CPU ONNX numbers are of that order), which is fine for an upload-and-wait
  demo.

## Sources
- https://docs.ultralytics.com/models/yolo11/
- https://github.com/ultralytics/ultralytics/blob/main/LICENSE
- https://discuss.huggingface.co/t/question-about-the-cpu-basic-quota-limit/176628
- https://discuss.huggingface.co/t/403-cpu-basic-quota-limit-on-my-first-and-only-space/178658
- https://pytorch.org/get-started/locally/
