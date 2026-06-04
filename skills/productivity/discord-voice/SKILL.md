---
name: discord-voice
description: Send and receive voice messages on Discord via TTS/STT pipeline. Triggered by voice message, send voice, voice response, /voiceresponse, TTS, or STT.
---

# Discord Voice

Voice interaction pipeline for Discord: TTS (text→speech→Discord ogg/opus) and STT (mic→Whisper→text).

## /voiceresponse toggle

User controls whether replies are sent as voice or text:

| Command | Effect |
|---|---|
| `/voiceresponse on` | Replies as voice messages (ogg/opus via Discord MEDIA) |
| `/voiceresponse off` | Plain text (default) |
| `/voiceresponse status` | Show current state |

Store toggle state in memory key `Voice response toggle: on|off`. When on, run the full TTS pipeline before replying.

## TTS → Discord pipeline

### Generate speech

```bash
OUT="/tmp/voice_$(date +%s).wav"
edge-tts --voice "nb-NO-FinnNeural" --text "$TEXT" --write-media "$OUT" 2>/dev/null
```

Default voice: `nb-NO-FinnNeural` (male). Alternative: `nb-NO-PernilleNeural` (female).

### Convert to ogg/opus

Discord renders `.ogg/opus` as voice message player:

```bash
ffmpeg -y -i voice.wav -c:a libopus -b:a 64k voice.ogg 2>/dev/null
```

### Send as voice

```
send_message(action='send', target='discord:#channel', message='MEDIA:/path/to/voice.ogg')
```

## STT pipeline

See `references/stt-pipeline.md` for full reference.

One-shot:
```bash
voice-input -s 5 -l no          # record 5s, Norwegian
```

Streaming (lower latency, requires `sounddevice`):
```bash
python3 <skill_dir>/scripts/stt-stream.py no     # continuous mic → text
```

## Available scripts

| Script | Purpose |
|---|---|
| `scripts/stt-stream.py` | Continuous microphone → transcribed text (streaming) |
| `scripts/tmux_agent.py` | Spawn/manage Hermes agents in tmux windows |
| `scripts/orchestrate.py` | Higher-level task delegation to tmux agents |
| `references/stt-pipeline.md` | STT setup, audio backends, model info |
| `references/multi-agent-tmux.md` | Multi-agent tmux orchestration patterns |

## Voice quality — Finn vs Pernille

`nb-NO-PernilleNeural` handles Norwegian text more accurately than `nb-NO-FinnNeural` for short phrases. Finn tends to garble Norwegian words (e.g. "på nå" → "pa na", "kanon" → "voyce"). For primarily Norwegian conversation, use Pernille as default:

```bash
# Recommended default
edge-tts --voice "nb-NO-PernilleNeural" --text "$TEXT" --write-media "$OUT"
```

Switch to Finn only if user explicitly prefers male voice.

## Multi-agent tmux spawning

For spawning multiple Hermes agents in tmux windows (parallel interactive agents), see:
`~/bin/tmux_agent.py` and `~/bin/orchestrate.py`

Or create a new tmux session with:

```bash
python3 ~/bin/tmux_agent.py create mysession /working/dir
python3 ~/bin/tmux_agent.py interactive mysession planner -m openrouter/owl-alpha
python3 ~/bin/tmux_agent.py interactive mysession builder -m openrouter/owl-alpha
python3 ~/bin/tmux_agent.py interactive mysession reviewer -m openrouter/owl-alpha
tmux attach -t mysession  # View all agents
```

## Pitfalls

- Keep clips under ~30s; split long responses
- Only `.ogg/opus` renders as voice player — `.mp3`/`.wav` appear as file attachments
- `edge-tts` output is mp3-in-wav-container — ffmpeg handles it fine
- For long replies, prefer text + short voice summary over multi-minute clips
- **PernilleNeural** is more accurate for Norwegian than FinnNeural — use Pernille as default
- **Voice response toggle** — Store state in memory key `Voice response toggle: on|off`. Check memory before each reply to determine if TTS pipeline should run.
