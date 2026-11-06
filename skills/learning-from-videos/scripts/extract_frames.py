#!/usr/bin/env python3
"""Extract the frames worth looking at from a fetched video, driven by screen changes.

Usage:
  extract_frames.py WORKDIR --depth light|standard|deep [options]

Options:
  --cap N                 override the frame cap for this depth
  --fps 1|2               thumbnail sampling rate (default 1; 2 halves timestamp error)
  --change-threshold F    override the depth's change threshold (fraction of pixels)
  --cut-threshold F       override CUT_FRAC
  --min-spacing S         override the depth's minimum spacing between frames (seconds)
  --out-root DIR          write frames/, sheets/, pairs/ under DIR instead of WORKDIR
  --no-sheets             skip contact sheets
  --no-pairs              skip before/after pair images
  --dry-run               print candidates and counts, write only diff_series.json
  --json                  print a JSON summary instead of text

Reads WORKDIR/meta.json and WORKDIR/transcript.json (made by fetch_video.py).
Writes (under --out-root, default WORKDIR):
  frames/f_NNN_<timestamp>.jpg     full-size frames (max 1280 wide)
  frames/manifest.md, .json        one row per frame: why, delta, prev, chapter, speech
  frames/diff_series.json          per-second changed fraction, for evals and debugging
  sheets/sheet_NN.jpg              contact sheets, 6 frames each, in order
  pairs/p_NNN.jpg                  previous frame | this frame, for UI changes

How frames are chosen. One ffmpeg pass decodes small grayscale thumbnails. For each
second, changed_frac is the fraction of pixels that moved by more than PIXEL_DELTA.
A big jump is a cut. A run of small changes on an otherwise still screen is UI activity
(typing, a click, a menu): keep its first frame, samples inside it, and the settled state
after it. A run with a high median is camera or B-roll motion: keep one frame and sparse
samples. A coarse clock fills long quiet stretches.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

THUMB_W, THUMB_H = 160, 90
PIXEL_DELTA = 24        # gray delta that counts a pixel as changed; measured static floor is 0.005 of pixels
CUT_FRAC = 0.60         # cuts measured 0.62..1.00; the largest UI panel load measured 0.59
MOTION_MEDIAN = 0.20    # a run whose median changed_frac is at least this is camera or B-roll motion
MOTION_STEP = 15        # seconds between samples inside a motion run
SAFETY_INTERVAL = 60    # coarse safety net, all depths
SAFETY_CLEARANCE = 20   # add a safety frame only when no other candidate is within this many seconds
CUT_CLUSTER = 3.0       # a cut less than this after the previous cut is a montage cut, dropped first at cap
GRAB_OFFSET = 0.3       # grab slightly after the thumbnail time to guard seek rounding
SIMILARITY_DROP = 6.0   # mean pixel diff (0-255) below which a non-UI frame is a near-duplicate
SPEECH_SPAN = 4         # seconds of transcript shown before and after each frame
BUSY_FRAC = 0.4         # a pixel that changes in more than this share of seconds (a webcam overlay, an
                        # animated element) is ignored by the change signal and the boxes

DEPTHS = {
    # change_thr starts a UI run; run_step samples inside a run (None = no samples)
    "light":    dict(change_thr=0.15,  run_step=None, min_spacing=3.0, cap=25),
    "standard": dict(change_thr=0.03,  run_step=8,    min_spacing=2.0, cap=100),
    "deep":     dict(change_thr=0.012, run_step=4,    min_spacing=1.0, cap=200),
}
PRIORITY = {"change": 0, "settled": 1, "cut": 2, "motion": 3, "cut-fast": 4,
            "sample": 5, "interval": 6, "start": 7}
UI_REASONS = {"change", "settled"}
DEDUPE_REASONS = {"cut", "cut-fast", "motion", "sample", "interval", "start"}

_FF = {}


def ffbin(name):
    """Pick a working ffmpeg/ffprobe. Prefer a Homebrew build over an older one earlier on
    PATH (miniconda ships 4.x), but only if it actually runs."""
    if name in _FF:
        return _FF[name]
    cands = [os.environ.get("VIDEO_NOTES_FFMPEG_DIR", ""), "/opt/homebrew/bin", "/usr/local/bin"]
    paths = [os.path.join(c, name) for c in cands if c and os.path.isfile(os.path.join(c, name))]
    on_path = shutil.which(name)
    if on_path:
        paths.append(on_path)
    for p in paths:
        try:
            if subprocess.run([p, "-version"], capture_output=True, timeout=10).returncode == 0:
                _FF[name] = p
                return p
        except Exception:
            continue
    sys.exit(f"ERROR: no working '{name}' found. Install one with: brew install ffmpeg")


def fmt_ts(sec):
    sec = int(sec)
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def file_ts(sec):
    return fmt_ts(sec).replace(":", "-")


def thin(items, n):
    """Keep n items spread evenly across the list."""
    if n <= 0:
        return []
    if len(items) <= n:
        return list(items)
    step = len(items) / n
    return [items[int(i * step)] for i in range(n)]


# ---------- signal ----------

def decode_thumbs(video, fps):
    """One ffmpeg pass to small grayscale thumbnails. Returns uint8 array (n, H, W)."""
    cmd = [ffbin("ffmpeg"), "-hide_banner", "-loglevel", "error", "-i", str(video),
           "-vf", f"fps={fps},scale={THUMB_W}:{THUMB_H}", "-pix_fmt", "gray",
           "-f", "rawvideo", "-"]
    r = subprocess.run(cmd, capture_output=True)
    err = r.stderr.decode(errors="replace")
    m = re.search(r"Decoder \(codec (\w+)\) not found", err)
    if m:
        sys.exit(f"ERROR: this ffmpeg cannot decode {m.group(1)} in {video}. Delete video.mp4 "
                 f"in the work directory and rerun fetch_video.py (it prefers H.264), or "
                 f"install a newer ffmpeg (brew install ffmpeg). See references/troubleshooting.md.")
    n = len(r.stdout) // (THUMB_W * THUMB_H)
    if r.returncode != 0 or n < 2:
        tail = err.strip()[-400:] or "no frames produced"
        sys.exit(f"ERROR: could not decode {video}: {tail}")
    return np.frombuffer(r.stdout, dtype=np.uint8)[: n * THUMB_W * THUMB_H].reshape(n, THUMB_H, THUMB_W)


def busy_mask(thumbs, lag):
    """Pixels that change in most seconds: a webcam overlay or an animated element. They are
    excluded from the change signal. If they cover most of the frame (a talking-head video),
    the mask is disabled because there is nothing still to compare."""
    step = np.abs(thumbs[lag:].astype(np.int16) - thumbs[:-lag].astype(np.int16)) > PIXEL_DELTA
    busy = step.mean(axis=0) > BUSY_FRAC
    if busy.mean() > 0.6:
        return np.zeros_like(busy)
    return busy


def changed_frac(a, b, mask=None):
    diff = np.abs(a.astype(np.int16) - b.astype(np.int16)) > PIXEL_DELTA
    if mask is None:
        return float(diff.mean())
    keep = ~mask
    return float(diff[keep].sum() / max(1, keep.sum()))


def diff_series(thumbs, lag, mask=None):
    """changed_frac between thumb k and thumb k+lag, so entry i describes the change that
    arrives at thumb index i+lag."""
    a = thumbs[lag:].astype(np.int16)
    b = thumbs[:-lag].astype(np.int16)
    diff = np.abs(a - b) > PIXEL_DELTA
    if mask is None:
        return diff.mean(axis=(1, 2)).astype(np.float32)
    keep = ~mask
    return (diff[:, keep].sum(axis=1) / max(1, keep.sum())).astype(np.float32)


def changed_bbox(prev_thumb, cur_thumb, mask=None, pad=4):
    """Bounding box of changed pixels in thumbnail coordinates, or None."""
    diff = np.abs(prev_thumb.astype(np.int16) - cur_thumb.astype(np.int16)) > PIXEL_DELTA
    mask = diff if mask is None else (diff & ~mask)
    rows = np.where(mask.any(axis=1))[0]
    cols = np.where(mask.any(axis=0))[0]
    if len(rows) == 0 or len(cols) == 0:
        return None
    return (max(0, int(cols[0]) - pad), max(0, int(rows[0]) - pad),
            min(THUMB_W, int(cols[-1]) + pad + 1), min(THUMB_H, int(rows[-1]) + pad + 1))


# ---------- selection ----------

def select_candidates(d, thumbs, fps, duration, cfg, mask=None):
    """State machine over the change signal. Returns candidates sorted by time."""
    lag = fps
    n = len(d)
    thr = cfg["change_thr"]
    cands = [dict(t=0.5, reason="start", signal=0.0, run=None)]

    def tt(i):
        return (i + lag) / fps

    def thumb_at(t):
        return thumbs[min(int(round(t * fps)), len(thumbs) - 1)]

    i, run_id, last_cut_t = 0, 0, -99.0
    while i < n:
        v = float(d[i])
        t = tt(i)
        if v >= CUT_FRAC:
            reason = "cut-fast" if t - last_cut_t < CUT_CLUSTER else "cut"
            cands.append(dict(t=t + GRAB_OFFSET, reason=reason, signal=v, run=None))
            last_cut_t = t
            i += 1
            continue
        if v < thr:
            i += 1
            continue
        j = i
        while j < n and thr <= d[j] < CUT_FRAC:
            j += 1
        seg = d[i:j]
        run_id += 1
        t0, t1 = tt(i), tt(j - 1)
        med = float(np.median(seg))
        # Motion is sustained. A one- or two-second burst, however large, is a change
        # (a panel appearing, a prompt box filling) and must survive the cap.
        if med >= MOTION_MEDIAN and t1 - t0 >= 2.0:
            cands.append(dict(t=t0 + GRAB_OFFSET, reason="motion", signal=med, run=run_id))
            step = MOTION_STEP
        else:
            cands.append(dict(t=t0 + GRAB_OFFSET, reason="change", signal=float(seg[0]), run=run_id))
            step = cfg["run_step"]
        if step is not None:
            s = t0 + step
            while s <= t1:
                cands.append(dict(t=s, reason="sample", signal=med, run=run_id))
                s += step
        # The screen at t1 already holds the finished state (the next second changed by
        # less than the threshold), so grab the settled frame shortly after t1.
        if t1 - t0 >= 1.0:
            ts = t1 + 0.5
            if ts < duration - 0.5:
                net = changed_frac(thumb_at(t0 - 1.0 / fps), thumb_at(t1 + 1.0), mask)
                cands.append(dict(t=ts + GRAB_OFFSET, reason="settled", signal=net, run=run_id))
        i = j

    for s in range(SAFETY_INTERVAL, int(duration), SAFETY_INTERVAL):
        if not any(abs(c["t"] - s) <= SAFETY_CLEARANCE for c in cands):
            cands.append(dict(t=float(s), reason="interval", signal=0.0, run=None))

    cands = [c for c in cands if 0 <= c["t"] < max(duration - 0.2, 1.0)]
    cands.sort(key=lambda c: c["t"])

    merged = []
    for c in cands:
        if merged and c["t"] - merged[-1]["t"] < cfg["min_spacing"]:
            if PRIORITY[c["reason"]] < PRIORITY[merged[-1]["reason"]]:
                merged[-1] = c
        else:
            merged.append(c)
    return merged


def cap_score(c):
    """Higher is more worth keeping. Settled frames carry the end state of an action, so
    they rank above the small changes that led to it. Cuts score by their size."""
    if c["reason"] == "start":
        return float("inf")
    if c["reason"] == "settled":
        return 0.5 + c["signal"]
    return c["signal"]


def apply_cap(cands, cfg):
    cap = cfg["cap"]
    for cls in ("interval", "cut-fast", "sample", "motion"):
        if len(cands) <= cap:
            return cands
        cands = [c for c in cands if c["reason"] != cls]
    if len(cands) <= cap:
        return cands
    ranked = sorted(cands, key=cap_score, reverse=True)[:cap]
    ranked.sort(key=lambda c: c["t"])
    return ranked


# ---------- frames ----------

def grab(video, t, out):
    cmd = [ffbin("ffmpeg"), "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{t:.2f}",
           "-i", str(video), "-frames:v", "1", "-vf", "scale='min(1280,iw)':-2",
           "-q:v", "4", str(out)]
    r = subprocess.run(cmd, text=True, capture_output=True)
    if not out.exists():
        print(f"warning: no frame at {t:.1f}s: {r.stderr.strip()[-200:]}", file=sys.stderr)
    return out.exists()


def grab_all(video, cands, frame_dir, workers=8):
    jobs = [(k, c) for k, c in enumerate(cands)]

    def one(job):
        k, c = job
        out = frame_dir / f"tmp_{k:05d}.jpg"
        return (k, c, out) if grab(video, c["t"], out) else None

    with ThreadPoolExecutor(max_workers=workers) as ex:
        results = [r for r in ex.map(one, jobs) if r]
    results.sort(key=lambda r: r[0])
    return [dict(c, tmp=out) for _, c, out in results]


def near_duplicate(prev_path, cur_path):
    try:
        from PIL import Image, ImageChops, ImageStat
        a = Image.open(prev_path).convert("L").resize((32, 18))
        b = Image.open(cur_path).convert("L").resize((32, 18))
        return ImageStat.Stat(ImageChops.difference(a, b)).mean[0] < SIMILARITY_DROP
    except Exception:
        return False


def dedupe(frames):
    """Drop near-duplicate non-UI frames. UI-change frames are never dropped: they were
    selected because they differ by a small amount."""
    kept, dropped, prev = [], {}, None
    for fr in frames:
        if prev is not None and fr["reason"] in DEDUPE_REASONS and near_duplicate(prev, fr["tmp"]):
            fr["tmp"].unlink(missing_ok=True)
            dropped[fr["reason"]] = dropped.get(fr["reason"], 0) + 1
            continue
        kept.append(fr)
        prev = fr["tmp"]
    return kept, dropped


def finalize_names(frames, frame_dir):
    for n, fr in enumerate(frames, 1):
        out = frame_dir / f"f_{n:03d}_{file_ts(fr['t'])}.jpg"
        fr["tmp"].rename(out)
        fr["index"] = n
        fr["file"] = str(out)
        fr["time"] = round(fr["t"], 2)
        fr["timestamp"] = fmt_ts(fr["t"])
        del fr["tmp"]
    return frames


# ---------- annotation ----------

def chapter_for(chapters, t):
    name = ""
    for c in sorted(chapters, key=lambda c: c.get("start", 0)):
        if t >= c.get("start", 0):
            name = c.get("title", "")
    return name


def speech_window(segments, t, span=SPEECH_SPAN):
    before = " ".join(s["text"] for s in segments if s["end"] >= t - span and s["start"] <= t).strip()
    after = " ".join(s["text"] for s in segments if t < s["start"] <= t + span).strip()
    return before, after


def region_name(bbox_thumb):
    if not bbox_thumb:
        return ""
    area = (bbox_thumb[2] - bbox_thumb[0]) * (bbox_thumb[3] - bbox_thumb[1]) / (THUMB_W * THUMB_H)
    if area > 0.6:
        return "most of the screen"
    cx = (bbox_thumb[0] + bbox_thumb[2]) / 2 / THUMB_W
    cy = (bbox_thumb[1] + bbox_thumb[3]) / 2 / THUMB_H
    col = "left" if cx < 1 / 3 else "right" if cx > 2 / 3 else "centre"
    row = "upper" if cy < 1 / 3 else "lower" if cy > 2 / 3 else "middle"
    if row == "middle" and col == "centre":
        return "centre"
    return f"{row}-{col}" if col != "centre" else f"{row}-centre"


def frame_size(path):
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.size
    except Exception:
        return (1280, 720)


def annotate(frames, segments, chapters, thumbs, fps, mask=None):
    prev = None
    for fr in frames:
        t = fr["t"]
        fr["chapter"] = chapter_for(chapters, t)
        fr["said_before"], fr["said_after"] = speech_window(segments, t)
        k = min(int(round(t * fps)), len(thumbs) - 1)
        fr["thumb_index"] = k
        if prev is None:
            fr.update(prev_index=None, prev_time=None, delta=None, bbox=None, region="")
        else:
            pk = prev["thumb_index"]
            fr["prev_index"] = prev["index"]
            fr["prev_time"] = prev["t"]
            fr["delta"] = round(changed_frac(thumbs[pk], thumbs[k], mask), 4)
            bb = changed_bbox(thumbs[pk], thumbs[k], mask)
            fr["region"] = region_name(bb)
            if bb:
                w, h = frame_size(fr["file"])
                sx, sy = w / THUMB_W, h / THUMB_H
                fr["bbox"] = [int(bb[0] * sx), int(bb[1] * sy), int(bb[2] * sx), int(bb[3] * sy)]
            else:
                fr["bbox"] = None
        prev = fr
    return frames


# ---------- images ----------

def _font(size):
    from PIL import ImageFont
    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()


def _draw_box(draw, bbox, scale, offset=(0, 0), width=3):
    if not bbox:
        return
    x0, y0, x1, y1 = bbox
    draw.rectangle([offset[0] + x0 * scale, offset[1] + y0 * scale,
                    offset[0] + x1 * scale, offset[1] + y1 * scale],
                   outline=(255, 230, 0), width=width)


def make_sheets(frames, sheet_dir, per_sheet=6, tile=(640, 360)):
    try:
        from PIL import Image, ImageDraw
    except Exception:
        return []
    font = _font(22)
    sheet_dir.mkdir(parents=True, exist_ok=True)
    for old in sheet_dir.glob("sheet_*.jpg"):
        old.unlink()
    cols, rows = 2, 3
    sheets = []
    for n in range(0, len(frames), per_sheet):
        batch = frames[n:n + per_sheet]
        sheet = Image.new("RGB", (cols * tile[0], rows * tile[1]), (20, 20, 20))
        draw = ImageDraw.Draw(sheet)
        for k, fr in enumerate(batch):
            try:
                img = Image.open(fr["file"]).convert("RGB")
            except Exception:
                continue
            fw, fh = img.size
            img.thumbnail(tile)
            x = (k % cols) * tile[0]
            y = (k // cols) * tile[1]
            sheet.paste(img, (x, y))
            if fr["reason"] in UI_REASONS and fr.get("bbox"):
                _draw_box(draw, fr["bbox"], img.size[0] / fw, offset=(x, y))
            label = f"#{fr['index']}  {fr['timestamp']}  {fr['reason']}"
            if fr.get("delta") is not None and fr["reason"] in UI_REASONS:
                label += f"  chg {fr['delta'] * 100:.0f}% vs #{fr['prev_index']}"
            draw.rectangle([x, y, x + 12 + len(label) * 12, y + 32], fill=(0, 0, 0))
            draw.text((x + 6, y + 4), label, fill=(255, 230, 0), font=font)
        out = sheet_dir / f"sheet_{n // per_sheet + 1:02d}.jpg"
        sheet.save(out, quality=85)
        sheets.append(str(out))
    return sheets


def make_pairs(frames, pair_dir, tile=(640, 360), strip=32):
    try:
        from PIL import Image, ImageDraw
    except Exception:
        return 0
    font = _font(20)
    pair_dir.mkdir(parents=True, exist_ok=True)
    for old in pair_dir.glob("p_*.jpg"):
        old.unlink()
    by_index = {fr["index"]: fr for fr in frames}
    count = 0
    for fr in frames:
        if fr["reason"] not in UI_REASONS or fr.get("prev_index") is None:
            continue
        prev = by_index.get(fr["prev_index"])
        if not prev:
            continue
        try:
            a = Image.open(prev["file"]).convert("RGB")
            b = Image.open(fr["file"]).convert("RGB")
        except Exception:
            continue
        bw, bh = b.size
        a.thumbnail(tile)
        b.thumbnail(tile)
        canvas = Image.new("RGB", (2 * tile[0], tile[1] + strip), (20, 20, 20))
        canvas.paste(a, (0, strip))
        canvas.paste(b, (tile[0], strip))
        draw = ImageDraw.Draw(canvas)
        if fr.get("bbox"):
            _draw_box(draw, fr["bbox"], b.size[0] / bw, offset=(tile[0], strip))
        delta = f"chg {fr['delta'] * 100:.0f}%" if fr.get("delta") is not None else ""
        label = (f"#{fr['index']:03d} {fr['timestamp']} {fr['chapter']} | {delta} {fr['region']} | "
                 f"prev #{prev['index']:03d} {prev['timestamp']}   (left: before, right: after)")
        draw.text((6, 6), label[:150], fill=(255, 230, 0), font=font)
        out = pair_dir / f"p_{fr['index']:03d}.jpg"
        canvas.save(out, quality=85)
        fr["pair"] = str(out)
        count += 1
    return count


# ---------- output ----------

def clean_frame_dir(frame_dir):
    frame_dir.mkdir(parents=True, exist_ok=True)
    for f in frame_dir.iterdir():
        if f.is_file() and (f.suffix == ".jpg" or f.name.startswith("manifest")):
            f.unlink()


def write_manifest(frames, frame_dir, meta, depth, cfg, dropped, sheets, pair_count):
    rows = []
    for fr in frames:
        rows.append({k: fr.get(k) for k in (
            "index", "time", "timestamp", "reason", "signal", "delta", "region", "run", "chapter",
            "file", "pair", "prev_index", "prev_time", "bbox", "said_before", "said_after")})
    (frame_dir / "manifest.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")

    def cell(s, n=160):
        s = (s or "").replace("|", "/").replace("\n", " ")
        return s if len(s) <= n else s[: n - 3] + "..."

    lines = [f"# Frames for: {meta.get('title', '')}", "",
             f"depth={depth} cap={cfg['cap']} change_thr={cfg['change_thr']} kept={len(frames)} "
             f"near-duplicates-dropped={sum(dropped.values())}", "",
             "why: cut = new shot or slide; change = something changed on a mostly still screen "
             "(a click, a menu, typed text); settled = the end state after typing or dragging; "
             "sample = periodic frame inside a long run; motion = camera or B-roll movement; "
             "interval = safety net; start = first frame. Δ = share of the screen that changed "
             "since the previous kept frame, and where.", "",
             "| # | time | chapter | why | Δ | prev | file | pair | said before (-4 s) | said after (+4 s) |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for fr in frames:
        delta = "" if fr.get("delta") is None else f"{fr['delta'] * 100:.0f}% {fr.get('region', '')}".strip()
        prev = "" if fr.get("prev_index") is None else f"#{fr['prev_index']} {fmt_ts(fr['prev_time'])}"
        pair = Path(fr["pair"]).name if fr.get("pair") else ""
        lines.append(f"| {fr['index']} | {fr['timestamp']} | {cell(fr['chapter'], 40)} | {fr['reason']} | "
                     f"{delta} | {prev} | {Path(fr['file']).name} | {pair} | "
                     f"{cell(fr['said_before'])} | {cell(fr['said_after'])} |")
    if sheets:
        lines += ["", "## Contact sheets (6 frames each, in order)", ""] + [f"- {s}" for s in sheets]
    if pair_count:
        lines += ["", f"## Pair images: {pair_count} in {Path(frames[0]['file']).parent.parent / 'pairs'}"]
    (frame_dir / "manifest.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("workdir")
    ap.add_argument("--depth", choices=DEPTHS, default="standard")
    ap.add_argument("--cap", type=int)
    ap.add_argument("--fps", type=int, choices=(1, 2), default=1)
    ap.add_argument("--change-threshold", type=float)
    ap.add_argument("--cut-threshold", type=float)
    ap.add_argument("--min-spacing", type=float)
    ap.add_argument("--out-root")
    ap.add_argument("--no-sheets", action="store_true")
    ap.add_argument("--no-pairs", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    t_start = time.time()
    wd = Path(args.workdir).expanduser()
    if not (wd / "meta.json").is_file():
        sys.exit(f"ERROR: {wd / 'meta.json'} not found. Run fetch_video.py first.")
    meta = json.loads((wd / "meta.json").read_text())
    segments = json.loads((wd / "transcript.json").read_text()) if (wd / "transcript.json").is_file() else []
    video = Path(meta["video_path"])
    if not video.is_file():
        sys.exit(f"ERROR: video file not found: {video}")

    cfg = dict(DEPTHS[args.depth])
    if args.cap:
        cfg["cap"] = args.cap
    if args.change_threshold is not None:
        cfg["change_thr"] = args.change_threshold
    if args.min_spacing is not None:
        cfg["min_spacing"] = args.min_spacing
    global CUT_FRAC
    if args.cut_threshold is not None:
        CUT_FRAC = args.cut_threshold

    out_root = Path(args.out_root).expanduser() if args.out_root else wd
    frame_dir, sheet_dir, pair_dir = out_root / "frames", out_root / "sheets", out_root / "pairs"
    frame_dir.mkdir(parents=True, exist_ok=True)

    thumbs = decode_thumbs(video, args.fps)
    thumb_s = time.time() - t_start
    duration = float(meta.get("duration") or 0) or len(thumbs) / args.fps
    mask = busy_mask(thumbs, args.fps)
    d = diff_series(thumbs, args.fps, mask)
    (frame_dir / "diff_series.json").write_text(json.dumps(
        {"fps": args.fps, "lag": args.fps, "busy_pixels": round(float(mask.mean()), 4),
         "changed_frac": [round(float(x), 4) for x in d]}), encoding="utf-8")

    cands = apply_cap(select_candidates(d, thumbs, args.fps, duration, cfg, mask), cfg)
    by_reason = {}
    for c in cands:
        by_reason[c["reason"]] = by_reason.get(c["reason"], 0) + 1

    if args.dry_run:
        print(f"depth={args.depth} cap={cfg['cap']} change_thr={cfg['change_thr']} thumbs={len(thumbs)} "
              f"duration={fmt_ts(duration)} thumb_s={thumb_s:.1f} busy_pixels={mask.mean():.3f}")
        print("candidates:", len(cands), by_reason)
        for c in cands:
            print(f"  {fmt_ts(c['t'])}  {c['reason']:9s} signal={c['signal']:.3f}" + (f" run={c['run']}" if c['run'] else ""))
        return

    clean_frame_dir(frame_dir)
    frames = grab_all(video, cands, frame_dir)
    frames, dropped = dedupe(frames)
    frames = finalize_names(frames, frame_dir)
    frames = annotate(frames, segments, meta.get("chapters") or [], thumbs, args.fps, mask)
    sheets = [] if args.no_sheets else make_sheets(frames, sheet_dir)
    pair_count = 0 if (args.no_pairs or args.depth == "light") else make_pairs(frames, pair_dir)
    write_manifest(frames, frame_dir, meta, args.depth, cfg, dropped, sheets, pair_count)

    kept_by = {}
    for fr in frames:
        kept_by[fr["reason"]] = kept_by.get(fr["reason"], 0) + 1
    runtime = time.time() - t_start
    summary = {"depth": args.depth, "cap": cfg["cap"], "fps": args.fps, "change_thr": cfg["change_thr"],
               "candidates": len(cands), "kept": len(frames), "by_reason": kept_by,
               "dropped_by_reason": dropped, "runtime_s": round(runtime, 1), "thumb_s": round(thumb_s, 1),
               "frames_dir": str(frame_dir), "manifest": str(frame_dir / "manifest.md"),
               "sheets": len(sheets), "pairs": pair_count}
    if args.json:
        print(json.dumps(summary, indent=1))
        return
    print(f"depth:      {args.depth} (cap {cfg['cap']}, change threshold {cfg['change_thr']})")
    print(f"candidates: {len(cands)}  kept: {len(frames)}  {kept_by}  dropped: {dropped or 0}")
    print(f"runtime:    {runtime:.1f}s (thumbnails {thumb_s:.1f}s)")
    print(f"frames:     {frame_dir}")
    print(f"manifest:   {frame_dir / 'manifest.md'}")
    if sheets:
        print(f"sheets:     {len(sheets)} in {sheet_dir}")
    if pair_count:
        print(f"pairs:      {pair_count} in {pair_dir}")


if __name__ == "__main__":
    main()
