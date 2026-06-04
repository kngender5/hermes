---
name: colab-rlhf
description: RLHF and preference optimization on Colab — DPO, PPO, KTO, ORPO, reward modeling, GRPO, Rainbow. Train models to align with human preferences.
---

# Colab RLHF — Preference Optimization

Train models to align with human preferences using RLHF techniques on Colab GPU.

## RLHF Methods Comparison

| Method | Type | Reward Model | VRAM | Speed | Quality | Best For |
|--------|------|-------------|------|-------|---------|----------|
| DPO | Direct preference | ❌ Not needed | Low | Fast | High | Most use cases |
| ORPO | Odds ratio | ❌ Not needed | Low | Fast | Very High | Single-step alignment |
| KTO | Kahneman-Tversky | Optional | Low | Fast | High | Binary feedback |
| PPO | Online RL | ✅ Required | High | Slow | Varies | Complex rewards |
| GRPO | Group relative | Optional | Medium | Medium | High | Math/reasoning |
| RLOO | REINFORCE Left-Off | Optional | Medium | Fast | High | Simpler than PPO |

## VRAM Requirements (7B model)

| Method | VRAM (4-bit LoRA) |
|--------|-------------------|
| DPO | ~10GB |
| ORPO | ~10GB |
| KTO | ~10GB |
| PPO | ~16GB+ |
| GRPO | ~12GB |

## Method 1: DPO (Direct Preference Optimization)

Best for: Most alignment tasks — no reward model needed.

```python
!pip install trl peft bitsandbytes accelerate -q

from trl import DPOTrainer, DPOConfig
from unsloth import FastLanguageModel
from datasets import load_dataset

model, tokenizer = FastLanguageLanguageModel.from_pretrained(
    "unsloth/Llama-3.1-8B-Instruct-bnb-4bit",
    max_seq_length=2048, dtype=None, load_in_4bit=True,
)
model = FastLanguageModel.get_peft_model(model, r=16, lora_alpha=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"])

# Preference dataset: {"prompt": "...", "chosen": "...", "rejected": "..."}
dataset = load_dataset("Intel/orca_dpo_pairs", split="train")

config = DPOConfig(
    output_dir="dpo_output",
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    learning_rate=5e-6,
    beta=0.1,                    # KL divergence weight (0.01-0.5)
    num_train_epochs=1,
    optim="adamw_8bit",
    logging_steps=10,
    save_steps=100,
    report_to="none",
    fp16=True,                   # T4: use fp16 not bf16
)

trainer = DPOTrainer(
    model=model,
    ref_model=None,              # Unsloth handles this automatically
    args=config,
    train_dataset=dataset,
    tokenizer=tokenizer,
    max_length=1024,
    max_prompt_length=512,
)
trainer.train()
model.save_pretrained("dpo_model")
```

## Method 2: ORPO (Odds Ratio Preference Optimization)

Best for: Combining SFT and preference alignment in one step.

```python
from trl import ORPOConfig, ORPOTrainer

config = ORPOConfig(
    output_dir="orpo_output",
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    learning_rate=8e-6,
    beta=0.1,                    # ORPO lambda
    max_steps=200,
    optim="adamw_8bit",
    report_to="none",
)

trainer = ORPOTrainer(
    model=model,
    args=config,
    train_dataset=dataset,
    tokenizer=tokenizer,
)
trainer.train()
```

## Method 3: KTO (Kahneman-Tversky Optimization)

Best for: Binary feedback (good/bad) instead of preference pairs.

```python
from trl import KTOConfig, KTOTrainer

# KTO dataset: {"prompt": "...", "completion": "...", "label": True/False}
dataset = load_dataset("trl-lib/kto-mix-15k", split="train")

config = KTOConfig(
    output_dir="kto_output",
    per_device_train_batch_size=2,
    learning_rate=1e-5,
    beta=0.1,
    num_train_epochs=1,
    optim="adamw_8bit",
)

trainer = KTOTrainer(
    model=model,
    ref_model=None,
    args=config,
    train_dataset=dataset,
    tokenizer=tokenizer,
)
trainer.train()
```

## Method 4: RLOO (REINFORCE Leave-One-Out)

Best for: Simpler alternative to PPO.

```python
from trl import RLOOConfig, RLOOTrainer, RLOOTrainer

# RLOO requires a reward model or scoring function
def reward_fn(completions, **kwargs):
    """Score completions. Replace with your reward model."""
    scores = []
    for comp in completions:
        # Use a reward model or heuristic
        score = len(comp) * 0.01  # Placeholder
        scores.append(score)
    return scores

config = RLOOConfig(
    output_dir="rloo_output",
    per_device_train_batch_size=2,
    learning_rate=1e-5,
    num_train_epochs=1,
)

trainer = RLOOTrainer(
    model=model,
    reward_model=reward_fn,      # Function or model
    args=config,
    train_dataset=dataset,
    tokenizer=tokenizer,
)
trainer.train()
```

## Method 5: PPO (Proximal Policy Optimization)

Best for: Complex reward shaping, but needs a reward model and more VRAM.

```python
!pip install trl peft -q

from trl import PPOTrainer, PPOConfig, create_reference_model
from transformers import pipeline

# Reward model (can be a simple classifier)
reward_model = pipeline("text-classification", model="OpenAssistant/reward-model-deberta-v3-large-v2")

# Policy model
policy = model
ref_policy = create_reference_model(policy)

config = PPOConfig(
    learning_rate=1e-5,
    batch_size=8,
    mini_batch_size=2,
    gradient_accumulation_steps=4,
    cliprange=0.2,
    cliprange_value=0.2,
    vf_coef=0.1,
    entropy_coef=0.01,
    gamma=1.0,
    lam=0.95,
)

ppo_trainer = PPOTrainer(config, policy, ref_policy, tokenizer, dataset=dataset)

for batch in ppo_trainer.dataloader:
    query_tensors = batch["input_ids"]
    
    # Generate responses
    response_tensors = ppo_trainer.generate(query_tensors, max_new_tokens=128)
    
    # Compute rewards
    texts = [tokenizer.decode(r, skip_special_tokens=True) for r in response_tensors]
    rewards = [reward_model(t)[0]["score"] for t in texts]
    
    # PPO step
    stats = ppo_trainer.step(query_tensors, response_tensors, rewards)
```

## Reward Model Training

```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from torch.utils.data import Dataset

# Format: {"prompt": "...", "chosen": "...", "rejected": "..."}
class RewardDataset(Dataset):
    def __init__(self, data, tokenizer, max_length=512):
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __getitem__(self, idx):
        chosen = self.tokenizer(
            self.data[idx]["prompt"] + self.data[idx]["chosen"],
            max_length=self.max_length, truncation=True, padding="max_length",
            return_tensors="pt",
        )
        rejected = self.tokenizer(
            self.data[idx]["prompt"] + self.data[idx]["rejected"],
            max_length=self.max_length, truncation=True, padding="max_length",
            return_tensors="pt",
        )
        return {
            "input_ids_chosen": chosen["input_ids"].squeeze(),
            "attention_mask_chosen": chosen["attention_mask"].squeeze(),
            "input_ids_rejected": rejected["input_ids"].squeeze(),
            "attention_mask_rejected": rejected["attention_mask"].squeeze(),
        }
    
    def __len__(self):
        return len(self.data)

# Bradley-Terry loss for reward modeling
import torch.nn.functional as F

def reward_loss(model, chosen_ids, chosen_mask, rejected_ids, rejected_mask):
    chosen_reward = model(chosen_ids, attention_mask=chosen_mask).logits.squeeze()
    rejected_reward = model(rejected_ids, attention_mask=rejected_mask).logits.squeeze()
    loss = -F.logsigmoid(chosen_reward - rejected_reward).mean()
    return loss
```

## GRPO (Group Relative Policy Optimization)

Best for: Math, coding, reasoning — uses group-relative advantages instead of a critic.

```python
# GRPO is in the latest TRL (0.15+)
!pip install trl>=0.15.0 -q

from trl import GRPOConfig, GRPOTrainer

def reward_func(completions, **kwargs):
    """Evaluate completions. Return list of scores."""
    rewards = []
    for comp in completions:
        # Check if answer is correct
        if verify_answer(comp, kwargs.get("answer", "")):
            rewards.append(1.0)
        else:
            rewards.append(-0.5)
    return rewards

config = GRPOConfig(
    output_dir="grpo_output",
    per_device_train_batch_size=2,
    num_generations=8,           # Generate 8 responses, group-relative
    learning_rate=1e-5,
    beta=0.04,                   # KL penalty
    num_train_epochs=1,
)

trainer = GRPOTrainer(
    model=model,
    reward_funcs=reward_func,
    args=config,
    train_dataset=dataset,
    tokenizer=tokenizer,
)
trainer.train()
```

## Creating Preference Data

```python
# Generate preference data with LLM
import json

def create_preference_data(model, questions):
    data = []
    for q in questions:
        # Generate good response
        good = model.generate(q, temperature=0.7, max_tokens=200)
        
        # Generate bad response (with wrong instructions or low temp)
        bad = model.generate(q, temperature=0.1, max_tokens=50)
        
        data.append({
            "prompt": q,
            "chosen": good,
            "rejected": bad,
        })
    return data

# LLM-as-judge scoring
def llm_judge(question, response):
    prompt = f"""Rate this response on a scale of 1-10:

Question: {question}
Response: {response}

Score (1-10):"""
    return model.generate(prompt)
```

## Evaluation After RLHF

```python
# MT-Bench evaluation
!pip install fastchat -q
# Run: python -m fastchat.llm_judge --model-path /content/dpo_model

# Custom evaluation
def evaluate_alignment(model, test_questions):
    results = []
    for q in test_questions:
        response = model.generate(q)
        # Check for: helpfulness, harmlessness, honesty
        results.append({
            "question": q,
            "response": response,
            "helpful": judge_helpfulness(response),
            "harmless": judge_harmlessness(response),
        })
    return results
```

## Common Issues

| Problem | Fix |
|---------|-----|
| DPO model diverges | Reduce `beta` (0.01-0.05), reduce LR |
| NaN loss in DPO | Check for empty strings in dataset |
| PPO too slow on T4 | Use DPO or ORPO instead (no reward model) |
| Reward model overfitting | Use regularization, more data |
| ORPO quality worse than DPO alone | Increase training steps, check `beta` |
| GRPO unstable | Reduce `num_generations` to 4, adjust `beta` |
| Model becomes too cautious | Reduce KL penalty, increase diversity |
