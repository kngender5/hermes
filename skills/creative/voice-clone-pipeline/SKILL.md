---
name: voice-clone-pipeline
description: >
  End-to-end voice cloning pipeline with self-improving prompts: search/download reference
  audio from the web, analyze quality (SNR, music, noise), preprocess to remove noise without
  altering voice characteristics, generate voice descriptions, clone with Qwen3-TTS, evaluate
  the result, and learn from deviations to improve future prompts.
  Use when: voice cloning, voice reference, audio cleanup for TTS, voice design.
triggers:
  - voice clone
  - voice cloning
  - voice reference
  - clone voice from audio
  - audio cleanup for voice
  - voice design from audio
  - find voice sample
  - download voice reference
  - clean voice audio
  - denoise voice
  - voice descriptor
  - describe voice
---

# Voice Clone Pipeline

End-to-end pipeline: find reference audio on the web → analyze quality → clean noise → describe voice → clone with Qwen3-TTS.

## Prerequisites

- **mlops/qwen3-tts** skill — models loaded at `~/projects/qwen3-tts/`
- **creative/qwen-tts-voice** skill — for TTS daemon integration
- Python packages: `numpy`, `librosa`, `soundfile`, `scipy` (all pre-installed)
- System tools: `ffmpeg`, `ffprobe`, `yt-dlp` (all pre-installed)

## Quick Start

```bash
cd ~/.hermes/skills/voice-clone-pipeline/scripts

# Full automatic pipeline from search query
python3 voice_clone_pipeline.py "Morgan Freeman deep voice" --auto

# Clone from existing audio file
python3 voice_clone_pipeline.py --ref-audio ./my_reference.wav --ref-text "Hello world" --auto
```

## Pipeline Stages

### Stage 1 — Search & Download (`voice_source_finder.py`)

Searches multiple sources for clean voice audio:

| Source | Description | Notes |
|--------|-------------|-------|
| `web` | SearXNG local search → DuckDuckGo fallback | Finds direct audio file URLs |
| `youtube` | YouTube search via yt-dlp | Best for interviews, speeches, podcasts |
| `librivox` | Public domain audiobooks | Very clean, professional narration |
| `freesound` | FreeSound.org | Requires `FREESOUND_TOKEN` env var |

### Stage 2 — Quality Analysis (`voice_quality_analyzer.py`)

Scores each file 0-100: SNR, music detection, clipping, voice activity ratio, duration, sample rate.

Files scoring ≥ 70 are recommended for cloning.

### Stage 3 — Preprocessing (`voice_preprocess.py`)

Three levels designed to preserve voice character:

| Level | Use when | Filters |
|-------|----------|---------|
| `light` | SNR > 25dB | HPF 60Hz, LPF 12kHz, gentle afftdn, loudnorm |
| `medium` | SNR 15-25dB | HPF 80Hz, LPF 11kHz, medium afftdn, compression, loudnorm |
| `aggressive` | SNR < 15dB | HPF 100Hz, LPF 10kHz, aggressive afftdn + anlmdn, strong compression |

Output standardized to 24kHz mono 16-bit WAV.

### Stage 4 — Voice Description (`voice_descriptor.py`)

Analyzes acoustic features and generates natural language descriptions for Qwen3-TTS
VoiceDesign model: pitch (F0 via librosa PYIN), speaking rate (onset density), energy profile,
spectral quality (centroid, bandwidth, rolloff), formants (LPC).

Outputs both human-readable description and VoiceDesign-optimized prompt.

### Stage 5 — Voice Cloning (Qwen3-TTS Integration)

Uses `design_then_clone.py` pipeline from the `qwen3-tts` skill:
VoiceDesign → reference clip → Base model → voice clone → generate speech.

## Reference Audio Best Practices

- **Duration**: 8-30 seconds of continuous speech single speaker, no music
- **Quality**: > 20dB SNR, no clipping, ≥ 22050 Hz
- **Good sources**: YouTube interviews, LibriVox audiobooks, Archive.org recordings
- **Avoid**: songs, multi-speaker overlap, heavy reverb, compressed low-bitrate files
- **Norwegian voices**: use `language="auto"` (not natively supported)

## The Learning Loop

Every clone iteration teaches the system how to write better prompts:

```
voice_descriptor.py → prompt → design_then_clone.py → TTS output
                                                        ↓
                              voice_clone_evaluator.py → deviations + suggestions
                                                        ↓
                              voice_prompt_learner.py → stores corrections
                                                        ↓
                    Next run: descriptor applies learned fixes automatically (--correct)
```

### Auto-learn mode

```bash
# Clone + evaluate + learn in one command:
python3 voice_clone_pipeline.py --ref-audio ref.wav --ref-text "transcript" --auto-learn

# Or step by step:
python3 voice_clone_pipeline.py --ref-audio ref.wav --ref-text "transcript"
python3 voice_prompt_learner.py record --prompt "..." --source-audio ref.wav --eval-file eval.json
python3 voice_prompt_learner.py correct --prompt "..." --voice-name my_voice
```

### What gets learned

- **Descriptor word → acoustic effect**: e.g., "slow consistently under-delivers — pair with stronger synonym"
- **Systematic deviations**: e.g., "rate lands 2 onsets/s higher than expected — add 'measured deliberate tempo'"
- **Correction rules**: stored per-voice, auto-applied on next `--correct` run
- **Per-descriptor confidence**: accumulates with each iteration

### Manual learning commands

```bash
# Record feedback from an eval run
python3 voice_prompt_learner.py record \
  --prompt "Male, low baritone, calm measured pace" \
  --source-audio ref.wav \
  --eval-file eval_report.json

# Apply learned corrections to a prompt
python3 voice_prompt_learner.py correct \
  --prompt "Male, low baritone, calm measured pace" \
  --voice-name batman_voice

# Reflect on accumulated learning
python3 voice_prompt_learner.py reflect

# Show all learned profiles and corrections
python3 voice_prompt_learner.py status
```

### Descriptor corrections (automatic)

The descriptor now runs with `--correct` by default, which means:
- If the learner has recorded deviations for your voice, corrections are applied automatically
- e.g., if "slow/measured" was present but output was too fast → adds "deliberate tempo, pauses between phrases"
- Corrections persist in `~/data/hermes/voice/learner/` and accumulate across sessions

## Learning Data Storage

```
~/data/hermes/voice/learner/
  corrections.json     — deviation → fix rules (words_to_add, words_to_remove)
  descriptor_map.json  — per-word learned acoustic effects (confidence, actual Hz/delta)
  profiles.json        — per-voice iteration history, best scores
  history.jsonl        — full evaluation history (append-only)
```

## Pitfalls

1. **YouTube uploads always have background music** — most content creators add music to Batman/character clips, movie compilations, etc. The 10-second previews sometimes score higher than full downloads because the preview catches a clean segment. Use the quality analyzer to find the best segment.
2. **yt-dlp default download clips to ~10-15s** — the finder script's `--duration` parameter controls this. For full-length downloads, omit `--duration` or use a large value. Full downloads often have more music mixed in.
3. **Garbage in, garbage out** — even perfect processing can't fix a poor reference
4. **Qwen3-TTS resamples internally** — any sample rate input works, but 24kHz mono is optimal
5. **Design→Clone pipeline takes 15-45s** — use the daemon pattern for repeated use
6. **FreeSound API key** — set `FREESOUND_TOKEN` environment variable to enable FreeSound search
7. **Path resolution in WSL2** — scripts create files relative to CWD. When CWD is `/mnt/c/Users/rkarl` (Windows mount), files end up there instead of WSL home. Use absolute paths or `cd ~` before running scripts.
8. **VoiceDesign prompt quality** depends on reference audio quality — clean refs → better prompts
9. **Always evaluate after cloning** — run `voice-clone-evaluator` after every clone iteration. It catches prompt drift, rate/pitch mismatches, and gives specific keyword suggestions.
10. **Learning convergence** — the learner needs 2-3 iterations per voice to build meaningful corrections. First eval records the deviation; second eval confirms whether the fix worked; third+ refines. Run with `--auto-learn` each time to accumulate data.
11. **Correction logic: additive vs replacement** — the learner applies corrections in two modes: (a) *replacement* — if the prompt contains problematic words (e.g., "fast" when rate was too fast), they are removed and replaced; (b) *additive* — if the right words are present but too weak (e.g., "slow" present but rate still too fast), stronger synonyms are appended (e.g., "deliberate tempo, pauses between phrases"). The additive mode fires even when no problematic words are found.
12. **Learner data accumulates across sessions** — `~/data/hermes/voice/learner/` persists between sessions. Don't delete this directory unless you want to reset all learned corrections. Each voice profile tracks its own iteration history independently.
13. **`voice_descriptor.py --correct` is automatic in pipeline** — the pipeline always passes `--correct` to the descriptor. To run the descriptor manually without corrections, omit `--correct`. To see what corrections were applied, the descriptor prints `[Learned corrections applied]` to stderr when changes are made.

## See Also

- `voice-clone-evaluator` — quality evaluation and prompt feedback (run after every clone)
- `mlops/qwen3-tts` — Qwen3-TTS model setup and daemon
- `creative/qwen-tts-voice` — dynamic voice TTS with mood selection
