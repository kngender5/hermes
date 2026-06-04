#!/usr/bin/env python3
"""Continuous STT from microphone using faster-whisper.
Usage: stt-stream [lang]
  lang: no, nb, en, auto (default: no)
Ctrl+C to stop.
"""
import sys, os, queue, threading
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

MODEL = "NbAiLab/nb-whisper-large"   # or nb-whisper-medium for lower latency
DEVICE = "cuda"
COMPUTE = "float16"
SAMPLE_RATE = 16000
CHUNK_SEC = 4                          # seconds per inference batch
LANG = sys.argv[1] if len(sys.argv) > 1 else "no"

print(f"Loading {MODEL} on {DEVICE}...", file=sys.stderr)
model = WhisperModel(MODEL, device=DEVICE, compute_type=COMPUTE)
print(f"Ready -- speaking (lang={LANG}, chunk={CHUNK_SEC}s, Ctrl+C to quit)", file=sys.stderr)

audio_q = queue.Queue()

def callback(indata, frames, time_info, status):
    if status:
        print(f"Audio status: {status}", file=sys.stderr)
    audio_q.put(indata.copy())

try:
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='int16', callback=callback):
        buf = []
        while True:
            for _ in range(int(SAMPLE_RATE / 1024 * CHUNK_SEC)):
                buf.append(audio_q.get())
            pcm = np.concatenate(buf).flatten().astype(np.float32) / 32768.0
            buf.clear()

            kwargs = dict(beam_size=5, vad_filter=True)
            if LANG and LANG != "auto":
                kwargs["language"] = LANG
            segs, info = model.transcribe(pcm, **kwargs)
            text = " ".join(s.text.strip() for s in segs).strip()
            if text:
                print(f"🎤 {text}")
                sys.stdout.flush()
except KeyboardInterrupt:
    print("\n=== Stopped ===")
