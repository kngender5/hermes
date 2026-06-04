---
name: colab-multimodal-pipelines
description: Multimodal pipelines on Colab — text+image+audio+video combined processing. Chaining vision LLMs, TTS, ASR, image gen in unified workflows.
---

# Colab Multimodal Pipelines — Text + Image + Audio + Video

Combine multiple modalities in unified Colab pipelines.

## Pipeline Architecture Patterns

### Pattern 1: Sequential Chain
```
Input → Vision Model → LLM → TTS → Audio Output
(Input image → LLaVA describes it → Llama writes story → XTTS reads it aloud)
```

### Pattern 2: Parallel Processing
```
Input Image ─┬→ Vision Encoder → Visual Embeds
             ├→ OCR Model → Extracted Text
             └→ Object Detection → Bounding Boxes
              ↓
         LLM (multi-input) → Unified Response
```

### Pattern 3: Interactive Agent
```
User → (Voice input → Whisper) → Agent (LLM + tools) → (TTS → Voice output)
                                    ↓
                              Image gen, web search, code execution
```

## Pipeline 1: Image → Description → Audio Story

```python
!pip install torch transformers diffusers TTS gradio -q

import torch
from transformers import pipeline, AutoProcessor, LlavaForConditionalGeneration
from diffusers import StableDiffusionXLPipeline
from TTS.api import TTS
import gradio as gr

# Load models (one-time startup)
print("Loading models...")
llava = LlavaForConditionalGeneration.from_pretrained(
    "llava-hf/llava-1.5-7b-hf", torch_dtype=torch.float16, device_map="auto"
)
llava_processor = AutoProcessor.from_pretrained("llava-hf/llava-1.5-7b-hf")

llm = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
               device_map="auto", torch_dtype=torch.float16)

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cuda")
print("All models loaded!")

def image_to_audio_story(image, genre="fantasy"):
    # Step 1: Describe image
    prompt = f"Describe this image in detail for a {genre} story:"
    conversation = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": prompt}]}]
    llava_prompt = llava_processor.apply_chat_template(conversation, add_generation_prompt=True)
    inputs = llava_processor(images=image, text=llava_prompt, return_tensors="pt").to("cuda")
    desc_output = llava.generate(**inputs, max_new_tokens=200)
    description = llava_processor.decode(desc_output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    
    # Step 2: Generate story
    story_prompt = f"Write a short {genre} story inspired by this scene: {description}"
    story = llm(story_prompt, max_new_tokens=512, do_sample=True)[0]["generated_text"]
    
    # Step 3: Read story aloud
    wav_path = "/tmp/story.wav"
    tts.tts_to_file(text=story[:500], file_path=wav_path)
    
    return description, story, wav_path

with gr.Blocks(title="Image → Story → Audio") as demo:
    gr.Markdown("# 🎨 Image → 📖 Story → 🔊 Audio")
    img_input = gr.Image(type="pil")
    genre = gr.Dropdown(["fantasy", "sci-fi", "noir", "romance", "horror"], value="fantasy")
    describe_btn = gr.Button("Create Story")
    description = gr.Textbox(label="Image Description")
    story = gr.Textbox(label="Generated Story", lines=10)
    audio = gr.Audio(label="Audio Narration")
    describe_btn.click(image_to_audio_story, [img_input, genre], [description, story, audio])

demo.launch(share=True)
```

## Pipeline 2: Voice → Transcribe → Reason → Respond (Voice)

```python
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
from TTS.api import TTS
import gradio as gr

asr = pipeline("automatic-speech-recognition", model="openai/whisper-medium", device=0)
llm_model = AutoModelForCausalLM.from_pretrained(
    "microsoft/Phi-3-mini-4k-instruct", torch_dtype=torch.float16, device_map="auto"
)
llm_tokenizer = AutoTokenizer.from_pretrained("microsoft/Phi-3-mini-4k-instruct")
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cuda")

def voice_assistant(audio_input):
    # STT
    transcript = asr(audio_input)["text"]
    
    # LLM
    messages = [{"role": "user", "content": transcript}]
    inputs = llm_tokenizer.apply_chat_template(messages, return_tensors="pt", add_generation_prompt=True).to("cuda")
    outputs = llm_model.generate(**inputs, max_new_tokens=256)
    response = llm_tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
    
    # TTS
    wav_path = "/tmp/response.wav"
    tts.tts_to_file(text=response[:300], file_path=wav_path)
    
    return transcript, response, wav_path

with gr.Blocks(title="Voice Assistant") as demo:
    gr.Markbed("# 🎙️ Voice Assistant")
    audio_in = gr.Audio(sources=["microphone"], type="filepath")
    gr.Button("Process").click(voice_assistant, [audio_in],
        [gr.Textbox(label="Transcript"), gr.Textbox(label="Response"), gr.Audio(label="Voice Response")])

demo.launch(share=True)
```

## Pipeline 3: Text → Image → Image Caption → Refine

```python
from diffusers import StableDiffusionXLPipeline
from transformers import AutoProcessor, LlavaForConditionalGeneration
import torch, gradio as gr

# Load models
sdxl = StableDiffusionXLPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16
).to("cuda")
sdxl.enable_model_cpu_offload()

llava = LlavaForConditionalGeneration.from_pretrained(
    "llava-hf/llava-1.5-7b-hf", torch_dtype=torch.float16, device_map="auto"
)
processor = AutoProcessor.from_pretrained("llava-hf/llava-1.5-7b-hf")

def generate_and_refine(prompt, n_iterations=2):
    images = []
    current_prompt = prompt
    
    for i in range(n_iterations):
        # Generate image
        image = sdxl(current_prompt, num_inference_steps=25).images[0]
        images.append(image)
        
        # Critique the image
        conversation = [{"role": "user", "content": [
            {"type": "image"},
            {"type": "text", "text": f"Critique this image. What could be improved to better match: '{prompt}'?"}
        ]}
        inputs = processor.apply_chat_template(conversation, add_generation_prompt=True)
        inputs = processor(images=image, text=inputs, return_tensors="pt").to("cuda")
        critique = llava.generate(**inputs, max_new_tokens=200)
        critique_text = processor.decode(critique[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        
        # Refine prompt
        current_prompt = f"{prompt}. Additional details: {critique_text}"
    
    return images, critique_text

with gr.Blocks() as demo:
    prompt = gr.Textbox(label="Prompt")
    btn = gr.Button("Generate & Refine")
    gallery = gr.Gallery(label="Iteration Results")
    critique = gr.Textbox(label="Final Critique")
    btn.click(generate_and_refine, [prompt], [gallery, critique])

demo.launch(share=True)
```

## Pipeline 4: Video → Frames → Analyze → Summarize

```python
from transformers import VideoMAEImageProcessor, VideoMAEForVideoClassification
import cv2, torch, gradio as gr
from PIL import Image
import numpy as np

def extract_frames(video_path, n_frames=8):
    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    indices = np.linspace(0, total-1, n_frames, dtype=int)
    frames = []
    for i in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if ret:
            frames.append(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
    cap.release()
    return frames

def analyze_video(video_path):
    frames = extract_frames(video_path)
    
    # Frame-level analysis with vision-LLM
    descriptions = []
    for frame in frames:
        # Use CLIP or LLaVA for frame description
        desc = analyze_frame(frame)  # Placeholder
        descriptions.append(desc)
    
    # Summarize
    summary = llm(f"Summarize what happens in this video based on frame descriptions:\n{descriptions}",
                  max_new_tokens=200)[0]["generated_text"]
    
    return frames, summary

with gr.Blocks() as demo:
    video = gr.Video()
    frames = gr.Gallery()
    summary = gr.Textbox()
    gr.Button("Analyze").click(analyze_video, [video], [frames, summary])

demo.launch(share=True)
```

## Pipeline 5: Document → OCR → Extract → Structured Output

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from paddleocr import PaddleOCR
import json, gradio as gr

ocr = PaddleOCR(use_angle_cls=True, lang="en", ocr_version="PP-OCRv4")
llm = pipeline("text-generation", model="microsoft/Phi-3-mini-4k-instruct", device_map="auto")

def process_document(image):
    # OCR
    result = ocr.ocr(np.array(image))
    text = "\n".join([line[1][0] for line in result[0]])
    
    # Extract structured data
    prompt = f"""Extract structured JSON from this document text:

{text}

Output JSON with relevant fields:"""
    
    output = llm(prompt, max_new_tokens=500)[0]["generated_text"]
    
    try:
        structured = json.loads(output)
        return text, json.dumps(structured, indent=2)
    except:
        return text, output

gr.Interface(process_document, "image", ["text", "json"], title="Document Processor").launch(share=True)
```

## Memory Management for Multi-Model Pipelines

```python
# When running multiple large models, be VRAM-conscious:
# 1. Load models one at a time
# 2. Use CPU offloading
# 3. Clear cache between steps

def clear_gpu():
    import gc
    gc.collect()
    torch.cuda.empty_cache()

# Between pipeline steps:
result = model1(input)
clear_gpu()
result = model2(result)
clear_gpu()

# Or use sequential loading:
class Pipeline:
    def __init__(self):
        self.models = {}
    
    def load(self, name, model_id):
        self.models[name] = AutoModelForCausalLM.from_pretrained(
            model_id, torch_dtype=torch.float16, device_map="auto"
        )
    
    def unload(self, name):
        del self.models[name]
        clear_gpu()
```

## Common Issues

| Problem | Fix |
|---------|-----|
| OOM with multiple models | Load sequentially, clear cache between steps |
| Slow pipeline | Use smaller models per step, batch what you can |
| Model quality drop | Ensure each step uses appropriate model size |
| TTS garbled output | Truncate text to <500 chars per call |
| Video OOM | Reduce frame count, resize frames |
| Gradio timeout for long pipelines | Add `concurrency_limit=2`, use background tasks |
