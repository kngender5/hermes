# STT Pipeline Reference

## Installed versions

| Package | Version | Install |
|---|---|---|
| `sounddevice` | 0.5.5 | `pip install --break-system-packages sounddevice` (or `pip install --user sounddevice`) |
| `faster-whisper` | (present) | In `~/.local/lib/python3.14` |
| `edge-tts` | 7.2.8 | pip |
| `ffmpeg` | 8.0.1 | system (`apt`) |

## Audio backends (auto-detected by `voice-input`)

1. **ALSA** (`arecord`) — native Linux
2. **PulseAudio** (`ffmpeg -f pulse`) — WSLg audio bridge
3. **Windows dshow** (`ffmpeg.exe`) — WSL2 fallback

## Whisper model

- **Model**: `NbAiLab/nb-whisper-large` (Norwegian-optimized, CUDA)
- Also available: `NbAiLab/nb-whisper-medium` (lower latency)
- Device: `cuda`, compute: `float16`

## Quick scripts

| Script | Purpose |
|---|---|
| `~/bin/tts` | TTS: text → wav file |
| `~/bin/voice-input` | STT: record mic → transcribe → stdout |
| `~/bin/voice_transcribe.py` | STT: transcribe WAV file |
| `~/bin/stt-stream` | STT: continuous streaming mic → text |
| `~/bin/tts-loop` | TTS: interactive text loop → play audio |

## Windows paths

- ffmpeg.exe: `/mnt/c/Users/rkarl/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_*/ffmpeg-*/bin/ffmpeg.exe`
- Microphone: `Microphone Array (Realtek(R) Audio)`
