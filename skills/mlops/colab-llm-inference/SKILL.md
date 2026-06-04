---
name: colab-llm-inference
description: Serve LLM text-generation models (LLaMA, Mistral, Qwen, DeepSeek, Phi, Gemma) via Google Colab GPU + Gradio public URL. Handles quantization, vLLM, Unsloth, T4/A100 optimization.
---

# Colab LLM Inference — Text Generation Models

Serve autoregressive LLMs on Google Colab GPU with Gradio UI and public share URL.

## Supported Architectures

| Family | Models | Size Range | VRAM (T4-16GB) |
|--------|--------|------------|-----------------|
| LLaMA | Llama-3.1/3.2/4 | 1B–405B | 1B–8B fits T4 |
| Mistral | Mistral-7B, Mixtral-8x7B | 7B–47B | 7B fits T4 (fp16) |
| Qwen | Qwen2/2.5/3 | 0.5B–72B | 0.5B–14B fits T4 |
| DeepSeek | DeepSeek-V2/V3/R1 | 7B–671B | 7B–14B fits T4 |
| Phi | Phi-3/4 | 3.8B–14B | 3.8B fits T4 |
| Gemma | Gemma-2/3 | 2B–27B | 2B–9B fits T4 |

## GPU VRAM Guide (Colab)

| GPU | VRAM | bf16 | Max Model (fp16) | Max Model (4-bit) |
|-----|------|------|-------------------|-------------------|
| T4 | 16 GB | ❌ (Turing) | ~7B | ~30B |
| L4 | 22.5 GB | ✅ | ~13B | ~70B |
| V100 | 16 GB | ✅ | ~7B | ~30B |
| A100 | 40/80 GB | ✅ | ~30B | ~180B+ |

**⚠️ T4 does NOT support bf16** — use `torch.float16` or `torch.float32`.

## Method 1: transformers + bitsandbytes (Simplest)

Best for: quick demos, <13B models, T4 GPU.

### requirements.txt
```
torch>=2.4.0
transformers>=4.48.0
accelerate>=1.3.0
bitsandbytes>=0.45.0
gradio>=5.0.0
huggingface-hub>=0.28.0
```

### Notebook Cell — Install
```python
# uv is pre-installed on Colab since mid-2025 — 10-100x faster than pip
!uv pip install torch transformers accelerate bitsandbytes gradio huggingface-hub -q
```

### Notebook Cell — Load Model (4-bit quantized)
```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import gradio as gr

model_id = "unsloth/Llama-3.2-3B-Instruct-bnb-4bit"

quant_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,  # T4: use float16, NOT bfloat16
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
```

### Notebook Cell — Gradio Chat
```python
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

demo = gr.ChatInterface(
    fn=chat,
    title="LLM Chat",
    description=f"Model: {model_id}",
)
demo.launch(share=True, debug=True)
```

## Method 2: Unsloth (2x faster, less VRAM)

Best for: fine-tuning + inference, T4 optimization.

### requirements.txt
```
unsloth>=2025.1.8
gradio>=5.0.0
xformers>=0.0.28
```

### Notebook Cell — Install
```python
!uv pip install unsloth gradio xformers -q
# If error: !pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
```

### Notebook Cell — Load + Serve
```python
from unsloth import FastLanguageModel
import gradio as gr

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Llama-3.2-3B-Instruct-bnb-4bit",
    max_seq_length=2048,
    dtype=None,  # Auto-detect
    load_in_4bit=True,
)
FastLanguageModel.for_inference(model)

def chat(message, history):
    messages = []
    for h in history:
        messages.append({"role": "user", "content": h[0]})
        messages.append({"role": "assistant", "content": h[1]})
    messages.append({"role": "user", "content": message})

    input_ids = tokenizer.apply_chat_template(
        messages, return_tensors="pt", add_generation_prompt=True
    ).to("cuda")

    outputs = model.generate(
        input_ids,
        max_new_tokens=512,
        temperature=0.7,
        use_cache=True,
    )
    return tokenizer.decode(outputs[0][input_ids.shape[-1]:], skip_special_tokens=True)

gr.ChatInterface(fn=chat, title="Unsloth Chat").launch(share=True)
```

## Method 3: vLLM (Production-grade, OpenAI-compatible)

Best for: high throughput, larger models, A100/L4.

### requirements.txt
```
vllm>=0.7.0
gradio>=5.0.0
```

### Notebook Cell — Install + Serve
```python
!uv pip install vllm gradio -q

# Start vLLM server in background
import subprocess, time
proc = subprocess.Popen([
    "python", "-m", "vllm.entrypoints.openai.api_server",
    "--model", "Qwen/Qwen2.5-7B-Instruct",
    "--dtype", "float16",
    "--max-model-len", "4096",
    "--gpu-memory-utilization", "0.9",
    "--port", "8000",
])
time.sleep(30)  # Wait for model load

# Gradio UI wrapping vLLM
import openai, gradio as gr

client = openai.OpenAI(base_url="http://localhost:8000/v1", api_key="none")

def chat(message, history):
    messages = []
    for h in history:
        messages.append({"role": "user", "content": h[0]})
        messages.append({"role": "assistant", "content": h[1]})
    messages.append({"role": "user", "content": message})
    response = client.chat.completions.create(
        model="Qwen/Qwen2.5-7B-Instruct",
        messages=messages,
        max_tokens=512,
        temperature=0.7,
        stream=True,
    )
    result = ""
    for chunk in response:
        if chunk.choices[0].delta.content:
            result += chunk.choices[0].delta.content
            yield result

gr.ChatInterface(fn=chat, title="vLLM Chat").launch(share=True)
```

## Method 4: TGI (HuggingFace Text Generation Inference)

Best for: production serving, OpenAI-compatible API, larger models on A100/L4.

### Notebook Cell — Install + Serve
```python
!pip install colab-xterm
%load_ext colabxterm
%xterm
# In xterm:
# text-generation-launcher --model-id TheBloke/Llama-2-13B-chat-AWQ \
#   --quantize awq --port 5000

# Then call it from another cell:
from huggingface_hub import InferenceClient
client = InferenceClient(model="http://127.0.0.1:5000")
for token in client.text_generation("What is JAX?", max_new_tokens=256, stream=True):
    print(token, end="", flush=True)
```

## Quantization Guide

| Method | Bits | Quality | Speed | VRAM Savings |
|--------|------|---------|-------|--------------|
| fp16 | 16 | ★★★★★ | ★★★★★ | baseline |
| int8 | 8 | ★★★★ | ★★★★ | ~50% |
| nf4 (bnb) | 4 | ★★★★ | ★★★ | ~75% |
| GPTQ | 4 | ★★★ | ★★★★ | ~75% |
| AWQ | 4 | ★★★★ | ★★★★ | ~75% |
| GGUF (Q4_K_M) | 4 | ★★★★ | ★★★ | ~75% |

## Model Selection by VRAM

### T4 (16GB) — Free Tier
```python
# 4-bit quantized (recommended)
"unsloth/Llama-3.2-3B-Instruct-bnb-4bit"    # ~2GB VRAM
"unsloth/Llama-3.1-8B-Instruct-bnb-4bit"    # ~5GB VRAM
"Qwen/Qwen2.5-7B-Instruct-GPTQ-Int4"        # ~4GB VRAM
"microsoft/Phi-3-mini-4k-instruct"           # ~3GB VRAM (fp16)
```

### L4 (22.5GB) — Colab Pro
```python
"unsloth/Llama-3.1-8B-Instruct-bnb-4bit"    # ~5GB
"Qwen/Qwen2.5-14B-Instruct-GPTQ-Int4"       # ~8GB
"mistralai/Mistral-7B-Instruct-v0.3"         # ~14GB (fp16)
```

### A100 (40GB) — Colab Pro+
```python
"meta-llama/Llama-3.1-70B-Instruct"          # ~40GB (fp16)
"Qwen/Qwen2.5-72B-Instruct-AWQ"             # ~20GB
"deepseek-ai/DeepSeek-R1-0528-AWQ"           # ~20GB
```

## Common Issues

| Problem | Fix |
|---------|-----|
| `bf16 not supported` on T4 | Use `torch.float16` instead |
| OOM on T4 | Use 4-bit quantization, reduce `max_new_tokens` |
| Colab disconnects | Use `debug=True`, keep tab active |
| Slow first response | Model loading — add loading indicator |
| `share=True` timeout | Gradio tunnel issue — try again or use localtunnel |
| vLLM OOM | Reduce `--gpu-memory-utilization` to 0.8 |
| Import error unsloth | `pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"` |

## Colab Runtime Setup

```python
# Check GPU
!nvidia-smi

# Verify GPU available
import torch
print(f"GPU: {torch.cuda.get_device_name(0)}")
print(f"VRAM: {torch.cuda.get_device_properties(0).total_mem / 1e9:.1f} GB")
```

## See Also

- **colab** skill — full Colab platform guide (terminal, Drive, secrets, GPU memory, background processes, SSH, widgets, Gemini AI, TPU, tier comparison, power user patterns)

## Common Issues

| Problem | Fix |
|---------|-----|
| `bf16 not supported` on T4 | Use `torch.float16` instead |
| OOM on T4 | Use 4-bit quantization, reduce `max_new_tokens` |
| Colab disconnects | Use `debug=True`, keep tab active |
| Slow first response | Model loading — add loading indicator |
| `share=True` timeout | Gradio tunnel issue — try again or use localtunnel |
| vLLM OOM | Reduce `--gpu-memory-utilization` to 0.8 |
| Import error unsloth | `pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"` |
| Slow pip installs | Use `uv pip install` (10-100x faster, pre-installed since mid-2025) |
