#!/usr/bin/env python3
"""Score a notes file produced by the learning-from-videos skill against a fixture.

Usage:
  python3 evals/check_notes.py NOTES.md --fixture SLUG [--workdir DIR]

Checks:
  facts        every string in notes_must_contain is present (case and whitespace folded); pass at 0.8
  avoid        strings in notes_should_not_contain are absent (warning only)
  timestamps   at least notes_min_timestamps [mm:ss] markers
  sections     the template headings are present
  frame_refs   every cited frames/f_NNN_*.jpg exists in the work directory
  resource_refs every cited resources/<file> exists in the work directory

Exit 1 on any failed check (warnings do not fail).
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE = Path(os.environ.get("VIDEO_NOTES_CACHE", "~/.cache/video-notes")).expanduser()
SECTIONS = ["## TL;DR", "## Key learnings", "## What was only on screen", "## Code, commands, and config seen",
            "## Architecture, diagrams, and UI", "## Resources mentioned", "## Caveats and open questions", "## Timeline"]


def fold(s):
    return re.sub(r"\s+", " ", s).lower()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("notes")
    ap.add_argument("--fixture", required=True, help="fixture slug (file name without .json)")
    ap.add_argument("--workdir")
    args = ap.parse_args()

    fx = json.loads((HERE / "fixtures" / f"{args.fixture}.json").read_text())
    notes = Path(args.notes).read_text(encoding="utf-8")
    wd = Path(args.workdir).expanduser() if args.workdir else CACHE / fx["slug"]
    folded = fold(notes)
    failed = False

    must = fx.get("notes_must_contain", [])
    hits = [f for f in must if fold(f) in folded]
    misses = [f for f in must if fold(f) not in folded]
    score = len(hits) / len(must) if must else 1.0
    ok = score >= 0.8
    failed |= not ok
    print(f"{'PASS' if ok else 'FAIL'}  facts {score:.2f} ({len(hits)}/{len(must)})" + (f"; missing: {misses}" if misses else ""))

    avoid = [f for f in fx.get("notes_should_not_contain", []) if fold(f) in folded]
    print(f"{'WARN' if avoid else 'PASS'}  avoid" + (f": found {avoid}" if avoid else ""))

    n_ts = len(re.findall(r"\[\d{1,2}:\d{2}(?::\d{2})?\]", notes))
    need = fx.get("notes_min_timestamps", 0)
    ok = n_ts >= need
    failed |= not ok
    print(f"{'PASS' if ok else 'FAIL'}  timestamps {n_ts} (need {need})")

    missing_sections = [s for s in SECTIONS if s.lower() not in notes.lower()]
    ok = not missing_sections
    failed |= not ok
    print(f"{'PASS' if ok else 'FAIL'}  sections" + (f": missing {missing_sections}" if missing_sections else ""))

    refs = sorted(set(re.findall(r"f_\d{3}_[0-9-]+\.jpg", notes)))
    missing = [r for r in refs if not (wd / "frames" / r).is_file()]
    ok = not missing
    failed |= not ok
    print(f"{'PASS' if ok else 'FAIL'}  frame_refs {len(refs)} cited" + (f"; missing: {missing[:5]}" if missing else ""))

    rrefs = sorted(set(r.rstrip(".,;:") for r in re.findall(r"resources/([A-Za-z0-9._-]+)", notes)))
    missing = [r for r in rrefs if not (wd / "resources" / r).is_file()]
    ok = not missing
    failed |= not ok
    print(f"{'PASS' if ok else 'FAIL'}  resource_refs {len(rrefs)} cited" + (f"; missing: {missing}" if missing else ""))

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
