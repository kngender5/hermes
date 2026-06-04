---
name: colab-distributed
description: Distributed training on Colab — DDP, DeepSpeed ZeRO, FSDP, multi-GPU, mixed precision, gradient accumulation. Scale training across GPUs.
---

# Colab Distributed Training — Multi-GPU, DeepSpeed, FSDP

Distributed training strategies for scaling on Colab and multi-GPU setups.

## Colab GPU Tiers

| Tier | GPU | VRAM | Multi-GPU | Max Hours |
|------|-----|------|-----------|-----------|
| Free | T4 | 16GB | ❌ | 12 |
| Pro | T4 / L4 | 16-22.5GB | ❌ | 12 |
| Pro+ | A100 | 40-80GB | ❌ | 24 |
| Enterprise | A100 | 80GB | ✅ | 24 |
| Pay-as-you-go | A100/H100 | 40-80GB | ✅ | Unlimited |

**Note:** Standard Colab provides only 1 GPU. Multi-GPU requires Colab Enterprise/Pay-as-you-go or external compute.

## Distributed Strategies Comparison

| Strategy | Memory Efficiency | Speed | Complexity | Best For |
|----------|-------------------|-------|------------|----------|
| DDP | Medium | Fast | Low | Multi-GPU same-node |
| DeepSpeed ZeRO-1 | High | Fast | Medium | Large models, single-node |
| DeepSpeed ZeRO-2 | Very High | Fast | Medium | 10B+ models |
| DeepSpeed ZeRO-3 | Maximum | Medium | High | 70B+ models |
| FSDP | Maximum | Medium | Medium | PyTorch native |
| DeepSpeed + FSDP | Maximum | Slow | Very High | 100B+ |

## Method 1: DDP (Data Distributed Parallel)

Best for: Multi-GPU training where each GPU holds a full model copy.

```python
import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader, DistributedSampler
import os

def setup_ddp():
    dist.init_process_group("nccl")
    rank = dist.get_rank()
    torch.cuda.set_device(rank)
    return rank

def train():
    rank = setup_ddp()
    
    model = MyModel().to(rank)
    model = DDP(model, device_ids=[rank])
    
    dataset = MyDataset()
    sampler = DistributedSampler(dataset, num_replicas=dist.get_world_size(), rank=rank)
    dataloader = DataLoader(dataset, batch_size=32, sampler=sampler)
    
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)
    
    for epoch in range(num_epochs):
        sampler.set_epoch(epoch)
        for batch in dataloader:
            loss = model(batch)
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()

# Launch: torchrun --nproc_per_node=2 train.py
```

## Method 2: DeepSpeed ZeRO

Best for: Single-node multi-GPU with maximum memory efficiency.

### Install
```python
!pip install deepspeed -q
```

### DeepSpeed ZeRO-2 Config
```python
ds_config = {
    "train_batch_size": 32,
    "gradient_accumulation_steps": 4,
    "fp16": {"enabled": True},
    "zero_optimization": {
        "stage": 2,               # ZeRO-1/2/3
        "offload_optimizer": {"device": "cpu"},  # Offload to CPU
        "allgather_partitions": True,
        "allgather_bucket_size": 2e8,
        "overlap_comm": True,
        "reduce_scatter": True,
        "reduce_bucket_size": 2e8,
        "contiguous_gradients": True,
    },
    "gradient_clipping": 1.0,
    "wall_clock_breakdown": False,
}
```

### Training with DeepSpeed
```python
import deepspeed
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8B")

# Initialize DeepSpeed
model_engine, optimizer, _, _ = deepspeed.initialize(
    model=model,
    config=ds_config,
)

for batch in dataloader:
    loss = model_engine(batch)
    model_engine.backward(loss)
    model_engine.step()
```

### DeepSpeed ZeRO-3 (Maximum memory savings)
```python
ds_config["zero_optimization"]["stage"] = 3
ds_config["zero_optimization"]["offload_param"] = {"device": "cpu"}
ds_config["zero_optimization"]["offload_optimizer"] = {"device": "cpu"}
ds_config["zero_optimization"]["stage3_param_persistence_threshold"] = 1e6
ds_config["zero_optimization"]["stage3_max_live_parameters"] = 1e9
ds_config["zero_optimization"]["stage3_prefetch_bucket_size"] = 5e8
```

## Method 3: FSDP (Fully Sharded Data Parallel)

Best for: PyTorch-native distributed training, 70B+ models.

```python
import torch
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP
from torch.distributed.fsdp import MixedPrecision, ShardingStrategy, CPUOffload
from torch.distributed.fsdp.wrap import transformer_auto_wrap_policy
from functools import partial

# Mixed precision policy
mp_policy = MixedPrecision(
    param_dtype=torch.float16,
    reduce_dtype=torch.float16,
    buffer_dtype=torch.float16,
)

# Auto-wrap policy for transformer layers
auto_wrap_policy = partial(
    transformer_auto_wrap_policy,
    transformer_layer_cls={LlamaDecoderLayer},
)

model = FSDP(
    model,
    auto_wrap_policy=auto_wrap_policy,
    mixed_precision=mp_policy,
    sharding_strategy=ShardingStrategy.FULL_SHARD,  # or SHARD_GRAD_OP, NO_SHARD
    cpu_offload=CPUOffload(offload_params=True),    # Offload to CPU
    device_id=torch.cuda.current_device(),
)
```

## Method 4: Accelerate (HuggingFace — Easiest)

Best for: Quick distributed training with minimal code changes.

```python
!pip install accelerate -q

from accelerate import Accelerator

accelerator = Accelerator(
    mixed_precision="fp16",
    gradient_accumulation_steps=4,
    deepspeed_plugin=None,  # or DeepSpeedPlugin(ds_config=ds_config)
)

model, optimizer, dataloader = accelerator.prepare(model, optimizer, dataloader)

for batch in dataloader:
    with accelerator.accumulate(model):
        loss = model(batch)
        accelerator.backward(loss)
        optimizer.step()
        optimizer.zero_grad()
```

### Accelerate + DeepSpeed
```python
from accelerate import DeepSpeedPlugin

ds_plugin = DeepSpeedPlugin(ds_config=ds_config)
accelerator = Accelerator(deepspeed_plugin=ds_plugin)
```

## Method 5: Colab-Specific — Simulate Multi-GPU

Since Colab gives 1 GPU, simulate distributed for testing:

```python
# Fake multi-GPU for code testing
import os
os.environ["MASTER_ADDR"] = "localhost"
os.environ["MASTER_PORT"] = "12355"
os.environ["RANK"] = "0"
os.environ["WORLD_SIZE"] = "1"

# Use Accelerate with CPU offload to simulate ZeRO-3
from accelerate import Accelerator
accelerator = Accelerator(
    split_batches=True,
    dispatch_batches=True,
    even_batches=True,
    use_cpu=True,  # Offload to CPU to simulate multi-GPU
)
```

## Gradient Accumulation

Essential for effective large batch training on limited VRAM:

```python
# Manual
accumulation_steps = 8
for i, batch in enumerate(dataloader):
    loss = model(batch) / accumulation_steps
    loss.backward()
    if (i + 1) % accumulation_steps == 0:
        optimizer.step()
        optimizer.zero_grad()

# With Accelerate
accelerator = Accelerator(gradient_accumulation_steps=8)
with accelerator.accumulate(model):
    loss = model(batch)
    accelerator.backward(loss)
    optimizer.step()
```

## Mixed Precision Training

```python
# FP16 (T4 compatible)
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()
for batch in dataloader:
    with autocast(dtype=torch.float16):
        loss = model(batch)
    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()

# BF16 (A100+ only)
with autocast(dtype=torch.bfloat16):
    loss = model(batch)
```

## Memory Optimization Checklist

| Technique | VRAM Saved | Speed Impact |
|-----------|------------|--------------|
| Gradient checkpointing | ~40% | -20% |
| Mixed precision (FP16) | ~50% | +10% |
| Gradient accumulation | Effective batch ↑ | None |
| DeepSpeed ZeRO-2 | ~60% | -5% |
| DeepSpeed ZeRO-3 | ~80% | -15% |
| CPU offload | ~90% | -40% |
| LoRA (instead of full) | ~70% | +10% |
| 4-bit quantization (QLoRA) | ~75% | -10% |

## Common Issues

| Problem | Fix |
|---------|-----|
| NCCL timeout | Increase `NCCL_TIMEOUT`, check network |
| OOM with ZeRO-3 | Enable CPU offload, reduce batch size |
| Slow ZeRO-3 | Use ZeRO-2 instead, or increase bucket size |
| Gradient explosion | Add gradient clipping, reduce LR |
| `torchrun` not found | `pip install torch`, use `python -m torch.distributed.run` |
| Colab single GPU | Use DeepSpeed ZeRO + CPU offload, or FSDP |
