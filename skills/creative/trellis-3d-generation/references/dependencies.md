# TRELLIS Dependencies

## Minimal (Preprocessing Only)

```bash
pip install Pillow rembg onnxruntime opencv-python-headless numpy
```

## Full Installation — TRELLIS.2 (Recommended)

### Google Colab

```python
import os
os.environ['SPCONV_ALGO'] = 'native'

!apt-get update -qq && apt-get install -y -qq git-lfs ninja-build cmake
!git lfs install --quiet

!pip install -q torch torchvision --index-url https://download.pytorch.org/whl/cu121
!pip install -q diffusers transformers accelerate safetensors huggingface_hub
!pip install -q pillow rembg onnxruntime opencv-python-headless
!pip install -q trimesh open3d igraph easydict rembg
!pip install -q imageio imageio-ffmpeg scipy ninja
!pip install -q spconv-cu120 || pip install -q spconv-cu118
!pip install -q gradio==6.0.1 kornia timm zstandard pandas

# Clone TRELLIS.2 repo (includes trellis2/ package + o-voxel/ submodule)
!git clone --recursive https://github.com/microsoft/TRELLIS.2.git /content/TRELLIS2
%cd /content/TRELLIS2
!pip install -e . -q        # trellis2 package
!pip install -e o-voxel -q  # GLB export
%cd /content

# Render lib
!git clone --recursive https://github.com/NVlabs/nvdiffrast.git /tmp/nvdiffrast
!pip install /tmp/nvdiffrast --no-build-isolation -q

# Download checkpoints from HF (13.6GB, ~5-10 min)
from huggingface_hub import snapshot_download
snapshot_download(repo_id="microsoft/TRELLIS.2-4B", local_dir="/content/TRELLIS2_hf", local_dir_use_symlinks=False)
# Copy to trellis2 expected location
import shutil
shutil.copytree("/content/TRELLIS2_hf/ckpts", "/content/TRELLIS2/ckpts", dirs_exist_ok=True)
shutil.copy2("/content/TRELLIS2_hf/pipeline.json", "/content/TRELLIS2/pipeline.json")
```

### WSL2 / Local

Target conda env with PyTorch 2.x + CUDA already installed:

```bash
# Core ML stack
pip install diffusers transformers accelerate safetensors huggingface_hub

# Image processing + rendering
pip install pillow rembg onnxruntime opencv-python-headless
pip install trimesh open3d igraph easydict
pip install imageio imageio-ffmpeg scipy ninja

# Sparse convolution
pip install spconv-cu120 || pip install spconv-cu118

# TRELLIS.2 from GitHub (includes o-voxel as submodule)
git clone --recursive https://github.com/microsoft/TRELLIS.2.git ~/projects/TRELLIS2
cd ~/projects/TRELLIS2
pip install -e .        # trellis2 package
pip install -e o-voxel  # GLB export

# Optional renderers
pip install git+https://github.com/JeffreyXiang/diffoctreerast.git 2>/dev/null
pip install git+https://github.com/NVlabs/nvdiffrast.git 2>/dev/null
pip install git+https://github.com/autonomousvision/mip-splatting.git 2>/dev/null
```

## Full Installation — TRELLIS v1 (Legacy)

```bash
# WSL2
git clone --depth 1 https://github.com/microsoft/TRELLIS.git /tmp/trellis
cd /tmp/trellis && pip install -e .
cd /tmp/trellis/extensions/vox2seq && pip install -e .  # optional
```

## spconv Version Mapping

| CUDA Version | Package |
|-------------|---------|
| 11.x | `spconv-cu118` |
| 12.x | `spconv-cu120` |
| 13.x | `spconv-cu120` (works via CUDA runtime compat) |

## Verification (TRELLIS.2)

```python
import os
os.environ['SPCONV_ALGO'] = 'native'

import torch
assert torch.cuda.is_available(), "CUDA not available"

from trellis2.pipelines import Trellis2ImageTo3DPipeline
print("TRELLIS.2 import OK")

from trellis2.utils import render_utils
print("TRELLIS.2 utils OK")

import o_voxel
print("o_voxel OK")

import rembg
print("rembg OK")

import spconv
print("spconv OK")
```

## Common Failures

| Symptom | Fix |
|---------|-----|
| `spconv` import fails | `pip install spconv-cu120` or `spconv-cu118` for CUDA 11.x |
| `SPCONV_ALGO` warning | Set `os.environ['SPCONV_ALGO'] = 'native'` before importing trellis2 |
| rembg slow on large images | Script auto-scales to 1024px max before rembg |
| xformers not found | Optional — TRELLIS falls back to PyTorch SDPA |
| `vox2seq` build fails (v1 only) | Optional — install with `cd extensions/vox2seq && pip install -e .` |
| `No module named 'trellis2'` | You installed v1 (`microsoft/TRELLIS`) instead of v2 (`microsoft/TRELLIS.2`). Different repos! |
| `pip install -e .` fails in bucket dir | Bucket has only safetensors, no `pyproject.toml`. Clone from GitHub instead. |
| `FileNotFoundError: {path}.json` | Each TRELLIS.2 checkpoint needs both `.json` (config) and `.safetensors` (weights). Bucket-only sync misses the `.json` files. |
| `o_voxel` not found | Install from TRELLIS.2 submodule: `pip install -e o-voxel` inside the TRELLIS2 repo. |
