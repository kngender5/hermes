# Voice Prompt Writing Guide

## How Qwen3-TTS Interprets Prompts

The VoiceDesign model converts natural language descriptions into audio.
The Base clone model conditions on reference audio + text.

## Descriptor Categories

### Pitch Descriptors

| Descriptor | Expected F0 | Effect |
|-----------|-------------|--------|
| deep, bass, very low | 60-120 Hz | Very low male |
| low, baritone | 100-170 Hz | Classic low male |
| medium, tenor | 150-230 Hz | Average male / low female |
| high, alto | 200-300 Hz | Higher female |
| very high, soprano | 280-500 Hz | Very high, bright |
| bright | any + higher | Raises perceived pitch |
| dark, mellow, warm | any + lower | Lowers perceived pitch |

**Tips:** "Dark" and "warm" lower pitch AND reduce brightness. "Bright" raises pitch AND increases spectral centroid. Compound: "dark and warm" has stronger effect.

### Rate Descriptors

| Descriptor | Onset Rate | Effect |
|-----------|------------|--------|
| slow, deliberate, measured | 0-3/s | Unhurried, careful |
| calm, thoughtful, controlled | 1-4/s | Relaxed |
| moderate, conversational, natural | 2.5-5/s | Everyday pace |
| quick, energetic, animated | 4-7/s | Brisk, lively |
| very fast, rapid | 6+/s | Urged, rushed |

### Energy Descriptors

| Descriptor | RMS Level | Effect |
|-----------|-----------|--------|
| quiet, intimate, soft | < 0.03 | Close-mic'd, gentle |
| moderate, even | 0.02-0.08 | Normal level |
| loud, powerful, commanding, projected | > 0.06 | Strong presence |

**Note:** The design pipeline applies loudness normalization, so absolute energy differences are partially normalized.

### Quality Descriptors

| Descriptor | Effect |
|-----------|--------|
| husky | Raspy, rough male quality |
| raspy, gravelly, rough | Damaged/rough voice |
| breathy, airy | Lots of air in voice |
| clear, crisp | Clean articulation |
| nasal | Nasal resonance |
| monotone, flat | Unchanging pitch |
| expressive, animated | Varied intonation |
| smooth, rich | Polished, warm |
| thin | Lacking body |
| warm | Low centroid, intimate |
| cold, clinical | Sterile, precise |

**Tips:** "Husky" + "low" = Batman-style. "Breathy" needs good reference audio. Quality descriptors work best combined with pitch/rate.

### Age Descriptors

| Descriptor | Effect |
|-----------|--------|
| young, youthful | Higher pitch std, brighter |
| middle-aged | Standard |
| old, elderly, aged, seasoned | Weathered |
| child | High pitch, high variation |

### Style Descriptors

| Descriptor | Effect |
|-----------|--------|
| formal, professional | Measured, clear, authoritative |
| casual, conversational, relaxed | Natural, flowing |
| dramatic, theatrical | Expressive, projected |
| serious, authoritative | Firm, low variation |
| playful, cheerful | Animated, varied |

## Prompt Structure

```
[Gender], [age] [pitch] voice, [rate] pace, [quality], [energy]
```

### Templates

**Deep male narrator:** `"Male, low baritone, slow measured pace, dark warm mellow, husky raspy edge"`

**Batman:** `"Male, very low deep bass voice, dark warm mellow, slightly husky raspy edge, calm measured pace, slow deliberate"`

**News anchor:** `"Male middle-aged, medium tenor, controlled measured pace, clear crisp professional"`

**Elderly storyteller:** `"Male old aged, low bass, slow thoughtful pace, warm rich seasoned, gravelly weathered"`

**ASMR whisper:** `"Female, high alto, very slow deliberate, breathy airy soft, intimate quiet"`

## Common Mistakes

| Mistake | Example | Fix |
|---------|---------|-----|
| Too vague | "Nice male voice" | "Male, medium tenor, warm, conversational" |
| Contradictory | "High deep voice" | Pick one pitch axis |
| Over-specific | "Exactly 150Hz pitch, 4.2 onsets/s" | Use tendencies, not numbers |
| Ignoring interactions | "High + monotone + whisper" | These may conflict; test |

## Iterating on Prompts

1. Start with basics: gender, pitch, rate
2. Add quality: breathy/husky/clear
3. Add energy if needed
4. Add age/style for polish
5. Evaluate with voice-clone-evaluator
6. Read suggestions, adjust one dimension at a time
7. Re-evaluate and compare scores

## Evaluator Feedback → Prompt Fixes

| Evaluator Says | Fix |
|----------------|-----|
| "Pitch higher than expected" | Add "low", "deep", "bass", "dark" |
| "Pitch lower than expected" | Add "bright", "alto", "high" |
| "Faster than expected" | Add "slow", "deliberate", "measured", "calm" |
| "Slower than expected" | Add "fast", "energetic", "animated" |
| "Louder than expected" | Add "quiet", "intimate", "soft" |
| "Quieter than expected" | Add "loud", "powerful", "commanding" |
| "Breathy expected but not detected" | Add "airy", "soft-spoken", "whisper-like" |
| "Monotone but expressiveness expected" | Add "expressive", "animated", "dynamic" |
| "Clone similarity low" | Longer ref (10-30s), cleaner audio, no music |
