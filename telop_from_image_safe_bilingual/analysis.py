from __future__ import annotations

from typing import List
import cv2  # type: ignore
import numpy as np

from .models import TelopStyle


def infer_style_from_images(image_paths: List[str]) -> TelopStyle:
    """Infer a TelopStyle from given images. This implementation uses simple
    heuristics and defaults when analysis fails. All processing is offline."""
    if not image_paths:
        raise ValueError("No images provided")

    img = cv2.imread(image_paths[0])
    if img is None:
        raise ValueError(f"Failed to read image: {image_paths[0]}")

    height, width = img.shape[:2]

    style = TelopStyle(
        text=None,
        font_name="Noto Sans JP Black",
        font_size=100,
        tracking=-25,
        position={"x": width // 2, "y": int(height * 0.9)},
        fill={"enabled": True, "color": [1.0, 1.0, 1.0]},
        strokes=[{"color": [0.0, 0.0, 0.0], "width": 20}],
        shadow={
            "enabled": False,
            "color": [0.0, 0.0, 0.0],
            "distance": 0,
            "softness": 0,
            "opacity": 0,
            "direction": 0,
        },
        plate={
            "enabled": False,
            "shape": "rect",
            "size": {"w": width, "h": height},
            "radius": 0,
            "color": [0.0, 0.0, 0.0],
            "opacity": 0,
            "stroke_width": 0,
            "stroke_color": [0.0, 0.0, 0.0],
        },
        comp={"width": width, "height": height, "fps": 30, "duration": 10},
        template_name="ImageDerivedTelop_01",
    )
    return style
