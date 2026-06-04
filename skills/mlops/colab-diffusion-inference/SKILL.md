---
name: colab-diffusion-inference
description: Serve image generation diffusion models (Stable Diffusion, SDXL, FLUX, SD3) via Google Colab GPU + Gradio public URL. Handles quantization, optimization, T4/A100 configs.
---

# Colab Diffusion Inference — Image Generation

Serve diffusion-based image generation models on Google Colab GPU with Gradio UI.

## Supported Architectures

| Model | Params | VRAM (fp16) | VRAM (optimized) | T4 OK |
|-------|--------|-------------|-------------------|-------|
| SD 1.5 | 860MB | ~4GB | ~2GB | ✅ |
| SD 2.1 | 860MB | ~4GB | ~2GB | ✅ |
| SDXL | 2.6B | ~8GB | ~4GB | ✅ |
| SD3 Medium | 2B | ~10GB | ~5GB | ✅ |
| FLUX.1-dev | 12B | ~24GB | ~12GB | ❌ (needs L4/A100) |
| FLUX.1-schnell | 12B | ~24GB | ~12GB | ❌ |
| SD3.5 Large | 8B | ~16GB | ~8GB | ✅ (with optimizations) |

## Method 1: diffusers (Recommended)

### requirements.txt
```
torch>=2.4.0
diffusers>=0.32.0
transformers>=4.48.0
accelerate>=1.3.0
gradio>=5.0.0
safetensors>=0.5.0
Pillow>=11.0.0
```

### Notebook Cell — Install
```python
!pip install torch diffusers transformers accelerate gradio safetensors Pillow -q
```

### Notebook Cell — SDXL (T4 optimized)
```python
import torch
from diffusers import StableDiffusionXLPipeline
import gradio as gr

pipe = StableDiffusionXLPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16,  # T4: float16
    use_safetensors=True,
    variant="fp16",
)
pipe = pipe.to("cuda")

# T4 optimizations
pipe.enable_model_cpu_offload()  # Saves ~4GB VRAM
pipe.enable_vae_slicing()        # Saves ~1GB VRAM
# pipe.enable_xformers_memory_efficient_attention()  # +speed

def generate(prompt, negative_prompt="", steps=30, guidance=7.5, seed=-1):
    import random
    if seed == -1:
        seed = random.randint(0, 2**32 - 1)
    generator = torch.Generator("cuda").manual_seed(seed)
    image = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        num_inference_steps=steps,
        guidance_scale=guidance,
        generator=generator,
    ).images[0]
    return image, seed

with gr.Blocks(title="SDXL Generator") as demo:
    gr.Markdown("# 🎨 Stable Diffusion XL")
    with gr.Row():
        with gr.Column():
            prompt = gr.Textbox(label="Prompt", lines=3)
            neg_prompt = gr.Textbox(label="Negative Prompt", value="blurry, bad quality")
            steps = gr.Slider(10, 50, value=30, step=1, label="Steps")
            guidance = gr.Slider(1, 20, value=7.5, step=0.5, label="CFG Scale")
            seed = gr.Number(value=-1, label="Seed (-1=random)")
            btn = gr.Button("Generate")
        with gr.Column():
            output = gr.Image(label="Output")
            seed_out = gr.Number(label="Used Seed")
    btn.click(generate, [prompt, neg_prompt, steps, guidance, seed], [output, seed_out])

demo.launch(share=True, debug=True)
```

### Notebook Cell — FLUX (L4/A100)
```python
import torch
from diffusers import FluxPipeline
import gradio as gr

pipe = FluxPipeline.from_pretrained(
    "black-forest-labs/FLUX.1-dev",
    torch_dtype=torch.bfloat16,  # FLUX needs bf16
)
pipe.enable_model_cpu_offload()

def generate(prompt, steps=28, guidance=3.5):
    image = pipe(prompt, num_inference_steps=steps, guidance_scale=guidance).images[0]
    return image

gr.Interface(generate, ["text", gr.Slider(1, 50, value=28)], "image", title="FLUX").launch(share=True)
```

## Method 2: Stable Diffusion WebUI (AUTOMATIC1111)

Best for: full-featured UI, LoRA support, img2img, inpainting.

### Notebook Cell — One-Click Setup
```python
# Clone and setup
!git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui /content/sd-webui

# Download model (SDXL example)
!wget -O /content/sd-webui/models/Stable-diffusion/sdxl_base.safetensors \
    "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors"

# Launch with Gradio public URL
%cd /content/sd-webui
!python launch.py --share --xformers --enable-insecure-extension-access --no-half-vae
```

### With LoRA
```python
# Download LoRA
!wget -O /content/sd-webui/Lora/mylora.safetensors "URL_TO_LORA"

# In prompt use: <lora:mylora:0.8>
```

## Optimization Techniques

| Technique | VRAM Saved | Speed Impact | How |
|-----------|------------|--------------|-----|
| `enable_model_cpu_offload()` | ~4GB | -20% | Moves unused parts to CPU |
| `enable_vae_slicing()` | ~1GB | -5% | Processes VAE in slices |
| `enable_vae_tiling()` | ~2GB | -10% | For large images |
| `xformers` / `sdp` | ~1GB | +30% | Memory-efficient attention |
| `torch.compile()` | 0 | +20% | PyTorch 2.0+ optimization |
| FP16 (T4) | 50% | +10% | `torch.float16` |
| INT8 quantization | 75% | -10% | Via `optimum-quanto` |

### Apply All T4 Optimizations
```python
pipe = StableDiffusionXLPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16,
    use_safetensors=True,
)
pipe = pipe.to("cuda")
pipe.enable_model_cpu_offload()
pipe.enable_vae_slicing()
pipe.enable_vae_tiling()
# For PyTorch 2.0+:
# pipe.unet = torch.compile(pipe.unet, mode="reduce-overhead")
```

## SD3 / SD3.5 Specific

```python
from diffusers import StableDiffusion3Pipeline

pipe = StableDiffusion3Pipeline.from_pretrained(
    "stabilityai/stable-diffusion-3.5-large",
    torch_dtype=torch.float16,
)
pipe.enable_model_cpu_offload()
```

## Common Issues

| Problem | Fix |
|---------|-----|
| OOM on T4 with SDXL | Add `enable_model_cpu_offload()` + `enable_vae_slicing()` |
| Black images | Use `variant="fp16"` and `torch.float16` |
| Slow generation | Reduce steps to 20-25, use xformers |
| VAE decode OOM | Add `enable_vae_tiling()` for images >1024px |
| FLUX OOM on T4 | FLUX needs 12GB+ even optimized — use L4/A100 |
| NSFW filter | Add `safety_checker=None` to pipeline |
| Colab timeout | Use shorter generation, save to Drive |
