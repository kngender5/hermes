# TRELLIS v1 vs TRELLIS.2 — Complete API Mapping

## Package Installation

| Aspect | v1 | v2 |
|--------|----|----|
| Repo | `microsoft/TRELLIS` | `microsoft/TRELLIS.2` |
| Clone | `git clone --depth 1` | `git clone --recursive` (submodules required) |
| Install method | `pip install -e .` | PYTHONPATH (`sys.path.insert(0, REPO_DIR)`) |
| Import | `import trellis` | `import trellis2` |

## Pipeline Class

| Aspect | v1 | v2 |
|--------|----|----|
| Class | `TrellisImageTo3DPipeline` | `Trellis2ImageTo3DPipeline` |
| Import | `from trellis.pipelines import TrellisImageTo3DPipeline` | `from trellis2.pipelines import Trellis2ImageTo3DPipeline` |
| Load | `PipelineClass.from_pretrained(path)` | `PipelineClass.from_pretrained(path, config_file="pipeline.json")` |

## Sampler Parameters

| Aspect | v1 | v2 |
|--------|----|----|
| Sparse structure | `sparse_structure_sampler_params` | `sparse_structure_sampler_params` |
| Structured latent | `slat_sampler_params` (single) | `shape_slat_sampler_params` + `tex_slat_sampler_params` (split) |
| Key names | `cfg_strength`, `cfg_interval`, `rescale_t` | `guidance_strength`, `guidance_rescale`, `guidance_interval`, `rescale_t` |

### v1 Sampler Params
```python
sparse_structure_sampler_params={
    "steps": 12, "cfg_strength": 7.5,
    "cfg_interval": [0.5, 1.0], "rescale_t": 3.0,
},
slat_sampler_params={
    "steps": 12, "cfg_strength": 7.5,
    "cfg_interval": [0.5, 1.0], "rescale_t": 3.0,
},
```

### v2 Sampler Params
```python
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
```

## Pipeline Types (v2 only)

v1 has no `pipeline_type` parameter. v2 supports:
- `512` — 512px resolution, ~6GB VRAM
- `1024` — 1024px resolution, ~10GB VRAM
- `1024_cascade` — 512→1024 cascade, ~12GB VRAM (default, best quality)
- `1536_cascade` — 512→1536 cascade, ~16GB VRAM (needs A100)

## Image Preprocessing

| Aspect | v1 | v2 |
|--------|----|----|
| Resize before bg removal | Scale to max 1024px | Scale to max 1024px |
| BG removal | rembg/u2net | BiRefNet (via `trellis2/pipelines/rembg/BiRefNet.py`) |
| BBox padding | 120% (`size * 1.2`) | 100% (`size * 1`, no padding) |
| Final resize | 518x518 (DinoV2 patch grid) | None (handled by `get_cond()` at runtime) |
| Output size | Fixed 518x518 | Variable |

## Image Conditioning

| Aspect | v1 | v2 |
|--------|----|----|
| Model | DinoV2 (via `torch.hub.load('facebookresearch/dinov2', ...)`) | DinoV3 (via `transformers.DINOv3ViTModel`) |
| Transform | `Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])` | Same |
| Resolution | Fixed 518x518 | Dynamic (512 or 1024 based on pipeline_type) |

## Output Format

| Aspect | v1 | v2 |
|--------|----|----|
| Return type | `dict` with keys `gaussian`, `mesh`, `radiance_field` | `List[MeshWithVoxel]` |
| Access | `outputs['gaussian'][0]`, `outputs['mesh'][0]` | `outputs[0]` (first mesh) |
| Gaussian | `outputs['gaussian'][0].save_ply()` | Not directly available |
| Mesh | `outputs['mesh'][0]` | `outputs[0]` with `.vertices`, `.faces`, `.attrs`, `.coords`, `.layout`, `.voxel_size` |

## GLB Export

### v1
```python
from trellis.utils import postprocessing_utils
glb = postprocessing_utils.to_glb(
    outputs['gaussian'][0],
    outputs['mesh'][0],
    simplify=0.95,
    texture_size=1024,
)
glb.export("output.glb")
```

### v2
```python
import o_voxel
mesh = outputs[0]
glb = o_voxel.postprocess.to_glb(
    vertices=mesh.vertices,
    faces=mesh.faces,
    attr_volume=mesh.attrs,
    coords=mesh.coords,
    attr_layout=mesh.layout,
    voxel_size=mesh.voxel_size,
    aabb=[[-0.5, -0.5, -0.5], [0.5, 0.5, 0.5]],
    texture_size=1024,
    remesh=True,
    verbose=False,
)
glb.export("output.glb", extension_webp=True)
```

## Model Checkpoints

### v1 (`microsoft/TRELLIS-image-large`)
- 6 checkpoints in `ckpts/`
- ~3GB total
- Files: `ss_dec_conv3d_16l8_fp16.safetensors`, `ss_flow_img_dit_1_3B_64_bf16.safetensors`, etc.

### v2 (`microsoft/TRELLIS.2-4B`)
- 8 checkpoints in `ckpts/`
- ~14GB total
- Files: `ss_dec_conv3d_16l8_fp16.safetensors`, `ss_flow_img_dit_1_3B_64_bf16.safetensors`, `shape_dec_next_dc_f16c32_fp16.safetensors`, `slat_flow_img2shape_dit_1_3B_512_bf16.safetensors`, `slat_flow_img2shape_dit_1_3B_1024_bf16.safetensors`, `tex_dec_next_dc_f16c32_fp16.safetensors`, `slat_flow_imgshape2tex_dit_1_3B_512_bf16.safetensors`, `slat_flow_imgshape2tex_dit_1_3B_1024_bf16.safetensors`

## pipeline.json Structure

### v1
```json
{
  "name": "Trellis2ImageTo3DPipeline",
  "args": {
    "models": { "sparse_structure_decoder": "...", ... },
    "sparse_structure_sampler": { "name": "FlowEulerGuidanceIntervalSampler", "args": {...}, "params": {...} },
    "slat_sampler": { ... },
    "image_cond_model": { "name": "DinoV2FeatureExtractor", "args": {"model_name": "dinov2_vitl14"} },
    "rembg_model": { "name": "rembg", "args": {"model_name": "u2net"} }
  }
}
```

### v2
```json
{
  "name": "Trellis2ImageTo3DPipeline",
  "args": {
    "models": { "sparse_structure_decoder": "...", ... },
    "sparse_structure_sampler": { "name": "FlowEulerGuidanceIntervalSampler", "args": {...}, "params": {...} },
    "shape_slat_sampler": { ... },
    "tex_slat_sampler": { ... },
    "image_cond_model": { "name": "DinoV3FeatureExtractor", "args": {"model_name": "facebook/dinov3-vitl16-pretrain-lvd1689m"} },
    "rembg_model": { "name": "BiRefNet", "args": {"model_name": "ZhengPeng7/BiRefNet"} },
    "default_pipeline_type": "1024_cascade"
  }
}
```

## Colab-Specific Dependencies

| Package | v1 | v2 |
|---------|----|----|
| gradio | `gradio==4.44.1` + `gradio_litmodel3d==0.0.1` | `gradio==6.0.1` |
| rembg | `rembg` | `rembg` (fallback) |
| transformers | Not needed for pipeline | Required for DinoV3 + BiRefNet |
| timm | Not needed | Required for BiRefNet |
| kornia | Not needed | Required |
| zstandard | Not needed | Required for o-voxel |
| easydict | Recommended | Required |
| lpips | Not needed | Recommended |
| pandas | Not needed | Recommended |
