#!/usr/bin/env python3
"""Blind A/B pairing for a Gauntlet Loop.

Puts our item and the reference item into a pair folder as A and B, in random
order. Writes the key outside the project, so a critic cannot read it.

Usage:
  blind_pair.py pair   --piece NAME --ours PATH --ref PATH [--round N]
  blind_pair.py reveal --piece NAME --round N --pick A|B [--confidence C] [--gap TEXT]
  blind_pair.py status

pair   copies the files to .gauntlet/pairs/<piece>/round-<N>/A.<ext> and B.<ext>
       and prints the pair folder. Give that folder to the critic.
reveal reads the key, prints WIN or LOSE, and appends a line to .gauntlet/log.jsonl.
status prints rounds, wins and the last gap for each piece.

Run from the project root. Keys go to ~/.cache/gauntlet/<project-name>/keys/.
PATH may be a file or a folder. Ours and ref should have the same format.
"""
import argparse
import json
import random
import shutil
import sys
import time
from pathlib import Path

ROOT = Path.cwd()
GAUNTLET = ROOT / ".gauntlet"
KEYS = Path.home() / ".cache" / "gauntlet" / ROOT.name / "keys"
LOG = GAUNTLET / "log.jsonl"


def safe(name):
    return "".join(c if c.isalnum() or c in "-_" else "-" for c in name)


def suffix(p):
    return "" if p.is_dir() else p.suffix


def copy(src, dst):
    if src.is_dir():
        shutil.copytree(src, dst, copy_function=shutil.copyfile)
    else:
        shutil.copyfile(src, dst)  # no metadata: dates could reveal which side is new


def next_round(piece):
    d = GAUNTLET / "pairs" / safe(piece)
    if not d.exists():
        return 1
    nums = [int(p.name.split("-")[1]) for p in d.glob("round-*") if p.name.split("-")[1].isdigit()]
    return max(nums, default=0) + 1


def cmd_pair(a):
    ours, ref = Path(a.ours), Path(a.ref)
    for p in (ours, ref):
        if not p.exists():
            sys.exit(f"not found: {p}")
    if ours.is_dir() != ref.is_dir() or suffix(ours) != suffix(ref):
        print("warning: ours and ref have different formats. The critic may tell them apart.", file=sys.stderr)
    rnd = a.round or next_round(a.piece)
    out = GAUNTLET / "pairs" / safe(a.piece) / f"round-{rnd:03d}"
    if out.exists():
        sys.exit(f"pair exists: {out}")
    out.mkdir(parents=True)
    ours_is_a = random.SystemRandom().random() < 0.5
    first, second = (ours, ref) if ours_is_a else (ref, ours)
    copy(first, out / f"A{suffix(first)}")
    copy(second, out / f"B{suffix(second)}")
    KEYS.mkdir(parents=True, exist_ok=True)
    key = {"piece": a.piece, "round": rnd, "ours": "A" if ours_is_a else "B",
           "ours_src": str(ours), "ref_src": str(ref), "time": time.time()}
    (KEYS / f"{safe(a.piece)}-{rnd:03d}.json").write_text(json.dumps(key))
    print(out)


def cmd_reveal(a):
    kf = KEYS / f"{safe(a.piece)}-{a.round:03d}.json"
    if not kf.exists():
        sys.exit(f"no key: {kf}")
    key = json.loads(kf.read_text())
    pick = a.pick.upper()
    win = pick == key["ours"]
    entry = {"piece": a.piece, "round": a.round, "pick": pick, "ours": key["ours"],
             "result": "WIN" if win else "LOSE", "confidence": a.confidence,
             "gap": a.gap, "time": time.time()}
    GAUNTLET.mkdir(exist_ok=True)
    with LOG.open("a") as f:
        f.write(json.dumps(entry) + "\n")
    print(entry["result"])


def cmd_status(_):
    if not LOG.exists():
        print("no verdicts yet")
        return
    pieces = {}
    for line in LOG.read_text().splitlines():
        e = json.loads(line)
        s = pieces.setdefault(e["piece"], {"rounds": 0, "wins": 0, "streak": 0, "gap": ""})
        s["rounds"] += 1
        if e["result"] == "WIN":
            s["wins"] += 1
            s["streak"] = 0
        else:
            s["streak"] += 1
            s["gap"] = e.get("gap") or s["gap"]
    print(f"{'piece':30} {'rounds':>6} {'wins':>5} {'losing streak':>13}  last gap")
    for name, s in sorted(pieces.items()):
        print(f"{name[:30]:30} {s['rounds']:>6} {s['wins']:>5} {s['streak']:>13}  {(s['gap'] or '')[:80]}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pair")
    p.add_argument("--piece", required=True)
    p.add_argument("--ours", required=True)
    p.add_argument("--ref", required=True)
    p.add_argument("--round", type=int)
    r = sub.add_parser("reveal")
    r.add_argument("--piece", required=True)
    r.add_argument("--round", type=int, required=True)
    r.add_argument("--pick", required=True, choices=["A", "B", "a", "b"])
    r.add_argument("--confidence", default="")
    r.add_argument("--gap", default="")
    sub.add_parser("status")
    a = ap.parse_args()
    {"pair": cmd_pair, "reveal": cmd_reveal, "status": cmd_status}[a.cmd](a)


if __name__ == "__main__":
    main()
