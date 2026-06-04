#!/usr/bin/env python3
"""Qwen3-TTS Voice Design → Clone pipeline.

Step 1: Use VoiceDesign model to synthesize a reference clip matching your target persona.
Step 2: Build a reusable clone prompt from that clip using the Base model.
Step 3: Generate all subsequent speech with generate_voice_clone (consistent voice).

Usage:
  python design_then_clone.py
  python design_then_clone.py --design-instruct "Warm elderly female, gentle and wise" --texts "Hello." "Goodbye."
"""
import argparse
import os
import time
import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel


def main():
    parser = argparse.ArgumentParser(description="Qwen3-TTS Voice Design → Clone pipeline")
    parser.add_argument("--design-model", default="Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign")
    parser.add_argument("--clone-model", default="Qwen/Qwen3-TTS-12Hz-1.7B-Base")
    parser.add_argument(
        "--design-instruct",
        default="A warm, confident male voice in his mid-30s with a calm Nordic quality, speaking clearly at a measured pace with subtle warmth and authority.",
        help="Natural language voice description for VoiceDesign",
    )
    parser.add_argument(
        "--ref-text",
        default="Hey there! I just wanted to say hello and let you know I'm here if you need anything.",
        help="Text for the design reference clip (becomes ref_text for cloning)",
    )
    parser.add_argument(
        "--texts",
        nargs="+",
        default=[
            "The northern lights dance across the Arctic sky, painting the darkness with vivid colors.",
            "Automation engineering combines software, electronics, and mechanical systems into something greater than the sum of its parts.",
            "It's minus fifteen degrees outside, but the coffee is hot and the code is compiling.",
        ],
        help="Texts to synthesize with the designed+cloned voice",
    )
    parser.add_argument("--language", default="English")
    parser.add_argument("--output-dir", default="design_clone_output")
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--max-new-tokens", type=int, default=2048, help="Max new tokens per generation")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    # ── Step 1: Voice Design ──
    print("═══ Step 1: Voice Design ═══", flush=True)
    print(f"Loading VoiceDesign model: {args.design_model}", flush=True)
    t0 = time.time()
    design_model = Qwen3TTSModel.from_pretrained(
        args.design_model,
        device_map=args.device,
        dtype=torch.bfloat16,
        attn_implementation="sdpa",
    )
    print(f"  Loaded in {time.time()-t0:.1f}s", flush=True)

    print(f"  Design instruction: \"{args.design_instruct[:80]}...\"", flush=True)
    print(f"  Reference text: \"{args.ref_text[:60]}...\"", flush=True)
    t0 = time.time()
    ref_wavs, sr = design_model.generate_voice_design(
        text=args.ref_text,
        language=args.language,
        instruct=args.design_instruct,
        max_new_tokens=args.max_new_tokens,
    )
    design_time = time.time() - t0
    ref_path = os.path.join(args.output_dir, "designed_reference.wav")
    sf.write(ref_path, ref_wavs[0], sr)
    ref_duration = len(ref_wavs[0]) / sr
    print(f"  Reference clip: {ref_path} ({ref_duration:.2f}s, generated in {design_time:.1f}s)", flush=True)

    # Free design model to make room for clone model
    del design_model
    torch.cuda.empty_cache()
    print("  Design model freed, VRAM cleared", flush=True)

    # ── Step 2: Build Clone Prompt ──
    print("\n═══ Step 2: Build Clone Prompt ═══", flush=True)
    print(f"Loading Base model: {args.clone_model}", flush=True)
    t0 = time.time()
    clone_model = Qwen3TTSModel.from_pretrained(
        args.clone_model,
        device_map=args.device,
        dtype=torch.bfloat16,
        attn_implementation="sdpa",
    )
    print(f"  Loaded in {time.time()-t0:.1f}s", flush=True)

    print("  Building reusable clone prompt from designed reference...", flush=True)
    prompt = clone_model.create_voice_clone_prompt(
        ref_audio=(ref_wavs[0], sr),
        ref_text=args.ref_text,
    )
    print("  Prompt built successfully", flush=True)

    # ── Step 3: Generate with Cloned Voice ──
    print("\n═══ Step 3: Generate with Cloned Voice ═══", flush=True)
    total_gen_time = 0
    for i, text in enumerate(args.texts):
        print(f"  [{i+1}/{len(args.texts)}] \"{text[:60]}...\"", flush=True)
        t0 = time.time()
        wavs, _ = clone_model.generate_voice_clone(
            text=text,
            language=args.language,
            voice_clone_prompt=prompt,
            max_new_tokens=args.max_new_tokens,
        )
        gen_time = time.time() - t0
        total_gen_time += gen_time
        out_path = os.path.join(args.output_dir, f"clone_{i:03d}.wav")
        sf.write(out_path, wavs[0], sr)
        duration = len(wavs[0]) / sr
        print(f"    → {out_path} ({duration:.2f}s, {gen_time:.1f}s, RTF: {gen_time/duration:.2f})", flush=True)

    print(f"\n═══ Summary ═══")
    print(f"  Design reference: {ref_path}")
    print(f"  Generated {len(args.texts)} clips in {args.output_dir}/")
    print(f"  Total generation time: {total_gen_time:.1f}s")
    print(f"  Language: {args.language}, SR: {sr} Hz")


if __name__ == "__main__":
    main()
