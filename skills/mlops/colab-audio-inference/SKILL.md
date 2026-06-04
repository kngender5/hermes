---
name: colab-audio-inference
description: Serve audio models (Whisper, XTTS, Bark, MusicGen, WhisperX) via Google Colab GPU + Gradio. ASR, TTS, music generation, voice cloning.
---

# Colab Audio Inference — ASR, TTS, Music

Serve audio models on Google Colab GPU with Gradio UI.

## Supported Models

| Model | Task | Params | VRAM (T4) | T4 OK |
|-------|------|--------|-----------|-------|
| Whisper tiny/base | ASR | 39–74MB | ~1GB | ✅ |
| Whisper small/medium | ASR | 244–769MB | ~2GB | ✅ |
| Whisper large-v3 | ASR | 1.55B | ~5GB | ✅ |
| WhisperX large | ASR + diarization | 1.55B | ~6GB | ✅ |
| XTTS v2 | TTS/Voice clone | 750MB | ~4GB | ✅ |
| Bark | TTS | 8B–30B | ~8GB | ✅ (small) |
| MusicGen small | Music gen | 300MB | ~2GB | ✅ |
| MusicGen medium | Music gen | 1.5B | ~5GB | ✅ |
| MusicGen large | Music gen | 3.3B | ~10GB | ✅ |
| CosyVoice | TTS/Clone | 500MB | ~3GB | ✅ |
| GPT-SoVITS | Voice clone | 1B | ~4GB | ✅ |

## requirements.txt
```
torch>=2.4.0
transformers>=4.48.0
accelerate>=1.3.0
gradio>=5.0.0
soundfile>=0.13.0
librosa>=0.11.0
```

## Whisper (ASR — Speech to Text)

### Simple transcription
```python
!pip install transformers accelerate gradio soundfile -q

from transformers import pipeline
import gradio as gr

# Auto-selects GPU, loads model
asr = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-large-v3",
    torch_dtype=torch.float16,
    device=0,
)

def transcribe(audio):
    if audio is None:
        return ""
    result = asr(audio, return_timestamps=True)
    return result["text"]

gr.Interface(
    transcribe,
    gr.Audio(sources=["microphone", "upload"], type="filepath"),
    gr.Textbox(label="Transcription", lines=5),
    title="Whisper ASR",
).launch(share=True, debug=True)
```

### Whisper with language detection + translation
```python
from transformers import pipeline
import torch

asr_en = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-large-v3",
    torch_dtype=torch.float16,
    device=0,
    generate_kwargs={"task": "translate"},  # Translate to English
)

def transcribe_and_translate(audio, task="transcribe"):
    if audio is None:
        return "", ""
    kwargs = {"task": task}
    result = asr_en(audio, return_timestamps=True, generate_kwargs=kwargs)
    return result["text"], result.get("chunks", [])

with gr.Blocks(title="Whisper") as demo:
    gr.Markbed("# 🎙️ Whisper ASR + Translation")
    audio = gr.Audio(sources=["microphone", "upload"], type="filepath")
    task = gr.Radio(["transcribe", "translate"], value="transcribe", label="Task")
    text_out = gr.Textbox(label="Output")
    btn = gr.Button("Transcribe")
    btn.click(transcribe_and_translate, [audio, task], text_out)

demo.launch(share=True)
```

### WhisperX (with speaker diarization)
```python
!pip install whisperx gradio -q
import whisperx, gradio as gr, torch

device = "cuda"
model = whisperx.load_model("large-v3", device, compute_type="float16")

def transcribe(audio):
    if audio is None:
        return ""
    result = whisperx.transcribe(model, audio, device=device)
    return result["text"]

gr.Interface(transcribe, gr.Audio(type="filepath"), "text").launch(share=True)
```

## XTTS v2 (TTS — Text to Speech)

### requirements.txt (additional)
```
TTS>=0.22.0
gradio>=5.0.0
```

### Notebook Cell — Multilingual TTS
```python
!pip install TTS gradio soundfile -q

from TTS.api import TTS
import gradio as gr

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cuda")

def synthesize(text, speaker_wav, language="en"):
    if not text.strip():
        return None
    wav = tts.tts(text=text, speaker_wav=speaker_wav, language=language)
    return 22050, wav  # sample_rate, audio_data

with gr.Blocks(title="XTTS v2") as demo:
    gr.Markdown("# 🗣️ XTTS v2 — Multilingual TTS")
    text = gr.Textbox(label="Text", lines=3)
    speaker = gr.Audio(label="Speaker Reference (6+ sec)", type="filepath")
    lang = gr.Dropdown(["en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh-cn", "ja", "ko", "hi"], value="en", label="Language")
    audio_out = gr.Audio(label="Output")
    gr.Button("Synthesize").click(synthesize, [text, speaker, lang], audio_out)

demo.launch(share=True, debug=True)
```

## Bark (Natural TTS)

```python
!pip install transformers accelerate gradio scipy -q

from transformers import pipeline
import gradio as gr
import numpy as np

pipe = pipeline("text-to-audio", model="suno/bark", device=0)

def synthesize(text):
    if not text.strip():
        return None
    output = pipe(text)
    return (output["sampling_rate"], output["audio"])

gr.Interface(synthesize, "text", gr.Audio(), title="Bark TTS").launch(share=True)
```

## MusicGen (Music Generation)

### requirements.txt
```
audiocraft>=1.3.0
gradio>=5.0.0
torch>=2.4.0
torchaudio>=2.4.0
einops>=0.8.0
```

### Notebook Cell
```python
!pip install audiocraft gradio -q

from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write
import torchaudio, gradio as gr, torch, os, uuid

model = MusicGen.get_pretrained("facebook/musicgen-medium")
model.set_generation_params(duration=10)  # 10 seconds

def generate_music(prompt):
    if not prompt.strip():
        return None
    wav = model.generate([prompt])  # batch of 1
    out_path = f"/tmp/{uuid.uuid4()}.wav"
    audio_write(out_path, wav[0].cpu(), model.sample_rate, strategy="loudness")
    return out_path

gr.Interface(
    generate_music,
    gr.Textbox(label="Music description", placeholder="Upbeat electronic dance track with heavy beats"),
    gr.Audio(label="Generated Music"),
    title="MusicGen",
).launch(share=True, debug=True)
```

## CosyVoice (Chinese/English TTS)

```python
!pip install cosyvoice gradio -q

from cosyvoice.cli.cosyvoice import CosyVoice
import torchaudio, gradio as gr

cosyvoice = CosyVoice('iic/CosyVoice-300M-SFT')

def tts(text, prompt_audio=None):
    if prompt_audio:
        # Zero-shot voice cloning
        output = cosyvoice.inference_voice_clone(text, prompt_audio)
    else:
        output = cosyvoice.inference_sft(text, '中文女')
    return (output['tts_speech'].squeeze().numpy(), 22050)

gr.Interface(tts, [gr.Textbox(), gr.Audio(type="filepath")], gr.Audio()).launch(share=True)
```

## Common Issues

| Problem | Fix |
|---------|-----|
| Whisper OOM with large-v3 | Use `float16`, chunk_length_s=30 |
| XTTS needs speaker reference | Provide 6-10 second clean voice sample |
| Bark slow on T4 | Use `suno/bark-small` instead of `bark` |
| MusicGen OOM | Use `musicgen-small` or `musicgen-medium`, reduce duration |
| Gradio audio not playing | Return tuple `(sample_rate, numpy_array)` |
| XTTS language error | Check supported languages list for model version |
| Slow audio load | Use `type="filepath"` instead of `numpy` in gr.Audio |
