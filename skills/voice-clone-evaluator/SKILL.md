---
name: voice-clone-evaluator
description: >
  Evaluate voice cloning quality: compares prompt intent vs generated output,
  source voice vs cloned voice using speaker embeddings, and provides actionable
  feedback on how to improve prompts. Three modes: full (3-way), compare (2 files),
  analyze (audio vs text prompt). Use after every voice clone iteration.
triggers:
  - voice clone eval
  - evaluate voice clone
  - clone quality
  - voice clone feedback
  - prompt fidelity
  - voice comparison
  - speaker similarity
  - voice clone score
  - did the clone work
  - how good is this clone
---

# Voice Clone Evaluator

Three-axis evaluation of voice cloning results:

1. **Source ↔ Clone similarity** — speaker embedding cosine similarity (Resemblyzer d-vectors)
2. **Prompt ↔ Output fidelity** — acoustic checkpoints vs prompt expectations
3. **Prompt ↔ Design drift** — did VoiceDesign follow instructions or drift?

Plus: detailed feedback report with specific suggestions.

## Prerequisites

```bash
pip install resemblyzer speechbrain
```

Pre-installed: `librosa`, `numpy`, `scipy`, `soundfile`, `torch`

## Modes

### Full Evaluation

```bash
python3 voice_clone_evaluator.py full \
  --prompt "Male, low baritone, calm measured pace, husky raspy edge" \
  --source-audio original_ref.wav \
  --source-text "Reference transcript" \
  --designed-ref design_clone_output/designed_reference.wav \
  --cloned-output design_clone_output/clone_000.wav
```

Output: speaker similarity score, prompt fidelity score, per-feature deviations, actionable suggestions.

### Two-File Comparison

```bash
python3 voice_clone_evaluator.py compare source.wav clone.wav
```

Cosine similarity, quality classification, per-feature differences with % change.

### Single File vs Prompt

```bash
python3 voice_clone_evaluator.py analyze \
  --prompt "Low male voice, slow and deliberate, husky" \
  --audio test_output.wav
```

Matches, deviations, and improvement suggestions.

## What It Measures

### Speaker Similarity
- Resemblyzer d-vector embeddings on CUDA
- Cosine similarity → 0-100 score
- Classification: excellent (>0.92) / good (>0.85) / moderate (>0.75) / weak (>0.65) / poor

### Prompt Fidelity Checkpoints

| Feature | Prompt keywords | Method |
|---------|----------------|--------|
| Pitch | deep/low/high/bright/dark | F0 via librosa PYIN |
| Rate | slow/fast/calm/energetic | Onset density |
| Energy | quiet/loud/soft/powerful | RMS level |
| Quality | breathy/husky/monotone/expressive | Spectral flatness, pitch CV |
| Age | young/old/seasoned | Heuristics from F0 + variation |

### Score Interpretation

| Score | Meaning |
|-------|---------|
| 85-100 | Excellent — production-ready |
| 70-84  | Good — minor tuning |
| 55-69  | Moderate — iterate |
| 40-54  | Below expectations — rethink |
| 0-39   | Poor — fundamental mismatch |

## Prompt Parsing

Parses these attribute categories from free-text prompts: gender, pitch, rate, energy, quality, age, style.

See `references/prompt-guide.md` for full keyword lists and prompt templates.

## Integration with voice-clone-pipeline

Run evaluator after every `voice_clone_pipeline.py --auto`:

```bash
# 1. Clone
python3 voice_clone_pipeline.py "query" --auto

# 2. Evaluate
python3 voice_clone_evaluator.py full --prompt "..." --source-audio ... --designed-ref ... --cloned-output ...

# 3. Read suggestions → adjust prompt → re-clone
```

## JSON Output & Automation

**IMPORTANT**: `--json` must come BEFORE the subcommand:

```bash
python3 voice_clone_evaluator.py --json full --prompt "..." --source-audio ...
```

Use in quality gates:

```bash
python3 voice_clone_evaluator.py --json full ... | python3 -c "
import json, sys
d = json.load(sys.stdin)
score = d['feedback']['scores']['overall_quality']
if score < 70:
    for s in d['feedback']['suggestions']:
        print(f'  → {s}')
    sys.exit(1)
"
```

## Prompt Learner Integration

After evaluating, feed results to the voice-clone-pipeline's learner:

```bash
# Save JSON output
python3 voice_clone_evaluator.py --json full ... > eval.json

# Record to learner (stores corrections for future prompt generation)
python3 voice_prompt_learner.py record \
  --prompt "..." --source-audio ref.wav --eval-file eval.json
```

The learner accumulates corrections across iterations. Next time `voice_descriptor.py --correct` runs, fixes are applied automatically.

## Pitfalls

1. **Short references (< 5s)** → low similarity scores (not enough voice data to embed)
2. **Background music** → confuses both clone and evaluator — always denoise first
3. **VoiceDesign drift** — design model prioritizes "natural" over "precise." For exact match, use source audio directly
4. **Energy normalization** (loudnorm) can mask loudness deviations
5. **Norwegian prompts** — acoustic detection works on any audio, but prompt parsing is English-only
6. **Path resolution in WSL2** — use absolute paths; CWD may be `/mnt/c/Users/rkarl` instead of `~`
7. **`--json` flag position** — must be placed BEFORE the subcommand (`--json full`, not `full --json`)
8. **Resemblyzer encoder loads on first call** — the first run loads the speaker encoder model (~0.5s). This is a one-time cost per session. Subsequent calls reuse the cached encoder.
9. **stdout/stderr separation** — progress messages go to stderr, JSON output goes to stdout. When capturing JSON, redirect stderr: `python3 evaluator.py --json full ... > output.json 2>/dev/null`

## See Also

- `references/prompt-guide.md` — prompt writing guide, keyword tables, templates, common mistakes
- `creative/voice-clone-pipeline` — the cloning pipeline this evaluates (includes learner)
- `mlops/qwen3-tts` — Qwen3-TTS model and architecture
