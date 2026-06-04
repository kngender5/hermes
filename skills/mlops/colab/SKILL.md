---
name: colab
description: Full Google Colab platform guide — runtime types, GPU/TPU, terminal access, magic commands, package management (pip/uv/apt), secrets, Drive integration, file I/O, GPU memory management, background processes, SSH/ngrok, LLM/HF workflows, interactive widgets, Gemini AI integration, TPU/JAX, tier comparison, preinstalled packages, and power user patterns. Covers Colab through mid-2026.
---

# Google Colab — Deep Platform Guide

Comprehensive technical reference for Colab power users. Covers runtime management, terminal access, package control, secrets, Drive, GPU/TPU, background processes, SSH, LLM workflows, widgets, Gemini AI, and best practices.

## Table of Contents

1. [Architecture & Runtime Model](#1-architecture--runtime-model)
2. [Runtime Types, GPU & TPU Selection](#2-runtime-types-gpu--tpu-selection)
3. [Terminal & Shell Access](#3-terminal--shell-access)
4. [Essential Bash / Shell Commands](#4-essential-bash--shell-commands)
5. [IPython Magic Commands](#5-ipython-magic-commands)
6. [Keyboard Shortcuts](#6-keyboard-shortcuts)
7. [Package Management (pip, apt, uv)](#7-package-management-pip-apt-uv)
8. [Secrets & API Key Management](#8-secrets--api-key-management)
9. [Google Drive Integration](#9-google-drive-integration)
10. [File Operations & Data I/O](#10-file-operations--data-io)
11. [GPU Memory Management](#11-gpu-memory-management)
12. [Background Processes & nohup](#12-background-processes--nohup)
13. [SSH & Remote Access (ngrok)](#13-ssh--remote-access-ngrok)
14. [LLM & Hugging Face Workflows](#14-llm--hugging-face-workflows)
15. [Interactive Widgets & Forms](#15-interactive-widgets--forms)
16. [Gemini AI Integration](#16-gemini-ai-integration)
17. [TPU / JAX Workflows](#17-tpu--jax-workflows)
18. [Tier Comparison: Free vs Pro vs Pro+](#18-tier-comparison-free-vs-pro-vs-pro)
19. [Preinstalled Standard Packages](#19-preinstalled-standard-packages)
20. [Power User Patterns & Best Practices](#20-power-user-patterns--best-practices)

---

## 1. Architecture & Runtime Model

Google Colab is a hosted Jupyter Notebook service backed by ephemeral Linux VMs. Each notebook connects to a single kernel running on one VM with a standard Linux userspace, NVIDIA GPU (when selected), CUDA toolkit, Python 3, and a large preinstalled package set. Default working directory: `/content`.

**Key constraints:**
- **Ephemeral storage**: everything under `/content` not synced to Drive vanishes on disconnect
- **Session lifetime**: free runtimes ~12 hours; idle timeout ~90 min
- **Single kernel**: one Python process; parallel execution only via threads/multiprocessing/async inside the process
- **Preemption**: Google can reclaim VMs early on free tier
- **Network**: full internet access (`wget`, `curl`, `git clone`, `pip install` all work)

---

## 2. Runtime Types, GPU & TPU Selection

**Runtime → Change runtime type → Hardware accelerator**

| Accelerator | Use case | Notes |
|---|---|---|
| None (CPU) | Data wrangling, light tasks | Most stable, no quota pressure |
| GPU | DL training, inference, LLMs | T4, L4, A100 depending on tier/availability |
| TPU | TF/JAX large-scale training | Requires specific library versions |

GPU type is **not guaranteed** — assigned by availability and tier. Free tier commonly gets T4 (16 GB VRAM).

### Verify hardware

```python
!nvidia-smi
!nvidia-smi -L        # short form: GPU name only

# Assert minimum GPU
gpu = !nvidia-smi -L
assert any(x in gpu for x in ['A100', 'V100', 'L4', 'T4']), f"Got: {gpu}"

# Check CPU
!cat /proc/cpuinfo | grep "model name" | head -1

# Check RAM
import psutil
print(f"RAM: {psutil.virtual_memory().total / 1e9:.1f} GB")

# Check disk
!df -h /content
```

### RAM tier selection

"High-RAM" controls **system RAM**, not VRAM. Free: ~13.7 GB, Pro: ~27.4 GB.

---

## 3. Terminal & Shell Access

### Method 1: `!` prefix (non-interactive, one-shot)

```python
!ls /content
!nvidia-smi
!cat /proc/version
```

Each `!` spawns a new subshell. Variables don't persist between calls.

### Method 2: `%%shell` cell magic (multi-line, one subshell)

```python
%%shell
cd /content
mkdir -p myproject/data
echo "Project ready"
ls -la myproject/
```

### Method 3: `!bash` (interactive input prompt)

```python
!bash
```

Type `exit` to close.

### Method 4: `colab-xterm` (full TTY, no Pro required)

```python
!pip install colab-xterm
%load_ext colabxterm
%xterm
```

### Method 5: Pro/Pro+ built-in terminal

Pro and Pro+ users get a **Terminal** icon in the left sidebar.

---

## 4. Essential Bash / Shell Commands

### Filesystem & navigation

```bash
!pwd                         # default: /content
!ls -la
!ls -lah /content/drive
!find /content -name "*.pt"
!du -sh /content/*
!mkdir -p /content/runs/exp1
!cp src.py /content/drive/MyDrive/
!mv old_name.py new_name.py
!rm -rf /content/tmp/
```

### Text processing

```bash
!cat /content/log.txt
!head -n 50 /content/log.txt
!tail -f /content/train.log        # follow live log
!grep -n "error" output.txt
!wc -l /content/data.csv
!sed -i 's/old/new/g' config.yaml
!awk '{print $1,$3}' data.tsv
```

### Network & downloads

```bash
!wget -O /content/data.zip "https://example.com/file.zip"
!wget -q --show-progress URL
!curl -L URL -o output_file
!curl -s URL | python3 -
!git clone https://github.com/org/repo /content/myrepo
!git -C /content/myrepo pull
```

### Process management

```bash
!ps aux | grep python
!kill -9 <PID>
!pgrep -f train.py
```

### Archives

```bash
!unzip -q data.zip -d /content/data/
!tar -xzf archive.tar.gz -C /content/
!tar -czf backup.tar.gz /content/models/
!zip -r output.zip /content/results/
```

### Environment inspection

```bash
!env | sort
!python3 --version
!nvcc --version
!cat /etc/os-release
!free -h
```

### Capture shell output into Python variables

```python
result = !wc -l /content/data.csv
lines = int(result.split())

OUT_DIR = '/content/drive/MyDrive/checkpoints'
!mkdir -p {OUT_DIR}
!ls -la {OUT_DIR}
```

---

## 5. IPython Magic Commands

Line magics use `%` (one line); cell magics use `%%` (whole cell).

### Discovery

```python
%lsmagic
%magic
%timeit?
```

### Timing and profiling

```python
%time some_function()
%timeit some_function()
%%time
%%timeit
%prun some_function()
```

### Execution control

```python
%run myscript.py
%run -t myscript.py
%load path/to/file.py
%%writefile /content/config.yaml
```

### Environment variables

```python
%env
%env MY_VAR=value
%env HF_TOKEN
```

### Autoreload (essential for `.py` module development)

```python
%load_ext autoreload
%autoreload 2    # reload all changed modules before each cell run
```

### Shell interaction

```python
%%bash
echo "multi-line bash"
ls /content

%%javascript
console.log('hello from JS')

%%html
<b>Bold output</b>
```

### Colab-specific magics

```python
%load_ext google.colab.data_table   # interactive Pandas tables
%tensorflow_version 2.x
%load_ext tensorboard
%tensorboard --logdir /content/logs
```

### Suppress cell output

```python
%%capture
!pip install -q some_noisy_package
```

---

## 6. Keyboard Shortcuts

Colab uses `Ctrl+M` prefix where Jupyter uses no prefix.

### Cell execution

| Action | Shortcut |
|---|---|
| Run cell (stay) | `Ctrl+Enter` |
| Run cell → next | `Shift+Enter` |
| Run cell → insert below | `Alt+Enter` |
| Run selection | `Ctrl+Shift+Enter` |
| Run all | `Ctrl+F9` |
| Interrupt | `Ctrl+M I` |
| Restart runtime | `Ctrl+M .` |

### Cell management

| Action | Shortcut |
|---|---|
| Add cell above | `Ctrl+M A` |
| Add cell below | `Ctrl+M B` |
| Delete cell | `Ctrl+M D` |
| Code cell | `Ctrl+M Y` |
| Markdown cell | `Ctrl+M M` |
| Checkpoint | `Ctrl+M S` |

### Editor

| Action | Shortcut |
|---|---|
| Comment/uncomment | `Ctrl+/` |
| Line numbers | `Ctrl+M L` |
| Find & replace | `Ctrl+H` |
| All shortcuts | `Ctrl+M H` |

**Pro tip**: Tools → Keyboard shortcuts to remap. Customizations save globally.

---

## 7. Package Management (pip, apt, uv)

### pip

```python
!pip install package_name
!pip install "torch==2.3.0" "transformers>=4.40"
!pip install -r /content/requirements.txt
!pip install -q package_name
!pip list
!pip show transformers
```

### uv (10–100× faster, pre-installed since mid-2025)

```python
!uv pip install torch transformers accelerate datasets
!uv pip install -r requirements.txt
!uv pip compile requirements.in   # generate lock file with hashes
```

Prefer `uv pip install` for any session with many dependencies.

### apt-get (system packages)

```python
!apt-get update -qq
!apt-get install -y -qq ffmpeg libsm6 libxext6
!apt-get install -y -qq git-lfs
!apt-get install -y -qq build-essential
```

### Bypass reinstall on kernel restart (flag file trick)

```bash
![ ! -f "pip_installed" ] && uv pip install transformers accelerate bitsandbytes && touch pip_installed
```

### Persist packages across sessions via Drive

```python
import sys, os
from google.colab import drive
drive.mount('/content/drive')
pkg_path = '/content/drive/MyDrive/colab_packages'
os.makedirs(pkg_path, exist_ok=True)
sys.path.insert(0, pkg_path)
!pip install --target={pkg_path} some_package
```

### Detect runtime environment

```python
COLAB = 'google.colab' in str(get_ipython())
```

---

## 8. Secrets & API Key Management

Colab has a native **Secrets** panel (key icon 🔑 in the sidebar) — encrypted, per-account key-value storage.

### Setting up secrets

1. Click the **key icon** (🔑) in the left sidebar
2. Click **Add new secret**
3. Enter name (permanent once set) and value (editable)
4. Toggle **Notebook access** per notebook

### Reading secrets in code

```python
from google.colab import userdata
import os

hf_token = userdata.get('HF_TOKEN')
openai_key = userdata.get('OPENAI_API_KEY')

os.environ['HF_TOKEN'] = userdata.get('HF_TOKEN')
os.environ['OPENAI_API_KEY'] = userdata.get('OPENAI_API_KEY')
```

### Security rules

- Never print or display secret values
- Regularly audit which notebooks have access toggled on
- For numeric secrets: `int(userdata.get('PORT'))`

### Alternative: JSON secrets file in Drive

```python
import json
from google.colab import drive
drive.mount('/content/drive')

with open('/content/drive/MyDrive/secrets.json') as f:
    secrets = json.load(f)
os.environ['API_KEY'] = secrets['API_KEY']
```

Never commit `secrets.json` to any Git repository.

---

## 9. Google Drive Integration

Drive is the main persistence layer for Colab sessions.

### Basic mount

```python
from google.colab import drive
drive.mount('/content/drive')
# Files at: /content/drive/MyDrive/
```

### Force remount

```python
drive.mount('/content/drive', force_remount=True)
```

### Flush and unmount safely

```python
drive.flush_and_unmount()
```

### Avoid working directly on mounted Drive paths

Drive is accessed over a network mount and is **significantly slower** than local `/content`. Best practice:

1. Copy data from Drive to `/content` at session start
2. Work on `/content`
3. Copy results back to Drive at the end

```python
!cp -r "/content/drive/MyDrive/datasets/mydata" /content/data
# ... train on /content/data ...
!cp -r /content/checkpoints "/content/drive/MyDrive/checkpoints"
```

### Import custom Python modules from Drive

```python
import sys
sys.path.append('/content/drive/MyDrive/my_packages/')
from my_utils import helper_function
```

### gdown: download large Drive files

```python
!pip install -q gdown --upgrade
!gdown "https://drive.google.com/uc?id=FILE_ID"
```

### Google Cloud Storage with gsutil (preinstalled)

```python
!gsutil -m cp -r /content/data/ gs://my-bucket/data/
!gsutil -m cp -r gs://my-bucket/data/ /content/data/
```

---

## 10. File Operations & Data I/O

### Upload files from local machine

```python
from google.colab import files
uploaded = files.upload()   # opens file picker dialog
# Returns dict: {filename: bytes_content}
```

### Download files to local machine

```python
from google.colab import files
files.download('/content/results/output.zip')
```

### Write files directly from a cell

```python
%%writefile /content/config.yaml
model: llama3
quantization: q4_k_m
max_tokens: 2048
temperature: 0.7
```

Or in Python:

```python
with open('/content/config.json', 'w') as f:
    json.dump({'key': 'value'}, f)
```

### Large datasets: chunked loading

```python
import pandas as pd

chunks = []
for chunk in pd.read_csv('/content/data.csv', chunksize=100_000):
    chunk['total'] = chunk['price'] * chunk['qty']
    chunks.append(chunk[['id', 'total']])
df = pd.concat(chunks, ignore_index=True)
```

### Prefer Parquet over CSV for repeated loads

```python
df.to_parquet('/content/data.parquet', index=False)
df = pd.read_parquet('/content/data.parquet')
```

---

## 11. GPU Memory Management

### Monitor VRAM

```python
!nvidia-smi
!nvidia-smi --query-gpu=memory.used,memory.free --format=csv,noheader
```

### Check from Python

```python
!pip install nvidia-ml-py3
import pynvml
pynvml.nvmlInit()
handle = pynvml.nvmlDeviceGetHandleByIndex(0)
info = pynvml.nvmlDeviceGetMemoryInfo(handle)
print(f"Used: {info.used / 1e9:.2f} GB / Total: {info.total / 1e9:.2f} GB")
```

### Release GPU memory (PyTorch)

```python
import torch, gc
del model
gc.collect()
torch.cuda.empty_cache()
```

### Release GPU memory (TensorFlow/Keras)

```python
import tensorflow as tf
tf.keras.backend.clear_session()
```

### Load models in lower precision

```python
from transformers import AutoModelForCausalLM
import torch

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3-8B",
    torch_dtype=torch.float16,
    device_map="auto"
)
```

For 8-bit / 4-bit quantization:

```python
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3-8B",
    load_in_8bit=True,     # or load_in_4bit=True
    device_map="auto"
)
```

---

## 12. Background Processes & nohup

### Basic background process

```bash
!nohup python train.py > /content/train.log 2>&1 &
```

- `nohup`: immune to hangup signals
- `> /content/train.log 2>&1`: stdout + stderr → log file
- `&`: run in background (cell returns immediately)

### Capture the PID

```python
import subprocess
proc = subprocess.Popen(
    ["python", "-u", "train.py"],
    stdout=open("/content/train.log", "w"),
    stderr=subprocess.STDOUT
)
print(f"PID: {proc.pid}")
```

### Monitor the log live

```bash
!tail -f /content/train.log
```

### Find and kill

```bash
!ps aux | grep train.py
!kill <PID>
!kill -9 <PID>
!pgrep -f train.py
```

### Run TGI / vLLM server as background process

```python
%%shell
nohup python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3-8B-Instruct \
    --port 8000 > /content/vllm.log 2>&1 &
echo "Server PID: $!"
```

Call from another cell:

```python
import requests
response = requests.post("http://localhost:8000/v1/completions", json={
    "model": "meta-llama/Llama-3-8B-Instruct",
    "prompt": "Explain neural networks:",
    "max_tokens": 100
})
print(response.json())
```

### Auto-disconnect runtime when done

```python
from google.colab import runtime
runtime.unassign()
```

---

## 13. SSH & Remote Access (ngrok)

### SSH into Colab via colab-ssh

```python
!pip install colab_ssh --upgrade
from colab_ssh import launch_ssh
launch_ssh('YOUR_NGROK_AUTH_TOKEN', 'your_password')
```

Connect from your machine:

```bash
ssh -p <PORT> root@<NGROK_HOST>
```

### SSH + VSCode remote development

Use the SSH config generated by `colab_ssh`. In VSCode: Remote-SSH → Connect to Host.

### SSHFS mount locally

```bash
sshfs -p <PORT> root@<NGROK_HOST>:/content/drive/MyDrive /mnt/colab
```

### Full TTY xterm alternative (no ngrok account needed)

```python
!pip install colab-xterm
%load_ext colabxterm
%xterm
```

---

## 14. LLM & Hugging Face Workflows

### Environment setup cell

```python
# 1. GPU assert
gpu_info = !nvidia-smi -L
assert gpu_info, "No GPU detected!"

# 2. Install core stack
!uv pip install transformers accelerate bitsandbytes datasets huggingface_hub

# 3. Auth
from google.colab import userdata
import os
os.environ['HF_TOKEN'] = userdata.get('HF_TOKEN')
from huggingface_hub import login
login(token=os.environ['HF_TOKEN'])
```

### Load model with pipeline (simplest)

```python
from transformers import pipeline

generator = pipeline(
    "text-generation",
    model="meta-llama/Llama-3.2-3B-Instruct",
    device_map="auto",
    torch_dtype="auto"
)
result = generator("What is machine learning?", max_new_tokens=200)
print(result['generated_text'])
```

### Load model with AutoModel (full control)

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_id = "mistralai/Mistral-7B-Instruct-v0.3"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    attn_implementation="flash_attention_2"  # if available
)

inputs = tokenizer("Explain transformers:", return_tensors="pt").to("cuda")
with torch.no_grad():
    output = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(output, skip_special_tokens=True))
```

### 4-bit quantization (fit 7B+ models in free-tier T4 VRAM)

```python
from transformers import BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=bnb_config,
    device_map="auto"
)
```

### HF Text Generation Inference (TGI) server

```python
!pip install colab-xterm
%load_ext colabxterm
%xterm
# In xterm: text-generation-launcher --model-id TheBloke/Llama-2-13B-chat-AWQ \
#            --quantize awq --port 5000

from huggingface_hub import InferenceClient
client = InferenceClient(model="http://127.0.0.1:5000")
for token in client.text_generation("What is JAX?", max_new_tokens=256, stream=True):
    print(token, end="", flush=True)
```

### RAG: cache embeddings to Drive

```python
import pickle

def save_index(vector_db, path="/content/drive/MyDrive/rag_index.pkl"):
    with open(path, "wb") as f:
        pickle.dump(vector_db, f)

def load_index(path="/content/drive/MyDrive/rag_index.pkl"):
    with open(path, "rb") as f:
        return pickle.load(f)
```

---

## 15. Interactive Widgets & Forms

### Basic interact decorator

```python
import ipywidgets as widgets
from ipywidgets import interact

@interact(
    model=["gpt2", "distilgpt2", "mistral"],
    temperature=(0.0, 2.0, 0.1),
    max_tokens=(50, 500, 50)
)
def run_inference(model="gpt2", temperature=0.7, max_tokens=100):
    print(f"Running {model} at temp={temperature}, max_tokens={max_tokens}")
```

### Manual widget layout

```python
import ipywidgets as widgets
from IPython.display import display

dropdown = widgets.Dropdown(options=['fp16', 'int8', 'int4'], description='Precision:')
slider = widgets.IntSlider(value=128, min=16, max=512, description='Max tokens:')
button = widgets.Button(description="Run")
output = widgets.Output()

def on_click(b):
    with output:
        output.clear_output()
        print(f"Precision: {dropdown.value}, Max tokens: {slider.value}")

button.on_click(on_click)
display(widgets.VBox([dropdown, slider, button, output]))
```

### Colab `@param` form syntax (native, no imports)

```python
#@title Configuration
model_name = "mistral-7b" #@param ["mistral-7b", "llama3-8b", "gemma-2b"]
quantize = True #@param {type:"boolean"}
max_tokens = 256 #@param {type:"slider", min:64, max:2048, step:64}
temperature = 0.7 #@param {type:"number"}
```

### Interactive Pandas DataFrames

```python
%load_ext google.colab.data_table
# or
from google.colab import data_table
data_table.enable_dataframe_formatter()
```

---

## 16. Gemini AI Integration

Colab received an AI-first upgrade in mid-2025 with Gemini 2.5 Flash.

### Enabling Gemini assistance

**Tools → Settings → AI assistance:**
- "Show AI powered inline completions" → **enabled**
- "Consent to use generative features" → **enabled**

### Key AI features

- **Inline code completion**: autocompletes as you type
- **Generate code from natural language**: click spark icon, type prompt
- **Explain code**: select a cell and ask Gemini
- **Fix errors**: click "Fix error" on exceptions
- **Iterative querying**: conversational sidebar
- **Code transformation**: describe a refactor in natural language

---

## 17. TPU / JAX Workflows

### Select TPU runtime

Runtime → Change runtime type → Hardware accelerator → **TPU**

### JAX on TPU

```python
import jax.tools.colab_tpu
jax.tools.colab_tpu.setup_tpu()

import jax
print(jax.device_count())   # should show 8 TPU cores
print(jax.devices())
```

### TPU data requirements

Datasets must be in a Google Cloud Storage bucket (local Drive I/O too slow):

```bash
!gsutil -m cp -r /content/train_data/ gs://your-bucket/data/
```

---

## 18. Tier Comparison: Free vs Pro vs Pro+

| Feature | Free | Pro ($9.99/mo) | Pro+ ($49.99/mo) |
|---|---|---|---|
| GPU RAM | ~11–16 GB (T4/K80) | ~16 GB (T4/P100) | ~40 GB (A100) |
| System RAM | ~13.7 GB | ~27.4 GB | ~52 GB |
| Max runtime | ~12 hrs | ~24 hrs | ~24 hrs+ |
| Idle timeout | ~90 min | ~90 min | Extended |
| Background terminal | ✗ | ✓ | ✓ |
| Priority GPU | No | Higher | Highest |

**PAYG**: $9.99 for 100 compute units, no subscription.

---

## 19. Preinstalled Standard Packages

Core packages on every Colab runtime (2025–2026):

**ML / DL**: `torch`, `torchvision`, `torchaudio`, `tensorflow`, `keras`, `jax`, `jaxlib`, `scikit-learn`, `xgboost`, `lightgbm`

**Data science**: `numpy`, `scipy`, `pandas`, `statsmodels`, `matplotlib`, `seaborn`, `plotly`, `pillow`, `opencv-python`

**NLP / LLMs**: `transformers`, `tokenizers`, `datasets`, `huggingface_hub`

**Utilities**: `requests`, `httpx`, `aiohttp`, `tqdm`, `rich`, `loguru`, `pydantic`, `fastapi`, `flask`, `sympy`, `numba`, `gdown`, `gsutil`, `git-lfs`, `uv`

**Not preinstalled (common installs)**: `accelerate`, `bitsandbytes`, `peft`, `trl`, `vllm`, `llama-cpp-python`, `langchain`, `llama-index`, `colab-xterm`

---

## 20. Power User Patterns & Best Practices

### Notebook structure template

```
Cell 0: GPU assert + tier check
Cell 1: Drive mount (if needed)
Cell 2: uv installs (with flag-file guard)
Cell 3: Secrets / env vars setup
Cell 4: sys.path additions for custom modules
Cell 5: Imports
Cell 6: Config / hyperparameters (@param or dict)
Cell 7+: Data loading → preprocessing → model → training → eval → save
Last cell: drive.flush_and_unmount() + runtime.unassign()
```

### Checkpointing strategy

```python
import os

def save_checkpoint(model, optimizer, epoch, path):
    os.makedirs(path, exist_ok=True)
    torch.save({
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
    }, f"{path}/ckpt_epoch{epoch}.pt")
    # Keep only last 3 checkpoints
    ckpts = sorted(os.listdir(path))
    for old in ckpts[:-3]:
        os.remove(f"{path}/{old}")
```

### Open GitHub notebooks directly in Colab

Replace `github.com` with `githubtocolab.com` in any notebook URL, or use:
```
https://colab.research.google.com/github/<org>/<repo>/blob/<branch>/notebook.ipynb
```

### Add "Open in Colab" badge to README

```markdown
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yourorg/yourrepo/blob/main/notebook.ipynb)
```

### Custom snippet library

Create `snippets.ipynb` in Drive, then register: **Tools → Settings → paste snippet notebook URL**. Use the **<>** sidebar panel to search and insert snippets.

### Mirror cell as persistent side tab

**Tools → Command palette → Mirror cell in tab**. The mirrored cell stays visible while scrolling.

### Desktop notifications on task completion

**Tools → Settings → Site → enable Show desktop notifications**

### Detect local vs Colab

```python
COLAB = 'google.colab' in str(get_ipython())
LOCAL = not COLAB
```

### Send completion notification via messaging API

```python
import requests
from urllib.parse import quote_plus
requests.get(f'https://api.callmebot.com/signal/send.php?phone={number}&apikey={key}&text={quote_plus("Training done!")}')
```

### Run R in Colab

Open: `https://colab.research.google.com/notebook#create=true&language=r`

### Run Rust in Colab

Open: `https://colab.to/rust`, run the first cell, then reload.

---

*Guide covers Google Colab as of mid-2026. Gemini 2.5 Flash AI-first update released June 2025. `uv` pre-installed since ~mid-2025. Check [Colab release notes](https://colab.research.google.com/notebooks/relnotes.ipynb) for latest changes.*
