#!/usr/bin/env python3
"""
TRELLIS.2 Image Preprocessor — Template
=========================================
Copy and use as-is, or modify bg_color/threshold parameters.

Dependencies: pip install Pillow numpy rembg onnxruntime
              OR pip install transformers torch torchvision timm (for BiRefNet)
"""

import argparse, sys
from pathlib import Path
import numpy as np
from PIL import Image

try:
    import rembg
    HAS_REMBG = True
except ImportError:
    HAS_REMBG = False


def preprocess_image(img: Image.Image, alpha_threshold: int = 204,
                     bg_color: tuple = (255, 255, 255)) -> Image.Image:
    """Preprocess image for TRELLIS.2 — matches Trellis2ImageTo3DPipeline.preprocess_image."""
    # Handle alpha / background removal
    has_alpha = False
    if img.mode == "RGBA":
        alpha = np.array(img)[:, :, 3]
        if not np.all(alpha == 255):
            has_alpha = True

    max_size = max(img.size)
    scale = min(1.0, 1024 / max_size)
    if scale < 1:
        img = img.resize((int(img.width * scale), int(img.height * scale)), Image.Resampling.LANCZOS)

    if has_alpha:
        output = img
    else:
        if not HAS_REMBG:
            raise ImportError("rembg not installed: pip install rembg onnxruntime")
        session = rembg.new_session("u2net")
        output = rembg.remove(img.convert("RGB"), session=session)

    # Crop to content bounding box
    output_np = np.array(output)
    alpha = output_np[:, :, 3]
    bbox_coords = np.argwhere(alpha > alpha_threshold)
    if bbox_coords.size == 0:
        return output.convert("RGB")

    x_min, y_min = np.min(bbox_coords[:, 1]), np.min(bbox_coords[:, 0])
    x_max, y_max = np.max(bbox_coords[:, 1]), np.max(bbox_coords[:, 0])

    center_x, center_y = (x_min + x_max) / 2, (y_min + y_max) / 2
    size = max(x_max - x_min, y_max - y_min)  # No padding (size*1, not size*1.2)

    bbox = (int(center_x - size // 2), int(center_y - size // 2),
            int(center_x + size // 2), int(center_y + size // 2))
    output = output.crop(bbox)

    # Composite onto background
    output_np = np.array(output).astype(np.float32) / 255.0
    rgb, a = output_np[:, :, :3], output_np[:, :, 3:4]
    bg = np.array(bg_color, dtype=np.float32).reshape(1, 1, 3) / 255.0
    composited = rgb * a + bg * (1 - a)
    return Image.fromarray((composited * 255).astype(np.uint8))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preprocess image for TRELLIS.2")
    parser.add_argument("input", help="Input image")
    parser.add_argument("output", help="Output PNG")
    parser.add_argument("--threshold", type=int, default=204)
    parser.add_argument("--bg", type=str, default="255,255,255")
    args = parser.parse_args()
    bg = tuple(int(x) for x in args.bg.split(","))
    img = Image.open(args.input)
    processed = preprocess_image(img, args.threshold, bg)
    processed.save(args.output, "PNG")
    print(f"Saved: {args.output} ({processed.size})")
