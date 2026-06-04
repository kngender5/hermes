# TRELLIS Image Preprocessing

## Pipeline

```
Input Image (any PIL format)
    |
    v
[Has RGBA with real alpha?]
    | yes -> keep alpha
    | no  -> rembg.remove(img, session='u2net')
    |         (scale to max 1024px first for speed)
    |
    v
[Find bbox where alpha > 204 (80% of 255)]
    |
    v
[Pad bbox to 120% and make square]
    center = (x_min + x_max) / 2, (y_min + y_max) / 2
    size = max(width, height) * 1.2
    |
    v
[Crop to padded square bbox]
    |
    v
[Resize to 518x518 via Lanczos]
    |
    v
[Composite: RGB * alpha + BG_color * (1 - alpha)]
    default BG = white (255, 255, 255)
    |
    v
Output PNG (518x518, RGB)
```

## Why 518x518?

DinoV2 ViT-L/14 uses patch size 14. 518 / 14 = 37 patches per side. This is hardcoded in the pipeline's `preprocess_image()` method.

## Background Removal

- Model: `u2net` (via `rembg.new_session('u2net')`)
- NOT BiRefNet/RMBG-2.0 (those appear in the v2 pipeline.json config but the code uses u2net)
- Images are scaled down to max 1024px before rembg for speed
- If image already has alpha channel with transparency, rembg is skipped

## Standalone Script

`preprocess_for_trellis.py` can run without the full TRELLIS install:

```bash
pip install Pillow rembg onnxruntime opencv-python-headless numpy

# Single file
python preprocess_for_trellis.py input.png output.png

# With preview
python preprocess_for_trellis.py input.png output.png --preview

# Batch
python preprocess_for_trellis.py input_dir/ output_dir/ --batch

# Custom background color
python preprocess_for_trellis.py input.png output.png --bg 0,0,0  # black bg
```

## Parameters

| Param | Default | Description |
|-------|---------|-------------|
| `--size` | 518 | Output size (don't change unless model changes) |
| `--pad` | 1.2 | BBox padding factor (1.2 = 120%) |
| `--threshold` | 204 | Alpha threshold (204 = 80% of 255) |
| `--bg` | 255,255,255 | Background color R,G,B |
