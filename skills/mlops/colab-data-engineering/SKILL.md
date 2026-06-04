---
name: colab-data-engineering
description: Data engineering for ML on Colab — dataset prep, cleaning, augmentation, synthetic data generation, streaming large datasets, data versioning.
---

# Colab Data Engineering — Dataset Prep, Augmentation, Synthetic Data

Build and optimize datasets for ML training on Colab.

## Dataset Sources

```python
# HuggingFace Datasets (easiest)
!pip install datasets -q
from datasets import load_dataset

dataset = load_dataset("squad", split="train")
dataset = load_dataset("OpenAssistant/oasst1", split="train")
dataset = load_dataset("HuggingFaceFW/fineweb", split="train", streaming=True)  # 15T tokens

# Web scraping
!pip install datasets-web -q
dataset = load_dataset("web_parquet", data_files="https://huggingface.co/datasets/username/repo/data.parquet")

# Local files
dataset = load_dataset("csv", data_files="data.csv")
dataset = load_dataset("json", data_files="data.json")
dataset = load_dataset("parquet", data_files="data.parquet")
```

## Streaming Large Datasets (Don't OOM)

```python
# Stream instead of loading into memory
dataset = load_dataset("c4", "en", split="train", streaming=True)

for example in dataset.take(1000):
    process(example)

# Shard for parallel processing
dataset = load_dataset("c4", "en", split="train", streaming=True)
dataset = dataset.shard(num_shards=8, index=0)  # Process 1/8 of data

# Interleave multiple datasets
from datasets import interleave_datasets
dataset = interleave_datasets([
    load_dataset("dataset1", split="train", streaming=True),
    load_dataset("dataset2", split="train", streaming=True),
])
```

## Data Cleaning

```python
# Filter
dataset = dataset.filter(lambda x: len(x["text"]) > 100)
dataset = dataset.filter(lambda x: "spam" not in x["text"].lower())

# Remove duplicates
dataset = dataset.unique("text")  # Remove exact dedup

# Text cleaning
import re
def clean_text(example):
    text = example["text"]
    text = re.sub(r"<[^>]+>", "", text)     # Remove HTML
    text = re.sub(r"http\S+", "", text)     # Remove URLs
    text = re.sub(r"\s+", " ", text).strip()  # Normalize whitespace
    text = re.sub(r"[^\w\s.,!?-]", "", text) # Remove special chars
    example["text"] = text
    return example

dataset = dataset.map(clean_text)
```

## Text Augmentation

```python
# Back-translation augmentation
!pip install googletrans==4.0.0-rc1 -q
from googletrans import Translator

translator = Translator()
def back_translate(text, src="en", target="fr"):
    translated = translator.translate(text, src=src, dest=target).text
    back_translated = translator.translate(translated, src=target, dest=src).text
    return back_translated

# Synonym replacement (NLAugment)
!pip install nlaugmenter -q

# Paraphrase with model
def paraphrase(text):
    prompt = f"Paraphrase this: {text}"
    return model.generate(prompt)

# EDA (Easy Data Augmentation)
import random

def synonym_replacement(words, n):
    # Replace n random words with synonyms
    pass

def random_insertion(words, n):
    # Insert n random synonyms
    pass

def random_swap(words, n):
    # Swap n pairs of words
    pass

def random_deletion(words, p):
    # Delete words with probability p
    pass
```

## Synthetic Data Generation

```python
# LLM-based synthetic data for fine-tuning
import json, random

def generate_synthetic_data(model, tokenizer, topic, n_samples=100):
    prompts = [
        f"Generate a {topic} instruction and response pair in JSON format.",
        f"Create a question about {topic} and its detailed answer.",
    ]
    
    synthetic = []
    for i in range(n_samples):
        prompt = random.choice(prompts)
        output = model.generate(prompt)
        try:
            data = json.loads(output)
            synthetic.append(data)
        except:
            synthetic.append({"instruction": prompt, "output": output})
    
    return synthetic

# Evolve instructions
def evolve_instruction(model, instruction):
    """Make instruction harder/more specific"""
    prompt = f"""Make this instruction more complex:
    
Original: {instruction}

More complex version: """
    return model.generate(prompt)
```

## Dataset Formatting for Fine-Tuning

```python
# Alpaca format
def to_alpaca(example):
    return {
        "instruction": example["question"],
        "input": example.get("context", ""),
        "output": example["answer"],
    }

# Chat format
def to_chat_format(example):
    return {
        "messages": [
            {"role": "user", "content": example["question"]},
            {"role": "assistant", "content": example["answer"]},
        ]
    }

# Preference format (DPO)
def to_preference_format(example):
    return {
        "prompt": example["question"],
        "chosen": example["good_answer"],
        "rejected": example["bad_answer"],
    }

dataset = dataset.map(to_alpaca)
```

## Data Versioning

```python
# Push to HuggingFace Hub
dataset.push_to_hub("username/dataset-name", private=True)

# Save locally
dataset.save_to_disk("/content/my_dataset")

# Load from disk
from datasets import load_from_disk
dataset = load_from_disk("/content/my_dataset")

# Save as parquet (efficient, compressed)
dataset.to_parquet("data.parquet")

# Track with DVC
!pip install dvc -q
!dvc init
!dvc add data.parquet
!git add data.parquet.dvc
```

## Quality Analysis

```python
import matplotlib.pyplot as plt

# Text length distribution
lengths = [len(ex["text"]) for ex in dataset]
plt.hist(lengths, bins=50)
plt.title("Text Length Distribution")
plt.show()

# Deduplication analysis
from collections import Counter
texts = [ex["text"][:100] for ex in dataset]  # First 100 chars
dupes = Counter(texts)
print(f"Duplicate prefixes: {sum(1 for c in dupes.values() if c > 1)}")

# Label classification (classification tasks)
labels = [ex["label"] for ex in dataset]
plt.bar(Counter(labels).keys(), Counter(labels).values())
plt.title("Label Distribution")
plt.xticks(rotation=45)
plt.show()
```

## Upload Large Datasets to HuggingFace

```python
# Using huggingface_hub
!pip install huggingface_hub -q
huggingface-cli login

# Upload folder
from huggingface_hub import HfApi
api = HfApi()
api.upload_folder(
    folder_path="/content/my_dataset",
    repo_id="username/dataset-name",
    repo_type="dataset",
)
```
