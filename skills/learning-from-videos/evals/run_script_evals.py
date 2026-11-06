#!/usr/bin/env python3
"""Deterministic evals for the learning-from-videos scripts. No model calls.

Usage:
  python3 evals/run_script_evals.py [--slug S] [--depth D] [--quick] [--sweep] [--fetch] [--slow]

Checks, per fixture in evals/fixtures/*.json that has a cache dir in ~/.cache/video-notes:
  transcript_integrity   monotonic starts, end >= start, no repeated lines, word count in range
  extraction_<depth>     script runs, runtime under budget, kept <= cap, no Traceback
  coverage_<depth>       fraction of labelled moments with a frame within +-2 s
  max_gap_<depth>        largest gap between frames inside each UI segment
  dedupe_keeps_ui        no change/settled frame was dropped as a near-duplicate
  manifest_shape         rows have chapter, prev, speech windows, pairs; files exist
  resources_index        harvest index lists the expected saved files (if present)
Plus two failure cases (corrupt and missing video) that must exit non-zero with ERROR.

--quick   only transcript_integrity, manifest_shape, resources_index against the existing cache
--sweep   print candidate counts and coverage for a range of change thresholds (calibration)
--fetch   run fetch_video.py for fixtures with no cache
--slow    also run the Whisper path on a local copy of the Postgres clip (about 1 minute)

Exit 1 if any check fails.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
SCRIPTS = SKILL / "scripts"
FIXTURES = HERE / "fixtures"
CACHE = Path(os.environ.get("VIDEO_NOTES_CACHE", "~/.cache/video-notes")).expanduser()
TOLERANCE = 2.0
DEPTHS = ("light", "standard", "deep")

results = []


def report(name, ok, detail=""):
    results.append((name, ok))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f": {detail}" if detail else ""))
    return ok


def run(cmd, timeout=600):
    t0 = time.time()
    r = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
    return r, time.time() - t0


def load_fixtures(slug=None):
    out = []
    for f in sorted(FIXTURES.glob("*.json")):
        fx = json.loads(f.read_text())
        if slug and fx["slug"] != slug:
            continue
        out.append(fx)
    return out


# ---------- checks ----------

def check_transcript(fx, wd):
    tj = wd / "transcript.json"
    meta = json.loads((wd / "meta.json").read_text())
    if not tj.is_file():
        return report(f"{fx['slug'][:24]} transcript_integrity", False, "transcript.json missing")
    segs = json.loads(tj.read_text())
    problems = []
    for a, b in zip(segs, segs[1:]):
        if b["start"] < a["start"]:
            problems.append(f"non-monotonic at {a['start']}")
            break
    if any(s["end"] < s["start"] for s in segs):
        problems.append("end < start")
    if any(a["text"] == b["text"] for a, b in zip(segs, segs[1:])):
        problems.append("repeated consecutive line")
    words = sum(len(s["text"].split()) for s in segs)
    lo, hi = fx["transcript"]["min_words"], fx["transcript"]["max_words"]
    if not (lo <= words <= hi):
        problems.append(f"word count {words} not in [{lo}, {hi}]")
    if meta.get("transcript_source") != fx["transcript"]["source"]:
        problems.append(f"source {meta.get('transcript_source')} != {fx['transcript']['source']}")
    txt = (wd / "transcript.txt").read_text() if (wd / "transcript.txt").is_file() else ""
    if fx["transcript"].get("chapters") and txt.count("\n## [") < fx["transcript"]["chapters"]:
        problems.append("chapter headers missing in transcript.txt")
    return report(f"{fx['slug'][:24]} transcript_integrity", not problems, "; ".join(problems) or f"{words} words")


def coverage(rows, moments, kinds):
    times = [r["time"] for r in rows]
    hits, missed = 0, []
    wanted = [m for m in moments if m["kind"] in kinds]
    for m in wanted:
        if any(abs(t - m["t"]) <= TOLERANCE for t in times):
            hits += 1
        else:
            missed.append(f"{m['t']}s {m['label']}")
    return (hits / len(wanted) if wanted else 1.0), missed, len(wanted)


def max_gap(rows, segments):
    worst = 0.0
    for seg in segments:
        pts = [seg["start"]] + sorted(r["time"] for r in rows if seg["start"] <= r["time"] <= seg["end"]) + [seg["end"]]
        gap = max(b - a for a, b in zip(pts, pts[1:]))
        worst = max(worst, gap)
    return worst


def check_extraction(fx, wd, depth):
    exp = fx["expect"][depth]
    tag = f"{fx['slug'][:24]} {depth}"
    with tempfile.TemporaryDirectory(prefix="vn-eval-") as tmp:
        r, secs = run([sys.executable, str(SCRIPTS / "extract_frames.py"), str(wd), "--depth", depth,
                       "--out-root", tmp, "--json"])
        if r.returncode != 0 or "Traceback" in r.stderr:
            report(f"{tag} extraction", False, (r.stderr or r.stdout).strip()[-300:])
            return
        summary = json.loads(r.stdout)
        rows = json.loads((Path(tmp) / "frames" / "manifest.json").read_text())
        ok = summary["runtime_s"] <= exp["runtime_s"] and summary["kept"] <= exp["max_frames"]
        report(f"{tag} extraction", ok,
               f"kept={summary['kept']} (cap {exp['max_frames']}) runtime={summary['runtime_s']}s "
               f"(budget {exp['runtime_s']}s) by_reason={summary['by_reason']}")

        ui_kinds = ("ui", "ui-small") if depth == "deep" else ("ui",)
        ui_cov, ui_missed, n_ui = coverage(rows, fx["moments"], ui_kinds)
        cut_cov, cut_missed, n_cut = coverage(rows, fx["moments"], ("cut",))
        report(f"{tag} coverage", ui_cov >= exp["ui_coverage"] and cut_cov >= exp["cut_coverage"],
               f"ui {ui_cov:.2f} of {n_ui} (need {exp['ui_coverage']}) cut {cut_cov:.2f} of {n_cut} "
               f"(need {exp['cut_coverage']})" + (f"; missed: {', '.join(ui_missed + cut_missed)}" if ui_missed + cut_missed else ""))

        gap = max_gap(rows, fx.get("ui_segments", []))
        report(f"{tag} max_gap", gap <= exp["max_gap_ui"], f"{gap:.0f}s (limit {exp['max_gap_ui']}s)")

        dropped = summary.get("dropped_by_reason", {})
        report(f"{tag} dedupe_keeps_ui", not (dropped.get("change") or dropped.get("settled")), f"dropped={dropped}")
        check_manifest_rows(tag, rows, depth)


def check_manifest_rows(tag, rows, depth):
    problems = []
    for i, r in enumerate(rows):
        if "chapter" not in r or "said_before" not in r or "said_after" not in r:
            problems.append(f"row {r.get('index')} missing speech/chapter fields")
            break
        if i > 0 and r.get("prev_index") is None:
            problems.append(f"row {r['index']} has no prev")
            break
        if not Path(r["file"]).is_file():
            problems.append(f"row {r['index']} file missing")
            break
        if depth != "light" and r["reason"] in ("change", "settled") and i > 0:
            if not r.get("pair") or not Path(r["pair"]).is_file():
                problems.append(f"row {r['index']} ({r['reason']}) has no pair image")
                break
    report(f"{tag} manifest_shape", not problems, "; ".join(problems) or f"{len(rows)} rows")


def check_existing_manifest(fx, wd):
    mj = wd / "frames" / "manifest.json"
    if not mj.is_file():
        return report(f"{fx['slug'][:24]} manifest_shape", False, "no frames/manifest.json in cache; run the extractor")
    rows = json.loads(mj.read_text())
    depth = "standard"
    md = (wd / "frames" / "manifest.md").read_text() if (wd / "frames" / "manifest.md").is_file() else ""
    if "depth=light" in md:
        depth = "light"
    check_manifest_rows(f"{fx['slug'][:24]} cache", rows, depth)


def check_resources(fx, wd):
    idx = wd / "resources" / "index.json"
    expected = fx.get("resources_expected") or []
    if not expected:
        return
    if not idx.is_file():
        return report(f"{fx['slug'][:24]} resources_index", False, "resources/index.json missing; run harvest_links.py")
    saved = {e.get("saved") for e in json.loads(idx.read_text())}
    missing = [e for e in expected if e not in saved or not (wd / "resources" / e).is_file()]
    report(f"{fx['slug'][:24]} resources_index", not missing, f"missing {missing}" if missing else f"{len(expected)} expected files present")


def check_failures():
    with tempfile.TemporaryDirectory(prefix="vn-eval-fail-") as tmp:
        tmp = Path(tmp)
        bad = tmp / "video.mp4"
        bad.write_bytes(os.urandom(4096))
        (tmp / "meta.json").write_text(json.dumps({"title": "corrupt", "duration": 10, "video_path": str(bad), "chapters": []}))
        (tmp / "transcript.json").write_text("[]")
        r, _ = run([sys.executable, str(SCRIPTS / "extract_frames.py"), str(tmp), "--depth", "standard", "--out-root", str(tmp / "out")])
        ok = r.returncode != 0 and "ERROR" in r.stderr and "Traceback" not in r.stderr and "video.mp4" in r.stderr
        report("failure_corrupt_video", ok, r.stderr.strip()[-160:])

        (tmp / "meta.json").write_text(json.dumps({"title": "missing", "duration": 10, "video_path": str(tmp / "nope.mp4"), "chapters": []}))
        r, _ = run([sys.executable, str(SCRIPTS / "extract_frames.py"), str(tmp), "--depth", "standard", "--out-root", str(tmp / "out")])
        ok = r.returncode != 0 and "ERROR" in r.stderr and "Traceback" not in r.stderr and "nope.mp4" in r.stderr
        report("failure_missing_video", ok, r.stderr.strip()[-160:])


def check_slow_whisper():
    src = CACHE / "postgresql-in-100-seconds-n2Fluyr3lbc" / "video.mp4"
    if not src.is_file():
        return report("slow_whisper_local_file", False, "Postgres clip not in cache")
    with tempfile.TemporaryDirectory(prefix="vn-eval-whisper-") as tmp:
        clip = Path(tmp) / "local-clip.mp4"
        shutil.copy(src, clip)
        r, secs = run([sys.executable, str(SCRIPTS / "fetch_video.py"), str(clip), "--whisper-model", "base",
                       "--workdir", str(Path(tmp) / "wd")], timeout=1200)
        txt = (Path(tmp) / "wd" / "transcript.txt")
        text = txt.read_text() if txt.is_file() else ""
        words = len(text.split())
        ok = r.returncode == 0 and words > 400 and "1986" in text and "Berkeley" in text
        detail = f"{secs:.0f}s exit={r.returncode} file={txt.is_file()} words={words}"
        if not ok:
            detail += "; stdout: " + r.stdout.strip()[-200:] + "; stderr: " + r.stderr.strip()[-200:]
        report("slow_whisper_local_file", ok, detail)


def sweep(fx, wd):
    sys.path.insert(0, str(SCRIPTS))
    import extract_frames as ef
    meta = json.loads((wd / "meta.json").read_text())
    thumbs = ef.decode_thumbs(Path(meta["video_path"]), 1)
    mask = ef.busy_mask(thumbs, 1)
    d = ef.diff_series(thumbs, 1, mask)
    duration = float(meta.get("duration") or len(thumbs))
    print(f"\n{fx['slug']}: busy pixels {mask.mean():.3f}")
    print(f"{'thr':>6} {'cands':>5} {'change':>6} {'settled':>7} {'cut':>4} {'ui-cov':>7} {'cut-cov':>7} {'gap':>5}")
    for thr in (0.008, 0.012, 0.02, 0.03, 0.05, 0.08, 0.15):
        cfg = dict(change_thr=thr, run_step=4, min_spacing=1.0, cap=10000)
        cands = ef.select_candidates(d, thumbs, 1, duration, cfg, mask)
        rows = [{"time": c["t"]} for c in cands]
        by = {}
        for c in cands:
            by[c["reason"]] = by.get(c["reason"], 0) + 1
        ui_cov, _, _ = coverage(rows, fx["moments"], ("ui", "ui-small"))
        cut_cov, _, _ = coverage(rows, fx["moments"], ("cut",))
        gap = max_gap(rows, fx.get("ui_segments", []))
        print(f"{thr:>6} {len(cands):>5} {by.get('change', 0):>6} {by.get('settled', 0):>7} "
              f"{by.get('cut', 0) + by.get('cut-fast', 0):>4} {ui_cov:>7.2f} {cut_cov:>7.2f} {gap:>5.0f}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--slug")
    ap.add_argument("--depth", choices=DEPTHS)
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--slow", action="store_true")
    args = ap.parse_args()

    fixtures = load_fixtures(args.slug)
    if not fixtures:
        sys.exit("no fixtures found")
    for fx in fixtures:
        wd = CACHE / fx["slug"]
        if not (wd / "meta.json").is_file():
            if args.fetch:
                print(f"fetching {fx['url']} ...")
                run([sys.executable, str(SCRIPTS / "fetch_video.py"), fx["url"]], timeout=1800)
            if not (wd / "meta.json").is_file():
                report(f"{fx['slug'][:24]} cache", False, f"{wd} not fetched (use --fetch)")
                continue
        if args.sweep:
            sweep(fx, wd)
            continue
        check_transcript(fx, wd)
        check_resources(fx, wd)
        if args.quick:
            check_existing_manifest(fx, wd)
            continue
        for depth in ([args.depth] if args.depth else DEPTHS):
            check_extraction(fx, wd, depth)
    if not args.sweep and not args.quick:
        check_failures()
    if args.slow:
        check_slow_whisper()
    if args.sweep:
        return
    failed = [n for n, ok in results if not ok]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed")
    if failed:
        print("failed:", ", ".join(failed))
        sys.exit(1)


if __name__ == "__main__":
    main()
