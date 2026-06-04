# TRELLIS.2 Colab Notebook Template

## Cell Structure

A known-good TRELLIS.2 Colab notebook has 4 cells:

### Cell 1: Installation

```python
import os, subprocess
os.environ['SPCONV_ALGO'] = 'native'

subprocess.run(["apt-get", "update", "-qq"], check=True)
subprocess.run(["apt-get", "install", "-y", "-qq", "git-lfs", "ninja-build", "cmake"], check=True)

!pip install -q torch torchvision --index-url https://download.pytorch.org/whl/cu121 2>/dev/null
!pip install -q trimesh pillow numpy imageio imageio-ffmpeg tqdm easydict opencv-python-headless
!pip install -q transformers accelerate safetensors diffusers huggingface_hub
!pip install -q rembg gradio==6.0.1 kornia timm zstandard pandas
!pip install -q git+https://github.com/EasternJournalist/utils3d.git@9a4eb15e4021b67b12c460c7ec8

# Clone TRELLIS.2 (includes trellis2/ + o-voxel/)
!git clone --recursive https://github.com/microsoft/TRELLIS.2.git /content/TRELLIS2
%cd /content/TRELLIS2
!pip install -e . -q
!pip install -e o-voxel -q
%cd /content

!git clone --recursive https://github.com/NVlabs/nvdiffrast.git /tmp/nvdiffrast
!pip install /tmp/nvdiffrast --no-build-isolation -q
```

### Cell 2: Checkpoint Selection

Two options:

**Option A — Download from HF (recommended):**
```python
from huggingface_hub import snapshot_download
import shutil

snapshot_download(repo_id="microsoft/TRELLIS.2-4B", local_dir="/content/TRELLIS2_hf", local_dir_use_symlinks=False)
shutil.copytree("/content/TRELLIS2_hf/ckpts", "/content/TRELLIS2/ckpts", dirs_exist_ok=True)
shutil.copy2("/content/TRELLIS2_hf/pipeline.json", "/content/TRELLIS2/pipeline.json")
```

**Option B — Sync from HF bucket (only if bucket has BOTH .json + .safetensors):**
```python
import shutil, subprocess

if not shutil.which("hf"):
    subprocess.run(["pip", "install", "-q", "uv"], check=True)
    subprocess.run(["uv", "tool", "install", "hf"], check=True)

subprocess.run(["hf", "sync", "hf://buckets/USER/BUCKET", "/content/TRELLIS2/ckpts"])
# NOTE: This will FAIL if bucket only has .safetensors without .json configs.
```

### Cell 3: Gradio App

Key imports and API:
```python
import os
os.environ.setdefault("SPCONV_ALGO", "native")

from trellis2.pipelines import Trellis2ImageTo3DPipeline

# Load pipeline
pipeline = Trellis2ImageTo3DPipeline.from_pretrained("/content/TRELLIS2")
pipeline.cuda()

# Run inference
outputs = pipeline.run(
    image,
    seed=42,
    pipeline_type="1024_cascade",  # "512", "1024", or "1024_cascade"
    sparse_structure_sampler_params={"guidance_strength": 7.5},
    shape_slat_sampler_params={"guidance_strength": 7.5},
    tex_slat_sampler_params={"guidance_strength": 1.0},
)

# Export GLB
import o_voxel
mesh = outputs[0] if isinstance(outputs, (list, tuple)) else outputs
glb = o_voxel.postprocess.to_glb(
    vertices=mesh.vertices, faces=mesh.faces,
    attr_volume=mesh.attrs, coords=mesh.coords,
    attr_layout=mesh.layout, voxel_size=mesh.voxel_size,
    aabb=[[-0.5, -0.5, -0.5], [0.5, 0.5, 0.5]],
    texture_size=1024, remesh=True, verbose=False,
)
glb.export("output.glb", extension_webp=True)
```

### Cell 4: Batch Generation

Same API as Cell 3 but loop over files.

## Common Errors in Notebooks

| Error | Cause | Fix |
|-------|-------|-----|
| `does not appear to be a Python project` | Bucket synced as code dir, no `pyproject.toml` | Clone from GitHub instead |
| `No module named 'trellis2'` | Installed v1 (`microsoft/TRELLIS`) not v2 | `git clone microsoft/TRELLIS.2` |
| `FileNotFoundError: ...json` | Bucket missing config files | Use HF `snapshot_download` |
| `o_voxel` not found | Submodule not installed | `pip install -e o-voxel` in TRELLIS2 dir |
| `SPCONV_ALGO` warning | Not set before import | `os.environ['SPCONV_ALGO'] = 'native'` |
| Syntax error on `print()` in bash | Python `print()` used in `!` bash command | Use `echo` instead of `print()` in bash |
