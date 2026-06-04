# Learning Data Schema

See ~/data/hermes/voice/learner/ for live examples.

## corrections.json — deviation → fix rules

Key pattern: `{axis}_{direction}_fix` (e.g., `rate_fast_fix`, `pitch_high_fix`)

Each entry: `count` (observations), `examples[]` with `words_to_add`, `words_to_remove`, `fix` text.

## descriptor_map.json — word → acoustic effect

Per descriptor word: `axis` (pitch/rate/energy), `expected_hz`/`expected_delta`, `actual_hz`/`actual_delta` (EMA), `confidence` (observation count), `needs_strengthening` (bool).

## profiles.json — per-voice history

Per voice: `iterations`, `best_score`, `best_prompt`, `deviations[]`, `improvements[]`, `last_eval.scores`.

## history.jsonl — append-only eval log

One JSON line per evaluation: `timestamp`, `voice`, `prompt`, `deviations[]`, `matches[]`, `suggestions[]`, `scores{}`.

## Correction Rule Keys

| Key | Trigger | Default fix |
|-----|---------|-------------|
| `rate_fast_fix` | rate faster than expected | Add: slow, measured, deliberate tempo, pauses between phrases. Remove: fast, quick, rapid, animated, energetic |
| `rate_slow_fix` | rate slower than expected | Add: fast, energetic, animated, quick pace. Remove: slow, deliberate, measured, very slow |
| `pitch_high_fix` | pitch higher than expected | Add: deep, baritone, bass, low pitch. Remove: bright, high, alto, soprano |
| `pitch_low_fix` | pitch lower than expected | Add: bright, alto, higher pitch. Remove: deep, bass, baritone, very low |
| `energy_loud_fix` | louder than expected | Add: quiet, soft, intimate, restrained volume. Remove: loud, powerful, commanding, projected |
| `energy_quiet_fix` | quieter than expected | Add: loud, powerful, strong presence, commanding. Remove: quiet, soft, intimate, gentle |

## Correction Application Modes

1. **Replacement mode**: prompt contains problematic words → remove them, add fix words
2. **Additive mode**: right words present but too weak → append stronger synonyms (e.g., "slow" → add "deliberate tempo, pauses between phrases")

Both modes fire independently. A single correction can trigger both if the prompt has problematic words AND needs strengthening.
