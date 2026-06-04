---
name: claw3d-3d-printing
description: "Full 3D printing pipeline: AI model generation (FAL), OpenSCAD design, STL export, slicing, and printer control via claw3d CLI."
version: 1.0.0
author: agent
triggers:
  - 3D print
  - STL
  - 3D model
  - claw3d
  - FAL
  - openSCAD
  - slicing
  - G-code
---

# 3D Printing Pipeline

End-to-end workflow from concept to printed part.

## Tools

| Tool | Purpose | Install |
|------|---------|---------|
| `claw3d` | AI→3D, slicing, printer control | `pip install --break-system-packages claw3d` |
| `openscad` | Parametric CAD, STL export | `sudo apt-get install -y openscad` |
| `FAL_API_KEY` | AI model generation | Get from https://fal.ai/dashboard/keys |

## Workflow

### 1. Design → STL

**Option A: OpenSCAD (parametric)**
```bash
openscad design.scad --imgsize=1920,1080 -o preview.png  # Preview first
openscad design.scad -o model.stl                         # Export STL
```

Always render PNG preview and show user before exporting STL.

**Option B: Python mesh generation**
```bash
python3 scripts/stl_generator.py  # Custom mesh builder
```

**Option C: AI image→3D (claw3d + FAL)**
```bash
export FAL_API_KEY="key-id:secret"
claw3d convert --image reference.jpg --output model.glb
# Convert GLB→STL with Blender or meshlab
```

**Option D: TRELLIS.2 (microsoft/TRELLIS.2)**
- For high-quality image-to-3D with PBR textures
- See `image-to-3d-generation` skill for full workflow
- Colab notebook recommended (14GB VRAM for 4B model)
- Exports GLB with WebP textures via `o_voxel`

### 2. Validate

```bash
claw3d dimensions model.stl          # Check bounding box (mm)
claw3d fit-check model.stl           # Check vs build volume
```

### 3. Slice

```bash
claw3d slice model.stl -o output.gcode --profile my_printer
```

### 4. Print

```bash
claw3d printer list                  # List configured printers
claw3d print output.gcode --printer my_printer
```

## Build Volume Reference

| Printer | Volume (mm) |
|---------|-------------|
| Snapmaker A350T | 320×350×340 |
| Ender 3 | 220×220×250 |
| Prusa MK3S+ | 250×210×210 |

## Pitfalls

- **FAL_API_KEY not recognized** — Must be set as env var at runtime, not just in `.env`: `export FAL_API_KEY="..."`. If 401 error, key may be invalid — generate new at fal.ai.
- **Design confirmation** — Always show PNG preview to user before generating STL. If design doesn't match their mental model (e.g. "clam" vs "clip"), ask for clarification and iterate. Don't assume the object class.
- **OpenSCAD `reverse()`** — Doesn't exist. Use `[for (i = [len-1 : -1 : 0])` instead.
- **OpenSCAD `hull()` with few circles** → few CSG elements → flat shape. Use `polygon()` with many points for smooth profiles.
- **`concat()` in OpenSCAD** — Works with static lists. Test with `echo()` first for complex expressions.
- **Window Desktop path** — Use `/mnt/c/Users/<username>/Desktop/` not `~/Desktop/`.
- **Writing to Windows mount** — `cat > /mnt/c/Users/.../file` may fail with exit code 23 (write error / permission denied). Use `tee` as workaround: `curl -sL <url> | tee /mnt/c/Users/.../file > /dev/null`. Also works for redirecting command output to Windows paths.
- **Obliteratus config for WSL/CUDA** — Default `preset_quick.yaml` uses `device: cpu` which crashes with empty tensor on some datasets (GPT-2 + wikitext). Create a custom YAML with `device: cuda` and `dtype: float16` and limit samples: `max_samples: 100`, `max_length: 128`.
