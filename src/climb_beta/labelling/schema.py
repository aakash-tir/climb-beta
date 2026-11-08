"""Tag names shared by the Label Studio config generator and the export converter."""

IMAGE = "image"
BRUSH = "mask"  # BrushLabels: SAM 2 answers here; also hand-painted masks
POLYGON = "poly"  # PolygonLabels: hand-drawn outlines
KEYPOINT = "sam_point"  # KeyPointLabels (smart): click prompts for SAM 2
RECT = "sam_box"  # RectangleLabels (smart): box prompts for SAM 2
COLOUR = "colour"  # per-region Choices: hold colour
CHALKED = "chalked"  # per-region Choices: "chalked" flag
CHALKED_VALUE = "chalked"
