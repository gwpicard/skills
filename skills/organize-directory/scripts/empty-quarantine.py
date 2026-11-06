#!/usr/bin/env python3
"""
empty-quarantine.py — the separate, explicitly-confirmed deletion step.

The organizer never deletes during a normal run; it moves junk and duplicates
into <target>/_REVIEW/. This script empties that folder — and even then it
sends items to the macOS Trash (recoverable) by default rather than hard rm.

Usage:
    python3 empty-quarantine.py <target>            # list what would be removed
    python3 empty-quarantine.py <target> --confirm  # move _REVIEW to Trash
    python3 empty-quarantine.py <target> --confirm --hard   # permanent rm (last resort)
"""

import argparse
import os
import subprocess
import sys


def to_trash_macos(path):
    """Move a path to the macOS Trash via Finder (recoverable)."""
    script = (
        'on run argv\n'
        '  tell application "Finder" to delete (POSIX file (item 1 of argv) as alias)\n'
        'end run'
    )
    subprocess.run(["osascript", "-e", script, path], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def walk_review(review):
    total = 0
    items = []
    for root, _dirs, files in os.walk(review):
        for name in files:
            p = os.path.join(root, name)
            try:
                total += os.path.getsize(p)
            except OSError:
                pass
            items.append(os.path.relpath(p, review))
    return items, total


def main():
    ap = argparse.ArgumentParser(description="Empty the _REVIEW quarantine folder.")
    ap.add_argument("target")
    ap.add_argument("--confirm", action="store_true",
                    help="Actually remove. Without it, just lists.")
    ap.add_argument("--hard", action="store_true",
                    help="Permanent delete instead of moving to Trash.")
    args = ap.parse_args()

    review = os.path.join(os.path.abspath(args.target), "_REVIEW")
    if not os.path.isdir(review):
        sys.exit(f"no _REVIEW folder in {args.target} — nothing to empty.")

    items, total = walk_review(review)
    mb = total / (1024 * 1024)
    print(f"_REVIEW contains {len(items)} file(s), {mb:.1f}MB")
    for i in items[:60]:
        print(f"  - {i}")
    if len(items) > 60:
        print(f"  ... +{len(items) - 60} more")

    if not args.confirm:
        print("\nDry run. Re-run with --confirm to remove "
              "(moves to Trash unless --hard).")
        return

    if args.hard:
        import shutil
        shutil.rmtree(review)
        print(f"permanently deleted _REVIEW ({len(items)} files).")
    else:
        try:
            to_trash_macos(review)
            print(f"moved _REVIEW to Trash ({len(items)} files) — recoverable.")
        except Exception as e:
            sys.exit(f"could not move to Trash ({e}). "
                     f"Re-run with --hard to delete permanently, or empty manually.")


if __name__ == "__main__":
    main()
