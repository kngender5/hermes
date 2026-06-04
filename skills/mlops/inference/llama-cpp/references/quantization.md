# GGUF Quantization Guide

Complete guide to GGUF quantization formats and model conversion.

## Hub-first quant selection

Before using generic tables, open the model repo with:

```text
https://huggingface.co/<repo>?local-app=llama.cpp
```

Prefer the exact quant labels and sizes shown in the `Hardware compatibility` section of the fetched `?local-app=llama.cpp` page text or HTML. Then confirm the matching filenames in:

```text
https://huggingface.co/api/models/<repo>/tree/main?recursive=true
```

Use the Hub page first, and only fall back to the generic heuristics below when the repo page does not expose a clear recommendation.

## Quantization Overview

**GGUF** (GPT-Generated Unified Format) - Standard format for llama.cpp models.

### Format Comparison

| Format | Perplexity | Size (7B) | Tokens/sec | Notes |
|--------|------------|-----------|------------|-------|
| FP16 | 5.9565 (baseline) | 13.0 GB | 15 tok/s | Original quality |
| Q8_0 | 5.9584 (+0.03%) | 7.0 GB | 25 tok/s | Nearly lossless |
| **Q6_K** | 5.9642 (+0.13%) | 5.5 GB | 30 tok/s | Best quality/size |
| **Q5_K_M** | 5.9796 (+0.39%) | 4.8 GB | 35 tok/s | Balanced |
| **Q4_K_M** | 6.0565 (+1.68%) | 4.1 GB | 40 tok/s | **Recommended** |
| Q4_K_S | 6.1125 (+2.62%) | 3.9 GB | 42 tok/s | Faster, lower quality |
| Q3_K_M | 6.3184 (+6.07%) | 3.3 GB | 45 tok/s | Small models only |
| Q2_K | 6.8673 (+15.3%) | 2.7 GB | 50 tok/s | Not recommended |

**Recommendation**: Use **Q4_K_M** for best balance of quality and speed.

## Converting Models

### Hugging Face to GGUF

```bash
# 1. Download Hugging Face model
hf download meta-llama/Llama-2-7b-chat-hf \
    --local-dir models/llama-2-7b-chat/

# 2. Convert to FP16 GGUF
python convert_hf_to_gguf.py \
    models/llama-2-7b-chat/ \
    --outtype f16 \
    --outfile models/llama-2-7b-chat-f16.gguf

# 3. Quantize to Q4_K_M
./llama-quantize \
    models/llama-2-7b-chat-f16.gguf \
    models/llama-2-7b-chat-Q4_K_M.gguf \
    Q4_K_M
```

### Batch quantization

```bash
# Quantize to multiple formats
for quant in Q4_K_M Q5_K_M Q6_K Q8_0; do
    ./llama-quantize \
        model-f16.gguf \
        model-${quant}.gguf \
        $quant
done
```

## K-Quantization Methods

**K-quants** use mixed precision for better quality:
- Attention weights: Higher precision
- Feed-forward weights: Lower precision

**Variants**:
- `_S` (Small): Faster, lower quality
- `_M` (Medium): Balanced (recommended)
- `_L` (Large): Better quality, larger size

**Example**: `Q4_K_M`
- `Q4`: 4-bit quantization
- `K`: Mixed precision method
- `M`: Medium quality

## Quality Testing

```bash
# Calculate perplexity (quality metric)
./llama-perplexity \
    -m model.gguf \
    -f wikitext-2-raw/wiki.test.raw \
    -c 512

# Lower perplexity = better quality
# Baseline (FP16): ~5.96
# Q4_K_M: ~6.06 (+1.7%)
# Q2_K: ~6.87 (+15.3% - too much degradation)
```

## Use Case Guide

### General purpose (chatbots, assistants)
```
Q4_K_M - Best balance
Q5_K_M - If you have extra RAM
```

### Code generation
```
Q5_K_M or Q6_K - Higher precision helps with code
```

### Creative writing
```
Q4_K_M - Sufficient quality
Q3_K_M - Acceptable for draft generation
```

### Technical/medical
```
Q6_K or Q8_0 - Maximum accuracy
```

### GPU-constrained (8GB VRAM, e.g. RTX 4060)
```
MoE models (Qwen3.6-35B-A3B): IQ4_NL, --n-gpu-layers 99 --ctx-size 32768
- 35B total params but only 3B active per token
- Fits fully in 8GB VRAM, delivers 15-30 tok/s
- Best quality/speed ratio for 8GB GPUs

Dense models (7B): Q4_K_M, --n-gpu-layers 99
- ~4GB weights + KV cache fits easily in 8GB
- ~30-50 tok/s

Dense models (14B+): Cannot fit fully in 8GB
- Partial GPU offload has PCIe bottleneck
- Recommend CPU-only or smaller model
```

### Edge devices (Raspberry Pi)
```
Q2_K or Q3_K_S - Fit in limited RAM
```

## Model Size Scaling

### 7B parameter models

| Format | Size | RAM needed |
|--------|------|------------|
| Q2_K | 2.7 GB | 5 GB |
| Q3_K_M | 3.3 GB | 6 GB |
| Q4_K_M | 4.1 GB | 7 GB |
| Q5_K_M | 4.8 GB | 8 GB |
| Q6_K | 5.5 GB | 9 GB |
| Q8_0 | 7.0 GB | 11 GB |

### 13B parameter models

| Format | Size | RAM needed |
|--------|------|------------|
| Q2_K | 5.1 GB | 8 GB |
| Q3_K_M | 6.2 GB | 10 GB |
| Q4_K_M | 7.9 GB | 12 GB |
| Q5_K_M | 9.2 GB | 14 GB |
| Q6_K | 10.7 GB | 16 GB |

### 14B parameter models

| Format | Size | RAM needed | RTX 4060 8GB |
|--------|------|------------|--------------|
| Q3_K_M | ~6.5 GB | ~10 GB | Partial offload possible |
| Q4_K_M | ~8.5-9 GB | ~13 GB | **Too large** for full GPU offload; PCIe bottleneck for partial |
| Q5_K_M | ~10 GB | ~15 GB | CPU only |
| Q6_K | ~11 GB | ~17 GB | CPU only |
| Q8_0 | ~14 GB | ~20 GB | CPU only |

**Warning for Hermes Agent:** Hermes requires minimum 64K context window. Standard Qwen3-14B has `max_position_embeddings: 40960` (40K) — **below** the 64K minimum. Use the Unsloth 128K variant instead:
```
unsloth/Qwen3-14B-128K-GGUF  (Qwen3-14B-128K-Q4_K_M.gguf)
```
Q4_K_M at 14B ≈ 9GB runtime — exceeds RTX 4060 8GB VRAM. Options:
- `Q3_K_M` (~6.5-6.9GB): partial GPU offload feasible, less quality loss than Q4 on other sizes
- `Q4_K_M` CPU-only (`--n-gpu-layers 0`): needs ~13GB system RAM + context, ~3-4 tok/s
- Best tradeoff for RTX 4060 8GB: use a 7B model with `--n-gpu-layers 99` instead, or a MoE model (35B-A3B)

**Downloading the 128K variant:**
```bash
# Use hf download CLI (NOT Python API flags)
hf download unsloth/Qwen3-14B-128K-GGUF Qwen3-14B-128K-Q3_K_M.gguf \
    --local-dir ~/models/Qwen3-14B-128K-Q3_K_M
```
See `hermes-provider-integration.md` for the full Hermes profile setup.

### 70B parameter models

| Format | Size | RAM needed |
|--------|------|------------|
| Q2_K | 26 GB | 32 GB |
| Q3_K_M | 32 GB | 40 GB |
| Q4_K_M | 41 GB | 48 GB |
| Q4_K_S | 39 GB | 46 GB |
| Q5_K_M | 48 GB | 56 GB |

**Recommendation for 70B**: Use Q3_K_M or Q4_K_S to fit in consumer hardware.

## Finding Pre-Quantized Models

Use the Hub search with the llama.cpp app filter:

```text
https://huggingface.co/models?apps=llama.cpp&sort=trending
https://huggingface.co/models?search=<term>&apps=llama.cpp&sort=trending
https://huggingface.co/models?search=<term>&apps=llama.cpp&num_parameters=min:0,max:24B&sort=trending
```

For a specific repo, open:

```text
https://huggingface.co/<repo>?local-app=llama.cpp
https://huggingface.co/api/models/<repo>/tree/main?recursive=true
```

Then launch directly from the Hub without extra Hub tooling:

```bash
llama-cli -hf <repo>:Q4_K_M
llama-server -hf <repo>:Q4_K_M
```

If you need the exact file name from the tree API:

```bash
llama-server --hf-repo <repo> --hf-file <filename.gguf>
```

## Importance Matrices (imatrix)

**What**: Calibration data to improve quantization quality.

**Benefits**:
- 10-20% perplexity improvement with Q4
- Essential for Q3 and below

**Usage**:
```bash
# 1. Generate importance matrix
./llama-imatrix \
    -m model-f16.gguf \
    -f calibration-data.txt \
    -o model.imatrix

# 2. Quantize with imatrix
./llama-quantize \
    --imatrix model.imatrix \
    model-f16.gguf \
    model-Q4_K_M.gguf \
    Q4_K_M
```

**Calibration data**:
- Use domain-specific text (e.g., code for code models)
- ~100MB of representative text
- Higher quality data = better quantization

## Troubleshooting

**Model outputs gibberish**:
- Quantization too aggressive (Q2_K)
- Try Q4_K_M or Q5_K_M
- Verify model converted correctly

**Out of memory**:
- Use lower quantization (Q4_K_S instead of Q5_K_M)
- Offload fewer layers to GPU (`-ngl`)
- Use smaller context (`-c 2048`)

**Slow inference**:
- Higher quantization uses more compute
- Q8_0 much slower than Q4_K_M
- Consider speed vs quality trade-off
