#!/usr/bin/env python3
"""Extract readable transcripts from Claude Code and Codex session logs.

  python3 extract_logs.py --match <substring> [--match ...] [--since YYYY-MM-DD] [--until YYYY-MM-DD]
                          [--out DIR] [--max-user 4000] [--max-assistant 2500] [--min-assistant 200]

Claude Code: ~/.claude/projects/<encoded-path>/*.jsonl, where the folder name contains a --match
substring (path separators become "-" in folder names, so match on a distinctive name).
Codex: ~/.codex/sessions/**/rollout-*.jsonl, where the session's cwd contains a --match substring.

Writes one Markdown file per session to DIR (default: a new temporary folder), plus INDEX.md
with size, date, source and working folder. Tool calls, tool output and images are left out.
Sessions whose working folder is a temporary folder (often subagents or approval reviews) are
marked "temp" in the index.
"""
import argparse, glob, json, os, sys, tempfile
from datetime import datetime


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(x.get("text", "") for x in content
                         if isinstance(x, dict) and x.get("type") in ("text", "input_text", "output_text"))
    return ""


def in_range(ts, since, until):
    d = (ts or "")[:10]
    return (not since or d >= since) and (not until or d <= until)


def skip_user(s):
    s = s.lstrip()
    return (not s or s.startswith("<system-reminder") or s.startswith("<environment_context")
            or s.startswith("<user_instructions") or s.startswith("<skills_instructions")
            or s.startswith("<task-notification") or s.startswith("<local-command")
            or s.startswith("<command-") or "[Subagent hand-back]" in s[:300]
            or "AGENTS.md" in s[:200])


def claude_sessions(matches, a):
    root = os.path.expanduser("~/.claude/projects")
    for d in sorted(glob.glob(os.path.join(root, "*"))):
        if not any(m in os.path.basename(d) for m in matches):
            continue
        for f in sorted(glob.glob(os.path.join(d, "*.jsonl"))):
            out, first, cwd = [], None, os.path.basename(d)
            for line in open(f, errors="ignore"):
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                if e.get("isSidechain"):
                    continue
                ts, m = e.get("timestamp", ""), e.get("message") or {}
                if not in_range(ts, a.since, a.until):
                    continue
                first = first or ts
                cwd = e.get("cwd", cwd)
                s = text_of(m.get("content"))
                if e.get("type") == "user" and not skip_user(s) and "tool_use_id" not in s:
                    out.append(f"\n### USER {ts[:16]}\n{s[:a.max_user]}")
                elif e.get("type") == "assistant" and len(s.strip()) >= a.min_assistant:
                    out.append(f"\n--- ASSISTANT {ts[:16]}\n{s[:a.max_assistant]}")
            if out:
                yield "claude", f, first, cwd, out


def codex_sessions(matches, a):
    for f in sorted(glob.glob(os.path.expanduser("~/.codex/sessions/**/rollout-*.jsonl"), recursive=True)):
        try:
            with open(f, errors="ignore") as fh:
                meta = json.loads(fh.readline())
        except (ValueError, OSError):
            continue
        cwd = (meta.get("payload") or {}).get("cwd", "")
        if not any(m in cwd for m in matches):
            continue
        out, first = [], None
        for line in open(f, errors="ignore"):
            try:
                e = json.loads(line)
            except ValueError:
                continue
            p, ts = e.get("payload") or {}, e.get("timestamp", "")
            if e.get("type") != "response_item" or p.get("type") != "message" or not in_range(ts, a.since, a.until):
                continue
            first = first or ts
            s = text_of(p.get("content"))
            if p.get("role") == "user" and not skip_user(s):
                out.append(f"\n### USER {ts[:16]}\n{s[:a.max_user]}")
            elif p.get("role") == "assistant" and len(s.strip()) >= a.min_assistant:
                out.append(f"\n--- AGENT {ts[:16]}\n{s[:a.max_assistant]}")
        if out:
            yield "codex", f, first, cwd, out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--match", action="append", required=True)
    ap.add_argument("--since"); ap.add_argument("--until")
    ap.add_argument("--out")
    ap.add_argument("--max-user", type=int, default=4000)
    ap.add_argument("--max-assistant", type=int, default=2500)
    ap.add_argument("--min-assistant", type=int, default=200)
    a = ap.parse_args()
    out = a.out or tempfile.mkdtemp(prefix="harvest-")
    os.makedirs(out, exist_ok=True)
    rows = []
    for gen in (claude_sessions(a.match, a), codex_sessions(a.match, a)):
        for src, f, first, cwd, parts in gen:
            name = f"{src}-{(first or '')[:16].replace(':', '')}-{os.path.basename(f)[-14:-6]}.md"
            body = f"Source: {f}\nWorking folder: {cwd}\n" + "".join(parts)
            open(os.path.join(out, name), "w").write(body)
            temp = cwd.startswith(("/tmp", "/private/tmp", "/var/folders"))
            rows.append((first or "", src, name, len(body), cwd, temp))
    rows.sort()
    with open(os.path.join(out, "INDEX.md"), "w") as ix:
        ix.write(f"# Harvest index ({datetime.now():%Y-%m-%d})\n\n| Start | Source | File | KB | Working folder | Note |\n|---|---|---|---|---|---|\n")
        for first, src, name, size, cwd, temp in rows:
            ix.write(f"| {first[:16]} | {src} | {name} | {size // 1024} | {cwd} | {'temp' if temp else ''} |\n")
    total = sum(r[3] for r in rows) // 1024
    print(f"{len(rows)} sessions, {total} KB of text -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
