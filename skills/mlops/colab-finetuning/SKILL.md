---
name: colab-finetuning
description: Advanced fine-tuning on Colab — LoRA, QLoRA, DPO, ORPO, PPO via TRL and Unsloth. Multi-GPU, gradient checkpointing, dataset strategies, evaluation.
---

# Colab Fine-Tuning — LoRA, QLoRA, DPO, ORPO

Advanced parameter-efficient fine-tuning (PEFT) on Google Colab GPU.

## Fine-Tuning Methods Comparison

| Method | Type | VRAM | Speed | Quality | Best For |
|--------|------|------|-------|---------|----------|
| Full fine-tuning | All params | Very high | Slow | Highest | <7B, A100 |
| LoRA | Adapter only | Low | Fast | High | Most use cases |
| QLoRA | 4-bit + LoRA | Very low | Medium | High | T4, limited VRAM |
| DPO | Preference align | Low | Fast | High | Alignment |
| ORPO | Odds ratio + LoRA | Low | Fast | Very High | Alignment without reward model |
| PPO | RL | High | Slow | Varies | Complex reward shaping |

## VRAM Requirements

| Method | 7B model | 13B model | 70B model |
|--------|----------|-----------|-----------|
| Full fp16 | ~28GB | ~52GB | ~280GB+ |
| LoRA fp16 | ~14GB | ~26GB | ~140GB |
| QLoRA 4-bit | ~6GB | ~10GB | ~40GB |
| DPO (LoRA) | ~14GB | ~26GB | ~140GB |

## Method 1: Unsloth QLoRA (Fastest — 2x speed, 70% less VRAM)

### requirements.txt
```
unsloth>=2025.1.8
peft>=0.14.0
trl>=0.15.0
gradio>=5.0.0
bitsandbytes>=0.45.0
```

### Notebook Cell — Install
```python
!pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
!pip install peft trl bitsandbytes gradio -q
```

### Notebook Cell — QLoRA Fine-Tune
```python
from unsloth import FastLanguageModel
from trl import SFTTrainer
from datasets import load_dataset
import torch

max_seq_length = 2048
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Llama-3.1-8B-Instruct-bnb-4bit",
    max_seq_length=max_seq_length,
    dtype=None,
    load_in_4bit=True,
)

# Add LoRA adapters
model = FastLanguageModel.get_peft_model(
    model,
    r=16,                          # LoRA rank (higher = more capacity)
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_alpha=16,
    lora_dropout=0.05,
    bias="none",
    use_rslora=True,               # Rank-stabilized LoRA
    use_gradient_checkpointing="unsloth",  # Supports long context
    random_state=3407,
)

# Load dataset
dataset = load_dataset("mlabonne/guanaco-llama2-1k", split="train")

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=max_seq_length,
    dataset_num_proc=2,
    packing=True,                  # Pack multiple short samples
    args=dict(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=5,
        max_steps=60,              # Increase for real training
        learning_rate=2e-4,
        logging_steps=1,
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="linear",
        output_dir="outputs",
        report_to="none",
    ),
)

# Train
trainer.train()

# Save
model.save_pretrained("lora_model")
tokenizer.save_pretrained("lora_model")

# Merge and save as GGUF for Ollama
model.save_pretrained_gguf("merged_model", tokenizer, quantization_method="q4_k_m")
```

## Method 2: DPO (Direct Preference Optimization)

### Notebook Cell — DPO from LoRA checkpoint
```python
from unsloth import FastLanguageModel
from trl import DPOTrainer
from datasets import load_dataset

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Llama-3.1-8B-Instruct-bnb-4bit",
    max_seq_length=2048,
    dtype=None,
    load_in_4bit=True,
)

# Load LoRA from previous step
model = FastLanguageModel.get_peft_model(model, r=16, lora_alpha=16, target_modules=[...])
model.load_adapter("lora_model", adapter_name="default")

# Preference dataset format: {"prompt": "...", "chosen": "...", "rejected": "..."}
dpo_dataset = load_dataset("Intel/orca_dpo_pairs", split="train")

dpo_trainer = DPOTrainer(
    model=model,
    ref_model=None,  # Unsloth handles reference model automatically
    args=dict(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_ratio=0.1,
        num_train_epochs=1,
        learning_rate=5e-6,
        beta=0.1,          # KL divergence weight
        optim="adamw_8bit",
        output_dir="dpo_output",
        report_to="none",
    ),
    train_dataset=dpo_dataset,
    tokenizer=tokenizer,
    max_length=1024,
    max_prompt_length=512,
)
dpo_trainer.train()
```

## Method 3: ORPO (Odds Ratio Preference Optimization)

ORPO combines SFT and preference alignment in one step — no reward model needed.

```python
from trl import ORPOConfig, ORPOTrainer
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    "unsloth/Llama-3.1-8B-Instruct-bnb-4bit",
    max_seq_length=2048, dtype=None, load_in_4bit=True,
)
model = FastLanguageModel.get_peft_model(model, r=16, lora_alpha=16, ...)

orpo_config = ORPOConfig(
    output_dir="orpo_output",
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    learning_rate=8e-6,
    beta=0.1,                # ORPO lambda
    max_steps=100,
    optim="adamw_8bit",
    report_to="none",
)

trainer = ORPOTrainer(
    model=model,
    args=orpo_config,
    train_dataset=dpo_dataset,  # Same format as DPO
    tokenizer=tokenizer,
)
trainer.train()
```

## Method 4: LlamaFactory (100+ models, Web UI)

Best for: Quick fine-tuning without custom code, supports 100+ models.

```python
!pip install llama-factory gradio -q

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

from llamafactory.train import run_exp
from llamafactory.hparams import get_train_args

# Or use Web UI
!llamafactory-cli webui  # Opens Gradio UI for training config
```

### YAML config example
```yaml
### model
model_name_or_path: meta-llama/Llama-3.1-8B-Instruct

### method
stage: sft
finetuning_type: lora
lora_rank: 16
lora_target: all

### dataset
dataset: alpaca_en
template: llama3
cutoff_len: 2048
max_samples: 1000

### output
output_dir: saves/llama3-8b/lora/sft
logging_steps: 10
save_steps: 100
num_train_epochs: 3
per_device_train_batch_size: 2
gradient_accumulation_steps: 4
learning_rate: 5e-5
```

## Dataset Preparation

### Alpaca format (SFT)
```python
from datasets import Dataset
import json

data = [
    {
        "instruction": "What is Python?",
        "input": "",
        "output": "Python is a high-level programming language...",
    },
    # ...
]
dataset = Dataset.from_list(data)
```

### Preference format (DPO/ORPO)
```python
data = [
    {
        "prompt": "Write a poem about AI",
        "chosen": "AI is a wondrous thing...\nA marvel bright...",
        "rejected": "AI is robots. AI is good. The end.",
    },
    # ...
]
dataset = Dataset.from_list(data)
```

### Conversation format (ChatML)
```python
data = [
    {
        "messages": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there! How can I help?"},
        ]
    },
]
```

## Evaluation

### During training
```python
from trl import SFTTrainer

trainer = SFTTrainer(
    # ... other args ...
    eval_dataset=eval_dataset,
    eval_strategy="steps",
    eval_steps=50,
)
```

### After training — MT-Bench style
```python
!pip install llm-eval -q
!python -m lm_eval --model hf \
    --model_args pretrained=/content/merged_model \
    --tasks hellaswag,arc_challenge,truthfulqa \
    --device cuda:0 \
    --batch_size 8
```

## Export Formats

```python
# 1. GGUF (for Ollama / llama.cpp)
model.save_pretrained_gguf("model_gguf", tokenizer, quantization_method="q4_k_m")

# 2. Safetensors (HuggingFace)
model.push_to_hub("username/model-name", safe_serialization=True)

# 3. Merged full model (for vLLM / production)
model = model.merge_and_unload()
model.save_pretrained("merged_model")

# 4. ONNX (for optimized inference)
!pip install optimum[onnxruntime-gpu] -q
!optimum-cli export onnx --model merged_model --task text-generation onnx_model/

# 5. AWQ (for fast inference)
!pip install autoawq -q
from awq import AutoAWQForCausalLM
quant_model = AutoAWQForCausalLM.from_pretrained("merged_model")
model.quantize(tokenizer, quant_config={"zero_point": True, "q_group_size": 128, "w_bit": 4})
```

## Gradient Checkpointing Levels

| Method | VRAM Saved | Speed Impact | How |
|--------|------------|--------------|-----|
| None | 0% | None | Default |
| `use_gradient_checkpointing=True` | ~40% | -20% | Recomputes activations |
| `use_gradient_checkpointing="unsloth"` | ~50% | -5% | Unsloth optimized |

## Common Issues

| Problem | Fix |
|---------|-----|
| OOM during training | Reduce batch_size to 1, increase gradient_accumulation_steps to 8 |
| LoRA not loading | Check `target_modules` match model architecture |
| NaN loss | Reduce learning_rate, check dataset for empty strings |
| Slow training on T4 | Use Unsloth, `optim="adamw_8bit"`, reduce dataset |
| Dataset too large | Use `max_samples=5000` for quick experiments |
| `Cannot patch` error in Unsloth | `pip install "unsloth[colab-new] @ git+https://..."` |
