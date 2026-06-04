# WSL Bridge Setup — Session Notes (2025-05-27, 2026-06-01)

## Environment
- WSL2 Ubuntu, RTX 4060 (8GB VRAM), CUDA 13.2
- System Python 3.14+ locked (PEP 668 externally-managed-environment)
- `faster-whisper` 1.2.1 installed system-wide via pip --break-system-packages (or uv)
- `ffmpeg` (Linux) installed via apt — has NO `dshow` support (Linux-only: alsa, pulse)

## ⚠️ Venv in `/tmp` — VOLATILE
`/tmp/whisper-env/` is wiped on every reboot. Do NOT hardcode it in scripts.

**Current approach (2026-06-01):** `voice-input` uses system Python directly:
```bash
VENV="$(command -v python3)"
```
`faster-whisper` is available system-wide. No venv needed unless additional deps are required.

If a new venv IS needed:
```bash
cd /tmp && uv venv whisper-env
source whisper-env/bin/activate
uv pip install faster-whisper
```
Remember: must be recreated after every reboot.

## Model Choice (updated 2026-06-01)
- **CURRENT:** `NbAiLab/nb-whisper-medium` — Norwegian-optimized, fast download, excellent Norwegian
- Previous: `large-v3` — weak on Norwegian, replaced
- `nb-whisper-large` — best accuracy but very slow download (30+ min), only if quality critical
- `nb-whisper-small` — low-resource fallback

## CUDA Probe (validated)
```python
from faster_whisper import WhisperModel
m = WhisperModel("NbAiLab/nb-whisper-medium", device="cuda", compute_type="float16")
import numpy as np
audio = np.zeros(16000, dtype=np.float32)  # 1s silence
segs, _ = m.transcribe(audio, beam_size=1, vad_filter=False)
list(segs)  # forces CUDA init
```
RTX 4060 8GB: medium model uses ~1.5GB VRAM — plenty of headroom.

## Norwegian Language
- Default `-l no` for voice input
- User communicates in English/Norwegian mix
- `nb-whisper-medium` handles code-switching well

## Mic Access in WSL — Three-Tier Fallback

**WSL2 has NO direct mic access.** The `voice-input` script auto-detects in this order:

### Backend 1: ALSA (arecord)
```bash
arecord -D default -f S16_LE -r 16000 -c 1 -d 10 out.wav
```
Rarely available in WSL2. Native Linux audio.

### Backend 2: PulseAudio (WSLg)
```bash
ffmpeg -y -f pulse -i default -t 10 -ac 1 -ar 16000 out.wav
```
Requires WSLg + PulseAudio sink. Check: `pactl list sources`.

### Backend 3: Windows dshow (ffmpeg.exe) — MOST RELIABLE IN WSL2
```bash
WIN_FFMPEG="/mnt/c/Users/rkarl/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.1.1-full_build/bin/ffmpeg.exe"
"$WIN_FFMPEG" -y -f dshow -i "audio=Microphone Array (Realtek(R) Audio)" -t 10 -ac 1 -ar 16000 -sample_fmt s16 out.wav
```

**CRITICAL:** Linux `ffmpeg` (from `apt`) does NOT have `dshow`. You MUST use `ffmpeg.exe` from Windows.

Find mic device names:
```bash
ffmpeg.exe -list_devices true -f dshow -i dummy 2>&1 | grep "audio"
```

Known device on this machine: `"Microphone Array (Realtek(R) Audio)"`

## ffmpeg.exe PATH Notes
- Installed via WinGet: `winget install -e --id Gyan.FFmpeg`
- Location: `%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg_*full_build\bin\ffmpeg.exe`
- From WSL: access via `/mnt/c/...` path
- WSL-shell does NOT inherit Windows PATH for `.exe` files reliably — use absolute path

## TTS Status (2026-06-01)
- NeuTTS: BROKEN — `neutts_samples/jo.wav` missing, non-functional
- edge-tts: works (`nb-NO-FinnNeural`, `nb-NO-IselinNeural`)
- Hermes built-in TTS: configured via hermes config
