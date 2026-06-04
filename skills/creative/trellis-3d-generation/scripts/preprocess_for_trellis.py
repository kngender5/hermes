#!/usr/bin/env python3
"""
TRELLIS Image Preprocessor
Prepares images for TRELLIS image-to-3D inference.

Usage:
  python preprocess_for_trellis.py input.png output.png
  python preprocess_for_trellis.py input_dir/ output_dir/ --batch
  python preprocess_for_trellis.py input.png output.png --preview
"""

import argparse
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

try:
    import rembg
    HAS_REMBG = True
except ImportError:
    HAS_REMBG = False


def remove_background_u2net(img: Image.Image) -> Image.Image:
    if not HAS_REMBG:
        raise ImportError("rembg not installed. Run: pip install rembg onnxruntime")
    session = rembg.new_session("u2net")
    return rembg.remove(img, session=session)


def preprocess_image(
    img: Image.Image,
    target_size: int = 518,
    pad_factor: float = 1.2,
    alpha_threshold: int = 204,
    bg_color: tuple = (255, 255, 255),
) -> Image.Image:
    # Handle alpha / background removal
    has_alpha = False
    if img.mode == "RGBA":
        alpha = np.array(img)[:, :, 3]
        if not np.all(alpha == 255):
            has_alpha = True

    if has_alpha:
        output = img
    else:
        img_rgb = img.convert("RGB")
        max_size = max(img_rgb.size)
        scale = min(1.0, 1024 / max_size)
        if scale < 1:
            img_rgb = img_rgb.resize(
                (int(img_rgb.width * scale), int(img_rgb.height * scale)),
                Image.Resampling.LANCZOS,
            )
        output = remove_background_u2net(img_rgb)

    # Crop to content bounding box
    output_np = np.array(output)
    alpha = output_np[:, :, 3]
    bbox_coords = np.argwhere(alpha > alpha_threshold)

    if bbox_coords.size == 0:
        print("  WARNING: No alpha channel detected, resizing without crop")
        return output.convert("RGB").resize(
            (target_size, target_size), Image.Resampling.LANCZOS
        )

    x_min = np.min(bbox_coords[:, 1])
    y_min = np.min(bbox_coords[:, 0])
    x_max = np.max(bbox_coords[:, 1])
    y_max = np.max(bbox_coords[:, 0])

    center_x = (x_min + x_max) / 2
    center_y = (y_min + y_max) / 2
    size = max(x_max - x_min, y_max - y_min)
    size = int(size * pad_factor)

    bbox = (
        int(center_x - size // 2),
        int(center_y - size // 2),
        int(center_x + size // 2),
        int(center_y + size // 2),
    )

    output = output.crop(bbox)
    output = output.resize((target_size, target_size), Image.Resampling.LANCZOS)

    # Composite onto background color
    output_np = np.array(output).astype(np.float32) / 255.0
    rgb = output_np[:, :, :3]
    alpha = output_np[:, :, 3:4]
    bg = np.array(bg_color, dtype=np.float32).reshape(1, 1, 3) / 255.0
    composited = rgb * alpha + bg * (1 - alpha)
    return Image.fromarray((composited * 255).astype(np.uint8))


def process_batch(input_dir: str, output_dir: str, **kwargs) -> list:
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    extensions = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}
    results = []

    for img_file in sorted(input_path.iterdir()):
        if img_file.suffix.lower() not in extensions:
            continue
        out_file = output_path / f"{img_file.stem}.png"
        try:
            img = Image.open(img_file)
            processed = preprocess_image(img, **kwargs)
            processed.save(out_file, "PNG")
            results.append(str(out_file))
            print(f"  OK: {img_file.name} -> {out_file.name}")
        except Exception as e:
            print(f"  FAIL: {img_file.name}: {e}", file=sys.stderr)

    return results


def main():
    parser = argparse.ArgumentParser(description="Preprocess images for TRELLIS image-to-3D")
    parser.add_argument("input", help="Input image file or directory")
    parser.add_argument("output", help="Output image file or directory")
    parser.add_argument("--batch", action="store_true", help="Batch process a directory")
    parser.add_argument("--size", type=int, default=518, help="Output size (default: 518)")
    parser.add_argument("--pad", type=float, default=1.2, help="Bbox padding factor (default: 1.2)")
    parser.add_argument("--threshold", type=int, default=204, help="Alpha threshold 0-255 (default: 204)")
    parser.add_argument("--bg", type=str, default="255,255,255", help="Background color R,G,B")
    parser.add_argument("--preview", action="store_true", help="Show side-by-side preview")

    args = parser.parse_args()
    bg_color = tuple(int(x) for x in args.bg.split(","))

    kwargs = dict(
        target_size=args.size,
        pad_factor=args.pad,
        alpha_threshold=args.threshold,
        bg_color=bg_color,
    )

    if args.batch or Path(args.input).is_dir():
        print(f"Batch processing: {args.input} -> {args.output}")
        results = process_batch(args.input, args.output, **kwargs)
        print(f"\nDone: {len(results)} images processed")
    else:
        img = Image.open(args.input)
        processed = preprocess_image(img, **kwargs)
        processed.save(args.output, "PNG")
        print(f"Saved: {args.output} ({processed.size[0]}x{processed.size[1]})")


if __name__ == "__main__":
    main()
