#!/usr/bin/env python3
"""Transcribe audio file using faster-whisper on CUDA."""
import sys
import os
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

from faster_whisper import WhisperModel

MODEL = "large-v3"
DEVICE = "cuda"
COMPUTE = "float16"

def load_model():
    return WhisperModel(MODEL, device=DEVICE, compute_type=COMPUTE)

def transcribe(audio_path, language="no"):
    m = load_model()
    segs, info = m.transcribe(audio_path, language=language, beam_size=5, vad_filter=True)
    text = " ".join(s.text.strip() for s in segs)
    return text.strip(), info.language, info.language_probability

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("audio", help="Path to WAV file")
    ap.add_argument("-l", "--language", default="no", help="Language code (no/nb/en/auto)")
    args = ap.parse_args()

    text, lang, prob = transcribe(args.audio, args.language)
    print(text)
    print(f"# detected: {lang} ({prob:.0%})", file=sys.stderr)
