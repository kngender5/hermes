---
name: colab-deployment
description: Deploy ML models from Colab — FastAPI serving, ngrok/cloudflared tunnels, Docker export, ONNX/TFLite conversion, HuggingFace Spaces, model cards.
---

# Colab Deployment — Serve Models as APIs

Deploy trained models from Colab as production-ready endpoints.

## Deployment Options Comparison

| Method | URL Type | Permanent? | HTTPS | Complexity | Best For |
|--------|----------|------------|-------|------------|----------|
| Gradio share | gradio.live | ❌ (session) | ✅ | Lowest | Quick demos |
| ngrok | ngrok.io | ❌ (session) | ✅ | Low | Testing |
| cloudflared | trycloudflare.com | ❌ (session) | ✅ | Low | Quick access |
| HF Spaces | huggingface.co/spaces | ✅ | ✅ | Medium | Permanent demos |
| FastAPI + ngrok | ngrok.io | ❌ (session) | ✅ | Medium | API serving |
| Docker export | N/A | ✅ (manual) | Manual | Medium | Production |
| Colab → GCE | Custom IP | ✅ | Manual | High | Full control |

## Method 1: FastAPI + ngrok (API Server)

### requirements.txt
```
fastapi>=0.115.0
uvicorn>=0.34.0
pyngrok>=7.2.0
pydantic>=2.10.0
gradio>=5.0.0
```

### Notebook Cell — API Server
```python
!pip install fastapi uvicorn pyngrok pydantic -q

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pyngrok import ngrok
import uvicorn, nest_asyncio, threading

nest_asyncio.apply()

app = FastAPI(title="Model API")

class PredictRequest(BaseModel):
    text: str
    max_tokens: int = 128
    temperature: float = 0.7

class PredictResponse(BaseModel):
    output: str
    tokens_used: int

@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    try:
        output = model.generate(
            request.text,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )
        return PredictResponse(output=output, tokens_used=len(output.split()))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok", "model": model_id}

# Start server in background
def run():
    uvicorn.run(app, host="0.0.0.0", port=8000)

thread = threading.Thread(target=run, daemon=True)
thread.start()

# Create ngrok tunnel
public_url = ngrok.connect(8000)
print(f"API URL: {public_url}")
print(f"Docs: {public_url}/docs")
```

### Notebook Cell — Test API
```python
import requests

url = public_url
response = requests.post(f"{url}/predict", json={
    "text": "Explain quantum computing",
    "max_tokens": 256,
    "temperature": 0.7,
})
print(response.json())
```

## Method 2: FastAPI + cloudflared (No auth needed)

```python
!pip install fastapi uvicorn -q
!wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared
!chmod +x cloudflared

# Start FastAPI in background
import subprocess, threading

def run_api():
    subprocess.run(["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"])

threading.Thread(target=run_api, daemon=True).start()

# Start cloudflared tunnel
import time
time.sleep(3)
!./cloudflared tunnel --url http://localhost:8000 2>&1 | grep "trycloudflare"
```

## Method 3: HuggingFace Spaces (Permanent, Free)

### Project structure
```
my-space/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
```

### app.py
```python
import gradio as gr
from transformers import pipeline

pipe = pipeline("text-generation", model="my-model", device=0)

def generate(text, max_tokens=128):
    return pipe(text, max_new_tokens=max_tokens)[0]["generated_text"]

demo = gr.Interface(fn=generate, inputs="text", outputs="text")
demo.launch(server_name="0.0.0.0", server_port=7860)
```

### Push to HF Spaces
```bash
huggingface-cli login --token $HF_TOKEN
cd my-space
git init && git add . && git commit -m "init"
git remote add origin https://huggingface.co/spaces/USERNAME/SPACE_NAME
git push -u origin main
```

## Method 4: Docker Export from Colab

```python
# Generate Dockerfile
dockerfile = """
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04
RUN apt-get update && apt-get install -y python3-pip
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
"""

with open("Dockerfile", "w") as f:
    f.write(dockerfile)

# Build and push to Docker Hub (from Colab)
!docker build -t username/model-api:latest .
!docker login
!docker push username/model-api:latest
```

## Method 5: ONNX Export for Edge/Mobile

```python
!pip install optimum[onnxruntime] -q

# Export PyTorch model to ONNX
import torch

dummy_input = torch.zeros(1, 128, dtype=torch.long)
torch.onnx.export(
    model,
    dummy_input,
    "model.onnx",
    input_names=["input_ids"],
    output_names=["logits"],
    dynamic_axes={
        "input_ids": {0: "batch_size", 1: "sequence_length"},
        "logits": {0: "batch_size", 1: "sequence_length"},
    },
)

# Quantize ONNX
!pip install onnxruntime-tools -q
from onnxruntime.quantization import quantize_dynamic, QuantType

quantize_dynamic("model.onnx", "model-quantized.onnx", weight_type=QuantType.QInt8)
```

## Method 6: TFLite Export (Mobile/Edge)

```python
!pip install tensorflow -q

# Convert PyTorch → ONNX → TF → TFLite
import torch, tf2onnx, tensorflow as tf

# PyTorch to ONNX
torch.onnx.export(model, dummy_input, "model.onnx")

# ONNX to TF
!python -m tf2onnx.convert --onnx model.onnx --output model.pb --opset 13

# TF to TFLite
converter = tf.lite.TFLiteConverter.from_saved_model("model.pb")
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.target_spec.supported_types = [tf.float16]
tflite_model = converter.convert()

with open("model.tflite", "wb") as f:
    f.write(tflite_model)
```

## Model Card & Documentation

```python
from huggingface_hub import ModelCard

card = ModelCard.load("username/model-name")
card.text = """
# Model Card

## Model Details
- **Model:** Llama-3.1-8B fine-tuned on domain X
- **Training:** QLoRA 4-bit on T4 GPU
- **Dataset:** Custom dataset of 10K examples
- **Metrics:** Accuracy 92%, F1 0.89

## Usage
```python
from transformers import pipeline
pipe = pipeline("text-generation", model="username/model-name")
```

## Limitations
- May hallucinate on rare topics
- English only
- Max context 4096 tokens
"""
card.push_to_hub("username/model-name")
```

## Monitoring & Logging

```python
import logging, time
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

request_count = defaultdict(int)

@app.middleware("http")
async def log_requests(request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {duration:.2f}s")
    request_count[request.url.path] += 1
    return response

@app.get("/stats")
async def stats():
    return {
        "total_requests": sum(request_count.values()),
        "endpoint_counts": dict(request_count),
        "uptime": time.time() - start_time,
    }
```

## Common Issues

| Problem | Fix |
|---------|-----|
| ngrok auth error | `ngrok config add-authtoken YOUR_TOKEN` |
| HF Spaces build fail | Check `requirements.txt`, use exact versions |
| ONNX export error | Ensure model is in `.eval()` mode, use correct opset |
| Docker build OOM | Use smaller base image, install fewer packages |
| API timeout | Increase `server_timeout`, use async handlers |
| Model too large for HF Spaces (free) | Use git-lfs, or use GPU Spaces (Pro) |
| Cold start on HF Spaces | Use `warmup` endpoint, keep model in memory |
