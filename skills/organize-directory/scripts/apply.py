#!/usr/bin/env python3
"""
apply.py — Phase 3 executor. Reads a move-plan.json produced by the model and
either previews (default) or commits it.

Safety model:
  * DRY-RUN BY DEFAULT. Nothing changes without --commit.
  * Same-filesystem moves use an atomic rename (no copy, no wasted disk) — this
    is the normal "reorganize a folder into its own subfolders" case.
  * Cross-filesystem moves use copy -> verify (size + sha256) -> delete original.
    The original is deleted ONLY after the copy is byte-verified.
  * Every commit writes undo.sh FIRST (before touching files) so the run is
    reversible with a plain, human-readable shell script.
  * Destinations that would overwrite an existing file are never clobbered.
  * All destinations must resolve inside the target directory.
  * Deletion is never performed here. "quarantine" actions move junk/dupes into
    _REVIEW/; emptying that folder is a separate, explicitly confirmed step
    (see empty-quarantine.py behavior described in SKILL.md).

Plan schema (move-plan.json):
{
  "target": "/abs/path",
  "mkdirs": ["Documents", "Images/2025", "_REVIEW/duplicates"],
  "moves": [
    {"src": "a.pdf", "dst": "Documents/a.pdf", "action": "move", "reason": "..."},
    {"src": "dup.png", "dst": "_REVIEW/duplicates/dup.png",
     "action": "quarantine", "reason": "exact duplicate of x.png"}
  ]
}
Paths in src/dst are RELATIVE to target.

Usage:
    python3 apply.py --plan move-plan.json            # dry-run preview
    python3 apply.py --plan move-plan.json --commit   # execute
    python3 apply.py --plan move-plan.json --commit --verify size   # skip hashing
    python3 apply.py --plan move-plan.json --commit --on-collision quarantine
"""

import argparse
import hashlib
import json
import os
import shutil
import sys
import time


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sh_quote(p):
    return "'" + p.replace("'", "'\\''") + "'"


def load_plan(plan_path):
    with open(plan_path) as f:
        plan = json.load(f)
    for key in ("target", "moves"):
        if key not in plan:
            sys.exit(f"error: plan missing required key '{key}'")
    plan.setdefault("mkdirs", [])
    return plan


def resolve_inside(target, rel):
    """Resolve rel against target and ensure it stays inside target."""
    full = os.path.normpath(os.path.join(target, rel))
    if os.path.commonpath([target, full]) != target:
        raise ValueError(f"path escapes target: {rel}")
    return full


def unique_dst(dst):
    """Return a non-colliding path by inserting ' (2)', ' (3)', ... before ext."""
    if not os.path.exists(dst):
        return dst
    root, ext = os.path.splitext(dst)
    i = 2
    while os.path.exists(f"{root} ({i}){ext}"):
        i += 1
    return f"{root} ({i}){ext}"


def validate(plan, target):
    """Return (ops, problems). ops are resolved {src,dst,action,reason,samefs}."""
    problems, ops = [], []
    try:
        target_dev = os.stat(target).st_dev
    except OSError as e:
        sys.exit(f"error: cannot stat target: {e}")

    seen_dst = {}
    for m in plan["moves"]:
        try:
            src = resolve_inside(target, m["src"])
            dst = resolve_inside(target, m["dst"])
        except (ValueError, KeyError) as e:
            problems.append(f"invalid entry {m}: {e}")
            continue
        if not os.path.exists(src):
            problems.append(f"missing source: {m['src']}")
            continue
        if os.path.isdir(src):
            problems.append(f"source is a directory (moves are file-only): {m['src']}")
            continue
        if src == dst:
            problems.append(f"src == dst (no-op): {m['src']}")
            continue
        if dst in seen_dst:
            problems.append(f"two files target the same dst {m['dst']}: "
                            f"{seen_dst[dst]} and {m['src']}")
        seen_dst[dst] = m["src"]
        try:
            samefs = os.stat(os.path.dirname(src)).st_dev == target_dev
        except OSError:
            samefs = False
        ops.append({"src": src, "dst": dst, "rel_src": m["src"], "rel_dst": m["dst"],
                    "action": m.get("action", "move"),
                    "reason": m.get("reason", ""), "samefs": samefs})
    return ops, problems


def preview(ops, problems, plan, target):
    print(f"\n=== DRY RUN — target: {target} ===")
    print(f"planned operations: {len(ops)}   new folders: {len(plan['mkdirs'])}")
    moves = [o for o in ops if o["action"] == "move"]
    quar = [o for o in ops if o["action"] == "quarantine"]
    cross = [o for o in ops if not o["samefs"]]
    collisions = [o for o in ops if os.path.exists(o["dst"])]

    print(f"  moves: {len(moves)}   quarantine: {len(quar)}")
    print(f"  same-filesystem (instant rename): {len(ops) - len(cross)}")
    print(f"  cross-filesystem (copy+verify+delete): {len(cross)}")
    if collisions:
        print(f"  ! destination already exists for {len(collisions)} file(s) "
              f"(will auto-suffix unless --on-collision changes it)")
    print()
    for o in ops[:60]:
        tag = "Q" if o["action"] == "quarantine" else " "
        fs = " " if o["samefs"] else "*"
        print(f"  [{tag}{fs}] {o['rel_src']}  ->  {o['rel_dst']}"
              + (f"   ({o['reason']})" if o["reason"] else ""))
    if len(ops) > 60:
        print(f"  ... +{len(ops) - 60} more")
    if problems:
        print("\n!! PROBLEMS (these entries will be skipped):")
        for p in problems[:40]:
            print(f"   - {p}")
    print("\n(* = cross-filesystem copy+verify+delete)")
    print("Nothing has changed. Re-run with --commit to execute.\n")


def write_undo(ops, target, run_id):
    """Write undo.sh BEFORE any file operation. Reverses each committed move
    with plain `mv -n` so it is transparent and script-independent."""
    path = os.path.join(target, f"_organize-undo-{run_id}.sh")
    lines = ["#!/usr/bin/env bash",
             "# Auto-generated undo script. Reverses the organize run.",
             "# Review before running. Uses mv -n (never overwrites).",
             "set -euo pipefail", ""]
    for o in ops:
        parent = os.path.dirname(o["src"])
        lines.append(f"mkdir -p {sh_quote(parent)}")
        lines.append(f"mv -n {sh_quote(o['dst'])} {sh_quote(o['src'])}")
    lines.append("")
    with open(path, "w") as f:
        f.write("\n".join(lines))
    os.chmod(path, 0o755)
    return path


def commit(ops, plan, target, verify, on_collision, run_id):
    for d in plan["mkdirs"]:
        os.makedirs(resolve_inside(target, d), exist_ok=True)

    undo_path = write_undo(ops, target, run_id)
    print(f"undo script written: {os.path.relpath(undo_path, target)}")

    done, skipped, failed = [], [], []
    for o in ops:
        src, dst = o["src"], o["dst"]
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.exists(dst):
            if on_collision == "skip":
                skipped.append((o, "destination exists"))
                continue
            if on_collision == "quarantine":
                dst = resolve_inside(target, os.path.join("_REVIEW", "collisions",
                                                          os.path.basename(dst)))
                os.makedirs(os.path.dirname(dst), exist_ok=True)
            dst = unique_dst(dst)
        try:
            if o["samefs"]:
                os.rename(src, dst)  # atomic, no copy
            else:
                tmp = dst + ".part"
                shutil.copy2(src, tmp)
                ok = os.path.getsize(tmp) == os.path.getsize(src)
                if ok and verify == "hash":
                    ok = sha256(tmp) == sha256(src)
                if not ok:
                    os.remove(tmp)
                    failed.append((o, "verification failed — original kept"))
                    continue
                os.rename(tmp, dst)
                os.remove(src)  # only after verified copy
            done.append((o, dst))
        except OSError as e:
            failed.append((o, str(e)))

    summary = write_summary(target, done, skipped, failed, undo_path, run_id)
    print(f"\ncommitted: {len(done)}   skipped: {len(skipped)}   failed: {len(failed)}")
    print(f"summary: {os.path.relpath(summary, target)}")
    print(f"undo:    bash {sh_quote(os.path.relpath(undo_path, target))}")
    if failed:
        print("\nfailures:")
        for o, why in failed[:40]:
            print(f"  - {o['rel_src']}: {why}")


def write_summary(target, done, skipped, failed, undo_path, run_id):
    path = os.path.join(target, f"_organize-summary-{run_id}.md")
    lines = [f"# Organize summary — {run_id}", "",
             f"- Target: `{target}`",
             f"- Moved: {len(done)}",
             f"- Skipped: {len(skipped)}",
             f"- Failed: {len(failed)}",
             f"- Undo: `bash {os.path.basename(undo_path)}`", "",
             "## Moved", ""]
    for o, dst in done:
        rel_dst = os.path.relpath(dst, target)
        lines.append(f"- `{o['rel_src']}` -> `{rel_dst}`"
                     + (f" ({o['reason']})" if o["reason"] else ""))
    if skipped:
        lines += ["", "## Skipped", ""]
        lines += [f"- `{o['rel_src']}` ({why})" for o, why in skipped]
    if failed:
        lines += ["", "## Failed (originals untouched)", ""]
        lines += [f"- `{o['rel_src']}` ({why})" for o, why in failed]
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    return path


def main():
    ap = argparse.ArgumentParser(description="Preview or commit a move-plan.")
    ap.add_argument("--plan", required=True)
    ap.add_argument("--commit", action="store_true",
                    help="Execute. Without this flag, only previews (dry-run).")
    ap.add_argument("--verify", choices=["hash", "size"], default="hash",
                    help="Cross-filesystem copy verification (default hash). "
                         "Same-filesystem moves are atomic and need no verify.")
    ap.add_argument("--on-collision", choices=["suffix", "quarantine", "skip"],
                    default="suffix",
                    help="What to do if a destination already exists.")
    ap.add_argument("--run-id", default=None,
                    help="Label for undo/summary files (default: timestamp).")
    args = ap.parse_args()

    plan = load_plan(args.plan)
    target = os.path.abspath(plan["target"])
    if not os.path.isdir(target):
        sys.exit(f"error: target is not a directory: {target}")

    ops, problems = validate(plan, target)
    run_id = args.run_id or time.strftime("%Y%m%d-%H%M%S")

    if not args.commit:
        preview(ops, problems, plan, target)
        return
    if problems:
        print("Refusing to commit — plan has problems (fix these first):")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)
    commit(ops, plan, target, args.verify, args.on_collision, run_id)


if __name__ == "__main__":
    main()
