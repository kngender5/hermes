---
name: trellis-3d-generation
description: >
  Generate 3D models from images using Microsoft TRELLIS (structured 3D latents).
  Covers image preprocessing (background removal, crop, resize), model loading,
  inference with sampler parameters, and export to GLB/PLY. Use this skill when
  the user wants image-to-3D, 3D reconstruction from photos, or TRELLIS pipelines.
---

# TRELLIS 3D Generation

Generate 3D models from single or multi-view images using Microsoft TRELLIS.

**Two versions exist — do not confuse them:**

| | TRELLIS v1 | TRELLIS.2 |
|---|---|---|
| GitHub | `microsoft/TRELLIS` | `microsoft/TRELLIS.2` |
| PyPI package | `trellis` | `trellis2` |
| HF model | `microsoft/TRELLIS-image-large` | `microsoft/TRELLIS.2-4B` |
| Pipeline class | `TrellisImageTo3DPipeline` | `Trellis2ImageTo3DPipeline` |
| GLB export | `postprocessing_utils.to_glb()` | `o_voxel.postprocess.to_glb()` |
| Config format | `pipeline.json` with 6 models under `ckpts/` | `pipeline.json` with 8 models under `ckpts/` |

## When to Use

- Converting a product photo to a 3D model
- Generating 3D assets from reference images
- Batch processing images to GLB/PLY
- Multi-view 3D reconstruction (3-4 angles of same object)

## Environment

**Primary**: Google Colab (T4 GPU or better)
**Local**: WSL2 + conda env with PyTorch 2.x + CUDA

Tested with:
- PyTorch 2.12.0+cu130, CUDA 13.0, RTX 4060 8GB
- Python 3.10-3.12

## Install Methods

### Method A: TRELLIS.2 from GitHub (Recommended)

TRELLIS.2 is the newer version with better quality. The GitHub repo includes `trellis2/` package, `o-voxel/` submodule, and all configs.

```bash
# Colab / fresh env
import os
os.environ['SPCONV_ALGO'] = 'native'

!git clone --recursive https://github.com/microsoft/TRELLIS.2.git /content/TRELLIS2
%cd /content/TRELLIS2
!pip install -e . -q        # installs trellis2 package
!pip install -e o-voxel -q  # installs o_voxel for GLB export
%cd /content

# Render lib
!git clone --recursive https://github.com/NVlabs/nvdiffrast.git /tmp/nvdiffrast
!pip install /tmp/nvdiffrast --no-build-isolation -q
```

```bash
# WSL2 / local conda env
git clone --recursive https://github.com/microsoft/TRELLIS.2.git ~/projects/TRELLIS2
cd ~/projects/TRELLIS2
pip install -e .
pip install -e o-voxel
```

**Python deps (install before trellis2):**
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install diffusers transformers accelerate safetensors huggingface_hub
pip install rembg onnxruntime trimesh pillow numpy imageio imageio-ffmpeg
pip install easydict opencv-python-headless ninja
pip install spconv-cu120 || pip install spconv-cu118
```

### Method B: TRELLIS v1 from GitHub (Legacy)

```bash
git clone --depth 1 https://github.com/microsoft/TRELLIS.git /tmp/trellis
cd /tmp/trellis && pip install -e .
```

### Method C: HuggingFace Bucket (Custom Forks / User Buckets)

**WARNING:** HF buckets often contain only `.safetensors` weight files WITHOUT the required `.json` config files. TRELLIS.2's `models.from_pretrained()` expects BOTH `{path}.json` (config with `name` + `args`) AND `{path}.safetensors` (state_dict) for EACH model module. A bucket with only safetensors will FAIL.

**If your bucket only has safetensors:** Use Method A (GitHub clone) + download the official `microsoft/TRELLIS.2-4B` repo from HF for configs, then optionally replace the `.safetensors` files with your own.

```bash
# Download official TRELLIS.2-4B for complete config + weights
from huggingface_hub import snapshot_download
snapshot_download(repo_id="microsoft/TRELLIS.2-4B", local_dir="/content/TRELLIS2_hf", local_dir_use_symlinks=False)
```

**Colab vs WSL paths:** Workflow scripts designed for Colab use `/content/TRELLIS2` — translate to `~/projects/TRELLIS2/` in WSL.

## Quick Start (Local, TRELLIS.2)

```python
import os
os.environ['SPCONV_ALGO'] = 'native'

from PIL import Image
from trellis2.pipelines import Trellis2ImageTo3DPipeline

pipeline = Trellis2ImageTo3DPipeline.from_pretrained('microsoft/TRELLIS.2-4B')
pipeline.cuda()

img = Image.open('input.png').convert('RGB')
outputs = pipeline.run(img, seed=42, pipeline_type='1024_cascade')

import o_voxel
mesh = outputs[0] if isinstance(outputs, (list, tuple)) else outputs
glb = o_voxel.postprocess.to_glb(
    vertices=mesh.vertices, faces=mesh.faces,
    attr_volume=mesh.attrs, coords=mesh.coords,
    attr_layout=mesh.layout, voxel_size=mesh.voxel_size,
    aabb=[[-0.5, -0.5, -0.5], [0.5, 0.5, 0.5]],
    texture_size=1024, remesh=True, verbose=False,
)
glb.export('output.glb', extension_webp=True)
```

## Image Preprocessing

See `references/preprocessing.md` for full details.

Key points:
- Input: any PIL-supported format (PNG, JPG, WebP, etc.)
- Background removal: rembg with `u2net` model (if no alpha channel)
- Output: 518x518 RGB PNG (DinoV2 patch grid: 37 * 14 = 518)
- BBox padding: 120% of content bounds
- Composite onto white background by default

## Model Selection

| Model | Version | VRAM | Quality | Speed (T4) |
|-------|---------|------|---------|------------|
| `microsoft/TRELLIS-image-large` | v1 | ~8GB | Good | 3-5 min |
| `microsoft/TRELLIS-image-base` | v1 | ~4GB | Decent | 1-2 min |
| `microsoft/TRELLIS.2-4B` | v2 | ~8GB | Best | 2-4 min |

## Sampler Parameters (TRELLIS.2)

| Parameter | Default | Range | Effect |
|-----------|---------|-------|--------|
| `sparse_structure_sampler_params.guidance_strength` | 7.5 | 1-15 | Structure adherence to image |
| `shape_slat_sampler_params.guidance_strength` | 7.5 | 1-15 | Shape detail |
| `tex_slat_sampler_params.guidance_strength` | 1.0 | 0-5 | Texture adherence |
| `pipeline_type` | `1024_cascade` | `512`, `1024`, `1024_cascade` | Resolution/quality |

**Pipeline types:**
- `512`: Fastest, single-pass at 512³
- `1024`: Better, single-pass at 1024³
- `1024_cascade`: Best, 512→1024 cascade (default)

## Output Formats (TRELLIS.2)

- **GLB**: Use `o_voxel.postprocess.to_glb()` — see Quick Start example
- **PLY**: Gaussian splatting — use `render_utils` from `trellis2.utils`
- **Preview**: `render_utils.render_video()` for MP4/GIF

## Multi-View Generation (TRELLIS.2)

```python
outputs = pipeline.run(
    images=[img1, img2, img3],  # list of PIL Images
    seed=42,
    pipeline_type='1024_cascade',
)
```

3-4 views of same object from different angles.

## Dependencies

See `references/dependencies.md` for full install details.

Core:
- `torch` 2.x + CUDA
- `diffusers`, `transformers`, `accelerate`, `safetensors`
- `rembg`, `onnxruntime` (background removal)
- `trimesh`, `open3d` (mesh processing)
- `spconv-cu120` or `spconv-cu118` (sparse convolution)
- `imageio`, `imageio-ffmpeg` (video export)
- `o-voxel` (GLB export — installed from TRELLIS.2 repo submodule)

## Pitfalls

- **TRELLIS v1 vs v2 confusion**: These are completely different packages. `trellis` ≠ `trellis2`. Different GitHub repos, different HF repos, different pipeline classes, different APIs. Always check which version the user's code/notebook targets.
- **No setup.py/pyproject.toml in buckets**: HF buckets with only `.safetensors` files cannot be installed with `pip install -e .`. TRELLIS.2 needs both `.json` config AND `.safetensors` per model module. Use GitHub clone + HF `snapshot_download` instead.
- **o-voxel is a submodule**: In TRELLIS.2, `o-voxel` is a git submodule at `TRELLIS2/o-voxel/`. Install with `pip install -e o-voxel` after cloning the main repo. It provides `o_voxel.postprocess.to_glb()`.
- **Colab path assumptions**: Workflow scripts often hardcode `/content/TRELLIS2`. In WSL, use `~/projects/TRELLIS2/` or equivalent.
- **hf CLI confusion**: Bucket sync requires the pipx `hf` binary, not the pip `huggingface_hub` CLI. See `huggingface-hub` skill for details.
- **DinoV2 vs DinoV3**: TRELLIS v1 uses DinoV2. TRELLIS.2 uses DinoV3-ViT-L. The pipeline.json config specifies which model class to instantiate.
- **rembg model**: TRELLIS v1 uses `u2net`. TRELLIS.2 uses `BiRefNet` (via its own rembg wrapper in `trellis2/pipelines/rembg/`).
- **spconv version**: Use `spconv-cu120` for CUDA 12.x/13.x. `spconv-cu118` as fallback.
- **SPCONV_ALGO**: Set `os.environ['SPCONV_ALGO'] = 'native'` BEFORE importing trellis2 to skip benchmarking.
- **First run slow**: Model downloads take ~5-10 min for TRELLIS.2-4B (~13.6GB). Subsequent runs use HF cache.
- **VRAM**: TRELLIS.2-4B needs ~8GB. On 8GB cards, close other GPU processes. Use `pipeline.low_vram = True` to move models between CPU/GPU during inference.
- **518x518 required**: Don't change this — it's hardcoded by DinoV2's patch grid (37*14). TRELLIS.2 may use different resolution via DinoV3.
- **TRELLIS.2 pipeline API**: Uses `pipeline_type` string + sampler param dicts (`sparse_structure_sampler_params`, `shape_slat_sampler_params`, `tex_slat_sampler_params`), NOT the v1 API of flat `cfg_scale` / `density_temperature` kwargs.

## Reference Files

- `references/preprocessing.md` — Image preprocessing pipeline details
- `references/dependencies.md` — Full dependency list and install commands
- `references/trellis2_notebook_template.md` — Known-good Colab notebook template with correct TRELLIS.2 API patterns and common error table
- `scripts/preprocess_for_trellis.py` — Standalone image preprocessor script
- `scripts/preprocess_for_trellis.py` — Standalone image preprocessor script
