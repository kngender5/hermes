# Qwen3-TTS Daemon — Detailed Setup & Troubleshooting

## Daemon Scripts

| Script | Purpose |
|--------|---------|
| `tts-daemon` | Persistent server, holds Base model in VRAM (~5.7GB) |
| `tts-client` | Send TTS request over Unix socket |
| `tts-speak` | Generate + auto-play via PulseAudio |
| `tts-bridge` | Standalone TTS (no daemon, slower) |
| `tts-discord` | Generate + convert to .opus for Discord |

## Protocol

HTTP-like over Unix socket (`/tmp/tts-daemon.sock`).

**Request:** `POST /tts HTTP/1.0\r\nContent-Length: N\r\n\r\n{json}`  
**Client:** `shutdown(SHUT_WR)` after sending  
**Server:** Sends JSON response, **closes connection** (client reads until EOF)

### Mood TTS Request
```json
{"text": "...", "mood": "neutral", "out": "/tmp/out.wav", "mode": "tts"}
```

### Voice Clone Request
```json
{"text": "...", "ref_audio": "/path/ref.wav", "ref_text": "...", "out": "/tmp/out.wav", "mode": "clone"}
```

## 8 Mood Profiles

neutral | alert | calm | urgent | friendly | serious | curious | warning

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Client timeout | Daemon doing voice design (~20-45s). Pre-cache moods. |
| Connection refused | Start daemon. Check /tmp/tts-daemon.sock exists. |
| Two daemons | `pkill -f tts-daemon`. Check /tmp/tts-daemon.pid. |
| No audio | `pulseaudio --start`. WSLg auto-starts PulseServer. |
| Blocking playback | Use `terminal(background=true)`, never `&` in Hermes. |
