"""climb-beta demo: upload a wall photo, pick a colour, see that route highlighted.

Run locally:
    uv sync --extra ml --extra app
    CLIMB_DETECTOR_WEIGHTS=weights/detector-yolo11n-seg.pt python app/app.py

On Hugging Face Spaces this file is the Space's app.py (see app/build_space.py).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

# In the packaged Space, configs/ sits next to this file; in the repo it doesn't.
_HERE = Path(__file__).resolve().parent
if (_HERE / "configs").is_dir():
    os.environ.setdefault("CLIMB_CONFIG_DIR", str(_HERE / "configs"))

from climb_beta.demo import DemoService  # noqa: E402

TITLE = "climb-beta: find a route by colour"
DESCRIPTION = (
    "Phase 1 demo for Basecamp Climbing (Toronto). A colour-blind segmentation model finds "
    "every hold; a separate colour step labels each hold (ignoring chalk); holds of the "
    "colour you pick are grouped into a route. Its tape diamonds give the grade (pick one to "
    "choose between same-colour routes); the start holds are marked **S** and the finish **F**."
)


def build_ui(service: DemoService | None = None) -> Any:
    import gradio as gr  # lazy: app extra

    svc = service or DemoService()
    with gr.Blocks(title=TITLE) as demo:
        gr.Markdown(f"# {TITLE}\n{DESCRIPTION}")
        with gr.Row():
            with gr.Column():
                photo = gr.Image(label="Wall photo", type="numpy", sources=["upload", "webcam"])
                colour = gr.Dropdown(svc.colours, value=svc.colours[0], label="Hold colour")
                grade = gr.Dropdown(
                    svc.grades, value=svc.grades[0], label="Grade (tape diamond colour)"
                )
                go = gr.Button("Find route", variant="primary")
            with gr.Column():
                out = gr.Image(label="Route", type="numpy")
                summary = gr.Markdown()
        go.click(svc.handle, inputs=[photo, colour, grade], outputs=[out, summary])
    return demo


if __name__ == "__main__":
    build_ui().launch()
