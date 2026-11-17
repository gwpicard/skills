#!/usr/bin/env python3
"""List repositories that have agent instruction files, for a review across projects.

Sources:
  default        projects Claude Code was used in, from ~/.claude/projects session logs
  --under DIR    git repositories under DIR (up to 3 levels deep) instead

Worktrees and subdirectories are merged into their main repository. Only
repositories with a CLAUDE.md, CLAUDE.local.md, AGENTS.md or .claude/rules file
are listed, most recently used first.

Temporary and hidden locations (temp folders, ~/.cache, ~/.local and other
dot-folders) are skipped, since they usually hold throwaway clones.

Usage: discover_projects.py [--under DIR] [--since DAYS] [--all] [--json]
  --since DAYS   only projects used in the last DAYS days (default 90; history source only)
  --all          keep temporary and hidden locations
"""
import json
import re
import subprocess
import sys
import time
from pathlib import Path

NAMES = ("CLAUDE.md", "CLAUDE.local.md", "AGENTS.md", "GEMINI.md", ".claude/CLAUDE.md")
CWD = re.compile(r'"cwd":"((?:[^"\\]|\\.)*)"')


def arg(name: str, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


def main_repo_root(path: Path) -> Path | None:
    """Return the main worktree root of the repository containing path."""
    try:
        common = subprocess.run(["git", "-C", str(path), "rev-parse", "--path-format=absolute",
                                 "--git-common-dir"], capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if common.returncode != 0:
        return None
    git_dir = Path(common.stdout.strip())
    return git_dir.parent if git_dir.name == ".git" else None


def from_history(since_days: int) -> dict[Path, float]:
    """Map path -> last-used time, from Claude Code session logs."""
    cutoff = time.time() - since_days * 86400
    found: dict[Path, float] = {}
    base = Path.home() / ".claude" / "projects"
    if not base.is_dir():
        return found
    for proj in base.iterdir():
        try:
            if not proj.is_dir() or proj.stat().st_mtime < cutoff:
                continue
            logs = sorted(proj.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
        except OSError:
            continue
        for log in logs[:1]:
            mtime = log.stat().st_mtime
            if mtime < cutoff:
                continue
            with log.open(errors="replace") as fh:
                for _, line in zip(range(50), fh):
                    m = CWD.search(line)
                    if m:
                        cwd = Path(json.loads(f'"{m.group(1)}"'))
                        found[cwd] = max(found.get(cwd, 0), mtime)
                        break
    return found


def from_directory(root: Path) -> dict[Path, float]:
    found: dict[Path, float] = {}
    for depth in ("*/.git", "*/*/.git", "*/*/*/.git"):
        for git in root.glob(depth):
            found[git.parent] = git.stat().st_mtime
    return found


def is_throwaway(repo: Path) -> bool:
    if str(repo).startswith(("/tmp", "/private/", "/var/")):
        return True
    rel = repo.relative_to(Path.home()).parts if repo.is_relative_to(Path.home()) else repo.parts
    return any(part.startswith(".") for part in rel)


def instruction_files(repo: Path) -> list[str]:
    files = [n for n in NAMES if (repo / n).is_file()]
    rules = repo / ".claude" / "rules"
    if rules.is_dir():
        files += [str(p.relative_to(repo)) for p in sorted(rules.rglob("*.md"))]
    return files


def main() -> None:
    under = arg("--under")
    candidates = from_directory(Path(under).expanduser().resolve()) if under \
        else from_history(int(arg("--since", "90")))

    repos: dict[Path, float] = {}
    for path, used in candidates.items():
        if not path.is_dir():
            continue
        root = main_repo_root(path)
        if root is None or root == Path.home():
            continue
        if "--all" not in sys.argv and is_throwaway(root):
            continue
        repos[root] = max(repos.get(root, 0), used)

    rows = []
    for repo, used in sorted(repos.items(), key=lambda kv: kv[1], reverse=True):
        files = instruction_files(repo)
        if not files:
            continue
        lines = sum(len((repo / f).read_text(errors="replace").splitlines()) for f in files)
        rows.append({"repo": str(repo), "files": files, "lines": lines,
                     "last_used": time.strftime("%Y-%m-%d", time.localtime(used))})

    user = Path.home() / ".claude" / "CLAUDE.md"
    if "--json" in sys.argv:
        print(json.dumps({"user_file": str(user) if user.is_file() else None, "projects": rows}, indent=2))
        return
    print(f"User file: {user if user.is_file() else 'none'}\n")
    if not rows:
        print("No repositories with instruction files found.")
        return
    print("| # | Repository | Instruction files | Lines | Last used |\n|---|---|---|---|---|")
    for i, r in enumerate(rows, 1):
        print(f"| {i} | {r['repo']} | {', '.join(r['files'])} | {r['lines']} | {r['last_used']} |")


if __name__ == "__main__":
    main()
