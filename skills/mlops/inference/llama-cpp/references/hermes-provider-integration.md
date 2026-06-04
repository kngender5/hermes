# llama.cpp as Hermes Provider — Profile Integration Guide

## Bash Reserved Word Pitfall

`local` is a bash reserved word. The profile wrapper at `~/.local/bin/local` CANNOT be invoked as just `local`. Always use full path `~/.local/bin/local`.

## Context Length Minimum

Hermes requires minimum 64K context. Setting `context_length: 32768` causes ValueError. Always set at least `65536` in the profile config. The `--ctx-size` flag on llama-server must match.

**Important:** Standard Qwen3-14B has `max_position_embeddings: 40960` (40K) — **below** the 64K minimum. You MUST use the Unsloth 128K variant:
```
unsloth/Qwen3-14B-128K-GGUF  →  Qwen3-14B-128K-Q3_K_M.gguf (or Q4_K_M.gguf)
```

## Port Conflicts

SearXNG uses port 8080. Use 18080 for llama-server. Check with `ss -tlnp | grep 8080`.

## Ubuntu 25.04 + CUDA 12.8 Header Patches

Building llama.cpp with CUDA on Ubuntu 25.04 (glibc 2.43) requires patching two CUDA headers:

1. **crt/host_config.h** — bypass GCC version check (GCC 15 not officially supported):
   `sudo sed -i 's/#error -- unsupported GNU version! gcc versions later than 14 are not supported!.*/#warning -- GCC 15 allowed (patched)/' /usr/local/cuda/targets/x86_64-linux/include/crt/host_config.h`

2. **crt/math_functions.h** — add noexcept to conflicting declarations and comment out __func__ wrappers:
   - sinpi, cospi, sinpif, cospif: add ` noexcept(true)` to extern declarations
   - rsqrt, rsqrtf: add ` noexcept(true)` to extern declarations
   - Comment out `__func__(double rsqrt(double a))`, `__func__(double sinpi(double a))`, `__func__(double cospi(double a))`, `__func__(float rsqrtf(float a))`, `__func__(float sinpif(float a))`, `__func__(float cospif(float a))`
   - Comment out `__MATH_FUNCTIONS_DECL__ float rsqrt/sinpi/cospi` file-scope declarations

3. Install GCC 13: `sudo apt install gcc-13 g++-13`
4. Use as host compiler: `-DCMAKE_CUDA_HOST_COMPILER=/usr/bin/g++-13`

Test compile before running cmake: `nvcc -std=c++17 --compiler-bindir /usr/bin/g++-13 -o /tmp/test /tmp/test.cu`

## Reasoning Model Output (Qwen 3.6+)

Output goes to `reasoning_content` field, not `content`. The `content` field may appear empty. This is expected behavior.

## --log-format Flag

`--log-format json` is NOT available in all builds. If llama-server fails to start with "invalid argument: --log-format", remove the flag.

## GPU Offload for RTX 4060 (8GB)

27B Q4_K_M (~16GB) cannot fit fully in 8GB VRAM. Partial offload (`--n-gpu-layers 10-20`) creates a PCIe data transfer bottleneck that negates the GPU speed benefit.

**Recommendations:**
- **27B model:** Use `--n-gpu-layers 0` (all CPU). ~3 tok/s.
- **14B 128K Q3_K_M (~6.9GB):** Partial offload `--n-gpu-layers 20` feasible.
- **For max GPU speed:** Use 7B with `--n-gpu-layers 99`. ~30-50 tok/s.
- **Sweet spot for RTX 4060 8GB:** 7B Q4_K_M fully offloaded, or 14B Q3_K_M partial

Monitor with `nvidia-smi` after starting server to verify GPU memory allocation.

## Model Name Matching

`model.default` in the profile config must exactly match the model ID that llama-server reports via `/v1/models`. Run `curl http://127.0.0.1:18080/v1/models` to see the exact name. Using an alias causes Hermes to fail model lookup, falling back to default context of 32768 and rejecting it as below the 64K minimum.

Example: if llama-server reports `"id": "Qwen3-14B-128K-Q3_K_M.gguf"`, then:
```yaml
model:
  default: Qwen3-14B-128K-Q3_K_M.gguf   # must match exactly
```

## context_length Placement

Hermes reads `model.context_length` (top-level), NOT `providers.llama.cpp.context_length`. BOTH must be set to >=65536:

```yaml
model:
  context_length: 65536          # <- Hermes checks THIS
providers:
  llama.cpp:
    context_length: 65536          # <- also set this for consistency
```

## Config Template

`~/.hermes/profiles/local/config.yaml`:

**IMPORTANT:** Replace the model name with the EXACT model ID from your llama-server's `/v1/models` endpoint.

```yaml
model:
  api_mode: chat_completions
  base_url: http://127.0.0.1:18080/v1
  default: Qwen3-14B-128K-Q3_K_M.gguf    # MUST match /v1/models ID exactly
  context_length: 65536                    # Hermes checks THIS top-level key
  provider: llama.cpp
providers:
  llama.cpp:
    name: llama.cpp local
    base_url: http://127.0.0.1:18080/v1
    api_mode: chat_completions
    default_model: Qwen3-14B-128K-Q3_K_M.gguf
    context_length: 65536
    key_env: LLAMA_CPP_API_KEY
    rate_limit_delay: 0
    request_timeout_seconds: 300
```

## Server Start Command

```bash
llama-server \
  --model /path/to/model.gguf \
  --host 127.0.0.1 --port 18080 \
  --ctx-size 65536 --n-gpu-layers 20 \
  --jinja --metrics
```

First load takes 30-60s. Poll health: `curl http://127.0.0.1:18080/health`

## Downloading Models via `hf download`

The `hf download` CLI (from `huggingface_hub`) uses different flags than the Python API:

```bash
# CORRECT - CLI syntax
hf download <repo> <filename> --local-dir <path>

# WRONG - Python API flags, not CLI
hf download <repo> <filename> --local-dir <path> --local-dir-use-symlinks=false  # FAILS
```

- Always include `.gguf` extension in the filename argument.
- The CLI downloads to `.cache/huggingface/download/` inside `--local-dir`, then moves to final location. Don't panic if you see an `.incomplete` file.
- Large models (6-7GB) take 15-30 min. No progress bar until download starts after LFS pointer resolution.

## Finding 128K Context Variants

Standard Qwen3-14B has `max_position_embeddings: 40960` - below Hermes 64K minimum. Use Unsloth's 128K variants:

```bash
# List available quants in a 128K repo
python3 -c "
from huggingface_hub import HfApi
api = HfApi()
files = api.list_repo_files('unsloth/Qwen3-14B-128K-GGUF', repo_type='model')
for f in files:
    if '.gguf' in f.lower():
        print(f)
"
```

Key repo: `unsloth/Qwen3-14B-128K-GGUF`
- `Qwen3-14B-128K-Q3_K_M.gguf` (~6.9GB) - best for RTX 4060 8GB partial offload
- `Qwen3-14B-128K-Q4_K_M.gguf` (~8.5-9GB) - too large for 8GB VRAM full offload

Download:
```bash
hf download unsloth/Qwen3-14B-128K-GGUF Qwen3-14B-128K-Q3_K_M.gguf \
    --local-dir ~/models/Qwen3-14B-128K-Q3_K_M
```
