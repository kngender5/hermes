# Norwegian Whisper Model Notes

## Model Comparison (tested 2026-05-27, RTX 4060)

| Model | Size | Download Time | Norwegian Quality | Notes |
|-------|------|--------------|-------------------|-------|
| `openai/whisper-large-v3` | ~3 GB | 15+ min (HF rate limit) | **Poor** — frequent misrecognition of Norwegian | Generic multilingual, weak on Norwegian |
| `NbAiLab/nb-whisper-small` | ~0.5 GB | ~2 min | OK | Fast but misses nuances |
| `NbAiLab/nb-whisper-medium` | ~1.5 GB | ~5 min | **Excellent** — purpose-trained on Norwegian | **Recommended default** |
| `NbAiLab/nb-whisper-large` | ~3 GB | 30+ min (timed out) | Best (untested) | Too slow to download without HF_TOKEN |

## Language Codes

- `no` / `nb` → Norwegian Bokmål (both work, `no` is more common in Whisper)
- `nn` → Norwegian Nynorsk (also recognized)
- `None` (auto-detect) → works OK but explicit `no` gives better results
- Mixed Norwegian/English speech → set `language="no"` still handles English loanwords OK

## Recommended voice_transcribe.py Settings

```python
MODEL = "NbAiLab/nb-whisper-medium"
DEVICE = "cuda"
COMPUTE = "float16"
# beam_size=5 for quality, vad_filter=True to skip silence
```

## HF Hub Rate Limiting

Without `HF_TOKEN`, large model downloads are throttled and can time out.
- Small/medium models download fine without token
- For large models, set `HF_TOKEN` env var or use `huggingface-cli login`
