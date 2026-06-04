#!/usr/bin/env python3
"""Qwen3-TTS Custom Voice - use 9 built-in speakers with style control.

Usage:
  python custom_voice_test.py
  python custom_voice_test.py --speaker Ryan --language english --instruct "Very excited"
"""
import argparse
import time
import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel


SPEAKERS = {
    "Vivian": "Bright, slightly edgy young female (Chinese)",
    "Serena": "Warm, gentle young female (Chinese)",
    "Uncle_Fu": "Seasoned male, low mellow timbre (Chinese)",
    "Dylan": "Youthful Beijing male, clear natural (Chinese dialect)",
    "Eric": "Lively Chengdu male, slightly husky (Chinese dialect)",
    "Ryan": "Dynamic male, strong rhythmic drive (English)",
    "Aiden": "Sunny American male, clear midrange (English)",
    "Ono_Anna": "Playful Japanese female, light nimble (Japanese)",
    "Sohee": "Warm Korean female, rich emotion (Korean)",
}


def main():
    parser = argparse.ArgumentParser(description="Qwen3-TTS Custom Voice test")
    parser.add_argument("--model", default="Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice")
    parser.add_argument("--speaker", default="Ryan", choices=list(SPEAKERS.keys()))
    parser.add_argument("--language", default="english")
    parser.add_argument("--instruct", default="", help="Style instruction")
    parser.add_argument("--text", default="Hello! I am a custom voice from Qwen3-TTS. This sounds amazing, doesn't it?")
    parser.add_argument("--output", default="custom_voice_output.wav")
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--no-flash-attn", action="store_true")
    args = parser.parse_args()

    attn = "sdpa" if args.no_flash_attn else "flash_attention_2"

    print(f"Loading model: {args.model}")
    t0 = time.time()
    model = Qwen3TTSModel.from_pretrained(
        args.model,
        device_map=args.device,
        dtype=torch.bfloat16,
        attn_implementation=attn,
    )
    print(f"  Model loaded in {time.time()-t0:.1f}s")

    print(f"\nSupported speakers: {model.get_supported_speakers()}")
    print(f"Supported languages: {model.get_supported_languages()}")

    print(f"\nGenerating with speaker={args.speaker}, language={args.language}")
    if args.instruct:
        print(f"  Style: {args.instruct}")
    t0 = time.time()
    wavs, sr = model.generate_custom_voice(
        text=args.text,
        language=args.language,
        speaker=args.speaker,
        instruct=args.instruct,
    )
    elapsed = time.time() - t0
    sf.write(args.output, wavs[0], sr)
    duration = len(wavs[0]) / sr
    print(f"\nDone in {elapsed:.1f}s")
    print(f"  Output: {args.output}")
    print(f"  Duration: {duration:.2f}s, RTF: {elapsed/duration:.2f}")


if __name__ == "__main__":
    main()
