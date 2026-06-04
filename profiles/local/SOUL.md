# SOUL.md — Local Agent Profile

This profile (named `local`) uses llama.cpp with a locally-hosted model.
No cloud APIs — everything runs on your hardware.

## Model
- Primary: Qwen3.6-27B-Q4_K_M (16GB GGUF, on H: drive)
- Vision: mmproj-Qwen3.6-27B-BF16 (889MB)
- Server: llama-server on port 8080

## Usage
- `hermes-local start` — start the llama-server
- `hermes-local chat` — interactive chat with local model
- `hermes-local stop` — stop the server
- `local chat` — use the Hermes `local` profile directly

## Performance Notes
- RTX 4060 8GB VRAM — partial GPU offload (~20 layers)
- Rest runs on system RAM (45GB available)
- Expect ~3-8 tokens/sec depending on context size
- First load takes ~30s to mmap the model

## Current Build
- CPU-only build pending CUDA toolkit installation
- Will rebuild with `-DGGML_CUDA=1 -DCMAKE_CUDA_ARCHITECTURES="89"` once CUDA toolkit finishes
