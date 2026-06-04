#!/usr/bin/env python3
"""Qwen3-TTS Voice Clone test - clone a voice from reference audio.

Usage:
  # Default: use built-in demo reference audio
  python voice_clone_test.py

  # With your own reference audio:
  python voice_clone_test.py --ref-audio my_voice.wav --ref-text "This is what I sound like."

  # Reusable prompt mode (avoids recomputing ref features):
  python voice_clone_test.py --ref-audio my_voice.wav --ref-text "..." --reuse-prompt
"""
import argparse
import time
import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel


def main():
    parser = argparse.ArgumentParser(description="Qwen3-TTS Voice Clone test")
    parser.add_argument("--model", default="Qwen/Qwen3-TTS-12Hz-1.7B-Base",
                        help="Model ID or local path (default: 1.7B Base for voice clone)")
    parser.add_argument("--ref-audio", default=None,
                        help="Path/URL to reference audio (3s+). Default: Qwen demo clip.")
    parser.add_argument("--ref-text", default=None,
                        help="Transcript of reference audio.")
    parser.add_argument("--text", default="Hei! Jeg er en klonet stemme. Dette er en test av Qwen3-TTS voice cloning pa norsk.",
                        help="Text to synthesize with cloned voice.")
    parser.add_argument("--language", default="auto",
                        help="Language for synthesis. Supported: auto, chinese, english, french, german, italian, japanese, korean, portuguese, russian, spanish. Use 'auto' for other languages.")
    parser.add_argument("--reuse-prompt", action="store_true",
                        help="Build reusable prompt from ref audio (faster for multiple calls)")
    parser.add_argument("--output", default="voice_clone_output.wav",
                        help="Output WAV file path")
    parser.add_argument("--device", default="cuda:0", help="Device (cuda:0, cpu)")
    parser.add_argument("--no-flash-attn", action="store_true",
                        help="Disable flash_attention_2 (use if flash-attn not installed)")
    args = parser.parse_args()

    # Default reference audio from Qwen
    if args.ref_audio is None:
        args.ref_audio = "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen3-TTS-Repo/clone.wav"
        args.ref_text = "Okay. Yeah. I resent you. I love you. I respect you. But you know what? You blew it! And thanks to you."

    attn = "sdpa" if args.no_flash_attn else "flash_attention_2"

    print(f"Loading model: {args.model}")
    print(f"  dtype: bfloat16, attn: {attn}, device: {args.device}")
    t0 = time.time()
    model = Qwen3TTSModel.from_pretrained(
        args.model,
        device_map=args.device,
        dtype=torch.bfloat16,
        attn_implementation=attn,
    )
    print(f"  Model loaded in {time.time()-t0:.1f}s")

    if args.reuse_prompt:
        print("Building reusable voice clone prompt...")
        prompt = model.create_voice_clone_prompt(
            ref_audio=args.ref_audio,
            ref_text=args.ref_text,
        )
        print(f"Generating: \"{args.text[:60]}...\"")
        t0 = time.time()
        wavs, sr = model.generate_voice_clone(
            text=args.text,
            language=args.language,
            voice_clone_prompt=prompt,
        )
    else:
        print(f"Generating: \"{args.text[:60]}...\"")
        print(f"  ref_audio: {args.ref_audio[:80]}")
        t0 = time.time()
        wavs, sr = model.generate_voice_clone(
            text=args.text,
            language=args.language,
            ref_audio=args.ref_audio,
            ref_text=args.ref_text,
        )

    elapsed = time.time() - t0
    sf.write(args.output, wavs[0], sr)
    duration = len(wavs[0]) / sr
    print(f"\nDone in {elapsed:.1f}s")
    print(f"  Output: {args.output}")
    print(f"  Sample rate: {sr} Hz, Duration: {duration:.2f}s")
    print(f"  RTF (realtime factor): {elapsed/duration:.2f}")


if __name__ == "__main__":
    main()
