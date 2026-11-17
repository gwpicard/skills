#!/usr/bin/env python3
"""Scan a repository's agent instruction files and print a markdown report.

Finds CLAUDE.md, CLAUDE.local.md, AGENTS.md, GEMINI.md, Copilot instruction
files and .claude/rules/*.md. For each file it reports when it loads, its size,
broken @imports, backticked paths and package scripts that do not exist, and
candidate passages for the review checks. It also estimates what a Claude Code
session started at the repository root loads, summarises the settings files,
and lists allow rules that may contradict the instructions.

Text is analysed by passage (a paragraph or list item, with wrapped lines
joined), so a rule and its alternative on the next line are read together.
Flags are candidates for the reviewer to judge, not findings.

Usage: scan_instructions.py [ROOT] [--user]
  ROOT    repository root (default: current directory)
  --user  also scan ~/.claude/CLAUDE.md
"""
import json
import re
import subprocess
import sys
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "vendor", "dist", "build", ".venv", "venv",
             "__pycache__", ".next", "target", ".tox", "coverage"}
NAMES = {"CLAUDE.md", "CLAUDE.local.md", "AGENTS.md", "GEMINI.md"}
TEMPLATE_DIRS = {"templates", "template", "fixtures", "fixture", "examples", "example",
                 "samples", "testdata", "__fixtures__", "skeleton", "scaffold"}

# Sentence-level flags, matched case-insensitively.
FLAGS = [
    ("history", r"\b(previously|used to|was renamed|"
                r"we (moved|switched|migrated)|(was|were) (added|removed|replaced)|"
                r"since v?\d|(19|20)\d\d-\d\d|(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]* (19|20)\d\d)\b"),
    ("time-sensitive", r"\b(currently|for now|temporarily|at the moment|todo|fixme|until we)\b"),
    ("vague", r"\b(clean code|best practices?|be careful|properly|high[- ]quality|"
              r"as needed|when appropriate|good code|readable|maintainable|robust)\b"),
]
RULE = re.compile(r"\b(never|always|don'?t|do not|must|only|make sure|ensure|avoid|"
                  r"before (committing|pushing|merging|finishing)|off limits|not allowed)\b", re.I)
ENFORCEABLE = re.compile(r"\b(push|merge|force|main|master|rebase|commit|rm -r|delete|"
                         r"\.env|secrets?|credentials?|tokens?|api keys?|prettier|eslint|ruff|"
                         r"lint\w*|format\w*|indent\w*|tabs|semicolons?|line length|"
                         r"deploy|production|migrations?|install|tests? (pass|run))\b", re.I)
NEGATIVE = re.compile(r"\b(never|don'?t|do not|avoid|must not|not allowed|forbidden)\b", re.I)
ALTERNATIVE = re.compile(r"\binstead\b|\bprefer|\brather than\b|\bin place of\b|(?:^|[;:,.]\s+|\band\s+)use\b|"
                         r"→|->|\breplace with\b|\bask\b|\bfollow\b|\bwrite\b|\bsave\b", re.I)
SHOUT = re.compile(r"\b(IMPORTANT|CRITICAL|MUST|NEVER|ALWAYS|DO NOT|REQUIRED)\b|!!")
HISTORY_HEADING = re.compile(r"^#+\s*(changelog|history|updates?|release notes|recent changes|"
                             r"what'?s new|migration notes)\b", re.I)
DERIVABLE_HEADING = re.compile(r"^#+\s*(project |repo(sitory)? |directory |folder |file )?(overview|structure|"
                               r"layout|architecture|tech(nology)? stack|dependencies|directory tree)\b", re.I)
MANDATORY_READ = re.compile(r"\b(?:before (?:any|every|starting|you start)|at the start|first|always|every session)"
                            r"\b[^.]*?\bread\s+`(?P<a>[^`]+)`|\bread\s+`(?P<b>[^`]+)`[^.]*?\b(?:first|before (?:any|every))",
                            re.I)
NOT_PRESENT = re.compile(r"\b(do(es)? not exist|doesn'?t exist|not exist here|no such|will (be )?creat|"
                         r"is created|are created|gets? created|generated (by|on|at)|once (it|you)|git ignores|"
                         r"(git-?)?ignored)", re.I)
TREE = re.compile(r"[├└│]──|^\s*[|`]-- ")
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
IMPORT = re.compile(r"(?<![\w`/])@((?:~|\.{1,2})?/?[\w.\-/]+\.[\w]+)")
INLINE_CODE = re.compile(r"`([^`\n]+)`")
PATHLIKE = re.compile(r"^(?:\./|\.\./|~/)?[\w.\-]+(?:/[\w.\-*]+)+/?$|"
                      r"^[\w\-.]+\.(md|json|ya?ml|toml|py|ts|tsx|js|mjs|sh|cfg|ini|lock|txt)$")
PKG_RUN = re.compile(r"\b(?:npm run|pnpm(?: run)?|yarn(?: run)?|bun run)\s+([\w:\-.]+)")
MAKE = re.compile(r"\bmake\s+([\w\-.]+)")
PKG_BUILTINS = {"install", "add", "remove", "exec", "dlx", "test", "start", "i", "ci",
                "run", "x", "create", "init", "update", "upgrade", "outdated", "why"}


def rel(path: Path, root: Path):
    return path.relative_to(root) if path.is_relative_to(root) else path


def walk(root: Path):
    for path in root.rglob("*"):
        parts = path.relative_to(root).parts
        if any(part in SKIP_DIRS for part in parts):
            continue
        yield path


def find_files(root: Path, include_user: bool) -> list[Path]:
    found = []
    for path in walk(root):
        if not path.is_file():
            continue
        r = path.relative_to(root)
        if path.name in NAMES:
            found.append(path)
        elif r.parts[:2] == (".claude", "rules") and path.suffix == ".md":
            found.append(path)
        elif r == Path(".github/copilot-instructions.md") or (
                r.parts[:2] == (".github", "instructions") and path.name.endswith(".instructions.md")):
            found.append(path)
    if include_user:
        user = Path.home() / ".claude" / "CLAUDE.md"
        if user.is_file():
            found.append(user)
    return sorted(found)


def load_kind(path: Path, root: Path) -> str:
    """When the file reaches a Claude Code session started at the repository root."""
    if not path.is_relative_to(root):
        return "startup (user file)"
    r = path.relative_to(root)
    if r.parts[:2] == (".claude", "rules"):
        return "startup (rule, no paths)" if not has_paths(path) else "on demand (path-scoped rule)"
    if r.parts[0] == ".github" or path.name == "GEMINI.md":
        return "other agents only" if path.parent in (root, root / ".github") or r.parts[0] == ".github" \
            else "other agents, nested"
    if path.parent in (root, root / ".claude"):
        return "startup"
    if any(part.lower() in TEMPLATE_DIRS for part in r.parts[:-1]):
        return "on demand (nested, under a template or fixture folder)"
    return "on demand (nested)"


def has_paths(path: Path) -> bool:
    text = path.read_text(errors="replace")
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    return bool(m and re.search(r"(?m)^paths\s*:", m.group(1)))


def passages(text: str):
    """Yield (first_line, last_line, joined_text, is_code). Wrapped lines are joined."""
    fence, buf, start = False, [], 0
    lines = text.splitlines()
    # Blank out YAML frontmatter, keeping line numbers.
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                lines[:i + 1] = [""] * (i + 1)
                break

    def flush(end):
        nonlocal buf
        if buf:
            yield start, end, " ".join(s.strip() for s in buf), False
        buf = []

    for n, line in enumerate(lines, 1):
        if line.lstrip().startswith(("```", "~~~")):
            yield from flush(n - 1)
            fence = not fence
            continue
        if fence:
            yield n, n, line, True
            continue
        if not line.strip():
            yield from flush(n - 1)
            continue
        if line.lstrip().startswith("#") or LIST_ITEM.match(line) or not buf:
            yield from flush(n - 1)
            start = n
        buf.append(line)
        if line.lstrip().startswith("#"):
            yield from flush(n)
    yield from flush(len(lines))


def sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z`*(])", text) if s.strip()]


class RepoIndex:
    """Every file path in the repository, for resolving short or relative references."""

    def __init__(self, root: Path):
        self.root = root
        self.paths: set[str] = set()
        self.names: set[str] = set()
        for i, p in enumerate(walk(root)):
            if i > 200_000:
                break
            r = p.relative_to(root).as_posix()
            self.paths.add(r + ("/" if p.is_dir() else ""))
            self.names.add(p.name)

    def resolves(self, token: str, base: Path, context_dirs: list[str]) -> bool:
        token = token.strip().rstrip("/")
        if token.startswith("~/"):
            return (Path.home() / token[2:]).exists()
        if "*" in token:
            parent = token.split("*")[0].rsplit("/", 1)[0]
            return not parent or (self.root / parent).exists() or (base / parent).exists()
        if (self.root / token).exists() or (base / token).exists():
            return True
        if any((self.root / d / token).exists() for d in context_dirs):
            return True
        if "/" not in token:
            return token in self.names
        suffix = "/" + token
        return any(p.rstrip("/").endswith(suffix) for p in self.paths)


def scan_file(path: Path, root: Path, index: RepoIndex, scripts, targets) -> dict:
    text = path.read_text(errors="replace")
    base = path.parent
    out = {"lines": len(text.splitlines()), "words": len(text.split()), "tokens": len(text) // 4,
           "kind": load_kind(path, root), "broken_imports": [], "missing_paths": [],
           "missing_commands": [], "flags": [], "tree_lines": 0, "imports": [], "reads": []}
    for first, last, body, code in passages(text):
        loc = f"L{first}" if first == last else f"L{first}-{last}"
        for cmd in PKG_RUN.findall(body):
            if scripts is not None and cmd not in scripts and cmd not in PKG_BUILTINS:
                out["missing_commands"].append((loc, f"package.json script `{cmd}`"))
        for target in MAKE.findall(body):
            if targets is not None and target not in targets:
                out["missing_commands"].append((loc, f"Makefile target `{target}`"))
        if TREE.search(body):
            out["tree_lines"] += 1
        if code:
            continue

        for imp in IMPORT.findall(re.sub(INLINE_CODE, "", body)):
            target = Path.home() / imp[2:] if imp.startswith("~/") else base / imp
            if target.exists():
                out["imports"].append(target.resolve())
            else:
                out["broken_imports"].append((loc, imp))

        if path.is_relative_to(root) and not NOT_PRESENT.search(body):
            context_dirs: list[str] = []
            for token in INLINE_CODE.findall(body):
                token = token.strip()
                if " " in token or not PATHLIKE.match(token):
                    continue
                if index.resolves(token, base, context_dirs):
                    if (root / token.rstrip("/")).is_dir():
                        context_dirs.append(token.rstrip("/"))
                else:
                    out["missing_paths"].append((loc, token))

        labels = []
        if HISTORY_HEADING.match(body):
            labels.append("history-heading")
        if DERIVABLE_HEADING.match(body):
            labels.append("derivable-heading")
        if SHOUT.search(body):
            labels.append("emphasis")
        sents = sentences(body)
        for i, s in enumerate(sents):
            nxt = sents[i + 1] if i + 1 < len(sents) else ""
            # Only a prohibition that leads the sentence; "an outcome, never a sentence" names the alternative.
            lead = " ".join(s.split()[:5])
            if NEGATIVE.search(lead) and not ALTERNATIVE.search(s + " " + nxt):
                labels.append("negative-only")
            if RULE.search(s) and ENFORCEABLE.search(s):
                labels.append("enforceable")
            for label, pattern in FLAGS:
                if re.search(pattern, s, re.I):
                    labels.append(label)
        m = MANDATORY_READ.search(body)
        if m:
            target = (m.group("a") or m.group("b") or "").strip()
            for cand in (root / target, base / target):
                if cand.is_file():
                    out["reads"].append((loc, cand.resolve()))
                    labels.append("mandatory-read")
                    break
        if labels:
            out["flags"].append((loc, sorted(set(labels)), body[:200]))
    return out


def package_scripts(root: Path):
    pkg = root / "package.json"
    if not pkg.is_file():
        return None
    try:
        return set(json.loads(pkg.read_text()).get("scripts", {}))
    except (json.JSONDecodeError, OSError):
        return None


def make_targets(root: Path):
    mk = root / "Makefile"
    if not mk.is_file():
        return None
    return set(re.findall(r"^([\w\-.]+)\s*:(?!=)", mk.read_text(errors="replace"), re.M))


def git_ignore_gaps(root: Path) -> list[str]:
    """Personal files that are not git-ignored by the repository itself."""
    if not (root / ".git").exists():
        return []
    gaps = []
    # Claude Code creates settings.local.json on its own, so check it even when absent.
    for name, always in (("CLAUDE.local.md", False), (".claude/settings.local.json", True)):
        exists = (root / name).exists()
        if not exists and not always:
            continue
        r = subprocess.run(["git", "-C", str(root), "check-ignore", "-v", "--no-index", name],
                           capture_output=True, text=True)
        source = r.stdout.split(":", 1)[0]
        if r.returncode == 0 and not (Path(source).is_absolute() and not Path(source).is_relative_to(root)):
            continue
        tracked = subprocess.run(["git", "-C", str(root), "ls-files", "--error-unmatch", name],
                                 capture_output=True).returncode == 0
        if tracked:
            gaps.append(f"`{name}` is COMMITTED to the repository; remove it from git and rotate any secret in it")
        elif r.returncode == 0:
            gaps.append(f"`{name}` is ignored only by your global git config ({source}); "
                        "add it to the repository's .gitignore so teammates are covered too")
        elif r.returncode == 1:
            gaps.append(f"`{name}` is not git-ignored" + (" (file exists)" if exists else ""))
    return gaps


def read_settings(root: Path) -> list[tuple[str, dict]]:
    out = []
    for name in (".claude/settings.json", ".claude/settings.local.json"):
        p = root / name
        if p.is_file():
            try:
                out.append((name, json.loads(p.read_text())))
            except json.JSONDecodeError:
                out.append((name, {"_error": "invalid JSON: deny rules and hooks in it may not apply"}))
    return out


def settings_conflicts(settings, texts: dict[Path, str], root: Path) -> list[str]:
    """Allow rules whose verb appears in an instruction sentence about approval or prohibition."""
    found = []
    approval = re.compile(r"\b(never|don'?t|do not|must not|person|approv\w*|ask|decides?|only|off limits)\b", re.I)
    for name, data in settings:
        for rule in data.get("permissions", {}).get("allow", []):
            m = re.match(r"Bash\(([^:*)]+)", rule)
            if not m:
                continue
            words = m.group(1).split()
            verb = words[-1] if len(words) > 1 else words[0]
            if len(verb) < 4:
                continue
            for f, text in texts.items():
                for first, last, body, code in passages(text):
                    if code:
                        continue
                    for s in sentences(body):
                        if re.search(rf"\b{re.escape(verb)}\w*\b", s, re.I) and approval.search(s):
                            found.append(f"{name} allows `{rule}`; {rel(f, root)} L{first}: \"{s[:140]}\"")
                            break
    return found[:15]


def duplicates(files: list[Path], root: Path):
    seen: dict[str, set[str]] = {}
    for f in files:
        for _, _, body, code in passages(f.read_text(errors="replace")):
            norm = re.sub(r"\W+", " ", body).strip().lower()
            if len(norm) >= 40 and not code:
                seen.setdefault(norm, set()).add(str(rel(f, root)))
    return [(k, sorted(v)) for k, v in seen.items() if len(v) > 1]


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = Path(args[0] if args else ".").resolve()
    files = find_files(root, "--user" in sys.argv)
    if not files:
        print(f"No agent instruction files under {root}.")
        return
    index = RepoIndex(root)
    scripts, targets = package_scripts(root), make_targets(root)
    results = {f: scan_file(f, root, index, scripts, targets) for f in files}

    print(f"# Instruction scan: {root}\n")
    print("| File | Loads (Claude Code, session at repo root) | Lines | ~Tokens |\n|---|---|---|---|")
    for f, r in results.items():
        print(f"| {rel(f, root)} | {r['kind']} | {r['lines']} | {r['tokens']} |")

    # Per-session load: startup files, their imports (recursively), and mandatory reads.
    startup = [f for f, r in results.items() if r["kind"].startswith("startup")]
    names = {rel(f, root) for f in files}
    has_claude = any(Path(n) in names for n in ("CLAUDE.md", ".claude/CLAUDE.md", "CLAUDE.local.md"))
    if not has_claude:
        startup = [f for f in startup if f.name != "AGENTS.md"] + \
                  [f for f in files if rel(f, root) == Path("AGENTS.md")]
    loaded, queue, reads = {}, [f.resolve() for f in startup], []
    depth = {p: 0 for p in queue}
    while queue:
        p = queue.pop(0)
        if p in loaded or not p.is_file():
            continue
        text = p.read_text(errors="replace")
        loaded[p] = len(text) // 4
        r = results.get(p) or scan_file(p, root, index, scripts, targets)
        for imp in r["imports"]:
            if depth[p] < 4 and imp not in loaded:
                depth[imp] = depth[p] + 1
                queue.append(imp)
        reads += [(p, loc, t) for loc, t in r["reads"]]
    read_tokens = {t: len(t.read_text(errors="replace")) // 4 for _, _, t in reads}
    print("\n**Per-session load** (Claude Code, session started at the repository root)")
    for p, tok in loaded.items():
        print(f"- {rel(p, root)}: ~{tok} tokens")
    for p, loc, t in reads:
        print(f"- required read {rel(t, root)} ({rel(p, root)} {loc}): ~{read_tokens[t]} tokens")
    total = sum(loaded.values()) + sum(read_tokens.values())
    print(f"- **Total: ~{total} tokens** ({sum(loaded.values())} loaded, {sum(read_tokens.values())} "
          "from instructions to read files first)")
    if not has_claude:
        print("- No CLAUDE.md, so Claude Code reads AGENTS.md instead")

    warnings = []
    for f, r in results.items():
        if r["kind"].startswith("startup") and r["lines"] > 200:
            warnings.append(f"{rel(f, root)} has {r['lines']} lines (Claude Code target: under 200)")
        if r["tree_lines"] >= 3:
            warnings.append(f"{rel(f, root)} contains a directory tree ({r['tree_lines']} lines)")
        if "template or fixture" in r["kind"] and f.name in ("CLAUDE.md", "AGENTS.md"):
            warnings.append(f"{rel(f, root)} sits under a template or fixture folder but is named like a live "
                            "instruction file; Claude Code loads it when it works in that folder")
    agents_bytes = sum(f.stat().st_size for f in files if f.name == "AGENTS.md")
    if agents_bytes > 32 * 1024:
        warnings.append(f"AGENTS.md files total {agents_bytes // 1024} KiB; Codex reads at most 32 KiB "
                        "along a path and drops the rest")
    if Path("CLAUDE.md") in names and Path("AGENTS.md") in names:
        if not re.search(r"(?m)^\s*@\.?/?AGENTS\.md\b", (root / "CLAUDE.md").read_text(errors="replace")):
            warnings.append("CLAUDE.md and AGENTS.md both exist but CLAUDE.md does not import "
                            "@AGENTS.md, so Claude Code does not read AGENTS.md by default")
    warnings += git_ignore_gaps(root)
    if warnings:
        print("\n**Warnings**")
        for w in warnings:
            print(f"- {w}")

    settings = read_settings(root)
    print("\n**Settings**")
    if not settings:
        print("- none")
    for name, data in settings:
        if "_error" in data:
            print(f"- {name}: {data['_error']}")
            continue
        perms = data.get("permissions", {})
        hooks = {event: len(v) for event, v in data.get("hooks", {}).items()}
        scope = " (personal: affects only this user's sessions)" if "local" in name else ""
        print(f"- {name}{scope}: allow {len(perms.get('allow', []))}, ask {len(perms.get('ask', []))}, "
              f"deny {len(perms.get('deny', []))}; hooks {hooks or 'none'}")
    conflicts = settings_conflicts(settings, {f: f.read_text(errors="replace") for f in startup}, root)
    if conflicts:
        print("\n**Allow rules that may contradict the instructions (check each)**")
        for c in conflicts:
            print(f"- {c}")
    print(f"\npackage.json scripts: {', '.join(sorted(scripts)) if scripts else 'none found'}")

    for f, r in results.items():
        print(f"\n## {rel(f, root)} ({r['kind']})\n")
        for key, title in (("broken_imports", "Broken @imports"),
                           ("missing_paths", "Backticked paths not found anywhere in the repository"),
                           ("missing_commands", "Commands not found")):
            if r[key]:
                print(f"**{title}**")
                for loc, item in r[key]:
                    print(f"- {loc}: {item}")
                print()
        if r["flags"]:
            print("**Flagged passages (candidates, judge each)**")
            for loc, labels, text in r["flags"]:
                print(f"- {loc} [{', '.join(labels)}] {text}")
        else:
            print("No flagged passages.")

    dups = duplicates(files, root)
    if dups:
        print("\n## Passages repeated across files\n")
        for text, where in dups[:30]:
            print(f"- \"{text[:100]}\" in {', '.join(where)}")


if __name__ == "__main__":
    main()
