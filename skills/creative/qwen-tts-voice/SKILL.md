---
name: qwen-tts-voice
description: >
  Dynamic Qwen3-TTS text-to-speech with context-aware voice selection and voice cloning.
  Analyzes response context, severity, mood, and intent to select an appropriate voice.
  Supports cloning any character voice from a reference audio clip.
  Use when: voice output, TTS, speak, narrate, voice cloning, character voices, Discord voice.
triggers: [tts, voice, speak, narrate, audio response, voice output, read aloud, voice clone, character voice]
---

# Qwen3-TTS Dynamic Voice System

Context-aware TTS with 8 mood profiles + custom voice cloning from reference audio.

## Voice Profiles

| Mood | When | Characteristics |
|------|------|-----------------|
| neutral | Default/informational | Measured, precise, clear |
| alert | Warnings, issues | Sharp, faster, commanding |
| calm | Success, completion | Soothing, slow, warm |
| urgent | Critical breaches | Rapid, intense, forceful |
| friendly | Greetings, help | Warm, conversational |
| serious | Reports, analysis | Deliberate, authoritative |
| curious | Questions, investigation | Inquisitive, thoughtful |
| warning | Security events | Firm, cautionary |

**Severity mapping**: info→neutral, low→calm, medium→friendly, high→alert, critical→urgent

## Usage

### Quick TTS with Auto-Play
```
~/bin/tts-speak "Text" [--mood MOOD]
```
Generates WAV → plays via PulseAudio → outputs file path. Non-blocking.

### Voice Cloning
```
# 1. Download reference
yt-dlp --extract-audio --audio-format mp3 -o "ref.%(ext)s)" "URL"
ffmpeg -y -i ref.mp3 -ss 10 -t 8 -ar 24000 -ac 1 ref_clean.wav

# 2. Send to daemon (mode=clone)
python3 ~/bin/tts-client.py --mode clone \
  --ref-audio ref_clean.wav --ref-text "Reference words" \
  --text "New text" --out output.wav
```

### Discord Voice Messages
```
~/bin/tts-discord "Text" [--mood MOOD]
```
Outputs `.opus` file — attach to Discord message. Non-blocking.

## Architecture

**tts-daemon.py**: Persistent process, keeps Qwen3-TTS Base model in VRAM (~5.7GB). Socket at `/tmp/tts-daemon.sock`. One request at a time.

**Protocol** (HTTP-like over Unix socket):
- Mood: `{"text":"...","mood":"neutral","out":"..."}`
- Clone: `{"text":"...","ref_audio":"...","ref_text":"...","out":"...","mode":"clone"}`

## Performance (RTX 4060 8GB)

| Scenario | Time |
|----------|------|
| Cached voice (daemon) | 6-8s |
| New voice design | 18-45s |
| Voice clone (daemon) | 8-15s |

## Voice Reference Audio Pipeline

For sourcing, cleaning, and preparing reference audio for voice cloning,
use the companion skill **voice-clone-pipeline** (`~/.hermes/skills/voice-clone-pipeline/`).

`voice-clone-pipeline` handles:
- Searching/downloading reference audio from web, YouTube, LibriVox, FreeSound
- Quality analysis (SNR, music detection, clipping)
- Noise reduction preprocessing (preserves voice characteristics)
- Voice description generation (for VoiceDesign prompts)
- End-to-end clone pipeline orchestration

This skill (`qwen-tts-voice`) focuses on the runtime TTS daemon, mood-based voice
selection, and Discord/Telegram voice output. Use both together for best results.

## Pitfalls

1. **Never block response on TTS** — 6-45s generation. Always background it.
2. **One request at a time** — Daemon handles sequentially.
3. **Clean reference audio** — 8-15s single speaker, no background music. Quality depends entirely on reference clarity.
4. **YouTube filenames** — yt-dlp produces `file.webm).mp3` — always quote paths.
5. **`language="auto"`** — Required for character voices and non-English.
6. **max_new_tokens** — 2048 for short text, 4096 for long. Higher = slower.
7. **Daemon crash recovery** — `pkill -f tts-daemon; rm -f /tmp/tts-daemon.sock /tmp/tts-daemon.pid; tts-daemon &`
8. **WSL2 path resolution** — When CWD is `/mnt/c/Users/rkarl` (Windows mount), downloaded files end up there instead of WSL home. Use absolute paths or `cd ~` before running voice-clone-pipeline scripts. Always verify file locations after downloads.
9. **yt-dlp clip duration** — Default `--duration 0` downloads full length. Specifying a duration clips to that many seconds. YouTube uploads of character clips often have background music added by uploaders — the short preview may score higher quality than the full download. Always run the quality analyzer on downloaded files.
10. **VoiceDesign from description alone** (no reference audio) works but produces less accurate clones than VoiceDesign→Clone with actual reference audio. For best results, provide both a description AND a reference clip.

## Reference Files

- `references/voice-cloning-guide.md` — Detailed cloning workflow
- `references/discord-tts-pipeline.md` — Discord voice message integration

## Prerequisites

Requires mlops/qwen3-tts skill for model setup:
- `~/projects/qwen3-tts/` project with `.venv/` (Python 3.12)
- Models: Base (clone), VoiceDesign (create new voices)
- PulseAudio running (`pulseaudio --start`)
- sox installed (`sudo apt install sox libsox-dev`)
