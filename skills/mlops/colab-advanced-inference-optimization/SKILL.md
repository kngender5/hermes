---
name: colab-advanced-inference-optimization
description: Advanced inference optimization — FlashAttention-2/3, KV-cache quantization, speculative decoding, continuous batching, paged attention, GGUF. Maximize throughput on limited VRAM.
---

# Colab Advanced Inference Optimization

Maximize inference speed and minimize VRAM for model serving on Colab GPU.

## Optimization Impact Summary

| Technique | Speed Gain | VRAM Saved | Quality Loss | Complexity |
|-----------|------------|------------|--------------|------------|
| FlashAttention-2 | +30-50% | ~10% | None | Low |
| KV-cache quantization | — | ~50% cache | Minimal | Medium |
| Speculative decoding | +2-3x | — | None (verified) | Medium |
| Continuous batching | +3-8x throughput | — | None | High |
| PagedAttention (vLLM) | +2-4x throughput | ~40% | None | Low |
| GGUF Q4_K_M (CPU) | N/A | ~75% | ~1% | Low |
| Token pruning | +20-40% | ~30% | ~2% | High |
| Model slicing / TP | — | Enabled by | None | Medium |

## FlashAttention-2/3

Best for: Any transformer model, 30-50% speedup with zero quality loss.

```python
# Option 1: Install flash-attn
!pip install flash-attn --no-build-isolation -q

from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8B-Instruct",
    attn_implementation="flash_attention_2",  # Key parameter
    torch_dtype=torch.float16,
    device_map="auto",
)

# Option 2: PyTorch SDPA (built-in, no install needed)
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8B-Instruct",
    attn_implementation="sdpa",  # Scaled dot-product attention
    torch_dtype=torch.float16,
    device_map="auto",
)
```

**FlashAttention-3** (H100 only):
```python
# Only for H100 GPUs
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    attn_implementation="flash_attention_3",
    torch_dtype=torch.float16,
)
```

## KV-Cache Optimization

Best for: Long context inference — the KV-cache grows linearly with sequence length.

### KV-Cache Quantization
```python
# With vLLM
from vllm import LLM, SamplingParams

llm = LLM(
    model="meta-llama/Llama-3.1-8B-Instruct",
    kv_cache_dtype="fp8",      # FP8 KV-cache (50% memory savings)
    # kv_cache_dtype="auto",   # Default FP16
)

# With transformers + quantization
# Use the `quanto` library for KV-cache quantization
!pip install quanto -q
from quanto import quantize

# Quantize the KV-cache tensors to int8
```

### Sliding Window Attention
```python
# For models that support it (Mistral, Gemma)
model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-Instruct-v0.3",
    attn_implementation="sdpa",
    sliding_window=4096,  # Only attend to last 4096 tokens
)

# LongQLoRA-style: extend context with position interpolation
# Supports contexts up to 32K+ on T4 with 4-bit base model
```

### GQA/MQA Optimization
```python
# Models with Grouped-Query Attention use less KV-cache
# Llama-3.1: GQA (8 KV heads vs 32 Q heads = 4x less cache)
# Use models with GQA/MQA for long context efficiency
```

## Speculative Decoding

Best for: 2-3x faster inference with a small draft model.

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Large target model
target_model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8B-Instruct",
    torch_dtype=torch.float16,
    device_map="auto",
)

# Small draft model (e.g., TinyLlama or same model quantized)
draft_model = AutoModelForCausalLM.from_pretrained(
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    torch_dtype=torch.float16,
    device_map="auto",
)

# Use with assisted generation
output = target_model.generate(
    input_ids,
    assistant_model=draft_model,  # Speculative decoding
    max_new_tokens=256,
    temperature=0.7,
    do_sample=True,
)
```

### Eagle / Medusa (Advanced Speculative Decoding)
```python
!pip install eagle-llm -q

# Eagle: Train a small draft head that predicts Medusa heads
# ~3x speedup on supported models
from eagle import EagleModel

model = EagleModel.from_pretrained(
    "meta-llama/Llama-3.1-8B-Instruct",
    draft_model="yuhuili/EAGLE3-LLaMA3.1-Instruct-8B",
)
output = model.generate(input_ids, max_new_tokens=256)
```

## vLLM (Best Throughput)

Best for: Production serving, continuous batching, PagedAttention.

```python
!pip install vllm -q

from vllm import LLM, SamplingParams

llm = LLM(
    model="meta-llama/Llama-3.1-8B-Instruct",
    dtype="float16",
    gpu_memory_utilization=0.9,
    max_model_len=4096,
    # Optimization options
    enable_prefix_caching=True,      # Reuse KV-cache across requests
    enable_chunked_prefill=True,     # Process long prompts in chunks
    max_num_batched_tokens=8192,     # Continuous batching budget
    quantization="awq",              # AWQ quantization for vLLM
)

sampling = SamplingParams(temperature=0.7, top_p=0.9, max_tokens=256)
outputs = llm.generate(["Hello, how are you?"], sampling)
print(outputs[0].outputs[0].text)
```

### vLLM + FlashInfer (Even Faster)
```python
!pip install flashinfer -q

llm = LLM(
    model="meta-llama/Llama-3.1-8B-Instruct",
    dtype="float16",
    kv_cache_dtype="fp8",
    gpu_memory_utilization=0.95,
)
```

## Continuous Batching

Best for: Serving multiple concurrent requests efficiently.

```python
# vLLM handles this natively — just use AsyncLLMEngine
from vllm import AsyncLLMEngine, AsyncEngineArgs, SamplingParams
import asyncio

engine = AsyncEngineArgs(
    model="meta-llama/Llama-3.1-8B-Instruct",
    dtype="float16",
    gpu_memory_utilization=0.9,
    max_num_seqs=256,  # Max concurrent requests
)
llm = AsyncLLMEngine.from_engine_args(engine)

async def generate(prompt, request_id):
    async for output in llm.generate(prompt, SamplingParams(max_tokens=128), request_id):
        if output.finished:
            return output.outputs[0].text

# Multiple concurrent requests processed efficiently
results = await asyncio.gather(
    generate("Question 1", "req-1"),
    generate("Question 2", "req-2"),
    generate("Question 3", "req-3"),
)
```

## Model Compilation (PyTorch 2.0+)

```python
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8B-Instruct", torch_dtype=torch.float16)

# Compile the model for +20-30% speedup
model = torch.compile(model, mode="reduce-overhead")
# Modes: "default", "reduce-overhead", "max-autotune"
```

## ONNX Runtime Optimization

```python
!pip install optimum[onnxruntime-gpu] -q

from optimum.onnxruntime import ORTModelForCausalLM, ORTConfig
from optimum.onnxruntime.configuration import AutoQuantizationConfig

# Convert and quantize
model = ORTModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8B-Instruct",
    export=True,
    provider="CUDAExecutionProvider",
    quantization_config=AutoQuantizationConfig.avx512_vnni(is_static=False),
)
```

## Memory-Effective Generation

```python
# Clear KV-cache between generations
model.generate(input_ids, max_new_tokens=256, use_cache=True)
torch.cuda.empty_cache()  # Free GPU memory

# Use max_new_tokens limit to control memory
model.generate(input_ids, max_new_tokens=128)  # Low memory
model.generate(input_ids, max_new_tokens=4096)  # High memory

# Batch decoding with attention mask
outputs = model.generate(
    input_ids,
    attention_mask=attention_mask,  # Don't attend to padding
    max_new_tokens=256,
    pad_token_id=tokenizer.eos_token_id,
)
```

## Benchmarking

```python
import time, torch

def benchmark(model, tokenizer, prompt, n_runs=10, max_new_tokens=128):
    times = []
    for _ in range(n_runs):
        inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
        torch.cuda.synchronize()
        start = time.time()
        outputs = model.generate(**inputs, max_new_tokens=max_new_tokens)
        torch.cuda.synchronize()
        times.append(time.time() - start)
    
    avg_time = sum(times) / len(times)
    tokens_per_sec = max_new_tokens / avg_time
    print(f"Avg: {avg_time:.2f}s, {tokens_per_sec:.1f} tok/s")
    print(f"VRAM: {torch.cuda.max_memory_allocated() / 1e9:.1f} GB")
    return avg_time, tokens_per_sec

benchmark(model, tokenizer, "Explain quantum computing")
```

## Common Issues

| Problem | Fix |
|---------|-----|
| FlashAttention install fails | Use `attn_implementation="sdpa"` instead (built-in) |
| vLLM OOM | Reduce `gpu_memory_utilization` to 0.8, reduce `max_model_len` |
| Speculative decoding slower | Draft model too large — use <1B model |
| Slow first token | Model loading — use `enable_chunked_prefill` |
| KV-cache OOM on long context | Use sliding window, GQA models, or KV-cache quantization |
| `torch.compile` errors | Use `mode="default"` instead of `"max-autotune"` |
| vLLM import error | `pip install vllm --no-build-isolation` |
