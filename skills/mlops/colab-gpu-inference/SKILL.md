---
name: colab-gpu-inference
description: Generate clean Colab notebooks for cloud GPU LLM inference with Gradio UI and public share links. Use when the user wants a Colab notebook to run models on cloud GPUs (T4, A100, H100) with a Gradio chat interface.
version: 1.0.0
author: owl
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [colab, gpu, inference, gradio, notebook, cloud, llm, transformers]
    category: mlops
    requires_toolsets: [file]
---

# Colab GPU Inference Notebook Generator

Generate clean, minimal Colab notebooks for running LLMs on cloud GPUs with Gradio UI and public share links.

## When to Use

- User wants a Colab notebook for cloud GPU inference
- User mentions Gradio, public link, share link, or Colab GPU runtime
- User has a model on Google Drive or HuggingFace Hub
- User wants OpenAI-compatible API endpoint on Colab

## Key Principles

1. **Minimal dependencies** — Colab has torch + CUDA pre-installed. Only install what's missing. NEVER do pip uninstall/reinstall cycles on torch.
2. **No Google Drive dependency in code logic** — mount is optional, model path is configurable
3. **BF16 default for A100/H100** (80GB+), **4-bit quant for T4** (16GB)
4. **Gradio `share=True`** for public link — this is the primary access pattern
5. **FastAPI background thread** for OpenAI-compatible API
6. **Validate JSON output** — write notebooks via Python `json.dump()`, never hand-craft JSON strings

## Notebook Structure (10 cells)

| Cell | Title | Purpose |
|------|-------|---------|
| 1 | Config | Model path, port, defaults — only cell user edits |
| 2 | Mount Drive | Optional, verify model folder |
| 3 | Install deps | Check what's present, install only missing |
| 4 | Load model | BF16 or 4-bit, `device_map="auto"`, show VRAM |
| 5 | Quick test | One-sentence generation test |
| 6 | FastAPI server | OpenAI-compatible `/v1/chat/completions` |
| 7 | Gradio UI | `share=True`, sliders for temp/tokens/top-p/top-k |
| 8 | API test | curl against local server |
| 9 | Unload | Free VRAM |

## Generation Template

Use this Python script to generate the notebook (ensures valid JSON):

```python
import json

def make_colab_notebook(model_path, port=8000, gpu_type="A100"):
    """Generate a clean Colab inference notebook as dict."""
    nb = {
        "nbformat": 4,
        "nbformat_minor": 0,
        "metadata": {
            "accelerator": "GPU",
            "colab": {"gpuType": gpuType, "provenance": []},
            "kernelspec": {"display_name": "Python 3", "name": "python3"},
            "language_info": {"name": "python"}
        },
        "cells": [
            # ... see templates/colab-inference.ipynb for full structure
        ]
    }
    return nb

# Write it
nb = make_colab_notebook("/content/drive/MyDrive/model", gpu_type="A100")
with open("output.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=2, ensure_ascii=False)

# Verify round-trip
with open("output.ipynb") as f:
    json.load(f)  # raises on invalid JSON
print("Valid notebook generated")
```

## Critical Pitfalls

### JSON Validation
- **Always** generate notebooks via Python `json.dump()`, never hand-craft JSON
- **Always** verify with `json.load()` after writing
- Colab's JS JSON parser is stricter than Python's — valid Python JSON may still fail in Colab
- Common issues: unescaped backslashes in code strings, trailing commas, BOM markers
- If Colab reports "Unexpected string at position X" but file is smaller than X, the user loaded the **wrong file** (old cached version)

### Dependency Management
- Do NOT uninstall/reinstall torch on Colab — it's pre-installed with CUDA
- Use `importlib.import_module()` to check what's present, install only missing
- Pin versions loosely: `>=4.51.0` not `==4.51.0`
- For T4 (16GB): use BitsAndBytesConfig 4-bit quant
- For A100/H100 (80GB+): BF16 full precision

### Model Loading
- Always use `device_map="auto"` for multi-GPU or single GPU
- Always use `trust_remote_code=True` for Qwen and custom models
- Show VRAM usage after load: `torch.cuda.memory_allocated() / 1e9`
- Set `model.eval()` after loading

### Gradio
- `share=True` generates public `https://xxxxx.gradio.live` link
- `server_name="0.0.0.0"` required for Colab
- Default port: 7860
- Use `inline=False` to avoid iframe issues

### FastAPI
- Run in daemon thread: `threading.Thread(target=uvicorn.run, daemon=True)`
- Default port: 8000
- Always implement `/health` and `/v1/models` endpoints
- Include VRAM cleanup in error handler: `gc.collect(); torch.cuda.empty_cache()`

## GPU VRAM Guidelines

| GPU | VRAM | Strategy |
|-----|------|----------|
| T4 | 16 GB | 4-bit quant (BitsAndBytesConfig) |
| L4 | 24 GB | 4-bit quant or BF16 for ≤13B |
| A100 | 40 GB | BF16 for ≤27B |
| A100 | 80 GB | BF16 for ≤70B |
| H100 | 80 GB | BF16 for ≤70B |

## Verification Checklist

After generating a notebook:
- [ ] Valid JSON (Python `json.load()` passes)
- [ ] All code cells have valid Python syntax
- [ ] No hardcoded paths (use config cell variables)
- [ ] Model path is a `#@param` input
- [ ] Gradio uses `share=True`
- [ ] FastAPI runs in daemon thread
- [ ] Error handlers clean up VRAM
