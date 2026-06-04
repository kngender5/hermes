# Whisper vs Panopto Caption Quality Analysis

## Test Setup
- Video: WEB 7 mai (143 MB, ~1.5 hour lecture on fiber optics)
- Panopto: Embedded mov_text captions (auto-generated)
- Whisper: large-v3 model, Norwegian language, GPU (RTX 4060, float16)

## Results

### Panopto Embedded Captions
**Accuracy: ~70-80%**

Sample errors from first 5 minutes:
- "God kveld alle sammen! Og jeg skal hvis jeg." (incomplete)
- "De som hørte meg. Greit nok Bea at det er bra jeg er gul..." (word salad)
- "Holder det å tenke en skal vi se. Det var gjennomgang av hver fiber app kom." (garbled)
- "Og som Tone presset ned presiserte sist og svaret han at det denne adaptere verdien." (nonsensical)

**Issues:**
- Word salad: random word combinations that sound similar to speech
- Technical terms garbled: "fiber app kom" instead of proper terms
- 30-second blocks: too coarse for precise timing
- Missing punctuation and sentence structure

### Whisper large-v3 Transcription
**Accuracy: ~90-95%**

Sample output (same time range):
- "Det var å gjennomgå hvilke målinger som er viktige som kontroll"
- "Jeg tenkte det må vi gå og så, men går gjennom flere er jo en del av hele installasjonen"
- "Sertifisere og dokumentere"

**Strengths:**
- Coherent Norwegian sentences
- Correct technical terms (splitter, OTDR, dB, fiber, connector)
- ~2-second segments with precise timing
- Proper punctuation and sentence boundaries
- Handles multiple speakers

**Weaknesses:**
- May occasionally hallucinate on very technical jargon
- Requires GPU for reasonable speed (~30 min per hour of video)
- Needs libcublas12 library installed

## Recommendation
- **For keyword search:** Panopto captions are sufficient
- **For study notes / exam prep:** Always use whisper
- **For consistency:** Run whisper on ALL videos, even those with embedded captions
- **For videos with watermarks:** Check for repeated phrases (>50% same text) and skip whisper

## Performance
- Whisper large-v3 on RTX 4060: ~30 min per hour of video (float16)
- Panopto caption extraction: instantaneous (already embedded)
- Storage: ~100-200 KB SRT per hour of video
