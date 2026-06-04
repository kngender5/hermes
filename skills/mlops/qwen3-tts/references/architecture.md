# Qwen3-TTS Architecture

## How It Generates Speech

Qwen3-TTS is an **autoregressive discrete token language model** — not a traditional mel-spectrogram→vocoder TTS. It "writes" audio tokens the same way GPT writes text tokens, one at a time.

```
Text input  →  1.7B Language Model  →  audio token codes  →  Tokenizer decoder  →  WAV
               (autoregressive,       (discrete ints,        (lightweight
                like GPT text gen)     ~12 frames/sec)        non-DiT model)
```

## Three Key Components

| Component | What it does | Size |
|---|---|---|
| **1.7B LM** (Base/CustomVoice/VoiceDesign) | Takes text → generates audio codes token-by-token | 4.3GB |
| **Tokenizer-12Hz** (codec) | Encode: audio→codes. Decode: codes→audio. The "vocabulary" of audio. | 651MB |
| **Speech tokenizer** (inside each model) | Sub-module for acoustic tokenization of reference audio | bundled |

## Voice Clone Flow

1. `ref_audio` (3s+ WAV) → **encoded** into discrete audio tokens by the tokenizer
2. Those tokens + `ref_text` → prepended as context (the "voice prompt")
3. The LM generates **new** audio tokens conditioned on that voice, one token at a time
4. Generated tokens → **decoded** back to waveform by the tokenizer

## Voice Design → Clone Flow (recommended)

1. VoiceDesign model: synthesize a short reference clip matching your target persona from NL description
2. Base model: `create_voice_clone_prompt()` from that clip → reusable prompt
3. All subsequent `generate_voice_clone()` calls use the prompt — **consistent voice across all outputs without recomputing features**

## Why It's Slow

Autoregressive token generation: each forward pass through 1.7B model produces one step.
At ~12 frames/sec × multiple codebooks, a 5-second clip needs ~60+ codebook steps.
Each step = full forward pass of 1.7B parameters.

## Why It's Good

No information bottleneck from mel-spectrograms. The model "hears" actual audio tokens,
so voice cloning fidelity is much higher than traditional TTS approaches.

## vs Traditional TTS (edge-tts, Coqui, XTTS)

Traditional: text → mel spectrogram → vocoder (fast pipeline, lower clone fidelity)
Qwen3-TTS: text → autoregressive LM → discrete audio tokens → decoder (slower, higher fidelity)

## Performance Characteristics

- **Model load**: ~19s (first load), ~8s (subsequent with HF cache)
- **Generation RTF**: ~1.7x realtime (warmed up, SDPA, RTX 4060)
- **First inference RTF**: ~9x (includes warmup/compile overhead)
- **VRAM**: ~5.7-6.5GB during inference
- **Output**: 24000 Hz, 16-bit mono WAV
- **Both models cannot fit in VRAM simultaneously** (~13GB needed) — must `del model; torch.cuda.empty_cache()` between switches
