# GGUF Troubleshooting Guide

## Ubuntu 25.04 / CUDA 12.8 Header Conflicts

**Symptom:** cmake configure or nvcc compile fails with errors about `bits/mathcalls.h` exception specification conflicts (sinpi, cospi, rsqrt, etc.) and/or "unsupported GCC version! gcc versions later than 14".

**Root cause:** Ubuntu 25.04 ships glibc 2.43 which declares `noexcept(true)` on math functions (cospi, sinpi, rsqrt, etc.). CUDA 12.8's `crt/math_functions.h` declares the same functions WITHOUT noexcept, causing conflicts. Additionally, CUDA 12.8's `crt/host_config.h` rejects GCC 15+.

**Fix (in order):**

1. Install GCC 13:
   ```bash
   sudo apt install gcc-13 g++-13
   ```

2. Patch `crt/host_config.h` to allow GCC 15:
   ```bash
   sudo sed -i 's/#error -- unsupported GCC version! gcc versions later than 14 are not supported!.*/#warning -- GCC 15 allowed (patched)/' \
     /usr/local/cuda/targets/x86_64-linux/include/crt/host_config.h
   ```

3. Patch `crt/math_functions.h` — add noexcept to conflicting extern declarations AND comment out conflicting __func__ wrappers:
   ```bash
   MHDIR=/usr/local/cuda/targets/x86_64-linux/include/crt
   # Add noexcept to extern declarations
   sudo sed -i 's/^extern __DEVICE_FUNCTIONS_DECL__ __device_builtin__ double                 sinpi(double x);/extern __DEVICE_FUNCTIONS_DECL__ __device_builtin__ double                 sinpi(double x) noexcept(true);/' "$MHDIR/math_functions.h"
   sudo sed -i 's/^extern __DEVICE_FUNCTIONS_DECL__ __device_builtin__ double                 cospi(double x);/extern __DEVICE_FUNCTIONS_DECL__ __device_builtin__ double                 cospi(double x) noexcept(true);/' "$MHDIR/math_functions.h"
   sudo sed -i 's/^extern __DEVICE_FUNCTIONS_DECL__ __device_builtin__ double                 rsqrt(double x);/extern __DEVICE_FUNCTIONS_DECL__ __device_builtin__ double                 rsqrt(double x) noexcept(true);/' "$MHDIR/math_functions.h"
   sudo sed -i 's/^extern __DEVICE_FUNCTIONS_DECL__ __device_builtin__ float                  sinpif(float x);/extern __DEVICE_FUNCTIONS_DECL__ __device_builtin__ float                  sinpif(float x) noexcept(true);/' "$MHDIR/math_functions.h"
   sudo sed -i 's/^extern __DEVICE_FUNCTIONS_DECL__ __device_builtin__ float                  cospif(float x);/extern __DEVICE_FUNCTIONS_DECL__ __device_builtin__ float                  cospif(float x) noexcept(true);/' "$MHDIR/math_functions.h"
   sudo sed -i 's/^extern __DEVICE_FUNCTIONS_DECL__ __device_builtin__ float                  rsqrtf(float x);/extern __DEVICE_FUNCTIONS_DECL__ __device_builtin__ float                  rsqrtf(float x) noexcept(true);/' "$MHDIR/math_functions.h"
   # Comment out conflicting __func__ wrappers
   sudo sed -i 's/^__func__(double sinpi(double a));/\/\/ glibc-compat: __func__(double sinpi(double a));/' "$MHDIR/math_functions.h"
   sudo sed -i 's/^__func__(double cospi(double a));/\/\/ glibc-compat: __func__(double cospi(double a));/' "$MHDIR/math_functions.h"
   sudo sed -i 's/^__func__(double rsqrt(double a));/\/\/ glibc-compat: __func__(double rsqrt(double a));/' "$MHDIR/math_functions.h"
   sudo sed -i 's/^__func__(float sinpif(float a));/\/\/ glibc-compat: __func__(float sinpif(float a));/' "$MHDIR/math_functions.h"
   sudo sed -i 's/^__func__(float cospif(float a));/\/\/ glibc-compat: __func__(float cospif(float a));/' "$MHDIR/math_functions.h"
   sudo sed -i 's/^__func__(float rsqrtf(float a));/\/\/ glibc-compat: __func__(float rsqrtf(float a));/' "$MHDIR/math_functions.h"
   # Comment out file-scope __MATH_FUNCTIONS_DECL__ rsqrt/sinpi/cospi
   sudo sed -i 's/^__MATH_FUNCTIONS_DECL__ float rsqrt(const float a);/\/\/ glibc-compat: __MATH_FUNCTIONS_DECL__ float rsqrt(const float a);/' "$MHDIR/math_functions.h"
   sudo sed -i 's/^__MATH_FUNCTIONS_DECL__ float sinpi(const float a);/\/\/ glibc-compat: __MATH_FUNCTIONS_DECL__ float sinpi(const float a);/' "$MHDIR/math_functions.h"
   sudo sed -i 's/^__MATH_FUNCTIONS_DECL__ float cospi(const float a);/\/\/ glibc-compat: __MATH_FUNCTIONS_DECL__ float cospi(const float a);/' "$MHDIR/math_functions.h"
   ```

4. Test before building:
   ```bash
   echo '__device__ int f(){return 42;} int main(){return 0;}' > /tmp/test.cu
   nvcc -std=c++17 --compiler-bindir /usr/bin/g++-13 -o /tmp/test_cuda /tmp/test.cu
   ```

5. Build with GCC 13 as host compiler:
   ```bash
   cmake -B build -DCMAKE_BUILD_TYPE=Release \
     -DGGML_CUDA=1 -DGGML_CUDA_F16=1 \
     -DCMAKE_CUDA_ARCHITECTURES="89" \
     -DCMAKE_CUDA_HOST_COMPILER=/usr/bin/g++-13
   cmake --build build -j$(nproc) --target llama-server
   ```

**Note:** These patches will be overwritten by CUDA toolkit updates. Re-apply after `apt upgrade`.

## Hermes Agent — Model Context Length Check

**Symptom:** "Model X has a context window of 32,768 tokens, which is below the minimum 64,000 required by Hermes Agent."

**Root cause:** Hermes Agent enforces a minimum 64K context window. Most standard GGUF models only have 32K-40K `max_position_embeddings`.

**Diagnosis — check context length:**
```bash
# For repos that ship config.json (non-GGUF-only):
python3 -c "
from huggingface_hub import hf_hub_download
import json
p = hf_hub_download(repo_id='Qwen/Qwen3-14B', filename='config.json', repo_type='model')
d = json.load(open(p))
print('max_position_embeddings:', d.get('max_position_embeddings'))
"

# For GGUF-only repos (no config.json), check the BASE model repo instead.
# E.g. Qwen/Qwen3-14B-GGUF → check Qwen/Qwen3-14B
```

**Fix:** Use a model variant with 64K+ context. Prefer "128K" labeled variants from unsloth:
```
unsloth/Qwen3-14B-128K-GGUF  →  Qwen3-14B-128K-Q4_K_M.gguf
```

**Download:**
```bash
hf download unsloth/Qwen3-14B-128K-GGUF Qwen3-14B-128K-Q4_K_M \
    --local-dir ~/models/Qwen3-14B-128K-Q4_K_M
```

**Note:** Do NOT try to override with `model.context_length` in config.yaml — the model genuinely cannot attend beyond its trained RoPE range. You'll get silent truncation/nonsense at the boundary.

## Build Fails

**Error**: `make: *** No targets specified and no makefile found`

**Fix**:
```bash
cd llama.cpp
cmake -B build ...
```

**Error**: `fatal error: cuda_runtime.h: No such file or directory`

**Fix**:
```bash
sudo apt install nvidia-cuda-toolkit
export CUDAToolkit_ROOT=/usr/local/cuda
export PATH=/usr/local/cuda/bin:$PATH
```

## CUDA Compiler Not Found

**Error:** `No CMAKE_CUDA_COMPILER found` or `nvcc: command not found`

WSL: CUDA toolkit must be installed IN WSL (not just Windows). Driver alone is not enough.
```bash
wget -q https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-keyring_1.1-1_all.deb -O /tmp/cuda-keyring.deb
sudo dpkg -i /tmp/cuda-keyring.deb
sudo apt-get update
sudo apt-get install -y cuda-toolkit-12-8
```

Clean cmake cache between attempts:
```bash
cd llama.cpp && rm -rf build
unset CFLAGS NVCC_FLAGS CUDAHOST_CXX   # prevent env pollution
```

Also unset any stray env vars that may leak into cmake: `CFLAGS`, `NVCC_FLAGS`, `CUDAHOSTCXX`.

### GPU Offload Performance on RTX 4060 (8GB)

**Key insight:** For 14B+ dense models on 8GB VRAM, Q4_K_M ≈ 9GB which exceeds VRAM. Partial GPU offload creates PCIe bottleneck (similar to 27B).

**Recommendations:**
- **14B Q4_K_M (9GB):** Use `--n-gpu-layers 0` (all CPU). Needs ~13GB system RAM. ~3 tok/s.
- **14B Q3_K_M (~6.5GB):** Can partially offload. Try `--n-gpu-layers 40` and monitor VRAM with `nvidia-smi`.
- **For GPU speed on 8GB:** 7B Q4_K_M fully offloaded (`--n-gpu-layers 99`) = ~30-50 tok/s, OR MoE 35B-A3B fully offloaded = 15-30 tok/s with only 3B active params.
- **Never use partial offload blindly for models that barely fit** — measure with `nvidia-smi dmon` first.

## Python Bindings Issues

**Error**: `ERROR: Failed building wheel for llama-cpp-python`

**Fix**:
```bash
pip install cmake scikit-build-core
CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python --force-reinstall --no-cache-dir
```

## Inference Issues

### Slow Generation

**Problem**: Generation is slower than expected

**Solutions**:
1. **Enable GPU offload**: `--n-gpu-layers 20` (RTX 4060 8GB) or `n_gpu_layers=35` (Python)
2. **Optimize threads**: `-t 8` (match physical cores)
3. **First load is slow**: 27B Q4 takes 30-60s to mmap; subsequent requests are faster

### Out of Memory

**Error**: `CUDA out of memory` or system freeze

**Solutions**:
1. Reduce GPU layers: `--n-gpu-layers 10`
2. Use smaller quantization: Q3_K_M instead of Q4_K_M
3. Reduce context: `--ctx-size 32768`

### Server Fails to Bind Port 18080

**Error**: "couldn't bind HTTP server socket, hostname: 127.0.0.1, port: 18080"

**Cause**: Previous llama-server instance still running.
**Fix**: `pkill -f llama-server && sleep 2` before starting new instance.
Or use `ss -tlnp | grep 18080` to find and kill the specific PID.

### Garbage Output

**Problem**: Model outputs random characters

**Diagnose**:
```bash
llama-cli -m model.gguf --verbose 2>&1 | head -50
```

**Check chat format**: Must match model (chatml, llama-3, etc.)

### Connection Refused

**Error**: `Connection refused` when accessing server

SearXNG uses port 8080. If llama-server defaults to 8080, it will collide. Use port 18080.
Check: `ss -tlnp | grep 8080`

### Server Crashes Under Load

```bash
llama-server -m model.gguf --parallel 2 --timeout 300
```

## Apple Silicon Issues

### Metal Not Working

```bash
make clean
make GGML_METAL=1
CMAKE_ARGS="-DGGML_METAL=on" pip install llama-cpp-python --force-reinstall
```

## Debugging

### Enable Verbose Output

```bash
llama-cli -m model.gguf --verbose -p "Hello" -n 50
```

### Validate GGUF File

```python
import struct
with open("model.gguf", "rb") as f:
    magic = f.read(4)
    assert magic == b'GGUF', f"Invalid: {magic}"
    version = struct.unpack('<I', f.read(4))[0]
    print(f"GGUF v{version}")
```

## Getting Help

- GitHub Issues: https://github.com/ggml-org/llama.cpp/issues
- Reddit: r/LocalLLaMA

### Reporting Issues

Include: llama.cpp version, build command, model name, full error, hardware specs, OS version.
