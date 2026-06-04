---
name: colab-quantization
description: Model quantization for Colab — AWQ, GPTQ, GGUF, bitsandbytes 4/8-bit, HQQ, EETQ. Benchmark quality vs speed vs VRAM tradeoffs.
---

# Colab Quantization — Compress Models for GPU Inference

Reduce model size 2-4x with minimal quality loss.

## Quantization Methods Comparison

| Method | Bits | Calibration | Speed | Quality Loss | VRAM Savings | Best For |
|--------|------|-------------|-------|--------------|--------------|----------|
| bitsandbytes NF4 | 4 | None | Medium | ~2% | ~75% | Easiest inference |
| bitsandbytes Int8 | 8 | None | Medium | ~1% | ~50% | Quality inference |
| AWQ | 4 | Yes (small) | **Fast** | ~1% | ~75% | Speed inference |
| GPTQ | 2/3/4/8 | Yes | Medium | ~2-5% | ~75-90% | Minimum storage |
| GGUF Q4_K_M | 4 | Yes | N/A (CPU) | ~1% | ~75% | CPU inference |
| AQLM | 2 | Yes | Fast | ~1% | ~87% | 2-bit research |
| HQQ | 2/3/4 | None | Medium | ~3-5% | ~75-87% | No calibration |
| EETQ | 8 | None | Fast | ~0.5% | ~50% | Training+inference |

## bitsandbytes (Easiest)

```python
import torch
from transformers import BitsAndBytesConfig, AutoModelForCausalLM

# 4-bit (NF4 + double quant)
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8B-Instruct",
    quantization_config=bnb_config,
    device_map="auto",
)
```

## AWQ (Fastest Inference)

```python
# Pre-quantized
model = AutoModelForCausalLM.from_pretrained(
    "TheBloke/Llama-3.1-8B-Instruct-AWQ",
    device_map="auto", torch_dtype=torch.float16,
)

# Or quantize yourself
!pip install autoawq -q
from awq import AutoAWQForCausalLM
model = AutoAWQForCausalLM.from_pretrained("meta-llama/Llama-3.1-8B-Instruct")
model.quantize(tokenizer, quant_config={"zero_point": True, "q_group_size": 128, "w_bit": 4})
model.save_quantized("model-awq")
```

## GPTQ (2/3/4/8 bit flexible)

```python
!pip install auto-gptq optimum -q
from auto_gptq import AutoGPTQForCausalLM, BaseQuantizeConfig

quant_config = BaseQuantizeConfig(bits=4, group_size=128, damp_percent=0.1, desc_act=True)
model = AutoGPTQForCausalLM.from_pretrained("meta-llama/Llama-3.1-8B-Instruct", quantize_config=quant_config)
model.quantize(["calibration text " * 50 for _ in range(128)])
model.save_quantized("model-gptq")
```

## GGUF (CPU/llama.cpp)

```python
from llama_cpp import Llama

# HF Hub download
from huggingface_hub import hf_hub_download
path = hf_hub_download("bartowski/Llama-3.1-8B-Instruct-GGUF", "Llama-3.1-8B-Instruct-Q4_K_M.gguf")

llm = Llama(model_path=path, n_ctx=4096, n_gpu_layers=35)
output = llm("Hello!", max_tokens=128)
```

## ONNX Runtime (Optimized GPU)

```python
!pip install optimum[onnxruntime-gpu] -q
from optimum.onnxruntime import ORTModelForCausalLM

model = ORTModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8B-Instruct", export=True, provider="CUDAExecutionProvider")
model.save_pretrained("onnx_model")
```

## Choosing the Right Method

| Scenario | Method |
|----------|--------|
| Quick inference on T4 | bitsandbytes NF4 |
| Maximum inference speed | AWQ |
| Minimum file size | GPTQ or AQLM 2-bit |
| CPU only (laptop) | GGUF via llama.cpp |
| No calibration data | HQQ or bitsandbytes |
| Production serving | AWQ or ONNX |

## Common Issues

| Problem | Fix |
|---------|-----|
| bitsandbytes CUDA error | `pip install bitsandbytes>=0.43.0`, ensure GPU runtime |
| AWQ quality loss | Try `w_bit=8` |
| GGUF slow | Increase `n_gpu_layers`, reduce `n_ctx` |
| GPTQ calibration OOM | Fewer samples, smaller batch |
