---
name: voice-input-windows
description: Set up voice input on Windows — global hotkeys for push-to-talk and always-on ASR using Python keyboard+sounddevice+faster-whisper. Covers both WSL-bridge and Windows-native approaches. Also covers WSL2↔Windows hardware bridge patterns for audio, camera, serial/USB, and GPIO device access.
triggers:
  - voice input
  - speech to text
  - voice hotkey
  - whisper hotkey
  - push to talk
  - always on asr
  - voice transcription
  - global hotkey
  - numpad voice
---

# Voice Input on Windows

Two architectures for voice input from a Windows microphone.

## Architecture A — WSL Bridge

Record via best available audio backend, transcribe in WSL with faster-whisper (CUDA).

**Script:** `~/bin/voice-input` (bash)

```
voice-input              # record 10s, Norwegian default
voice-input -s 15        # record 15 seconds
voice-input -l no        # force Norwegian
voice-input -l en        # force English
```

**Components:**
- `~/bin/voice-input` — orchestrator (bash), auto-detects audio backend
- `~/bin/voice_transcribe.py` — Whisper transcription (Python, WSL, CUDA, NbAiLab/nb-whisper-medium)

**Audio Backends (auto-detected, in order):**
1. **ALSA** (`arecord`) — native Linux audio, rarely available in WSL2
2. **PulseAudio** (`ffmpeg -f pulse`) — WSLg audio bridge, check with `pactl list sources`
3. **Windows dshow** (`ffmpeg.exe`) — most reliable in WSL2, uses WinGet ffmpeg + DirectShow

**⚠️ CRITICAL:** Linux `ffmpeg` (from `apt`) does NOT support `dshow`. You MUST use `ffmpeg.exe` from Windows for microphone capture. The `voice-input` script handles this automatically when ALSA/PulseAudio are unavailable.

See `references/wsl-setup-notes.md` for ffmpeg.exe path details and device names.

## Architecture B — Windows Native Hotkey Daemon

All-in-one Python on Windows. Global hotkeys for PTT and always-on ASR.

**Script:** `C:\Users\<user>\bin\voice_hotkey.py`

```
pythonw C:\Users\<user>\bin\voice_hotkey.py    # background
python  C:\Users\<user>\bin\voice_hotkey.py    # with console
```

**Dependencies (Windows Python):**
```
pip install keyboard faster-whisper sounddevice numpy pyperclip win10toast
```

### Default Hotkeys

| Hotkey | Action |
|--------|--------|
| Left + Numpad0 | Push-to-talk (15s record → transcribe → type) |
| Left + Numpad3 | Toggle always-on ASR |
| Left + Numpad4 | Language cycle: auto → EN → auto → ... |
| Left + Numpad6 | Language cycle: auto → NB → auto → ... |

### Log File

`C:\Users\<user>\Documents\voice_hotkey.log` — all activity, survives crashes.

## Critical Pitfalls

### keyboard module key names
Use `'num 0'` (with space), NOT `'numpad0'` or `'numpad 0'`:
```python
kb.add_hotkey('left+num 0', callback)   # CORRECT
kb.add_hotkey('left+numpad0', callback) # FAILS
```
Verified names: `num 0`–`num 9`, `left`, `right`.

### kb.wait() broken on Windows
`kb.wait()` returns immediately on Windows PowerShell. Use a blocking loop instead:
```python
while True:
    time.sleep(1)
```

### CUDA fallback probe
`WhisperModel()` constructor doesn't allocate GPU memory — lazy load. Constructor succeeds but `transcribe()` fails with `cublas64_12.dll not found`. Must probe with an actual transcription:
```python
tmp = create_silent_wav(1)  # 1s silence
m = WhisperModel(MODEL, device='cuda', compute_type='float16')
segs, _ = m.transcribe(tmp, beam_size=1, vad_filter=False)
list(segs)  # force iteration — this triggers CUDA init
```
If that fails, fall back to CPU `int8`.

### Re-entrant hotkey guard
Hotkey callbacks fire in a thread. If already recording, ignore duplicate triggers:
```python
_ptt_active = False

def push_to_talk():
    global _ptt_active
    if _ptt_active:
        return
    _ptt_active = True
    try:
        # ... record + transcribe ...
    finally:
        _ptt_active = False
```

### HF symlinks warning on Windows
Set `os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'` before importing huggingface.

### Write files from WSL to Windows
Use `/mnt/c/Users/<user>/path` for writes. PowerShell escaping via WSL `terminal()` is unreliable — write `.ps1` files from WSL and execute via `powershell.exe -File "C:\path\script.ps1"`.

### .pyc cache staleness
When updating scripts written from WSL, Windows Python may cache old `.pyc`. Delete `__pycache__` or use `python -B` flag.

## WSL Python Environment

`faster-whisper` is installed system-wide. `voice-input` uses `$(command -v python3)` — no venv needed.

If a venv IS needed for additional deps, use `uv`:
```bash
cd /tmp && uv venv whisper-env
source whisper-env/bin/activate
uv pip install <package>
```
**⚠️ Venvs in `/tmp` are wiped on every reboot.** Do NOT hardcode `/tmp/whisper-env` in scripts.

## ffmpeg on Windows
Install via winget: `winget install -e --id Gyan.FFmpeg`
After install, refresh PATH in new shells: `$env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User')`

ffmpeg on Windows supports `dshow` for microphone capture:
```
ffmpeg -y -f dshow -t 10 -i "audio=Microphone Array (Realtek(R) Audio)" -ac 1 -ar 16000 -sample_fmt s16 out.wav
```

## Project Layout

```
C:\Users\<user>\bin\
  voice_hotkey.py          # hotkey daemon (main entry point)
  voice_input.py           # record + transcribe module
C:\Users\<user>\Documents\
  voice_hotkey.log         # runtime log
  voice_hotkey.log.bak     # previous session log (rotated manually)
~/. WSL:
  bin/voice-input          # WSL bridge orchestrator (bash) — see templates/voice-input
  bin/voice_transcribe.py  # Whisper transcription (Python, CUDA) — see templates/voice_transcribe.py
```

## Mic Access in WSL

WSL2 does NOT have direct microphone access. The `voice-input` script auto-detects the best backend:
1. **ALSA** (`arecord -l`) — native Linux, rare in WSL2
2. **PulseAudio** (`pactl list sources`) — WSLg bridge
3. **Windows dshow** (`ffmpeg.exe`) — most reliable, uses `ffmpeg.exe` from WinGet

**⚠️ Linux `ffmpeg` does NOT have `dshow`.** You must use `ffmpeg.exe` from Windows. The script handles this automatically.

For manual mic device discovery: `ffmpeg.exe -list_devices true -f dshow -i dummy 2>&1 | grep "audio"`

## WSL2↔Windows Hardware Bridge Patterns

The WSL2→Windows bridge pattern works for any hardware, not just audio:

### Architecture
```
WSL2 (bash/python) → powershell.exe -File script.ps1 → Windows ffmpeg/Python → hardware
                                      ↓
                              output file on shared filesystem
                                      ↓
                         WSL2 reads file (CUDA Whisper, etc.)
```

Key: `/mnt/c/` provides shared filesystem access. Use `-ExecutionPolicy Bypass -File` (NOT `-Command`) for PowerShell to avoid `$env:` escaping issues.

### Cross-Platform Scripting Rules
- **✅ DO:** Use `powershell.exe -File` for PS1 scripts — gets fresh environment (new PATH), no escaping issues
- **❌ DON'T:** Use `powershell.exe -Command` with `$env:` — bash consumes `$env` before PowerShell sees it
- **✅ DO:** Land intermediate files on the shared filesystem (`/mnt/c/Users/<you>/Documents/` from WSL, `C:\Users\<you>\Documents\` from Windows)
- **✅ DO:** Use `cmd.exe /c` only for `.bat` files or simple commands

### Extending to Other Hardware
- **Camera:** `ffmpeg -f dshow -i video="Camera Name"`
- **Serial/USB:** Use Python `pyserial` on Windows via `powershell.exe -File`, read from `/mnt/c/` shared path or `\\wsl$\` network path
- **GPIO/IoT:** Run Flask/API server on Windows hardware agent, call from WSL via HTTP

The shared filesystem (`/mnt/c/`) is the simplest IPC mechanism — no sockets or network config needed.

### Bridge Pitfalls
1. **ffmpeg not found from WSL** — winget install updates PATH but WSL inherits old env. Restart WSL (`wsl --shutdown`) or use `-File` PS1 scripts (fresh env)
2. **Empty transcription** — mic privacy off. Check: Settings → Privacy → Microphone → "Let desktop apps access your microphone" = ON
3. **Recording too short** (`< 1000 bytes`) — ffmpeg failed silently or wrong device name. Verify with `ffmpeg -list_devices true -f dshow -i dummy`
4. **Hanging PowerShell** — if ffmpeg hangs (device in use), kill from WSL: `powershell.exe -Command "Get-Process ffmpeg | Stop-Process -Force"`
5. **Cross-profile write guard on `/mnt/c/`** — Writing to Windows paths from WSL triggers approval prompts. This is expected behavior.

See `references/voice-hotkeys.md` for the full Windows-side hotkey daemon setup, key name reference, and troubleshooting table.

**Do NOT use generic `large-v3` for Norwegian** — it performs poorly on Norwegian transcription. Use a Norwegian-specific model:

| Model | Size | Quality | Download |
|-------|------|---------|----------|
| `NbAiLab/nb-whisper-medium` | ~1.5 GB | **Best balance** — fast download, excellent Norwegian | **Recommended** |
| `NbAiLab/nb-whisper-large` | ~3 GB | Best accuracy but very slow to download (30+ min) | If quality critical |
| `NbAiLab/nb-whisper-small` | ~0.5 GB | Acceptable, fast | Low-resource fallback |

Set `MODEL = "NbAiLab/nb-whisper-medium"` in `voice_transcribe.py`.

## TTS (Text-to-Speech)

### ⚠️ NeuTTS is NOT suitable for Norwegian
The installed `neutts` package (v0.1.2) uses `EspeakBackend(language="en-us")` — English-only phonemizer. It will NOT produce correct Norwegian pronunciation even if the model supports multilingual input. **Do NOT use NeuTTS for Norwegian TTS.** It also requires a reference audio file (`jo.wav`) for voice cloning, which is typically missing.

### ✅ edge-tts — Recommended for Norwegian TTS
Microsoft's `edge-tts` is free, no voice cloning needed, and produces excellent Norwegian.

**Installation** (Python 3.14 on Ubuntu/WSL requires `--break-system-packages` or venv):
```bash
pip install --break-system-packages edge-tts
# OR use a venv (survives reboots if NOT in /tmp):
python3 -m venv ~/.venvs/tts && ~/.venvs/tts/bin/pip install edge-tts
```

**Norwegian voices** (verified):
| Voice | Gender | Notes |
|-------|--------|-------|
| `nb-NO-PernilleNeural` | Female | Default, warm, slightly formal |
| `nb-NO-FinnNeural` | Male | Clear, slightly deeper |

⚠️ Note: `nb-NO-IselinNeural` is **NOT** an actual edge-tts voice. Use `PernilleNeural` instead.

**Usage:**
```bash
# Direct CLI
edge-tts --voice nb-NO-PernilleNeural --text "Hei, dette er en test" --write-media /tmp/test.wav

# Convenience alias (create ~/bin/tts)
tts "Din tekst her"                        # default Pernille
tts "Din tekst her" nb-NO-FinnNeural       # Finn voice
```

**Convenience script** (`~/bin/tts` or `/home/kng/bin/tts`):
```bash
#!/bin/bash
TEXT="$1"
VOICE="${2:-nb-NO-PernilleNeural}"
OUT="/tmp/tts_$(date +%s).wav"
if [ -z "$TEXT" ]; then
    echo "Usage: tts \"text\" [voice]"; exit 1
fi
edge-tts --voice "$VOICE" --text "$TEXT" --write-media "$OUT" 2>/dev/null
echo "$OUT"
```

**Python API:**
```python
import asyncio
from edge_tts import Communicate

async def tts(text, voice="nb-NO-PernilleNeural", outfile="/tmp/out.wav"):
    await Communicate(text, voice).save(outfile)
```

**Wiring into text_to_speech Hermes tool:**
The built-in `text_to_speech` tool uses configured providers (edge/openai/xai/minimax/elevenlabs). For local edge-tts, use the `~/bin/tts` script or Python API above, then deliver the WAV via `MEDIA:/tmp/tts_*.wav`.

**Edge TTS pitfalls:**
- First call downloads voice model (~3 MB), subsequent calls are offline
- Output is 24kHz mono, efficient for streaming
- Unicode/Norwegian characters (æ, ø, å) work correctly

## Support Files

- `templates/voice-input` — bash orchestrator for WSL bridge recording + transcription
- `templates/voice_transcribe.py` — Python Whisper transcription script (CUDA, Norwegian default)
- `templates/tts` — bash wrapper for `edge-tts` TTS with Norwegian voices (Pernille/Finn)
- `references/wsl-setup-notes.md` — environment-specific setup notes, CUDA probe validation, venv location
- `references/norwegian-model-notes.md` — model comparison, download benchmarks, language code tips
- `references/voice-hotkeys.md` — Windows-side hotkey daemon: full setup, key name reference, `kb.wait()` pitfall, re-entrant guard, troubleshooting table, WSL↔Windows bridge patterns
