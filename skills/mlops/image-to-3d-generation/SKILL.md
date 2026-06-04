---
name: image-to-3d-generation
description: Generate 3D models from images using AI pipelines — TRELLIS.2, TRELLIS v1, and related image-to-3D workflows. Covers Colab notebook creation, dependency installation, image preprocessing (background removal + crop), model selection, and GLB export.
version: 1.0.0
author: owl
triggers:
  - image to 3d
  - image-to-3d
  - trellis
  - trellis2
  - generate 3d
  - 3d from image
  - glb export
  - 3d model generation
  - single image 3d
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [image-to-3d, trellis, colab, 3d-generation, glb, gradio]
    category: mlops
    requires_toolsets: [file, terminal]
---

# Image-to-3D Generation

Generate 3D models from single images using TRELLIS.2 (or TRELLIS v1) pipelines, with Colab notebooks or local inference.

## When to Use

- User wants to convert an image to a 3D model
- User mentions TRELLIS, TRELLIS.2, image-to-3D, or GLB generation
- User needs a Colab notebook for cloud GPU 3D generation
- User asks about background removal for 3D model input

## Version Detection: TRELLIS v1 vs TRELLIS.2

**Always check which version the user has or needs before writing code.**

| Signal | Version |
|--------|---------|
| `from trellis2.pipelines import Trellis2ImageTo3DPipeline` | v2 |
| `from trellis.pipelines import TrellisImageTo3DPipeline` | v1 |
| `TRELLIS.2-4B`, `microsoft/TRELLIS.2` | v2 |
| `TRELLIS-image-large`, `microsoft/TRELLIS-image-large` | v1 |
| `o_voxel.postprocess.to_glb()` | v2 |
| `postprocessing_utils.to_glb()` | v1 |
| `pipeline_type` param (`512`, `1024`, `1024_cascade`) | v2 |
| 3 samplers (sparse_structure, shape_slat, tex_slat) | v2 |
| 2 samplers (sparse_structure, slat) | v1 |
| BiRefNet bg removal | v2 |
| rembg/u2net bg removal | v1 |
| DinoV3 conditioner | v2 |
| DinoV2 conditioner | v1 |
| `PIPELINE_JSON` + `PYTHONPATH` install | v2 |
| `pip install -e .` install | v1 |

**If the user has an existing .ipynb file, READ IT FIRST to determine version.**

## TRELLIS.2 Workflow (Recommended)

### 1. Installation (Colab)

```python
# System deps
!apt-get update -qq && apt-get install -y -qq git-lfs ninja-build cmake libjpeg-dev
!git lfs install --quiet 2>/dev/null || true

# PyTorch (Colab has cu121 pre-installed)
!pip install -q torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Python deps
!pip install -q trimesh pillow numpy imageio imageio-ffmpeg tqdm easydict opencv-python-headless ninja
!pip install -q transformers accelerate safetensors diffusers huggingface_hub rembg gradio==6.0.1 kornia timm zstandard pandas lpips
!pip install -q git+https://github.com/EasternJournalist/utils3d.git@9a4eb15e4021b67b12c460c7057d642626897ec8

# Attention backend (sdpa for T4, flash_attn for A100)
os.environ['ATTN_BACKEND'] = 'sdpa'  # or 'flash_attn' or 'xformers'

# Clone TRELLIS.2 — uses PYTHONPATH, NOT pip install
REPO_DIR = "/content/TRELLIS2"
!git clone --recursive https://github.com/microsoft/TRELLIS.2.git {REPO_DIR}
import site, sys
site.addsitedir(REPO_DIR)
sys.path.insert(0, REPO_DIR)

# o-voxel (GLB export with CUDA extensions)
!pip install -e {REPO_DIR}/o-voxel -q

# nvdiffrast (optional)
!pip install git+https://github.com/NVlabs/nvdiffrast.git --no-build-isolation -q
```

### 2. Model Download

```python
from huggingface_hub import snapshot_download
import shutil
from pathlib import Path

HF_REPO = "microsoft/TRELLIS.2-4B"  # or "microsoft/TRELLIS-image-large" for v1
CKPT_DIR = "/content/TRELLIS2/ckpts"

hf_local = snapshot_download(repo_id=HF_REPO, local_dir=f"/content/trellis_cache", local_dir_use_symlinks=False)

# Copy checkpoints and pipeline.json
hf_ckpts = Path(hf_local) / "ckpts"
for f in hf_ckpts.iterdir():
    shutil.copy2(f, Path(CKPT_DIR) / f.name)
shutil.copy2(Path(hf_local) / "pipeline.json", "/content/TRELLIS2/pipeline.json")
```

### 3. Inference

```python
from trellis2.pipelines import Trellis2ImageTo3DPipeline
from PIL import Image

pipeline = Trellis2ImageTo3DPipeline.from_pretrained("/content/TRELLIS2")
pipeline.cuda()

image = Image.open("input.png")
# preprocess_image does: bg removal → crop to alpha bbox → square crop → composite
processed = pipeline.preprocess_image(image)

outputs = pipeline.run(
    processed,
    seed=42,
    pipeline_type="1024_cascade",  # 512, 1024, 1024_cascade, 1536_cascade
    sparse_structure_sampler_params={
        "steps": 12, "guidance_strength": 7.5,
        "guidance_rescale": 0.7, "guidance_interval": [0.6, 1.0], "rescale_t": 5.0,
    },
    shape_slat_sampler_params={
        "steps": 12, "guidance_strength": 7.5,
        "guidance_rescale": 0.5, "guidance_interval": [0.6, 1.0], "rescale_t": 3.0,
    },
    tex_slat_sampler_params={
        "steps": 12, "guidance_strength": 1.0,
        "guidance_rescale": 0.0, "guidance_interval": [0.6, 0.9], "rescale_t": 3.0,
    },
)

mesh = outputs[0]  # List[MeshWithVoxel]
```

### 4. GLB Export

```python
import o_voxel

glb = o_voxel.postprocess.to_glb(
    vertices=mesh.vertices,
    faces=mesh.faces,
    attr_volume=mesh.attrs,
    coords=mesh.coords,
    attr_layout=mesh.layout,
    voxel_size=mesh.voxel_size,
    aabb=[[-0.5, -0.5, -0.5], [0.5, 0.5, 0.5]],
    texture_size=1024,  # 512, 1024, 2048, 4096
    remesh=True,
    verbose=False,
)
glb.export("output.glb", extension_webp=True)
```

## Image Preprocessing (Standalone)

For preprocessing without the full pipeline, use `preprocess_for_trellis2.py`:

```bash
python preprocess_for_trellis2.py input.png output.png
python preprocess_for_trellis2.py input_dir/ output_dir/ --batch
python preprocess_for_trellis2.py input.png --preview
```

The standalone preprocessor:
- Uses BiRefNet (or rembg/u2net as fallback) for background removal
- Crops to alpha bbox, makes square (no padding — matches TRELLIS.2's `size*1`)
- Composites onto configurable background color
- Does NOT resize (TRELLIS.2 handles resolution internally)

## Model Selection

| Model | Params | VRAM | Quality | Conditioner | BG Removal |
|-------|--------|------|---------|-------------|------------|
| `microsoft/TRELLIS.2-4B` | ~4B | ~14GB | Best | DinoV3-L | BiRefNet |
| `microsoft/TRELLIS-image-large` | ~1B | ~3GB | Good | DinoV2-L | u2net |

## Pipeline Types

| Type | Resolution | VRAM | Quality |
|------|-----------|------|---------|
| `512` | 512px | ~6GB | Fast, lower detail |
| `1024` | 1024px | ~10GB | Good |
| `1024_cascade` | 512→1024 | ~12GB | Best (default) |
| `1536_cascade` | 512→1536 | ~16GB | Highest (needs A100) |

## Critical Pitfalls

### Version Mismatch
- **NEVER mix v1 and v2 APIs.** Check imports first.
- v2 uses `trellis2` package (PYTHONPATH), v1 uses `trellis` package (`pip install -e .`)
- v2 output is `List[MeshWithVoxel]`, v1 output is `dict` with keys `gaussian`, `mesh`, `radiance_field`
- v2 GLB export uses `o_voxel.postprocess.to_glb()`, v1 uses `postprocessing_utils.to_glb()`

### TRELLIS.2 Installation
- TRELLIS.2 does NOT use `pip install -e .` — it uses PYTHONPATH
- `git clone --recursive` is required (submodules needed)
- `o-voxel` requires CUDA extensions (nvcc compiler) — may fail on Colab T4 without proper setup
- If `o-voxel` build fails, the notebook should still work for inference, just not GLB export

### Image Preprocessing
- TRELLIS.2 `preprocess_image` does NOT resize to 518x518 (unlike v1)
- TRELLIS.2 uses `size * 1` (no padding), v1 uses `size * 1.2` (120% padding)
- BiRefNet requires `transformers`, `torch`, `timm` — heavy dependencies
- For lightweight preprocessing, fall back to `rembg` with `u2net`

### o-voxel Dependency Chain (CRITICAL)
- `o-voxel` depends on `cumesh` (CuMesh) and `flex_gemm` from GitHub — both have CUDA extensions
- These MUST be installed explicitly BEFORE o-voxel, not via `pyproject.toml` (which often fails silently)
- Use `--no-build-isolation` for o-voxel since torch is already installed:
  ```bash
  !pip install -q git+https://github.com/JeffreyXiang/CuMesh.git
  !pip install -q git+https://github.com/JeffreyXiang/FlexGEMM.git
  !pip install -e {REPO_DIR}/o-voxel --no-build-isolation
  ```
- If `cumesh`/`flex_gemm` fail to build (e.g., missing nvcc), GLB export will not work but inference still will
- `o-voxel` also needs: `plyfile`, `zstandard`, `easydict`, `tqdm`, `trimesh`, `torch`, `numpy`

### Notebooks / .ipynb JSON Format
- When writing `.ipynb` files programmatically, cell `source` must be a JSON array of strings (one per line), NOT a single string with `\n`
- Each element should be `"line content\n"` (with literal newline at end)
- The `patch` tool can mangle notebook cell source by collapsing lines into single strings with escaped `\\n` — verify with `json.load()` after patching
- If cell source is mangled, rewrite the entire cell source as a proper array of strings using `execute_code` + `json.dump()`
- Always verify: `python3 -c "import json; json.load(open('notebook.ipynb'))"` after writing

### Colab-Specific
- Set `os.environ['SPCONV_ALGO'] = 'native'` before importing trellis to skip benchmarking
- Set `os.environ['ATTN_BACKEND'] = 'sdpa'` for T4, `flash_attn` for A100
- `gradio==6.0.1` works with Colab; `gradio==4.44.1` + `gradio_litmodel3d` for v1
- Always verify notebook JSON with `json.load()` after writing

### BiRefNet Bundling
- TRELLIS.2 bundles its own `BiRefNet` class in `trellis2/pipelines/rembg/BiRefNet.py` — NOT the pip `rembg` package
- The bundled version uses `transformers.AutoModelForImageSegmentation.from_pretrained("ZhengPeng7/BiRefNet")`
- For standalone preprocessing outside TRELLIS.2, you can either:
  - Use the bundled class directly (copy from `trellis2/pipelines/rembg/BiRefNet.py`)
  - Fall back to `rembg.new_session("u2net")` + `rembg.remove()` (lighter weight)
- BiRefNet needs `transformers`, `torch`, `timm` — heavy dependencies (~2GB download)
- u2net (rembg) is much lighter and works CPU-only

### Local WSL
- `spconv-cu120` for CUDA 12.x/13.x; `spconv-cu118` for CUDA 11.x
- BiRefNet needs GPU for reasonable speed; u2net is CPU-friendly
- `o-voxel` CUDA extensions need `nvcc` and matching CUDA toolkit

## Reference Files

- `references/trellis-v1-vs-v2-mapping.md` — Complete API diff between versions
- `references/model-configs.md` — pipeline.json structures for each model
