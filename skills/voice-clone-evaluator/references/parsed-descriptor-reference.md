# Evaluator Prompt Parsing — Keyword Reference

## How the Evaluator Parses Free-Text Prompts

The evaluator's `PromptAnalyzer` scans prompts for known acoustic descriptor words, then compares expected vs actual acoustic measurements.

## Pitch Descriptors

| Word/Phrase | Expected F0 Range |Direction |
|-------------|------------------|-----------|
| very low, deep, bass | 60-120 Hz | Lower |
| low, baritone | 100-170 Hz | Lower |
| medium, tenor | 150-230 Hz | Neutral |
| high, alto | 200-300 Hz | Higher |
| very high, soprano | 280-500 Hz | Higher |
| bright | +20 Hz shift | Higher |
| dark, mellow, warm | -15 to -30 Hz shift | Lower |

## Rate Descriptors

| Word/Phrase | Expected Onset Rate | Direction |
|-------------|-------------------|-----------|
| slow, deliberate, measured, thoughtful, calm | 0-3 /s | Slower |
| conversational, natural, moderate | 2.5-5 /s | Neutral |
| fast, quick, energetic, rapid, animated, lively | 4-20 /s | Faster |

## Energy Descriptors

| Word/Phrase | Expected RMS | Direction |
|-------------|-------------|-----------|
| quiet, intimate, soft, gentle | < 0.03 | Lower |
| moderate, even | 0.02-0.08 | Neutral |
| loud, powerful, commanding, projected, strong | > 0.06 | Higher |

## Quality Descriptors

| Word/Phrase | Acoustic Cue | Detection Method |
|-------------|-------------|-----------------|
| husky, raspy, gravelly | Low centroid, high bandwidth | Spectral flatness |
| breathy, airy | High flatness, high bandwidth | Spectral flatness + bandwidth |
| monotone, flat | Low pitch CV (< 0.08) | F0 variation |
| expressive, animated | High pitch CV (> 0.15) | F0 variation |
| clear, crisp | Low bandwidth, focused | Spectral centroid |
| nasal | Formant shifts | LPC analysis |

## Age Descriptors

| Word | Cues |
|------|------|
| young, youthful | Higher pitch variation, brighter |
| old, elderly, aged, seasoned | Pitch instability, slower |
| middle-aged, adult | Standard (default) |

## Style Descriptors

| Word | Effect |
|------|--------|
| formal, professional | Measured, clear, authoritative |
| casual, conversational | Natural, flowing |
| dramatic, theatrical | Expressive, projected |
| serious, authoritative | Firm, low variation |
| playful, cheerful | Animated, varied |

## Parsing Notes

- Bigrams are checked: "very low" matches before "very" and "low" separately
- First match wins per category (only one pitch, one rate, one energy interpretation)
- Quality descriptors are additive (multiple can match)
- Style descriptors are additive
- Unrecognized words are silently ignored

## Example Prompt Analysis

Prompt: "male very low deep bass calm measured pace dark warm mellow slightly husky raspy edge"

Parsed:
- gender: male
- pitch: very low (from "very low" bigram, expected 60-120Hz)
- rate: slow (from "calm measured pace", expected 0-3 onsets/s)
- quality: ["husky", "raspy"] (from quality terms)
- energy: (none specified)

If actual F0 is 138Hz → deviation: "pitch: expected very low (60-120Hz), got 138Hz — higher than expected"
If actual onset rate is 5.3/s → deviation: "rate: expected slow (0-3 onsets/s), got 5.3/s — faster than expected"
