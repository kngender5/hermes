#!/usr/bin/env python3
"""Qwen3-TTS Voice Design - create new voices from natural language descriptions.

Usage:
  python voice_design_test.py
  python voice_design_test.py --instruct "Deep elderly male, slow and thoughtful"
"""
import argparse
import time
import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel


def main():
    parser = argparse.ArgumentParser(description="Qwen3-TTS Voice Design test")
    parser.add_argument("--model", default="Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign")
    parser.add_argument("--language", default="english")
    parser.add_argument("--instruct",
                        default="A warm, confident middle-aged male voice with a slight Nordic accent, speaking at a measured pace with subtle gravitas.",
                        help="Natural language voice description")
    parser.add_argument("--text",
                        default="The northern lights dance across the Arctic sky, painting the darkness with shades of green and violet.")
    parser.add_argument("--output", default="voice_design_output.wav")
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

    print(f"\nVoice design instruction: \"{args.instruct}\"")
    print(f"Text: \"{args.text[:80]}...\"")
    t0 = time.time()
    wavs, sr = model.generate_voice_design(
        text=args.text,
        language=args.language,
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
