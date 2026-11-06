#!/usr/bin/env python3
"""
scan.py — Phase 1 read-only inventory of a directory.

Walks a target directory and emits a JSON inventory used by the model to
classify the directory and propose an organization plan. This script only
reads: it does not modify, move, or delete anything.

Usage:
    python3 scan.py <directory> [--max-depth N] [--hash-cap-mb N] [--out FILE]

Output: JSON to stdout (or --out FILE). Includes:
  - totals (file count, bytes)
  - breakdown by category and by extension
  - age buckets (by mtime) and the oldest/largest files
  - duplicate clusters (files with identical content)
  - flags: git repos, node_modules, symlinks, files touched today, junk
The model reads this to decide the taxonomy; it does not need to re-walk.
"""

import argparse
import hashlib
import json
import os
import sys
import time

# Directories we never descend into or reorganize. Their presence is reported
# as a flag so the model can treat them as atomic units.
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__",
             ".Trash", ".cache", "Library", ".idea", ".vscode",
             "vendor", "dist", "build", ".next", "target"}

# A directory containing any of these at its top level is a project/repo root.
# We stop descending into it and report it as an atomic unit rather than
# walking (and hashing) all of its source — reorganizing inside a project is
# out of scope, and a workspace of many repos is what makes a deep scan hang.
PROJECT_MARKERS = {".git", ".hg", ".svn", "package.json", "pyproject.toml",
                   "Cargo.toml", "go.mod", "Gemfile", "pom.xml",
                   "build.gradle", "composer.json", "setup.py", "Makefile"}


def is_project_root(path):
    """True if `path` looks like the root of a self-contained project/repo."""
    try:
        entries = set(os.listdir(path))
    except OSError:
        return False
    return not entries.isdisjoint(PROJECT_MARKERS)

# Extension -> category. Keep broad; the model refines semantically.
CATEGORY_MAP = {
    "images": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".heic",
               ".tiff", ".bmp", ".ico", ".raw", ".cr2", ".nef"},
    "documents": {".pdf", ".doc", ".docx", ".txt", ".md", ".rtf", ".odt",
                  ".pages", ".tex", ".epub"},
    "spreadsheets": {".xls", ".xlsx", ".csv", ".tsv", ".numbers", ".ods"},
    "presentations": {".ppt", ".pptx", ".key", ".odp"},
    "video": {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v", ".wmv", ".flv"},
    "audio": {".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg", ".aiff"},
    "archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".tgz"},
    "installers": {".dmg", ".pkg", ".exe", ".msi", ".deb", ".rpm", ".appimage"},
    "code": {".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java", ".c",
             ".cpp", ".h", ".rb", ".php", ".sh", ".html", ".css", ".json",
             ".yaml", ".yml", ".toml", ".sql"},
    "design": {".fig", ".sketch", ".psd", ".ai", ".xd", ".indd"},
}
EXT_TO_CATEGORY = {ext: cat for cat, exts in CATEGORY_MAP.items() for ext in exts}

# Filenames / extensions treated as likely junk (candidates only — never acted
# on by this script).
JUNK_EXACT = {".DS_Store", "Thumbs.db", "desktop.ini"}
JUNK_EXT = {".tmp", ".temp", ".part", ".crdownload", ".download", ".log"}

DAY = 86400


def human(n):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:.1f}{unit}" if unit != "B" else f"{n}B"
        n /= 1024


def partial_hash(path, size, hash_cap):
    """Full sha256 for small files; a cheap positional signature for large
    ones (first + last chunk + size) so dedup stays fast on big media."""
    h = hashlib.sha256()
    try:
        if size <= hash_cap:
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(1 << 20), b""):
                    h.update(chunk)
            return h.hexdigest(), True  # exact
        with open(path, "rb") as f:
            h.update(f.read(1 << 20))
            f.seek(-(1 << 20), os.SEEK_END)
            h.update(f.read(1 << 20))
        h.update(str(size).encode())
        return h.hexdigest(), False  # probable
    except OSError:
        return None, False


def progress(msg):
    """Emit a status line to stderr so a long scan is never a silent hang."""
    print(msg, file=sys.stderr, flush=True)


def scan(target, max_depth, hash_cap, dedup=True, max_hash_files=5000,
         time_budget=60):
    now = time.time()
    notes = []
    files = []
    flags = {"git_repos": [], "node_modules": [], "project_roots": [],
             "symlinks": [], "modified_today": [], "junk_candidates": [],
             "hidden": []}
    by_ext, by_cat = {}, {}
    size_index = {}  # size -> [file idx] for dedup candidate grouping

    target = os.path.abspath(target)
    base_depth = target.rstrip(os.sep).count(os.sep)

    for root, dirs, filenames in os.walk(target):
        depth = root.count(os.sep) - base_depth
        # Report then prune skip-dirs and project roots so we don't descend
        # into them. A project root is treated as an atomic unit: recorded once,
        # never walked into (reorganizing a repo's insides is out of scope).
        project_children = set()
        for d in list(dirs):
            full = os.path.join(root, d)
            if d == ".git":
                flags["git_repos"].append(os.path.relpath(root, target))
            if d == "node_modules":
                flags["node_modules"].append(os.path.relpath(full, target))
            if os.path.islink(full):
                flags["symlinks"].append(os.path.relpath(full, target))
            elif d not in SKIP_DIRS and is_project_root(full):
                flags["project_roots"].append(os.path.relpath(full, target))
                project_children.add(d)
        dirs[:] = [d for d in dirs
                   if d not in SKIP_DIRS and d not in project_children
                   and not os.path.islink(os.path.join(root, d))]
        if max_depth is not None and depth >= max_depth:
            dirs[:] = []

        for name in filenames:
            full = os.path.join(root, name)
            rel = os.path.relpath(full, target)
            if os.path.islink(full):
                flags["symlinks"].append(rel)
                continue
            try:
                st = os.stat(full)
            except OSError:
                continue
            ext = os.path.splitext(name)[1].lower()
            cat = EXT_TO_CATEGORY.get(ext, "other")
            idx = len(files)
            files.append({"rel": rel, "name": name, "ext": ext, "cat": cat,
                          "size": st.st_size, "mtime": st.st_mtime,
                          "age_days": round((now - st.st_mtime) / DAY, 1)})
            by_ext[ext or "(none)"] = by_ext.get(ext or "(none)", 0) + 1
            by_cat[cat] = by_cat.get(cat, 0) + 1
            size_index.setdefault(st.st_size, []).append(idx)

            if name in JUNK_EXACT or ext in JUNK_EXT:
                flags["junk_candidates"].append(rel)
            if name.startswith("."):
                flags["hidden"].append(rel)
            if now - st.st_mtime < DAY:
                flags["modified_today"].append(rel)

            if len(files) % 2000 == 0:
                progress(f"  scanned {len(files)} files...")

    progress(f"  walk complete: {len(files)} files, "
             f"{len(flags['project_roots'])} project roots skipped.")

    # Duplicate detection: only hash files that share an exact byte size. This
    # phase reads file bytes, so it is the expensive one — bound it by a file
    # cap and a wall-clock budget, and skip it entirely if disabled or if the
    # candidate set is too large to be worth the I/O.
    dup_clusters = []
    candidates = sum(len(idxs) for size, idxs in size_index.items()
                     if len(idxs) >= 2 and size > 0)
    if not dedup:
        notes.append("Duplicate detection disabled (--no-dedup).")
    elif candidates > max_hash_files:
        notes.append(
            f"Duplicate detection skipped: {candidates} same-size candidate "
            f"files exceed the --max-hash-files cap ({max_hash_files}). "
            f"Re-run on a narrower target or raise the cap to dedup.")
        progress(f"  {notes[-1]}")
    else:
        progress(f"  hashing {candidates} duplicate candidates "
                 f"(budget {time_budget}s)...")
        started = now
        hashed = 0
        timed_out = False
        for size, idxs in size_index.items():
            if len(idxs) < 2 or size == 0:
                continue
            if time.time() - started > time_budget:
                timed_out = True
                break
            by_hash = {}
            for i in idxs:
                digest, exact = partial_hash(
                    os.path.join(target, files[i]["rel"]), size, hash_cap)
                hashed += 1
                if digest is None:
                    continue
                by_hash.setdefault(digest, {"exact": exact, "idxs": []})["idxs"].append(i)
            for digest, grp in by_hash.items():
                if len(grp["idxs"]) > 1:
                    dup_clusters.append({
                        "size": size, "confidence": "exact" if grp["exact"] else "probable",
                        "files": [files[i]["rel"] for i in grp["idxs"]],
                        "reclaimable_bytes": size * (len(grp["idxs"]) - 1)})
        if timed_out:
            notes.append(
                f"Duplicate detection stopped after {time_budget}s "
                f"({hashed}/{candidates} candidates hashed); results are "
                f"partial. Raise --time-budget for a complete pass.")
            progress(f"  {notes[-1]}")

    # Age buckets.
    buckets = {"<=7d": 0, "8-30d": 0, "31-90d": 0, "91-365d": 0, ">365d": 0}
    for f in files:
        a = f["age_days"]
        key = ("<=7d" if a <= 7 else "8-30d" if a <= 30 else "31-90d" if a <= 90
               else "91-365d" if a <= 365 else ">365d")
        buckets[key] += 1

    total_bytes = sum(f["size"] for f in files)
    largest = sorted(files, key=lambda f: -f["size"])[:15]
    oldest = sorted(files, key=lambda f: -f["age_days"])[:15]

    return {
        "target": target,
        "totals": {"files": len(files), "bytes": total_bytes,
                   "human": human(total_bytes)},
        "by_category": dict(sorted(by_cat.items(), key=lambda x: -x[1])),
        "by_extension": dict(sorted(by_ext.items(), key=lambda x: -x[1])),
        "age_buckets": buckets,
        "largest_files": [{"rel": f["rel"], "size": f["size"],
                           "human": human(f["size"])} for f in largest],
        "oldest_files": [{"rel": f["rel"], "age_days": f["age_days"]}
                         for f in oldest],
        "duplicate_clusters": sorted(dup_clusters,
                                     key=lambda c: -c["reclaimable_bytes"]),
        "duplicate_reclaimable_bytes": sum(c["reclaimable_bytes"] for c in dup_clusters),
        "flags": {k: (v if len(v) <= 50 else v[:50] + [f"... +{len(v)-50} more"])
                  for k, v in flags.items()},
        "flag_counts": {k: len(v) for k, v in flags.items()},
        "notes": notes,
    }


def main():
    ap = argparse.ArgumentParser(description="Read-only directory inventory.")
    ap.add_argument("directory")
    ap.add_argument("--max-depth", type=int, default=None,
                    help="Limit recursion depth (default: unlimited).")
    ap.add_argument("--hash-cap-mb", type=int, default=256,
                    help="Files larger than this use a fast partial hash "
                         "for dedup (default 256MB).")
    ap.add_argument("--no-dedup", action="store_true",
                    help="Skip duplicate detection (the byte-reading phase) "
                         "entirely — fastest, structure-only inventory.")
    ap.add_argument("--max-hash-files", type=int, default=5000,
                    help="Skip dedup if more than this many same-size "
                         "candidate files would be hashed (default 5000).")
    ap.add_argument("--time-budget", type=int, default=60,
                    help="Wall-clock seconds allowed for the dedup pass "
                         "before it stops with partial results (default 60).")
    ap.add_argument("--out", default=None, help="Write JSON here instead of stdout.")
    args = ap.parse_args()

    if not os.path.isdir(args.directory):
        sys.exit(f"error: not a directory: {args.directory}")

    result = scan(args.directory, args.max_depth, args.hash_cap_mb * 1024 * 1024,
                  dedup=not args.no_dedup, max_hash_files=args.max_hash_files,
                  time_budget=args.time_budget)
    text = json.dumps(result, indent=2)
    if args.out:
        with open(args.out, "w") as f:
            f.write(text)
        print(f"wrote inventory to {args.out} "
              f"({result['totals']['files']} files, {result['totals']['human']})")
    else:
        print(text)


if __name__ == "__main__":
    main()
