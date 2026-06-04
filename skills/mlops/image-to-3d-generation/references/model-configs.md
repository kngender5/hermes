# TRELLIS Model Configurations

## Available Models

### microsoft/TRELLIS.2-4B (v2, recommended)
- **Repo**: `microsoft/TRELLIS.2-4B`
- **Params**: ~4B
- **VRAM**: ~14GB (A100 recommended)
- **Checkpoints**: 8 files in `ckpts/`
  - `ss_dec_conv3d_16l8_fp16.safetensors` — Sparse structure decoder
  - `ss_flow_img_dit_1_3B_64_bf16.safetensors` — Sparse structure flow model
  - `shape_dec_next_dc_f16c32_fp16.safetensors` — Shape SLat decoder
  - `slat_flow_img2shape_dit_1_3B_512_bf16.safetensors` — Shape SLat flow (512)
  - `slat_flow_img2shape_dit_1_3B_1024_bf16.safetensors` — Shape SLat flow (1024)
  - `tex_dec_next_dc_f16c32_fp16.safetensors` — Texture SLat decoder
  - `slat_flow_imgshape2tex_dit_1_3B_512_bf16.safetensors` — Texture SLat flow (512)
  - `slat_flow_imgshape2tex_dit_1_3B_1024_bf16.safetensors` — Texture SLat flow (1024)
- **Image conditioner**: DinoV3-L (`facebook/dinov3-vitl16-pretrain-lvd1689m`)
- **BG removal**: BiRefNet (`ZhengPeng7/BiRefNet`)
- **Default pipeline**: `1024_cascade`
- **PBR textures**: Yes (base_color, metallic, roughness)

### microsoft/TRELLIS-image-large (v1)
- **Repo**: `microsoft/TRELLIS-image-large`
- **Params**: ~1B
- **VRAM**: ~3GB (T4 compatible)
- **Checkpoints**: 6 files in `ckpts/`
  - `ss_dec_conv3d_16l8_fp16.safetensors`
  - `ss_flow_img_dit_1_3B_64_bf16.safetensors`
  - `shape_dec_next_dc_f16c32_fp16.safetensors`
  - `slat_flow_img2shape_dit_1_3B_512_bf16.safetensors`
  - `tex_dec_next_dc_f16c32_fp16.safetensors`
  - `slat_flow_imgshape2tex_dit_1_3B_512_bf16.safetensors`
- **Image conditioner**: DinoV2-L (`dinov2_vitl14`)
- **BG removal**: rembg/u2net
- **PBR textures**: No

### TencentARC/Pixal3D-T (v2)
- **Repo**: `TencentARC/Pixal3D-T`
- **Params**: ~4B+
- **VRAM**: ~18GB
- **Checkpoints**: 7 files
- **Image conditioner**: DinoV3-L
- **BG removal**: BiRefNet
- **Default pipeline**: `1024_cascade`

## pipeline.json Key Fields

```json
{
  "name": "Trellis2ImageTo3DPipeline",
  "args": {
    "models": {
      "sparse_structure_decoder": "ckpts/ss_dec_conv3d_16l8_fp16",
      "sparse_structure_flow_model": "ckpts/ss_flow_img_dit_1_3B_64_bf16",
      "shape_slat_decoder": "ckpts/shape_dec_next_dc_f16c32_fp16",
      "shape_slat_flow_model_512": "ckpts/slat_flow_img2shape_dit_1_3B_512_bf16",
      "shape_slat_flow_model_1024": "ckpts/slat_flow_img2shape_dit_1_3B_1024_bf16",
      "tex_slat_decoder": "ckpts/tex_dec_next_dc_f16c32_fp16",
      "tex_slat_flow_model_512": "ckpts/slat_flow_imgshape2tex_dit_1_3B_512_bf16",
      "tex_slat_flow_model_1024": "ckpts/slat_flow_imgshape2tex_dit_1_3B_1024_bf16"
    },
    "sparse_structure_sampler": {
      "name": "FlowEulerGuidanceIntervalSampler",
      "args": { "sigma_min": 1e-5 },
      "params": { "steps": 12, "guidance_strength": 7.5, ... }
    },
    "shape_slat_sampler": { ... },
    "tex_slat_sampler": { ... },
    "shape_slat_normalization": { "mean": [...], "std": [...] },
    "tex_slat_normalization": { "mean": [...], "std": [...] },
    "image_cond_model": { "name": "DinoV3FeatureExtractor", "args": {...} },
    "rembg_model": { "name": "BiRefNet", "args": {...} },
    "default_pipeline_type": "1024_cascade"
  }
}
```

## VRAM Requirements by Pipeline Type

| Pipeline | Resolution | VRAM (4B model) | VRAM (1B model) |
|----------|-----------|-----------------|-----------------|
| `512` | 512px | ~6GB | ~2GB |
| `1024` | 1024px | ~10GB | ~4GB |
| `1024_cascade` | 512→1024 | ~12GB | ~5GB |
| `1536_cascade` | 512→1536 | ~16GB | ~7GB |

## Attention Backends

| Backend | Speed | VRAM | Compatibility |
|---------|-------|------|---------------|
| `sdpa` | Medium | Low | All GPUs (safe default) |
| `flash_attn` | Fast | Medium | A100/H100 (not T4) |
| `xformers` | Fast | Medium | T4/A100 (may have build issues) |

Set via: `os.environ['ATTN_BACKEND'] = 'sdpa'` before importing trellis.
