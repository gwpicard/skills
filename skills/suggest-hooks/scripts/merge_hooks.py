#!/usr/bin/env python3
"""Merge approved hooks into a settings file without touching the existing ones.

The fragment has the settings shape: {"hooks": {"Event": [{"matcher": ..., "hooks": [...]}]}}.
Without --apply it prints what would change and writes nothing. With --apply it
copies the settings file to <file>.bak-<timestamp> first, appends new handlers,
skips handlers that are already present, and checks the result parses.

Usage:
  python3 merge_hooks.py --settings ~/.claude/settings.json --fragment approved.json
  python3 merge_hooks.py --settings ~/.claude/settings.json --fragment approved.json --apply
"""
import argparse
import copy
import json
import os
import shutil
import time


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--settings", required=True)
    ap.add_argument("--fragment", required=True)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    path = os.path.expanduser(a.settings)
    current = {}
    if os.path.exists(path):
        with open(path) as fh:
            current = json.load(fh)  # fail loudly on invalid JSON rather than overwrite it
    with open(os.path.expanduser(a.fragment)) as fh:
        fragment = json.load(fh)

    merged = copy.deepcopy(current)
    hooks = merged.setdefault("hooks", {})
    added, skipped = [], []
    for event, groups in fragment.get("hooks", {}).items():
        target = hooks.setdefault(event, [])
        for g in groups:
            matcher = g.get("matcher", "")
            group = next((x for x in target if x.get("matcher", "") == matcher), None)
            if group is None:
                group = {"matcher": matcher, "hooks": []} if matcher else {"hooks": []}
                target.append(group)
            for h in g.get("hooks", []):
                label = f"{event} [{matcher or '*'}] {h.get('command') or h.get('prompt') or h.get('url')}"
                if h in group["hooks"]:
                    skipped.append(label)
                else:
                    group["hooks"].append(h)
                    added.append(label)

    for x in added:
        print("ADD   ", x[:200])
    for x in skipped:
        print("EXISTS", x[:200])
    if not added:
        print("Nothing to add.")
        return
    if not a.apply:
        print(f"\nDry run: {path} not changed. Re-run with --apply after the user approves.")
        return
    if os.path.exists(path):
        backup = f"{path}.bak-{time.strftime('%Y%m%d-%H%M%S')}"
        shutil.copy2(path, backup)
        print("backup:", backup)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(merged, fh, indent=2)
        fh.write("\n")
    with open(tmp) as fh:
        json.load(fh)
    os.replace(tmp, path)
    print(f"wrote {path}: {len(added)} handler(s) added. Check them with /hooks.")


if __name__ == "__main__":
    main()
