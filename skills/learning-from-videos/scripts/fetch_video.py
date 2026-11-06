#!/usr/bin/env python3
"""Fetch a video and its transcript into a work directory.

Usage:
  fetch_video.py URL_OR_PATH [--workdir DIR] [--whisper-model MODEL]
                 [--force-whisper] [--max-height 720] [--json]

Steps:
  1. Read metadata (yt-dlp for URLs, ffprobe for local files).
  2. Download the video at 720p or lower (skipped for local files).
  3. Get a transcript: YouTube captions first, local Whisper as fallback.
  4. Write meta.json, transcript.json, transcript.txt.

Exit code 0 on success. Prints a short summary; --json prints meta.json.
Work directory default: ~/.cache/video-notes/<slug>/
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

CACHE_ROOT = Path(os.environ.get("VIDEO_NOTES_CACHE", "~/.cache/video-notes")).expanduser()
DEFAULT_WHISPER_MODEL = "small"  # good balance of speed and accuracy on CPU

def ffbin(name):
    """Pick a working ffmpeg/ffprobe. Prefer a Homebrew build over an older one earlier on
    PATH (miniconda ships 4.x), but only if it actually runs (a Homebrew build can break
    when a linked library is upgraded)."""
    cands = [os.environ.get("VIDEO_NOTES_FFMPEG_DIR", ""), "/opt/homebrew/bin", "/usr/local/bin"]
    paths = [os.path.join(c, name) for c in cands if c and os.path.isfile(os.path.join(c, name))]
    on_path = shutil.which(name)
    if on_path:
        paths.append(on_path)
    for p in paths:
        try:
            if subprocess.run([p, "-version"], capture_output=True, timeout=10).returncode == 0:
                return p
        except Exception:
            continue
    sys.exit(f"ERROR: no working '{name}' found. Install one with: brew install ffmpeg")


FFMPEG, FFPROBE = ffbin("ffmpeg"), ffbin("ffprobe")


def die(msg, code=1):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def need(tool):
    if shutil.which(tool) is None:
        die(f"'{tool}' is not installed or not on PATH")


def run(cmd, **kw):
    return subprocess.run(cmd, text=True, capture_output=True, **kw)


def slugify(text, limit=60):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:limit].rstrip("-") or "video"


def fmt_ts(sec):
    sec = int(sec)
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def is_url(s):
    return bool(re.match(r"^https?://", s))


# ---------- metadata ----------

def meta_from_url(url):
    need("yt-dlp")
    r = run(["yt-dlp", "--dump-single-json", "--no-playlist", "--no-warnings", url])
    if r.returncode != 0:
        die(f"yt-dlp could not read the URL:\n{r.stderr.strip()[-1500:]}")
    info = json.loads(r.stdout)
    chapters = [
        {"start": c.get("start_time", 0), "title": c.get("title", "")}
        for c in (info.get("chapters") or [])
    ]
    return {
        "source": "url",
        "url": info.get("webpage_url") or url,
        "id": info.get("id"),
        "title": info.get("title") or "Untitled",
        "uploader": info.get("uploader") or info.get("channel"),
        "upload_date": info.get("upload_date"),
        "duration": info.get("duration") or 0,
        "description": (info.get("description") or "")[:8000],
        "chapters": chapters,
        "has_manual_subs": bool(info.get("subtitles")),
        "has_auto_subs": bool(info.get("automatic_captions")),
    }


def meta_from_file(path):
    p = Path(path).expanduser().resolve()
    if not p.is_file():
        die(f"file not found: {p}")
    r = run([FFPROBE, "-v", "error", "-show_entries", "format=duration",
             "-of", "json", str(p)])
    dur = 0.0
    try:
        dur = float(json.loads(r.stdout)["format"]["duration"])
    except Exception:
        pass
    return {
        "source": "file",
        "url": None,
        "id": None,
        "title": p.stem,
        "uploader": None,
        "upload_date": None,
        "duration": dur,
        "description": "",
        "chapters": [],
        "has_manual_subs": False,
        "has_auto_subs": False,
        "local_path": str(p),
    }


def video_codec(path):
    r = run([FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries",
             "stream=codec_name,width,height", "-of", "csv=p=0", str(path)])
    return r.stdout.strip().replace(",", " ") or "unknown"


# ---------- download ----------

def download_video(url, workdir, max_height):
    out = workdir / "video.mp4"
    if out.exists() and out.stat().st_size > 0:
        return out
    # Prefer H.264 (avc1). Older ffmpeg builds cannot decode AV1 or VP9, and the
    # frame extraction step needs ffmpeg to decode the file.
    h = max_height
    fmt = (f"bv*[height<={h}][vcodec^=avc1]+ba[ext=m4a]"
           f"/b[height<={h}][vcodec^=avc1]"
           f"/bv*[height<={h}][ext=mp4]+ba[ext=m4a]"
           f"/b[height<={h}][ext=mp4]/bv*[height<={h}]+ba/b")
    r = run(["yt-dlp", "--no-playlist", "--no-warnings", "-f", fmt,
             "--merge-output-format", "mp4", "-o", str(workdir / "video.%(ext)s"), url])
    if r.returncode != 0:
        die(f"download failed:\n{r.stderr.strip()[-1500:]}")
    found = sorted(workdir.glob("video.*"))
    found = [f for f in found if f.suffix.lower() in (".mp4", ".mkv", ".webm", ".mov")]
    if not found:
        die("download finished but no video file was produced")
    if found[0] != out:
        found[0].rename(out) if found[0].suffix == ".mp4" else None
        if not out.exists():
            out = found[0]
    return out


# ---------- captions ----------

def fetch_captions(url, workdir):
    """Return path to a VTT file or None."""
    existing = sorted(workdir.glob("subs.*.vtt"))
    if existing:
        return existing[0]
    r = run(["yt-dlp", "--no-playlist", "--no-warnings", "--skip-download",
             "--write-subs", "--write-auto-subs", "--sub-langs", "en.*,en,-live_chat",
             "--sub-format", "vtt", "--convert-subs", "vtt",
             "-o", str(workdir / "subs.%(ext)s"), url])
    found = sorted(workdir.glob("subs.*.vtt"))
    return found[0] if found else None


TAG_RE = re.compile(r"<[^>]+>")
TS_RE = re.compile(r"(\d+):(\d+):(\d+)[.,](\d+)|(\d+):(\d+)[.,](\d+)")


def parse_ts(s):
    m = TS_RE.match(s.strip())
    if not m:
        return None
    if m.group(1) is not None:
        h, mi, se, frac = int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4)
    else:
        h, mi, se, frac = 0, int(m.group(5)), int(m.group(6)), m.group(7)
    # keep the string so "080" stays 0.080 and not 0.8
    return h * 3600 + mi * 60 + se + int(frac) / (10 ** len(frac))


def parse_vtt(path):
    """Parse a VTT file into segments. Handles YouTube auto-caption rolling duplicates."""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    segments = []
    i = 0
    last_text = ""
    while i < len(lines):
        line = lines[i].strip()
        if "-->" in line:
            start_s, rest = line.split("-->", 1)
            end_s = rest.strip().split(" ")[0]
            start, end = parse_ts(start_s), parse_ts(end_s)
            i += 1
            text_lines = []
            while i < len(lines) and lines[i].strip() != "":
                t = TAG_RE.sub("", lines[i]).replace("&nbsp;", " ").replace("&amp;", "&")
                t = t.replace("&gt;", ">").replace("&lt;", "<").strip()
                if t:
                    text_lines.append(t)
                i += 1
            # Auto captions repeat the previous line in the next cue. Drop repeats.
            fresh = [t for t in text_lines if t != last_text]
            if fresh:
                text = " ".join(fresh)
                if text != last_text and start is not None:
                    segments.append({"start": round(start, 2), "end": round(end or start, 2), "text": text})
                    last_text = fresh[-1]
        i += 1
    # Merge segments that share a start time (some auto tracks emit zero-length cues)
    merged = []
    for seg in segments:
        if merged and abs(seg["start"] - merged[-1]["start"]) < 0.05:
            merged[-1]["text"] += " " + seg["text"]
            merged[-1]["end"] = max(merged[-1]["end"], seg["end"])
        else:
            merged.append(seg)
    return merged


# ---------- whisper ----------

def run_whisper(video, workdir, model):
    need("whisper")
    out_json = workdir / (video.stem + ".json")
    if not out_json.exists():
        print(f"Running Whisper ({model}). This can take several minutes...", file=sys.stderr)
        env = dict(os.environ)
        env["PATH"] = os.path.dirname(FFMPEG) + os.pathsep + env.get("PATH", "")
        r = subprocess.run(["whisper", str(video), "--model", model, "--output_format", "json",
                            "--output_dir", str(workdir), "--fp16", "False", "--verbose", "False"],
                           text=True, capture_output=True, env=env)
        if r.returncode != 0 or not out_json.exists():
            die(f"whisper failed:\n{r.stderr.strip()[-1500:]}")
    data = json.loads(out_json.read_text())
    return [{"start": round(s["start"], 2), "end": round(s["end"], 2), "text": s["text"].strip()}
            for s in data.get("segments", []) if s.get("text", "").strip()]


# ---------- transcript output ----------

def write_transcript_txt(segments, chapters, path, chunk_secs=25, chunk_chars=350):
    """Group segments into readable chunks with one timestamp each. Insert chapter headers."""
    chap_iter = sorted(chapters, key=lambda c: c["start"])
    ci = 0
    out = []
    buf, buf_start = [], None
    def flush():
        nonlocal buf, buf_start
        if buf:
            out.append(f"[{fmt_ts(buf_start)}] " + " ".join(buf))
        buf, buf_start = [], None
    for seg in segments:
        while ci < len(chap_iter) and seg["start"] >= chap_iter[ci]["start"]:
            flush()
            out.append(f"\n## [{fmt_ts(chap_iter[ci]['start'])}] {chap_iter[ci]['title']}\n")
            ci += 1
        if buf_start is None:
            buf_start = seg["start"]
        buf.append(seg["text"])
        if seg["end"] - buf_start >= chunk_secs or sum(len(b) for b in buf) >= chunk_chars:
            flush()
    flush()
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="video URL or local file path")
    ap.add_argument("--workdir", help="override work directory")
    ap.add_argument("--whisper-model", default=DEFAULT_WHISPER_MODEL,
                    help=f"whisper model for fallback (default {DEFAULT_WHISPER_MODEL})")
    ap.add_argument("--force-whisper", action="store_true", help="ignore captions, always run whisper")
    ap.add_argument("--max-height", type=int, default=720, help="max video height to download")
    ap.add_argument("--json", action="store_true", help="print meta.json to stdout")
    args = ap.parse_args()

    src = args.input.strip()
    meta = meta_from_url(src) if is_url(src) else meta_from_file(src)

    base = slugify(meta["title"])
    slug = f"{base}-{meta['id']}" if meta.get("id") else base
    workdir = Path(args.workdir).expanduser() if args.workdir else CACHE_ROOT / slug
    workdir.mkdir(parents=True, exist_ok=True)

    # video
    if meta["source"] == "url":
        video = download_video(meta["url"], workdir, args.max_height)
    else:
        video = Path(meta["local_path"])

    # transcript
    segments, source = [], None
    if meta["source"] == "url" and not args.force_whisper:
        vtt = fetch_captions(meta["url"], workdir)
        if vtt:
            segments = parse_vtt(vtt)
            source = "captions-manual" if meta["has_manual_subs"] else "captions-auto"
    if not segments:
        segments = run_whisper(video, workdir, args.whisper_model)
        source = f"whisper-{args.whisper_model}"
    if not segments:
        die("no transcript could be produced")

    (workdir / "transcript.json").write_text(json.dumps(segments, indent=1), encoding="utf-8")
    write_transcript_txt(segments, meta["chapters"], workdir / "transcript.txt")

    words = sum(len(s["text"].split()) for s in segments)
    meta.update({
        "slug": slug,
        "workdir": str(workdir),
        "video_path": str(video),
        "transcript_source": source,
        "transcript_words": words,
        "transcript_txt": str(workdir / "transcript.txt"),
        "transcript_json": str(workdir / "transcript.json"),
    })
    (workdir / "meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")

    if args.json:
        print(json.dumps(meta, indent=1))
        return
    print(f"title:      {meta['title']}")
    print(f"duration:   {fmt_ts(meta['duration'])}")
    print(f"transcript: {source} ({words} words)")
    print(f"chapters:   {len(meta['chapters'])}")
    print(f"workdir:    {workdir}")
    print(f"video:      {video} ({video_codec(video)})")
    print(f"transcript: {workdir / 'transcript.txt'}")
    print(f"meta:       {workdir / 'meta.json'}")


if __name__ == "__main__":
    main()
