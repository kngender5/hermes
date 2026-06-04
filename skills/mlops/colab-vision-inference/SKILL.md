---
name: colab-vision-inference
description: Serve vision models (ViT, CLIP, LLaVA, BLIP, SmolVLM, Qwen-VL) via Google Colab GPU + Gradio. Image classification, VQA, captioning, OCR.
---

# Colab Vision Inference — Image Models

Serve vision and vision-language models on Google Colab GPU with Gradio UI.

## Supported Architectures

| Model | Task | Params | VRAM (T4) | T4 OK |
|-------|------|--------|-----------|-------|
| ViT-B/16 | Classification | 86MB | ~1GB | ✅ |
| CLIP ViT-L/14 | Embedding/Zero-shot | 428MB | ~2GB | ✅ |
| BLIP-2 | Captioning/VQA | 4B | ~8GB | ✅ |
| LLaVA-1.5 | VQA/Chat | 7B | ~10GB | ✅ |
| LLaVA-Next | VQA/Chat | 7B–34B | ~10–20GB | ✅ (7B) |
| SmolVLM | VQA/Chat | 2B | ~4GB | ✅ |
| Qwen2-VL | VQA/OCR/Chat | 2B–72B | ~6–20GB | ✅ (2B-7B) |
| Idefics3 | VQA/Chat | 8B | ~12GB | ✅ |
| PaliGemma | VQA | 3B | ~6GB | ✅ |
| Florence-2 | Multi-task | 270MB–770MB | ~2GB | ✅ |

## Method 1: transformers pipeline (Simplest)

### requirements.txt
```
torch>=2.4.0
transformers>=4.48.0
accelerate>=1.3.0
gradio>=5.0.0
Pillow>=11.0.0
```

### Image Classification (ViT)
```python
from transformers import pipeline
import gradio as gr

classifier = pipeline("image-classification", model="google/vit-base-patch16-224", device=0)

def classify(image):
    results = classifier(image)
    return {r["label"]: r["score"] for r in results}

gr.Interface(classify, "image", "label", title="ViT Classifier").launch(share=True)
```

### CLIP Zero-Shot Classification
```python
from transformers import pipeline
import gradio as gr

classifier = pipeline("zero-shot-image-classification", model="openai/clip-vit-large-patch14", device=0)

def classify(image, labels):
    results = classifier(image, candidate_labels=labels.split(","))
    return {r["label"]: r["score"] for r in results}

with gr.Blocks() as demo:
    img = gr.Image(label="Image")
    labels = gr.Textbox(label="Labels (comma-separated)", value="cat,dog,car,person")
    output = gr.Label()
    btn = gr.Button("Classify")
    btn.click(classify, [img, labels], output)

demo.launch(share=True)
```

## Method 2: Vision-Language Models (VQA/Chat)

### LLaVA (Recommended for chat-with-images)
```python
!pip install torch transformers accelerate gradio Pillow -q

import torch
from transformers import AutoProcessor, LlavaForConditionalGeneration
import gradio as gr
from PIL import Image

model_id = "llava-hf/llava-1.5-7b-hf"

model = LlavaForConditionalGeneration.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    device_map="auto",
    low_cpu_mem_usage=True,
)
processor = AutoProcessor.from_pretrained(model_id)

def chat(image, message, history):
    if image is None:
        return history
    
    # Build conversation
    conversation = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": message}]}]
    prompt = processor.apply_chat_template(conversation, add_generation_prompt=True)
    
    inputs = processor(images=image, text=prompt, return_tensors="pt").to("cuda")
    output = model.generate(**inputs, max_new_tokens=256, do_sample=False)
    response = processor.decode(output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    
    history.append((message, response))
    return history, ""

with gr.Blocks(title="LLaVA Chat") as demo:
    gr.Markdown("# 👁️ LLaVA — Chat with Images")
    with gr.Row():
        img = gr.Image(type="pil", label="Upload Image")
    chatbot = gr.Chatbot()
    msg = gr.Textbox(label="Ask about the image")
    btn = gr.Button("Send")
    btn.click(chat, [img, msg, chatbot], [chatbot, msg])

demo.launch(share=True, debug=True)
```

### Qwen2-VL (Best OCR + VQA)
```python
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
import gradio as gr

model = Qwen2VLForConditionalGeneration.from_pretrained(
    "Qwen/Qwen2-VL-2B-Instruct",
    torch_dtype=torch.float16,
    device_map="auto",
)
processor = AutoProcessor.from_pretrained("Qwen/Qwen2-VL-2B-Instruct")

def chat(image, message, history):
    messages = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": message}]}]
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = processor(text=[text], images=[image], return_tensors="pt").to("cuda")
    output = model.generate(**inputs, max_new_tokens=256)
    response = processor.decode(output[0], skip_special_tokens=True)
    # Extract assistant response
    response = response.split("assistant\n")[-1].strip()
    history.append((message, response))
    return history, ""

gr.ChatInterface(...)  # Same pattern as LLaVA
```

### SmolVLM (Lightweight, T4-friendly)
```python
from transformers import AutoProcessor, AutoModelForVision2Seq

model = AutoModelForVision2Seq.from_pretrained(
    "HuggingFaceTB/SmolVLM-Instruct",
    torch_dtype=torch.float16,
    device_map="auto",
)
processor = AutoProcessor.from_pretrained("HuggingFaceTB/SmolVLM-Instruct")
# Same Gradio pattern as LLaVA
```

## Method 3: CLIP Embeddings (for RAG/search)

```python
from transformers import CLIPProcessor, CLIPModel
import torch, gradio as gr

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to("cuda")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def get_embedding(text="", image=None):
    if text:
        inputs = processor(text=[text], return_tensors="pt", padding=True).to("cuda")
        with torch.no_grad():
            emb = model.get_text_features(**inputs)
    else:
        inputs = processor(images=image, return_tensors="pt").to("cuda")
        with torch.no_grad():
            emb = model.get_image_features(**inputs)
    return emb.cpu().numpy().tolist()[0][:10]  # First 10 dims for display

with gr.Blocks() as demo:
    gr.Markdown("# CLIP Embeddings")
    with gr.Tab("Text"):
        txt = gr.Textbox()
        txt_out = gr.JSON()
        gr.Button("Encode").click(get_embedding, [txt, None], txt_out)
    with gr.Tab("Image"):
        img = gr.Image()
        img_out = gr.JSON()
        gr.Button("Encode").click(lambda x: get_embedding("", x), [img], img_out)

demo.launch(share=True)
```

## Florence-2 (Multi-task: caption, OCR, detection)

```python
from transformers import AutoProcessor, AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained(
    "microsoft/Florence-2-large", torch_dtype=torch.float16, device_map="auto"
)
processor = AutoProcessor.from_pretrained("microsoft/Florence-2-large")

def predict(image, task="<CAPTION>"):
    inputs = processor(text=task, images=image, return_tensors="pt").to("cuda")
    output = model.generate(**inputs, max_new_tokens=256)
    return processor.decode(output[0], skip_special_tokens=True)

# Tasks: <CAPTION>, <DETAILED_CAPTION>, <OCR>, <OBJECT_DETECTION>, <REGION_TO_DESCRIPTION>
gr.Interface(predict, ["image", gr.Dropdown(["<CAPTION>", "<OCR>", "<DETAILED_CAPTION>"])], "text").launch(share=True)
```

## Common Issues

| Problem | Fix |
|---------|-----|
| OOM with LLaVA on T4 | Use `low_cpu_mem_usage=True`, reduce `max_new_tokens` |
| Image not loading | Ensure `type="pil"` in gr.Image |
| Slow inference | Use SmolVLM or Qwen2-VL-2B instead of 7B+ |
| Wrong response format | Check model's chat template with `processor.apply_chat_template` |
| CUDA OOM | Add `device_map="auto"` instead of `.to("cuda")` |
