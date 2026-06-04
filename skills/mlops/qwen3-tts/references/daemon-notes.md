# TTS Daemon and Voice System — Operational Notes

## Architecture
Hermes Response → tts-speak.sh → tts-client.py → tts-daemon (Unix socket) → Qwen3-TTS → WAV → paplay

## Daemon Protocol
HTTP-like over Unix socket at /tmp/tts-daemon.sock. Client sends POST with JSON body, server responds with JSON then closes. Critical: server must close connection after response.

## Performance (RTX 4060 8GB)
- Cold model load: 19s
- Cached model load: 8s
- Cached voice generation: 6-7s
- New voice design: 18-45s
- Pure generation (model loaded): 3-4s

## Voice Profiles
neutral (default), alert (warnings), calm (success), urgent (critical), friendly (greetings), serious (reports), curious (questions), warning (security events)

## Voice Caching
Designed voices saved to ~/data/hermes/voice/cache/ref_{mood}.wav. Pre-cache all 8 moods for instant generation.

## Mood Auto-Detection
Severity mapping: info→neutral, low→calm, medium→friendly, high→alert, critical→urgent. Keyword overrides: error→warning, critical→urgent, success→friendly, question→curious.

## Discord Output
Convert WAV to Opus: ffmpeg -y -i input.wav -c:a libopus -b:a 64k output.opus

## WSL2 Audio
PulseAudio works via WSLg. Use paplay for playback.

## Known Issues
1. First inference ~9x RTF warmup
2. Model swap for new moods (can't fit both in 8GB VRAM)
3. Single-threaded daemon
4. Must use terminal(background=true) for daemon, never & or nohup
