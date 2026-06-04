#!/usr/bin/env python3
"""
voice_source_finder.py — Search and download voice/audio clips from the web.

Sources (in priority order):
  1. Web search (SearXNG) for direct audio file URLs
  2. YouTube / Vimeo / SoundCloud via yt-dlp
  3. LibriVox (public domain audiobooks)
  4. FreeSound (requires API key)
  5. Any direct URL (WAV, MP3, FLAC, OGG)

Usage:
  python3 voice_source_finder.py "query" [--source web|youtube|freesound|librivox|url] 
                                      [--max-results 10]
                                      [--output-dir ./refs]
                                      [--duration 0]   # 0 = full length
"""

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime

SEARXNG_URL = os.environ.get("SEARXNG_URL", "http://localhost:8080")
FREESOUND_TOKEN = os.environ.get("FREESOUND_TOKEN", "")
AUDIO_EXTENSIONS = {'.wav', '.mp3', '.flac', '.ogg', '.opus', '.m4a', '.aac', '.wma'}
VOICE_SOURCE_DOMAINS = ["librivox.org", "archive.org", "freesound.org", "soundcloud.com", "youtube.com", "youtu.be"]


def searxng_search(query, count=10):
    params = {"q": f"{query} audio filetype:mp3 OR filetype:wav OR filetype:flac", "format": "json", "language": "en", "categories": "general,files", "pageno": 1}
    url = f"{SEARXNG_URL}/search?{urllib.parse.urlencode(params)}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            results = data.get("results", [])
            audio_results = []
            for r in results:
                url_val = r.get("url", "")
                if any(ext in url_val.lower() for ext in AUDIO_EXTENSIONS) or any(d in url_val for d in VOICE_SOURCE_DOMAINS):
                    audio_results.append(r)
            return audio_results[:count]
    except Exception as e:
        print(f"  [searxng] unavailable: {e}", file=sys.stderr)
        return []


def generic_web_search(query, count=10):
    ddg_query = urllib.parse.quote_plus(f"{query} (mp3 OR wav OR flac) audio clip -youtube")
    url = f"https://html.duckduckgo.com/html/?q={ddg_query}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
            urls = re.findall(r'uddg=([^&]+)', html)
            results = []
            for u in urls[:count * 2]:
                try:
                    decoded = urllib.parse.unquote(u)
                    if any(ext in decoded.lower() for ext in AUDIO_EXTENSIONS) or any(d in decoded for d in VOICE_SOURCE_DOMAINS):
                        results.append({"url": decoded, "title": decoded, "source": "web"})
                except Exception:
                    pass
            return results[:count]
    except Exception as e:
        print(f"  [web] search failed: {e}", file=sys.stderr)
        return []


def search_youtube(query, count=10):
    try:
        result = subprocess.run(
            ["yt-dlp", f"ytsearch{count}:{query}", "--flat-playlist",
             "--print", "%(id)s|%(title)s|%(duration)s|%(view_count)s",
             "--no-warnings", "--quiet"],
            capture_output=True, text=True, timeout=30)
        results = []
        for line in result.stdout.strip().split("\n"):
            if "|" not in line:
                continue
            parts = line.split("|", 3)
            if len(parts) >= 2:
                duration = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
                views = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0
                results.append({"url": f"https://www.youtube.com/watch?v={parts[0]}", "title": parts[1], "duration": duration, "views": views, "source": "youtube"})
        return results
    except Exception as e:
        print(f"  [youtube] search failed: {e}", file=sys.stderr)
        return []


def search_librivox(query, count=10):
    try:
        url = f"https://librivox.org/api/feed/audiobooks?format=json&title={urllib.parse.quote(query)}&limit={count}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            books = data if isinstance(data, list) else data.get("books", [])
            results = []
            for book in books[:count]:
                url_val = book.get("url_zip_file", "") or book.get("url_librivox", "")
                title = book.get("title", "Unknown")
                author = book.get("authors", [{}])
                author_name = author[0].get("first_name", "") + " " + author[0].get("last_name", "") if author else ""
                results.append({"url": url_val, "title": f"{title} by {author_name.strip()}", "language": book.get("language", "English"), "source": "librivox"})
            return results
    except Exception as e:
        print(f"  [librivox] search failed: {e}", file=sys.stderr)
        return []


def search_freesound(query, count=10):
    if not FREESOUND_TOKEN:
        return []
    try:
        url = f"https://freesound.org/apiv2/search/text/?query={urllib.parse.quote(query)}&page_size={count}&fields=id,name,username,duration,previews,license"
        req = urllib.request.Request(url, headers={"Authorization": f"Token {FREESOUND_TOKEN}", "User-Agent": "voice-clone-pipeline/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            results = []
            for item in data.get("results", []):
                preview = item.get("previews", {})
                preview_url = preview.get("preview-hq-mp3", "") or preview.get("preview-lq-mp3", "")
                if preview_url:
                    results.append({"url": preview_url, "title": item.get("name", ""), "duration": item.get("duration", 0), "license": item.get("license", ""), "source": "freesound"})
            return results
    except Exception as e:
        print(f"  [freesound] search failed: {e}", file=sys.stderr)
        return []


def download_audio(url, output_path, duration=0):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if any(url.lower().endswith(ext) for ext in AUDIO_EXTENSIONS):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                output_path.write_bytes(resp.read())
            return True
        except Exception:
            return False
    try:
        cmd = ["yt-dlp", "--no-warnings", "-x", "--audio-format", "wav", "--audio-quality", "0", "-o", str(output_path.with_suffix(".%(ext)s"))]
        if duration and duration > 0:
            cmd += ["--download-sections", f"*00:00:00-{duration}"]
        cmd.append(url)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            downloaded = list(output_path.parent.glob(output_path.stem + ".*"))
            return bool(downloaded)
        return False
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(description="Find and download voice reference audio")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--source", choices=["web", "youtube", "freesound", "librivox", "url", "all"], default="all")
    parser.add_argument("--max-results", type=int, default=10)
    parser.add_argument("--output-dir", default="./voice_refs")
    parser.add_argument("--duration", type=int, default=0, help="Clip duration in seconds (0 = full)")
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    all_results = []

    print(f"Searching for: '{args.query}'  Sources: {args.source}")
    print("=" * 60)

    if args.source in ("web", "all"):
        print("\n[1/4] Web search...")
        web_results = searxng_search(args.query, args.max_results)
        if not web_results:
            web_results = generic_web_search(args.query, args.max_results)
        all_results.extend(web_results)
        print(f"  Found: {len(web_results)}")

    if args.source in ("youtube", "all"):
        print("\n[2/4] YouTube search...")
        yt_results = search_youtube(f"{args.query} interview speech narration -music -song", args.max_results)
        all_results.extend(yt_results)
        print(f"  Found: {len(yt_results)}")

    if args.source in ("librivox", "all"):
        print("\n[3/4] LibriVox search...")
        lv_results = search_librivox(args.query, args.max_results)
        all_results.extend(lv_results)
        print(f"  Found: {len(lv_results)}")

    if args.source in ("freesound", "all"):
        print("\n[4/4] FreeSound search...")
        fs_results = search_freesound(args.query, args.max_results)
        all_results.extend(fs_results)
        print(f"  Found: {len(fs_results)}")

    seen_urls = set()
    unique_results = []
    for r in all_results:
        url = r.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_results.append(r)
    unique_results.sort(key=lambda r: 0 if any(r.get("url", "").lower().endswith(e) for e in ['.wav', '.mp3', '.flac']) else (1 if "youtube" in r.get("url", "").lower() else 2))

    print(f"\nTotal unique results: {len(unique_results)}")
    if args.json:
        print(json.dumps(unique_results, indent=2))
    else:
        for i, r in enumerate(unique_results[:args.max_results], 1):
            dur = f"{r.get('duration', '')}s" if r.get('duration') else ""
            views = f"{r.get('views', '')} views" if r.get('views') else ""
            print(f"\n  [{i}] {r.get('title', 'Untitled')[:70]}")
            print(f"      Source: {r.get('source', '?')}  {dur} {views}")
            print(f"      URL: {r.get('url', '')[:90]}")

    if args.download and unique_results:
        print(f"\nDownloading to {output_dir}/")
        downloaded = []
        for i, r in enumerate(unique_results[:5]):
            url = r.get("url", "")
            if not url:
                continue
            safe_name = re.sub(r'[^\w\-.]', '_', r.get('title', f'clip_{i}'))[:60]
            out_file = output_dir / f"{safe_name}_{i}.wav"
            if download_audio(url, out_file, args.duration):
                downloaded.append(str(out_file))
                print(f"  [OK] {out_file.name}")
        print(f"\nDownloaded {len(downloaded)} files")

    manifest = {"query": args.query, "timestamp": datetime.now().isoformat(), "results_count": len(unique_results), "results": unique_results}
    manifest_path = output_dir / f"search_{args.query.replace(' ', '_')[:40]}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
