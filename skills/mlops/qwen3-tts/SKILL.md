---
name: qwen3-tts
description: "Qwen3-TTS: voice clone, voice design, custom voice TTS with 1.7B autoregressive token LM"
version: 2.0
triggers:
  - qwen3-tts
  - voice clone
  - tts
  - text to speech
  - voice design
  - voice cloning
---

# Qwen3-TTS: Autoregressive Token-LM TTS

Qwen3-TTS generates speech via an **autoregressive language model over discrete audio tokens** — not a traditional mel-spectrogram→vocoder pipeline. A 1.7B LM generates audio codes token-by-token, then a lightweight decoder converts them to waveform. See `references/architecture.md` for details.

## Location
- **Project:** `~/projects/qwen3-tts/`
- **Venv:** `.venv/` (Python 3.12, uv-managed — NOT system Python 3.14)
- **Models:** `models/` (~17.5GB total)
- **Activate:** `cd ~/projects/qwen3-tts && source .venv/bin/activate`

## Models

| Model | Purpose | Size | VRAM |
|---|---|---|---|
| Qwen3-TTS-Tokenizer-12Hz | Audio codec (encode/decode) — always loaded with models | 651MB | — |
| **1.7B-Base** | Voice clone from 3s+ ref audio | 4.3GB | ~5.7GB |
| **1.7B-CustomVoice** | 9 built-in speakers + instruction style control | 4.3GB | ~5.7GB |
| **1.7B-VoiceDesign** | Design new voices from NL descriptions | 4.3GB | ~5.7GB |

> ⚠️ Two models **cannot fit in VRAM simultaneously** (~13GB needed). Must `del model; torch.cuda.empty_cache()` before switching. The `design_then_clone.py` script handles this.

## Setup Requirements
- **Python 3.12** (3.14 incompatible — use `uv venv --python python3.12`)
- **sox** (`sudo apt install sox libsox-dev`)
- **Attention:** `attn_implementation="sdpa"` — flash-attn is **incompatible** with CUDA 13.0 + PyTorch cu130 (exception spec mismatch in `rsqrt`/`rsqrtf` math functions, fails at nvcc compile)
- **Package:** `pip install qwen-tts`

## Scripts

| Script | Model | Usage |
|---|---|---|
| `scripts/voice_clone_test.py` | Base | Clone voice from reference audio |
| `scripts/design_then_clone.py` | VoiceDesign → Base | **Recommended:** design voice, then clone for consistent output |
| `templates/custom_voice_test.py` | CustomVoice | 9 built-in speakers |
| `templates/voice_design_test.py` | VoiceDesign | Design voice from NL description |

Run from `~/projects/qwen3-tts/` with `.venv/bin/python <script>`.

## Voice Design → Clone (Recommended Workflow)

The optimal pipeline for a consistent custom voice across multiple outputs:

1. **VoiceDesign model** → synthesize a short reference clip from NL voice description
2. **Free VoiceDesign model** → `del model; torch.cuda.empty_cache()`
3. **Base model** → build reusable `create_voice_clone_prompt()` from the designed clip
4. **Generate all speech** with `generate_voice_clone(voice_clone_prompt=...)` — consistent voice, no recomputing ref features

```python
import torch, soundfile as sf
from qwen_tts import Qwen3TTSModel

# Step 1: Design
design_model = Qwen3TTSModel.from_pretrained(
    "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
    device_map="cuda:0", dtype=torch.bfloat16, attn_implementation="sdpa",
)
ref_text = "Hey there! I'm your new AI assistant."
ref_wavs, sr = design_model.generate_voice_design(
    text=ref_text, language="English",
    instruct="Warm male, mid-30s, calm Nordic quality, measured pace",
    max_new_tokens=2048,
)
sf.write("designed_ref.wav", ref_wavs[0], sr)

# Step 2: Free design model, load clone model
del design_model; torch.cuda.empty_cache()

clone_model = Qwen3TTSModel.from_pretrained(
    "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
    device_map="cuda:0", dtype=torch.bfloat16, attn_implementation="sdpa",
)
prompt = clone_model.create_voice_clone_prompt(ref_audio=(ref_wavs[0], sr), ref_text=ref_text)

# Step 3: Generate with consistent voice
wavs, sr = clone_model.generate_voice_clone(
    text="Any new text here.", language="English", voice_clone_prompt=prompt, max_new_tokens=2048,
)
sf.write("output.wav", wavs[0], sr)
```

## Custom Voice (9 Built-in Speakers)

| Speaker | Description | Native lang |
|---|---|---|
| Vivian | Bright, slightly edgy young female | Chinese |
| Serena | Warm, gentle young female | Chinese |
| Uncle_Fu | Seasoned male, low mellow timbre | Chinese |
| Dylan | Youthful Beijing male, clear natural | Chinese (dialect) |
| Eric | Lively Chengdu male, slightly husky | Chinese (dialect) |
| Ryan | Dynamic male, strong rhythmic drive | English |
| Aiden | Sunny American male, clear midrange | English |
| Ono_Anna | Playful Japanese female, light nimble | Japanese |
| Sohee | Warm Korean female, rich emotion | Korean |

## Supported Languages
chinese, english, french, german, italian, japanese, korean, portuguese, russian, spanish
- Use `language="auto"` for unsupported languages (Norwegian etc.) — quality varies

## Performance (RTX 4060 Laptop 8GB, SDPA, bfloat16)
- **Model load:** 8-19s (8s cached, 19s first load)
- **Generation RTF:** ~1.7x realtime (warmed up, design→clone pipeline)
- **First inference RTF:** ~9x (includes warmup/compile overhead)
- **Output:** 24000 Hz, 16-bit mono WAV
- **VRAM:** ~5.7-6.5GB during inference
- **`max_new_tokens`:** default 8192 → use 2048 for faster single-sentence generation

## Download Models
```bash
cd ~/projects/qwen3-tts && source .venv/bin/activate
huggingface-cli download Qwen/Qwen3-TTS-Tokenizer-12Hz --local-dir models/Qwen3-TTS-Tokenizer-12Hz
huggingface-cli download Qwen/Qwen3-TTS-12Hz-1.7B-Base --local-dir models/Qwen3-TTS-12Hz-1.7B-Base
huggingface-cli download Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice --local-dir models/Qwen3-TTS-12Hz-1.7B-CustomVoice
huggingface-cli download Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign --local-dir models/Qwen3-TTS-12Hz-1.7B-VoiceDesign
```

## Web UI Demo
```bash
.venv/bin/qwen-tts-demo Qwen/Qwen3-TTS-12Hz-1.7B-Base --ip 0.0.0.0 --port 8000
```

## Voice Design → Clone Interactive Workflow

When the user asks to start voice design, prompt them in this order:

1. **Language** — which language to speak (supported: chinese, english, french, german, italian, japanese, korean, portuguese, russian, spanish, or "auto" for others)
2. **Voice description** — natural language description of the desired voice (e.g. "Warm elderly male, slow and thoughtful", "Energetic young female with a bright tone")
3. **Text to speak** — the text to synthesize with the designed voice

Then run:
```bash
cd ~/projects/qwen3-tts
.venv/bin/python -u design_then_clone.py \
  --language "<language>" \
  --design-instruct "<voice description>" \
  --texts "<text>" \
  --max-new-tokens 2048 \
  --design-model models/Qwen3-TTS-12Hz-1.7B-VoiceDesign \
  --clone-model models/Qwen3-TTS-12Hz-1.7B-Base
```

Output goes to `design_clone_output/`. The designed reference clip + cloned output WAVs are saved there.

IMPORTANT: Always pass `--design-model` and `--clone-model` with local paths to avoid re-downloading from HF.

## Custom Voice Interactive Workflow

When the user asks to start custom voice, prompt them in this order:

1. **Language** — which language to speak (supported: chinese, english, french, german, italian, japanese, korean, portuguese, russian, spanish, or "auto" for others)
2. **Speaker** — which built-in speaker to use. Choices: Vivian (bright young female), Serena (warm gentle female), Uncle_Fu (seasoned low male), Dylan (Beijing male), Eric (Chengdu male), Ryan (dynamic male), Aiden (sunny American male), Ono_Anna (playful Japanese female), Sohee (warm Korean female)
3. **Style instruction** (optional) — emotional/style direction (e.g. "very angry", "whispering", "excited"). Can be empty.
4. **Text to speak** — the text to synthesize

Then run:
```bash
cd ~/projects/qwen3-tts
.venv/bin/python -u custom_voice_test.py \
  --no-flash-attn \
  --language "<language>" \
  --speaker "<speaker>" \
  --instruct "<style instruction>" \
  --text "<text>" \
  --model models/Qwen3-TTS-12Hz-1.7B-CustomVoice
```

Output saved as `custom_voice_output.wav`.

IMPORTANT: Always pass `--model` with local path to avoid re-downloading from HF.

## Persistent Daemon Pattern (Recommended)

Loading the model for every TTS call adds 8-19s overhead. For interactive/auto-play use, run a persistent daemon:

```bash
# Start daemon (pre-loads Base model in VRAM)
cd ~/projects/qwen3-tts && source .venv/bin/activate
.venv/bin/python ~/bin/tts-daemon

# Generate speech (6-7s for cached voices)
~/bin/tts-client "Your text here" --mood neutral

# Generate + play
paplay $(~/bin/tts-client "Hello world" --mood neutral)

# Convert to Opus for Discord
ffmpeg -y -i input.wav -c:a libopus -b:a 64k output.opus
```

**Daemon protocol**: HTTP-like over Unix socket (`/tmp/tts-daemon.sock`).
- Client sends: `POST /tts HTTP/1.0\r\nContent-Length: N\r\n\r\n{"text":"...","mood":"neutral","out":"/tmp/out.wav"}`
- Client calls `shutdown(SHUT_WR)` after sending
- Server responds with JSON, then **closes connection** (critical — client reads until EOF)

**Daemon scripts:**
- `~/bin/tts-daemon` — persistent process, holds Base model in ~5.7GB VRAM
- `~/bin/tts-client` — sends request, returns output path
- `~/bin/tts-speak` — generates + auto-plays via PulseAudio
- `~/bin/tts-discord` — generates + converts to `.opus` for Discord attachment

**Performance with daemon:**
| Scenario | Time |
|----------|------|
| Cached voice (neutral, alert, etc.) | ~6-7s |
| New voice design (first time) | ~18-45s |
| Model already loaded in daemon | ~3-4s pure generation |

## Voice Caching

Designed voices are cached as reference clips: `~/data/hermes/voice/cache/ref_{mood}.wav`.
First call to a new mood triggers the full VoiceDesign → Base clone pipeline (slow).
Subsequent calls reuse the cached reference (fast). Pre-cache all 8 moods during setup.

## Dynamic Voice Selection

The `tts-speak` and `tts-bridge` scripts auto-detect mood from text:
- **Severity mapping**: info→neutral, low→calm, medium→friendly, high→alert, critical→urgent
- **Keyword detection**: error/failed→warning, critical/emergency→urgent, success/done→friendly, question→curious, scanning→serious
- **Override**: `--mood urgent` or `--severity high`

## Pitfalls
1. **No Norwegian** in supported langs — use `language="auto"`, quality is decent but not native
2. **flash-attn + CUDA 13.0 = compile fail** — `rsqrt`/`rsqrtf` noexcept mismatch in nvcc. Use `sdpa` instead (nearly as fast)
3. **Python 3.12 required** — `qwen-tts` does not work on 3.14
4. **sox required** — `sudo apt install sox libsox-dev` (missing sox causes silent hang)
5. **max_new_tokens=8192 default** — slow for short text. Pass `max_new_tokens=2048` for sentences
6. **Both models can't fit VRAM at once** — must free one before loading the other
7. **First inference is ~5x slower** than subsequent — warmup/compile overhead
8. **uv venv has no pip** — use `uv pip install --python .venv/bin/python` not `.venv/bin/pip`
9. **flash-attn build needs `--no-build-isolation`** with uv — it requires torch at build time but doesn't declare it
10. **Daemon socket protocol**: Server MUST close connection after sending response. Client reads until EOF, not until empty recv(). Use the HTTP-like protocol shown above.
11. **Hermes backgrounding**: Use `terminal(background=true, command="...")` from Hermes, never `&`/`nohup`/`disown` in shell scripts. These are blocked by the security scanner.
12. **PulseAudio in WSL2**: Works via WSLg. Use `paplay` for playback. WSLg provides `/mnt/wslg/PulseServer` automatically.
13. **Single daemon instance**: Ensure only ONE tts-daemon runs. Check `/tmp/tts-daemon.pid` before starting. Multiple instances compete for VRAM and cause 2x model load times. Kill stale PIDs with `pkill -f tts-daemon` before restart.
14. **Daemon request serialization**: The daemon handles one request at a time. New-mood design (~18-45s) blocks all queued requests. Pre-cache all 8 moods during setup to avoid design pipeline during interactive use.
15. **Non-blocking playback**: Never use `paplay` synchronously in the main response path. Background it: `paplay "$wav" 2>/dev/null &`. If running from a Hermes background process, use `terminal(background=true)` for both TTS and playback.

## Voice Reference Audio Pipeline

For sourcing, cleaning, and describing reference audio for voice cloning,
use the companion skill **voice-clone-pipeline** (`~/.hermes/skills/voice-clone-pipeline/`).

It provides: web search for voice clips → quality scoring → noise removal →
voice description generation (pitch, timbre, pace) → VoiceDesign prompt output.

After cloning, evaluate quality with **voice-clone-evaluator**
(`~/.hermes/skills/voice-clone-evaluator/`). It compares source vs clone similarity
(using speaker embeddings), prompt vs output fidelity (acoustic checkpoints), and
generates specific feedback on how to improve prompts.

## Reference Files
- `references/architecture.md` — autoregressive token-LM architecture, component breakdown, performance characteristics
- `scripts/design_then_clone.py` — design→clone pipeline (recommended workflow)
- `scripts/voice_clone_test.py` — standalone voice clone from reference audio
