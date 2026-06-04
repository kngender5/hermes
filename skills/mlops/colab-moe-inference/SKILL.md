---
name: colab-moe-inference
description: Serve Mixture-of-Experts models (Mixtral, DeepSeek-V3, Qwen-MoE, OLMoE) via Google Colab GPU + Gradio. Handles sparse activation, multi-GPU, quantization for large MoE models.
---

# Colab MoE Inference — Mixture of Experts

Serve MoE models on Google Colab GPU with Gradio UI. MoE models activate only a subset of parameters per token, enabling larger models with less compute.

## Supported Architectures

| Model | Total Params | Active Params | VRAM (fp16) | VRAM (4-bit) | T4 OK |
|-------|-------------|---------------|-------------|--------------|-------|
| Mixtral-8x7B | 47B | ~13B | ~26GB | ~12GB | ✅ (4-bit) |
| DeepSeek-V3 | 671B | ~37B | ~80GB+ | ~24GB | ❌ |
| DeepSeek-R1 | 671B | ~37B | ~80GB+ | ~24GB | ❌ |
| DeepSeek-V2 | 236B | ~21B | ~48GB | ~14GB | ❌ |
| DeepSeek-V2-Lite | 16B | ~2.4B | ~8GB | ~4GB | ✅ |
| Qwen1.5-MoE-A2.7B | 14B | ~2.7B | ~8GB | ~4GB | ✅ |
| OLMoE-1B-7B | 7B | ~1B | ~4GB | ~2GB | ✅ |
| Jamba (AI21) | 52B | ~12B | ~28GB | ~12GB | ✅ (4-bit) |
| Qwen2-57B-A14B | 57B | ~14B | ~32GB | ~14GB | ❌ |
| DeepSeek-V3-BF16 (AWQ) | 671B | ~37B | ~48GB+ | ~24GB | ❌ |

**Key insight:** MoE models list TOTAL parameters, but ACTIVE parameters per token are much smaller. A 47B Mixtral only uses ~13B params per forward pass.

## Method 1: Mixtral on T4 (4-bit)

### requirements.txt
```
torch>=2.4.0
transformers>=4.48.0
accelerate>=1.3.0
bitsandbytes>=0.45.0
gradio>=5.0.0
```

### Notebook Cell — 4-bit quantized Mixtral
```python
!pip install torch transformers accelerate bitsandbytes gradio -q

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import gradio as gr

model_id = "mistralai/Mixtral-8x7B-Instruct-v0.1"

quant_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=quant_config,
    device_map="auto",
    torch_dtype=torch.float16,
)
model.eval()

def chat(message, history):
    messages = []
    for h in history:
        messages.append({"role": "user", "content": h[0]})
        messages.append({"role": "assistant", "content": h[1]})
    messages.append({"role": "user", "content": message})

    input_ids = tokenizer.apply_chat_template(
        messages, return_tensors="pt", add_generation_prompt=True
    ).to(model.device)

    outputs = model.generate(
        input_ids,
        max_new_tokens=512,
        temperature=0.7,
        top_p=0.9,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id,
    )
    response = tokenizer.decode(outputs[0][input_ids.shape[-1]:], skip_special_tokens=True)
    return response

gr.ChatInterface(
    fn=chat,
    title="Mixtral-8x7B MoE",
    description="4-bit quantized Mixtral on T4",
).launch(share=True, debug=True)
```

## Method 2: DeepSeek-V2-Lite (T4 native)

```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import gradio as gr

model_id = "deepseek-ai/DeepSeek-V2-Lite-Chat"

tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True,
)

def chat(message, history):
    messages = []
    for h in history:
        messages.append({"role": "user", "content": h[0]})
        messages.append({"role": "assistant", "content": h[1]})
    messages.append({"role": "user", "content": message})
    
    input_ids = tokenizer.apply_chat_template(
        messages, return_tensors="pt", add_generation_prompt=True
    ).to(model.device)
    
    outputs = model.generate(
        input_ids, max_new_tokens=512, temperature=0.7,
        pad_token_id=tokenizer.eos_token_id,
    )
    response = tokenizer.decode(outputs[0][input_ids.shape[-1]:], skip_special_tokens=True)
    return response

gr.ChatInterface(fn=chat, title="DeepSeek-V2-Lite MoE").launch(share=True)
```

## Method 3: vLLM with MoE (A100/L4)

For larger MoE models that don't fit in T4 even quantized.

```python
!pip install vllm gradio -q

import subprocess, time, openai, gradio as gr

proc = subprocess.Popen([
    "python", "-m", "vllm.entrypoints.openai.api_server",
    "--model", "deepseek-ai/DeepSeek-V2-Lite-Chat",
    "--dtype", "float16",
    "--max-model-len", "4096",
    "--gpu-memory-utilization", "0.9",
    "--tensor-parallel-size", "1",
    "--port", "8000",
    "--trust-remote-code",
])
time.sleep(30)

client = openai.OpenAI(base_url="http://localhost:8000/v1", api_key="none")

def chat(message, history):
    messages = []
    for h in history:
        messages.append({"role": "user", "content": h[0]})
        messages.append({"role": "assistant", "content": h[1]})
    messages.append({"role": "user", "content": message})
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V2-Lite-Chat",
        messages=messages,
        max_tokens=512,
        stream=True,
    )
    result = ""
    for chunk in response:
        if chunk.choices[0].delta.content:
            result += chunk.choices[0].delta.content
            yield result

gr.ChatInterface(fn=chat, title="vLLM MoE").launch(share=True)
```

## Method 4: OLMoE (Lightweight, efficient)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import gradio as gr

model_id = "allenai/OLMoE-1B-7B-0924"

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id, torch_dtype=torch.float16, device_map="auto"
)

def chat(message, history):
    messages = [{"role": "user", "content": message}]
    inputs = tokenizer.apply_chat_template(messages, return_tensors="pt", add_generation_prompt=True).to("cuda")
    outputs = model.generate(inputs, max_new_tokens=256, use_cache=True)
    return tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)

gr.ChatInterface(fn=chat, title="OLMoE-1B-7B").launch(share=True)
```

## MoE-Specific Optimizations

| Technique | Effect | Applicable |
|-----------|--------|------------|
| 4-bit quantization | ~75% VRAM reduction | All MoE |
| `device_map="auto"` | Automatic GPU/CPU offloading | All |
| `expert_parallelism` | Distribute experts across GPUs | Multi-GPU |
| Reduce `num_experts_per_tok` | Fewer active experts = faster | Mixtral (default 2) |
| FlashAttention-2 | Faster attention | Supported models |

### Reduce active experts (Mixtral)
```python
# Mixtral defaults to 2 experts per token. Reduce to 1 for speed:
model.config.num_experts_per_tok = 1  # Instead of 2
```

### Expert routing analysis
```python
# Inspect which experts are active
with torch.no_grad():
    outputs = model(**inputs, output_router_logits=True)
    router_logits = outputs.router_logits
    print(f"Router logits shape: {router_logits[0].shape}")
    # Shape: (layers, tokens, num_experts)
```

## VRAM Comparison: Dense vs MoE

| Model | Type | Total Params | Active/Tok | T4-16GB (4-bit) |
|-------|------|-------------|------------|-----------------|
| Llama-3-8B | Dense | 8B | 8B | ✅ ~5GB |
| Mistral-7B | Dense | 7B | 7B | ✅ ~4GB |
| Mixtral-8x7B | MoE | 47B | ~13B | ✅ ~12GB |
| Qwen1.5-MoE-A2.7B | MoE | 14B | ~2.7B | ✅ ~4GB |
| DeepSeek-V2-Lite | MoE | 16B | ~2.4GB | ✅ ~4GB |
| OLMoE-1B-7B | MoE | 7B | ~1B | ✅ ~2GB |

## Common Issues

| Problem | Fix |
|---------|-----|
| Mixtral OOM on T4 | Ensure 4-bit quantization, `device_map="auto"` |
| Slow MoE inference | Reduce `num_experts_per_tok` to 1 |
| vLLM MoE not starting | Add `--trust-remote-code`, check vLLM version |
| DeepSeek import errors | `trust_remote_code=True` is required |
| Expert routing errors | Ensure `accelerate` is up-to-date |
| Uneven GPU memory | `device_map="auto"` handles this automatically |
| Colab disconnects with large MoE | Save to Drive first, use shorter `max_new_tokens` |
