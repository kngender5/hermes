#!/usr/bin/env python3
"""
voice_clone_evaluator.py — Evaluate voice cloning quality and prompt fidelity.

Three-way comparison:
  1. PROMPT vs DESIGNED REFERENCE — did VoiceDesign follow instructions?
  2. SOURCE vs CLONE — does the clone sound like the original speaker?
  3. PROMPT vs CLONE OUTPUT — does the final output match the prompt intent?

Modes:
  full    — complete 3-way evaluation (recommended)
  compare — speaker similarity between two audio files
  analyze — single audio file vs text prompt

Usage:
  python3 voice_clone_evaluator.py full \\
    --prompt "Male, low baritone, calm measured pace" \\
    --source-audio original_ref.wav \\
    --source-text "Reference transcript" \\
    --designed-ref design_clone_output/designed_reference.wav \\
    --cloned-output design_clone_output/clone_000.wav

  python3 voice_clone_evaluator.py compare source.wav clone.wav

  python3 voice_clone_evaluator.py analyze \\
    --prompt "Low male voice, slow and deliberate" \\
    --audio test_output.wav
"""

import argparse
import json
import re
import sys
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")

try:
    from resemblyzer import VoiceEncoder, preprocess_wav
    HAS_RESEMBLYZER = True
except ImportError:
    HAS_RESEMBLYZER = False

try:
    import librosa
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False


# ── Speaker Embedding Comparator ──────────────────────────────────────

class SpeakerComparator:
    def __init__(self):
        self.encoder = None
        if HAS_RESEMBLYZER:
            try:
                self.encoder = VoiceEncoder()
            except Exception as e:
                print(f"Resemblyzer encoder failed: {e}", file=sys.stderr)

    def get_embedding(self, wav_path: str) -> np.ndarray:
        if not self.encoder:
            raise RuntimeError("Resemblyzer encoder not available")
        wav = preprocess_wav(wav_path)
        return self.encoder.embed_utterance(wav)

    @staticmethod
    def cosine_similarity(emb1: np.ndarray, emb2: np.ndarray) -> float:
        cos = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2) + 1e-10)
        return round(cos, 4)

    @staticmethod
    def similarity_to_score(cos: float) -> float:
        return round(max(0, min(100, (cos - 0.5) / 0.5 * 100)), 2)

    @staticmethod
    def classify_quality(cos: float) -> str:
        if cos > 0.92: return "excellent — very close match"
        elif cos > 0.85: return "good — same speaker family"
        elif cos > 0.75: return "moderate — noticeable differences"
        elif cos > 0.65: return "weak — different speaker characteristics"
        else: return "poor — different speakers"

    def compare(self, wav1: str, wav2: str) -> dict:
        try:
            emb1 = self.get_embedding(wav1)
            emb2 = self.get_embedding(wav2)
            cos = self.cosine_similarity(emb1, emb2)
            return {
                "cosine_similarity": cos,
                "similarity_score": self.similarity_to_score(cos),
                "quality": self.classify_quality(cos),
            }
        except Exception as e:
            return {"error": str(e), "cosine_similarity": 0, "similarity_score": 0, "quality": "error"}


# ── Acoustic Feature Extractor ───────────────────────────────────────

class AcousticAnalyzer:
    def extract_features(self, wav_path: str) -> dict:
        if not HAS_LIBROSA:
            return {"error": "librosa not available"}
        try:
            y, sr = librosa.load(wav_path, sr=24000, mono=True)
        except Exception as e:
            return {"error": str(e)}
        if len(y) < 2048:
            return {"error": "audio too short"}
        f = {"duration": round(len(y) / sr, 2), "samplerate": sr}
        # Pitch
        f0, _, _ = librosa.pyin(y, fmin=50, fmax=500, sr=sr, frame_length=2048, hop_length=512)
        f0v = f0[~np.isnan(f0)] if f0 is not None else np.array([])
        if len(f0v) > 0:
            f["pitch_mean"] = round(float(np.mean(f0v)), 1)
            f["pitch_std"] = round(float(np.std(f0v)), 1)
            f["pitch_min"] = round(float(np.min(f0v)), 1)
            f["pitch_max"] = round(float(np.max(f0v)), 1)
            f["pitch_cv"] = round(float(np.std(f0v) / np.mean(f0v)), 3)
            m = f["pitch_mean"]
            f["pitch_class"] = "very low / bass" if m < 120 else "low / baritone" if m < 160 else "medium / tenor" if m < 200 else "high / alto" if m < 260 else "very high / soprano"
        else:
            f["pitch_mean"] = 0
            f["pitch_class"] = "unvoiced"
        # Rate
        onsets = librosa.onset.onset_detect(y=y, sr=sr, hop_length=512, units='time')
        f["onset_rate"] = round(len(onsets) / max(f["duration"], 0.1), 2)
        f["speaking_rate_class"] = "very slow, deliberate" if f["onset_rate"] < 2 else "slow, measured" if f["onset_rate"] < 3 else "moderate, conversational" if f["onset_rate"] < 4.5 else "quick, energetic" if f["onset_rate"] < 6 else "very fast"
        # Spectral
        cent = librosa.feature.spectral_centroid(y=y, sr=sr, n_fft=2048, hop_length=512)
        f["spectral_centroid_mean"] = round(float(np.mean(cent)), 0)
        f["brightness"] = "dark, warm, mellow" if f["spectral_centroid_mean"] < 1500 else "balanced, natural" if f["spectral_centroid_mean"] < 2200 else "bright, clear, crisp" if f["spectral_centroid_mean"] < 3000 else "very bright, piercing"
        bw = librosa.feature.spectral_bandwidth(y=y, sr=sr, n_fft=2048, hop_length=512)
        f["spectral_bandwidth_mean"] = round(float(np.mean(bw)), 0)
        flat = librosa.feature.spectral_flatness(y=y, n_fft=2048, hop_length=512)
        f["spectral_flatness_mean"] = round(float(np.mean(flat)), 4)
        # Energy
        rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=512)[0]
        f["energy_mean"] = round(float(np.mean(rms)), 4)
        f["energy_std"] = round(float(np.std(rms)), 4)
        f["energy_cv"] = round(float(np.std(rms) / max(np.mean(rms), 1e-6)), 3)
        f["dynamic_range_db"] = round(float(20 * np.log10(max(np.max(rms), 1e-6) / max(np.mean(rms), 1e-6))), 1)
        f["energy_class"] = ("quiet, intimate" if f["energy_mean"] < 0.03 else "moderate" if f["energy_mean"] < 0.1 else "loud, powerful") + (", very even" if f["energy_cv"] < 0.15 else ", steady" if f["energy_cv"] < 0.3 else ", natural variation" if f["energy_cv"] < 0.5 else ", wide dynamic range")
        # Voice activity
        f["voice_activity_ratio"] = round(float(np.sum(rms > 0.05 * np.max(rms)) / max(len(rms), 1)), 3)
        return f


# ── Prompt Parser & Comparator ────────────────────────────────────────

class PromptAnalyzer:
    GENDER = {"male":"male","man":"male","masculine":"male","female":"female","woman":"female","feminine":"female"}
    PITCH = {"deep":"very low","bass":"very low","low":"low","baritone":"low","tenor":"medium","medium":"medium","alto":"high","high":"high","soprano":"very high","bright":"high","dark":"low","mellow":"low","warm":"low"}
    RATE = {"slow":"slow","deliberate":"slow","measured":"slow","thoughtful":"slow","calm":"slow","controlled":"slow","fast":"fast","quick":"fast","energetic":"fast","rapid":"fast","animated":"fast","lively":"fast","conversational":"moderate","natural":"moderate","moderate":"moderate"}
    ENERGY = {"quiet":"quiet","intimate":"quiet","soft":"quiet","gentle":"quiet","loud":"loud","powerful":"loud","commanding":"loud","strong":"loud","projected":"loud","moderate":"moderate","even":"moderate"}
    QUALITY = {"husky":"husky","raspy":"raspy","rough":"rough","gravelly":"raspy","breathy":"breathy","airy":"breathy","clear":"clear","crisp":"crisp","precise":"articulate","monotone":"monotone","flat":"monotone","expressive":"expressive","animated":"expressive","nasal":"nasal","smooth":"smooth","rich":"rich","full":"rich","warm":"warm","cold":"cold","clinical":"cold","thin":"thin"}
    AGE = {"young":"young","youthful":"young","middle-aged":"middle","adult":"adult","old":"old","elderly":"old","aged":"old","senior":"old","venerable":"old","child":"child"}
    STYLE = {"formal":"formal","professional":"formal","announcer":"formal","casual":"casual","conversational":"casual","relaxed":"casual","dramatic":"dramatic","theatrical":"dramatic","serious":"serious","authoritative":"serious","playful":"playful","cheerful":"playful","nordic":"nordic","scandinavian":"nordic","british":"british","american":"american"}

    def parse(self, prompt: str) -> dict:
        words = re.split(r'[,;\s]+', prompt.lower())
        bg = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
        terms = words + bg
        r = {"gender":None,"pitch":None,"rate":None,"energy":None,"quality":[],"age":None,"style":[],"raw_prompt":prompt}
        for t in terms:
            t = t.strip()
            if not t: continue
            if t in self.GENDER and not r["gender"]: r["gender"] = self.GENDER[t]
            if t in self.PITCH and not r["pitch"]: r["pitch"] = self.PITCH[t]
            if t in self.RATE and not r["rate"]: r["rate"] = self.RATE[t]
            if t in self.ENERGY and not r["energy"]: r["energy"] = self.ENERGY[t]
            if t in self.QUALITY:
                q = self.QUALITY[t]
                if q not in r["quality"]: r["quality"].append(q)
            if t in self.AGE and not r["age"]: r["age"] = self.AGE[t]
            if t in self.STYLE:
                s = self.STYLE[t]
                if s not in r["style"]: r["style"].append(s)
        return r

    def compare(self, prompt: dict, features: dict) -> dict:
        matches, deviations, suggestions = [], [], []
        # Pitch
        if prompt.get("pitch") and features.get("pitch_mean", 0) > 0:
            pp = prompt["pitch"]
            af = features["pitch_mean"]
            ranges = {"very low":(60,120),"low":(100,170),"medium":(150,230),"high":(200,300),"very high":(280,500)}
            lo, hi = ranges.get(pp, (100, 250))
            if lo <= af <= hi:
                matches.append(f"pitch: expected {pp}, got {af:.0f}Hz ({features.get('pitch_class','')})")
            else:
                d = "higher" if af > hi else "lower"
                deviations.append(f"pitch: expected {pp} ({lo}-{hi}Hz), got {af:.0f}Hz — {d} than expected")
                suggestions.append(f"Add {'low/deep/bass/dark' if d=='higher' else 'bright/high/alto/crisp'} to adjust pitch")
        # Rate
        if prompt.get("rate"):
            pr = prompt["rate"]
            ar = features.get("onset_rate", 0)
            rc = {"slow":(0,3),"moderate":(2.5,5),"fast":(4,20)}
            lo, hi = rc.get(pr, (2, 5))
            if lo <= ar <= hi:
                matches.append(f"rate: expected {pr}, got {ar:.1f} onsets/s")
            else:
                d = "faster" if ar > hi else "slower"
                deviations.append(f"rate: expected {pr}, got {ar:.1f} onsets/s — {d} than expected")
                suggestions.append(f"Add {'slow/deliberate/measured/calm' if d=='faster' else 'fast/energetic/animated/quick'}")
        # Energy
        if prompt.get("energy"):
            pe = prompt["energy"]
            ae = features.get("energy_mean", 0)
            ec = {"quiet":(0,0.03),"moderate":(0.02,0.08),"loud":(0.06,1.0)}
            lo, hi = ec.get(pe, (0.02, 0.1))
            if lo <= ae <= hi:
                matches.append(f"energy: expected {pe}, got {ae:.4f} RMS")
            else:
                d = "louder" if ae > hi else "quieter"
                deviations.append(f"energy: expected {pe}, got {ae:.4f} RMS — {d} than expected")
                suggestions.append(f"Add {'quiet/intimate/soft' if d=='louder' else 'loud/powerful/commanding'}")
        # Monotone check
        mono = "monotone" in prompt.get("quality", [])
        cv = features.get("pitch_cv", 0)
        if mono and cv < 0.08:
            matches.append(f"monotone delivery confirmed (CV={cv:.3f})")
        elif mono and cv >= 0.08:
            deviations.append(f"monotone expected but pitch CV={cv:.3f} shows variation")
            suggestions.append("For monotone: use 'flat', 'deadpan', 'robotic'")
        elif not mono and cv < 0.05:
            deviations.append(f"Voice is monotone (CV={cv:.3f}). Add 'expressive', 'animated', 'dynamic' if variation intended.")
        # Breathy
        if "breathy" in prompt.get("quality", []) or "airy" in prompt.get("quality", []):
            fl = features.get("spectral_flatness_mean", 0)
            bw = features.get("spectral_bandwidth_mean", 0)
            if fl > 0.15 or bw < 2000:
                suggestions.append("For breathiness: add 'airy', 'soft-spoken', 'whisper-like'")
        # Husky
        if "husky" in prompt.get("quality", []) or "raspy" in prompt.get("quality", []):
            if "dark" not in features.get("brightness", ""):
                suggestions.append("For huskier quality: try 'gravelly', 'rough', 'smoky', 'gritty'")
        return {"matches": matches, "deviations": deviations, "suggestions": suggestions,
                "match_count": len(matches), "deviation_count": len(deviations)}


# ── Main ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Voice Clone Evaluator")
    sub = parser.add_subparsers(dest="mode")

    fp = sub.add_parser("full", help="Full 3-way evaluation")
    fp.add_argument("--prompt", required=True)
    fp.add_argument("--source-audio", required=True)
    fp.add_argument("--source-text", default="")
    fp.add_argument("--designed-ref", required=True)
    fp.add_argument("--cloned-output", required=True)

    cp = sub.add_parser("compare", help="Compare two files")
    cp.add_argument("file1")
    cp.add_argument("file2")

    ap = sub.add_parser("analyze", help="Audio vs prompt")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--audio", required=True)

    parser.add_argument("--json", action="store_true")
    parser.add_argument("--report", action="store_true")
    args = parser.parse_args()

    if not args.mode:
        parser.print_help()
        sys.exit(1)

    spk = SpeakerComparator()
    ana = AcousticAnalyzer()
    ppa = PromptAnalyzer()

    if args.mode == "compare":
        sim = spk.compare(args.file1, args.file2)
        f1, f2 = ana.extract_features(args.file1), ana.extract_features(args.file2)
        diffs = {}
        for k in ["pitch_mean","pitch_std","onset_rate","spectral_centroid_mean","energy_mean","energy_cv","voice_activity_ratio"]:
            v1, v2 = f1.get(k), f2.get(k)
            if v1 is not None and v2 is not None and isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
                diffs[k] = {"file1": round(v1,4) if isinstance(v1,float) else v1, "file2": round(v2,4) if isinstance(v2,float) else v2,
                             "diff": round(abs(v1-v2),4), "pct_diff": round(abs(v1-v2)/max(abs(v1),1e-6)*100,1) if v1!=0 else 0}
        result = {"speaker_similarity": sim, "feature_diffs": diffs}
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            s = sim
            print(f"\nSpeaker Similarity")
            print(f"  Cosine: {s.get('cosine_similarity','?')}  Score: {s.get('similarity_score','?')}/100  {s.get('quality','?')}")
            for feat, v in diffs.items():
                arrow = "↑" if v["file2"]>v["file1"] else "↓" if v["file2"]<v["file1"] else "="
                print(f"  {feat:35s} {v['file1']:>10} → {v['file2']:<10} ({arrow} {v['pct_diff']:+.1f}%)")

    elif args.mode == "analyze":
        prompt = ppa.parse(args.prompt)
        feat = ana.extract_features(args.audio)
        comp = ppa.compare(prompt, feat)
        if args.json:
            print(json.dumps({"prompt": prompt, "features": feat, "comparison": comp}, indent=2, default=str))
        else:
            print(f"\nPrompt vs Audio Analysis")
            print(f"  Prompt: {args.prompt}")
            for k in ["pitch_mean","pitch_class","onset_rate","speaking_rate_class","spectral_centroid_mean","brightness","energy_mean","energy_class","voice_activity_ratio"]:
                if k in feat: print(f"  {k:35s}: {feat[k]}")
            for m in comp.get("matches",[]): print(f"  ✓ {m}")
            for d in comp.get("deviations",[]): print(f"  ✗ {d}")
            for s in comp.get("suggestions",[]): print(f"  → {s}")

    elif args.mode == "full":
        parsed = ppa.parse(args.prompt)
        sf_ = ana.extract_features(args.source_audio)
        df_ = ana.extract_features(args.designed_ref)
        of_ = ana.extract_features(args.cloned_output)
        s2c = spk.compare(args.source_audio, args.cloned_output)
        s2d = spk.compare(args.source_audio, args.designed_ref)
        p2d = ppa.compare(parsed, df_)
        p2o = ppa.compare(parsed, of_)
        clone_sim = s2c.get("similarity_score", 0)
        pm, pd = p2o.get("match_count", 0), p2o.get("deviation_count", 0)
        pf = round(pm / max(pm + pd, 1) * 100, 1)
        overall = round((clone_sim + pf) / 2, 1)
        if overall >= 85: verdict = "Excellent — production-ready"
        elif overall >= 70: verdict = "Good — minor tuning"
        elif overall >= 55: verdict = "Moderate — iterate"
        elif overall >= 40: verdict = "Below expectations"
        else: verdict = "Poor — fundamental mismatch"

        result = {
            "scores": {"clone_similarity": clone_sim, "prompt_fidelity": pf, "overall_quality": overall},
            "verdict": verdict,
            "parsed_prompt": parsed,
            "source_to_clone": s2c,
            "source_to_designed": s2d,
            "prompt_to_output": p2o,
            "suggestions": p2o.get("suggestions", []),
        }
        if clone_sim < 60:
            result["suggestions"].append("⚠ Clone similarity low: use longer (10-30s) clean reference, no music")
        if clone_sim < 75:
            result["suggestions"].append("Clone fidelity: try 15-30s clean single-speaker reference")

        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            print(f"\n╔══════════════════════════════════════════════╗")
            print(f"║  Voice Clone Evaluation Report               ║")
            print(f"╚══════════════════════════════════════════════╝")
            print(f"\n  VERDICT: {verdict}")
            print(f"  Clone similarity: {clone_sim:.1f}/100  Prompt fidelity: {pf:.1f}/100  Overall: {overall:.1f}")
            print(f"  Speaker: {s2c.get('quality','?')}  (cos={s2c.get('cosine_similarity','?')})")
            for m in p2o.get("matches",[]): print(f"  ✓ {m}")
            for d in p2o.get("deviations",[]): print(f"  ✗ {d}")
            for s in result["suggestions"]: print(f"  → {s}")

        if args.report:
            Path("voice_eval_report.json").write_text(json.dumps(result, indent=2, default=str))
            print(f"\n  Report saved: voice_eval_report.json")


if __name__ == "__main__":
    main()
