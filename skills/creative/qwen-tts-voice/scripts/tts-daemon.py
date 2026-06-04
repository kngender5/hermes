#!/usr/bin/env python3
"""
tts-daemon.py — Persistent Qwen3-TTS server with voice cloning support.

Protocol: HTTP-like over Unix socket.
  Mood TTS:  {"text": "...", "mood": "neutral", "out": "...", "mode": "tts"}
  Voice Clone: {"text": "...", "ref_audio": "...", "ref_text": "...", "out": "...", "mode": "clone"}

Start: cd ~/projects/qwen3-tts && source .venv/bin/activate && .venv/bin/python ~/bin/tts-daemon
"""
import os, sys, json, socket, signal, logging, time
from pathlib import Path

PROJECT = Path.home() / "projects/qwen3-tts"
MODEL_BASE = str(PROJECT / "models/Qwen3-TTS-12Hz-1.7B-Base")
MODEL_DESIGN = str(PROJECT / "models/Qwen3-TTS-12Hz-1.7B-VoiceDesign")
REF_AUDIO = str(Path.home() / "data/hermes/voice/owl_default_ref.wav")
REF_TEXT = "Hey there! I just wanted to say hello and let you know I'm here to help."
CACHE_DIR = Path.home() / "data/hermes/voice/cache"
SOCKET_PATH = "/tmp/tts-daemon.sock"
PID_FILE = "/tmp/tts-daemon.pid"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("tts-daemon")

VOICE_INSTRUCTS = {
    "neutral": "Male, early 30s, calm British-Scandinavian accent, measured and precise, clear diction, moderate pace",
    "alert": "Male, early 30s, urgent and sharp, faster pace, commanding tone, clear authority, slightly raised intensity",
    "calm": "Male, early 30s, very calm and soothing, slow measured pace, warm timbre, gentle delivery",
    "urgent": "Male, early 30s, rapid and intense, high urgency, sharp articulation, commanding presence",
    "friendly": "Male, early 30s, warm and approachable, slight smile in voice, conversational pace, genuine friendliness",
    "serious": "Male, early 30s, grave and deliberate, slow authoritative pace, no-nonsense tone, professional gravity",
    "curious": "Male, early 30s, inquisitive and engaged, slight upward inflection, thoughtful pace, intellectual warmth",
    "warning": "Male, early 30s, firm and cautionary, measured but forceful, clear warning tone, serious undertone",
}

class TTSManager:
    def __init__(self):
        self.model = None

    def ensure_model(self):
        if self.model is not None:
            return
        log.info("Loading Base model...")
        import torch
        from qwen_tts import Qwen3TTSModel
        self.model = Qwen3TTSModel.from_pretrained(
            MODEL_BASE, device_map="cuda:0", dtype=torch.bfloat16, attn_implementation="sdpa",
        )
        log.info("Model loaded.")

    def get_mood_prompt(self, mood):
        import soundfile as sf
        cache_file = CACHE_DIR / f"ref_{mood}.wav"
        if cache_file.exists():
            ref = sf.read(str(cache_file))
            return self.model.create_voice_clone_prompt(ref_audio=ref, ref_text=REF_TEXT)
        self.design_voice(mood)
        ref = sf.read(str(CACHE_DIR / f"ref_{mood}.wav"))
        return self.model.create_voice_clone_prompt(ref_audio=ref, ref_text=REF_TEXT)

    def design_voice(self, mood):
        import torch, soundfile as sf
        from qwen_tts import Qwen3TTSModel
        instruct = VOICE_INSTRUCTS.get(mood, VOICE_INSTRUCTS["neutral"])
        log.info(f"Designing voice: {mood}")
        if self.model:
            del self.model; torch.cuda.empty_cache(); self.model = None
        dm = Qwen3TTSModel.from_pretrained(
            MODEL_DESIGN, device_map="cuda:0", dtype=torch.bfloat16, attn_implementation="sdpa",
        )
        ref_wavs, sr = dm.generate_voice_design(
            text=REF_TEXT, language="English", instruct=instruct, max_new_tokens=2048,
        )
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        sf.write(str(CACHE_DIR / f"ref_{mood}.wav"), ref_wavs[0], sr)
        del dm; torch.cuda.empty_cache()
        self.ensure_model()
        ref = sf.read(str(CACHE_DIR / f"ref_{mood}.wav"))
        return self.model.create_voice_clone_prompt(ref_audio=ref, ref_text=REF_TEXT)

    def generate_tts(self, text, mood, out_file):
        import soundfile as sf
        self.ensure_model()
        prompt = self.get_mood_prompt(mood)
        wavs, sr = self.model.generate_voice_clone(
            text=text, language="English", voice_clone_prompt=prompt, max_new_tokens=2048,
        )
        sf.write(out_file, wavs[0], sr)
        return {"status": "ok", "file": out_file, "duration": round(len(wavs[0]) / sr, 2)}

    def generate_clone(self, text, ref_audio, ref_text, out_file):
        import soundfile as sf
        self.ensure_model()
        ref = sf.read(str(ref_audio))
        prompt = self.model.create_voice_clone_prompt(ref_audio=ref, ref_text=ref_text)
        wavs, sr = self.model.generate_voice_clone(
            text=text, language="auto", voice_clone_prompt=prompt, max_new_tokens=4096,
        )
        sf.write(out_file, wavs[0], sr)
        return {"status": "ok", "file": out_file, "duration": round(len(wavs[0]) / sr, 2)}


def handle(conn, mgr):
    try:
        data = b""
        while b"\r\n\r\n" not in data:
            chunk = conn.recv(4096)
            if not chunk: return
            data += chunk
        header, body = data.split(b"\r\n\r\n", 1)
        content_length = 0
        for line in header.decode().split("\r\n"):
            if line.lower().startswith("content-length:"):
                content_length = int(line.split(":")[1].strip())
        while len(body) < content_length:
            chunk = conn.recv(4096)
            if not chunk: break
            body += chunk
        req = json.loads(body.decode())
        mode = req.get("mode", "tts")
        if mode == "clone":
            result = mgr.generate_clone(req["text"], req["ref_audio"], req.get("ref_text", ""), req.get("out", "/tmp/tts_clone.wav"))
        else:
            result = mgr.generate_tts(req["text"], req.get("mood", "neutral"), req.get("out", "/tmp/tts_out.wav"))
        resp = json.dumps(result).encode()
        conn.sendall(f"HTTP/1.0 200 OK\r\nContent-Length: {len(resp)}\r\n\r\n".encode() + resp)
    except Exception as e:
        log.error(f"Error: {e}")
        resp = json.dumps({"status": "error", "message": str(e)}).encode()
        try: conn.sendall(f"HTTP/1.0 500 Error\r\nContent-Length: {len(resp)}\r\n\r\n".encode() + resp)
        except: pass


def main():
    if os.path.exists(SOCKET_PATH): os.unlink(SOCKET_PATH)
    Path(PID_FILE).write_text(str(os.getpid()))
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    server.listen(5)
    os.chmod(SOCKET_PATH, 0o666)
    log.info(f"Listening on {SOCKET_PATH}")
    mgr = TTSManager()
    mgr.ensure_model()
    log.info("Ready.")
    signal.signal(signal.SIGTERM, lambda s, f: (server.close(), sys.exit(0)))
    signal.signal(signal.SIGINT, lambda s, f: (server.close(), sys.exit(0)))
    while True:
        try:
            conn, _ = server.accept()
            handle(conn, mgr)
            conn.close()
        except OSError:
            break

if __name__ == "__main__":
    main()
