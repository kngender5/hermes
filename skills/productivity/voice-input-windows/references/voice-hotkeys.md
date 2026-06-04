# Voice Input Hotkeys (Windows-side daemon)

## Hotkey Models

Two interaction patterns for voice input:

| Mode | Trigger | Behavior |
|---|---|---|
| Push-to-talk | Left + Numpad0 | Record fixed duration (default 15s), transcribe, type text |
| Always-on ASR | Left + Numpad3 (toggle) | Continuously record small chunks, auto-type when speech detected |

## Architecture (Fully Windows-side)

Unlike the basic WSL2↔Windows bridge (record in Windows → transcribe in WSL), the hotkey daemon runs **entirely on Windows** to avoid cross-process latency. The `keyboard` Python library registers global hotkeys without needing AutoHotkey installed.

```
keyboard lib (global hotkey)
    ↓
sounddevice records chunk (3s default)
    ↓
faster-whisper transcribes (CUDA float16)
    ↓
keyboard.write() types at cursor position
```

## Dependencies (Windows Python)

```powershell
pip install keyboard faster-whisper sounddevice numpy pyperclip
```

- `keyboard` — global hotkey registration (requires admin/root on some systems)
- `faster-whisper` — CTranslate2-based Whisper inference
- `sounddevice` + `numpy` — cross-platform audio recording (no ffmpeg needed for recording)
- `pyperclip` — fallback clipboard-based text injection if `keyboard.write()` fails

## Scripts

| File | Location | Purpose |
|---|---|---|
| `voice_hotkey.py` | `C:\Users\<you>\bin\voice_hotkey.py` | Hotkey daemon with both PTT and always-on modes |
| `voice_input.py` | `C:\Users\<you>\bin\voice_input.py` | Record + transcribe engine (standalone or importable) |

## Starting the Daemon

```powershell
# Visible console (debugging)
python C:\Users\<you>\bin\voice_hotkey.py

# Hidden (pythonw = no console window)
pythonw C:\Users\<you>\bin\voice_hotkey.py
```

## Always-on ASR Loop Details

- Records 3-second chunks in a loop
- Loads Whisper model **once** at startup (reused across chunks)
- Uses VAD filter + no_speech_threshold=0.6 to skip silence
- Types text via `keyboard.write()` with 10ms inter-char delay
- Prints to stderr for debugging: `[asr] >> transcribed text`
- Toggle off with same hotkey (Left+Numpad3)

## Changing Hotkeys

Edit `voice_hotkey.py` and change the hotkey strings:
```python
kb.add_hotkey('left+numpad 0', push_to_talk)   # push-to-talk
kb.add_hotkey('left+numpad 3', toggle_asr)       # always-on ASR
```

Format: `keyboard` library uses `+` for combos, space-separated key names.

## `keyboard` Module Key Names (Critical)

The `keyboard` library uses specific names that differ from what you might expect.

**Numpad keys** — use `num <digit>` (space between):
- Numpad 0 → `num 0` (scan codes 11, 82)
- Numpad 3 → `num 3` (scan codes 4, 81)
- Numpad 1-9 → `num 1` through `num 9`
- Also works: `num_0`, `num_3` (underscore variant)

**NOT valid**: `numpad0`, `numpad 0`, `kp0`, `keypad0`, `numpad_ins`

**Arrow keys**: `left`, `right`, `up`, `down`

**Find all valid names**:
```python
# On Windows, run this to discover key names:
import keyboard
tests = ["num 0", "num 3", "left", "numpad0", "kp0"]
for t in tests:
    try:
        print(f"OK:   {t!r:20s} -> {keyboard.key_to_scan_codes(t)}")
    except:
        print(f"FAIL: {t!r:20s}")
```

## `kb.wait()` Pitfall on Windows

`keyboard.wait()` may not block properly when running from PowerShell, causing the script to exit immediately. Use an explicit loop instead:

```python
# ❌ DON'T — exits immediately on Windows PowerShell
kb.wait()

# ✅ DO — reliable on Windows
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    cleanup()
```

## Re-entrant Hotkey Guard

When a hotkey callback takes seconds (e.g., 15s recording), pressing the hotkey again during that time fires a second concurrent callback. Guard with a boolean flag:

```python
_ptt_active = False

def push_to_talk():
    global _ptt_active
    if _ptt_active:
        return  # already recording
    _ptt_active = True
    try:
        # ... record, transcribe, type ...
    finally:
        _ptt_active = False
```

## Suppressing HuggingFace Symlinks Warning

On Windows, HuggingFace Hub emits a verbose symlink warning that clutters stderr. Suppress it:

```python
import os
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
```

## Cross-Profile Write Guard

Writing files to `/mnt/c/` from WSL triggers Hermes' cross-profile soft guard and requires user approval each time. This is by design — the guard protects against accidental writes to another profile's territory. When building Windows-side scripts from WSL, expect to confirm the first write. Subsequent writes to the same path in the same session usually go through.

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| Hotkey doesn't fire | `keyboard` needs admin privileges for global hotkeys | Run terminal as Administrator |
| Script exits immediately | `kb.wait()` doesn't block on Windows | Use `while True: time.sleep(1)` loop instead |
| Hotkey fires twice / overlaps | Re-entrant callback during long operation | Add `_active` guard flag |
| No text typed | `sounddevice` can't find mic | `python -c "import sounddevice; print(sounddevice.query_devices())"` |
| Transcription slow on first run | Model downloading | Pre-download: `python -c "from faster_whisper import WhisperModel; WhisperModel('base', device='cuda')"` |
| Audio too quiet | Mic gain too low | Check Windows Sound Settings → Recording → Levels |
| `keyboard` lib not found | Not installed for the right Python | Ensure `pip install keyboard` runs for the same Python that runs the script |
| `ValueError: Key 'numpad0' is not mapped` | Wrong key name for `keyboard` module | Use `num 0` not `numpad0`. See key names section above. |
