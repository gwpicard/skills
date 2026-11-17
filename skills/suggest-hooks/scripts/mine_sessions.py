#!/usr/bin/env python3
"""Mine local Claude Code session transcripts for signals that a hook would help.

Reads ~/.claude/projects/<encoded-path>/*.jsonl, streams each file, and writes
one JSON report of aggregate counts plus short, truncated examples. It never
writes inside the scanned folders and never copies whole messages.

Usage:
  python3 mine_sessions.py --days 30 --out /path/to/signals.json
  python3 mine_sessions.py --project my-repo --include-automated --out signals.json
"""
import argparse
import collections
import glob
import json
import os
import re
import sys
import time

ROOT = os.path.expanduser("~/.claude/projects")
SNIP = 180  # max characters kept from any message or command

AUTOMATED_CWD = re.compile(r"^(/private)?/(var/folders|tmp|var/tmp)/")
CMD_PREFIX = re.compile(r"^\s*((cd\s+[^;&|]+|[A-Za-z_][A-Za-z0-9_]*=\S*)\s*(;|&&)\s*)+")

CATEGORIES = {
    "format": re.compile(r"\b(prettier|black|ruff format|gofmt|rustfmt|cargo fmt|biome (format|check)|isort|swiftformat|clang-format)\b"),
    "lint": re.compile(r"\b(eslint|ruff check|ruff\b(?! format)|flake8|pylint|mypy|tsc\b|clippy|golangci-lint|shellcheck|stylelint|biome lint)\b"),
    "test": re.compile(r"\b(pytest|vitest|jest|npm (run )?test|pnpm (run )?test|yarn test|bun test|go test|cargo test|make test|unittest|playwright test)\b"),
    "build": re.compile(r"\b(npm run build|pnpm build|vite build|next build|cargo build|go build|make\b(?! test))"),
}
RISKY = {
    "rm -rf": re.compile(r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f|\brm\s+-[a-zA-Z]*f[a-zA-Z]*r"),
    "git push --force": re.compile(r"git push\b.*(--force(?!-with-lease)|\s-f\b)"),
    "git reset --hard": re.compile(r"git reset --hard"),
    "git clean -f": re.compile(r"git clean -[a-zA-Z]*f"),
    "git checkout -- / restore": re.compile(r"git (checkout --|restore\s)"),
    "git push to main": re.compile(r"git push\b[^;&|]*\b(main|master)\b"),
    "sudo": re.compile(r"(^|[;&|]\s*)sudo\b"),
    "curl | sh": re.compile(r"curl[^|]*\|\s*(ba|z)?sh"),
    "publish/deploy": re.compile(r"\b(npm publish|netlify deploy --prod|vercel --prod|fly deploy|gh release create)\b"),
    "drop/truncate SQL": re.compile(r"\b(psql|sqlite3|mysql|duckdb)\b.*\b(DROP TABLE|TRUNCATE|DROP DATABASE)\b", re.I),
}
SENSITIVE_PATH = re.compile(r"(^|/)(\.env[^/]*|.*\.pem|.*\.key|id_rsa[^/]*|package-lock\.json|pnpm-lock\.yaml|yarn\.lock|uv\.lock|poetry\.lock|Cargo\.lock|\.git/.*|.*secrets?[^/]*)$")
CORRECTION = re.compile(
    r"\b(don'?t|do not|never|always|stop|instead|again|you forgot|forgot to|i told you|i said|"
    r"didn'?t (run|test|check)|run the tests|before you|make sure|remember to|why did you)\b", re.I)
NOISE_PROMPT = re.compile(r"^\s*(<command-|<local-command|<system-reminder>|<task-notification>|<bash-|<pasted_content|<agent-message|Caveat:|\[Request interrupted)")
OUTBOUND_TOOL = re.compile(r"(send|post|share|publish|comment|reply|create_event|update_event|create_file|update_file|"
                           r"upload|deploy|trash|delete|merge|create_issue|create_pr|respond)", re.I)
OUTBOUND_BASH = re.compile(r"\bgh (issue|pr) (comment|create|close|merge|edit|review)|\bgh release create|\bgh repo create|"
                           r"\bgit push\b|\b(curl|http)\b.*-X ?(POST|PUT|PATCH|DELETE)")
INTERRUPT = "[Request interrupted by user"
REJECT = "The user doesn't want to proceed with this tool use"
CLASSIFIER_DENY = re.compile(r"denied by the Claude Code auto mode classifier\. Reason: \[([^\]]+)\]")
NOT_FOUND = re.compile(r"(?:command not found: ?|: command not found|No such file or directory: ')([\w.\-/]+)")


def snip(text, n=SNIP):
    text = re.sub(r"\s+", " ", str(text)).strip()
    return text if len(text) <= n else text[: n - 1] + "…"


def first_line(cmd):
    """The command as typed, without leading cd/VAR= steps or heredoc bodies."""
    return CMD_PREFIX.sub("", str(cmd).strip().split("\n", 1)[0]).strip()


def cmd_head(cmd):
    cmd = first_line(cmd)
    parts = cmd.split()
    if not parts:
        return ""
    if parts[0] in {"npx", "uv", "uvx", "pnpm", "npm", "yarn", "bun", "python", "python3", "git", "gh", "cargo", "go", "make", "docker"} and len(parts) > 1:
        sub = parts[1] if not parts[1].startswith("-") else (parts[2] if len(parts) > 2 else "")
        if parts[0] in {"python", "python3"} and sub == "-m" and len(parts) > 2:
            sub = "-m " + parts[2]
        return f"{parts[0]} {sub}".strip()
    return parts[0]


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        out = []
        for c in content:
            if isinstance(c, dict):
                if c.get("type") == "text":
                    out.append(c.get("text", ""))
                elif isinstance(c.get("content"), (str, list)):
                    out.append(text_of(c["content"]))
        return "\n".join(out)
    return ""


def project_name(folder):
    # Encoded path: -Users-name-PROJECTS-repo -> last meaningful chunk.
    m = re.search(r"PROJECTS-(.+)$", folder)
    return (m.group(1) if m else folder.lstrip("-"))[:60]


class Stats:
    def __init__(self):
        self.c = collections.defaultdict(collections.Counter)
        self.examples = collections.defaultdict(list)
        self.sessions = collections.Counter()

    def ex(self, key, value, limit=12):
        if len(self.examples[key]) < limit and value not in self.examples[key]:
            self.examples[key].append(value)


def scan_file(path, st, include_automated):
    folder = os.path.basename(os.path.dirname(path))
    proj = project_name(folder)
    kind = None
    pending = {}  # tool_use_id -> (name, input)
    recent_edits = collections.deque(maxlen=4)  # extensions of the last edits, consumed by follow-up commands
    last_test = None  # (ok, cmd) of the last test command in the session
    after_interrupt = False
    first_prompt = None
    try:
        fh = open(path, encoding="utf-8", errors="replace")
    except OSError:
        return
    with fh:
        for line in fh:
            if '"type":"assistant"' not in line and '"type":"user"' not in line and '"type":"system"' not in line:
                continue
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if kind is None and d.get("type") == "user":
                automated = d.get("entrypoint") == "sdk-cli" or bool(AUTOMATED_CWD.match(d.get("cwd") or ""))
                kind = "automated" if automated else "interactive"
                if automated and not include_automated:
                    st.sessions["skipped_automated"] += 1
                    return
                st.sessions[kind] += 1
                st.c["projects"][proj] += 1
            if kind is None:
                continue
            t = d.get("type")
            if t == "system":
                sub = d.get("subtype")
                st.c["system_events"][sub] += 1
                if sub == "stop_hook_summary":
                    for h in d.get("hookInfos") or []:
                        st.c["existing_stop_hooks"][snip(h.get("command", ""), 120)] += 1
                    if d.get("preventedContinuation"):
                        st.c["stop_hook_effects"]["prevented_continuation"] += 1
                    if d.get("hookErrors"):
                        st.c["stop_hook_effects"]["errors"] += 1
                if sub == "compact_boundary":
                    st.c["compactions"][proj] += 1
                continue
            msg = d.get("message") or {}
            content = msg.get("content") if isinstance(msg, dict) else None
            if t == "assistant" and isinstance(content, list):
                for c in content:
                    if not isinstance(c, dict) or c.get("type") != "tool_use":
                        continue
                    name, inp = c.get("name", "?"), c.get("input") or {}
                    pending[c.get("id")] = (name, inp)
                    st.c["tools"][name if not name.startswith("mcp__") else "mcp__" + name.split("__")[1]] += 1
                    if name.startswith("mcp__"):
                        st.c["mcp_tools"][name[:90]] += 1
                        short = name.split("__")[-1]
                        if OUTBOUND_TOOL.search(short) and not re.search(r"(reader|read|get|list|search|query)", short, re.I):
                            st.c["outbound_actions"][name[:90]] += 1
                    if name == "Artifact" and inp.get("action", "publish") == "publish":
                        st.c["outbound_actions"]["Artifact publish"] += 1
                    if name in ("WebFetch", "WebSearch"):
                        st.c["research"][name] += 1
                    if name == "Skill":
                        st.c["skills_invoked"][str(inp.get("skill") or inp.get("command") or "?")[:60]] += 1
                    if name in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
                        fp = str(inp.get("file_path") or inp.get("notebook_path") or "")
                        ext = os.path.splitext(fp)[1].lower() or "(none)"
                        st.c["edited_ext"][ext] += 1
                        recent_edits.append(ext)
                        if SENSITIVE_PATH.search(fp):
                            st.c["sensitive_edits"][os.path.basename(fp)] += 1
                            st.ex("sensitive_edits", f"{proj}: {snip(fp, 100)}")
                    if name == "Bash":
                        cmd = first_line(inp.get("command", ""))
                        st.c["bash_heads"][cmd_head(cmd)] += 1
                        ob = OUTBOUND_BASH.search(cmd)
                        if ob:
                            st.c["outbound_actions"]["Bash: " + " ".join(ob.group(0).split()[:3])] += 1
                        for cat, rx in CATEGORIES.items():
                            if rx.search(cmd):
                                st.c["bash_categories"][cat] += 1
                                st.c[f"{cat}_commands"][snip(cmd, 80)] += 1
                                if recent_edits and cat in ("format", "lint"):
                                    for ext in set(recent_edits):
                                        st.c["post_edit_followups"][f"{cat} after {ext}"] += 1
                                    st.ex(f"post_edit_{cat}", snip(cmd, 100))
                        for label, rx in RISKY.items():
                            if rx.search(cmd):
                                st.c["risky_commands"][label] += 1
                                st.ex(f"risky:{label}", f"{proj}: {snip(cmd, 120)}", 5)
                        recent_edits.clear()
            elif t == "user":
                if isinstance(content, list) and any(isinstance(c, dict) and c.get("type") == "tool_result" for c in content):
                    for c in content:
                        if not isinstance(c, dict) or c.get("type") != "tool_result":
                            continue
                        name, inp = pending.pop(c.get("tool_use_id"), ("?", {}))
                        body = text_of(c.get("content"))
                        if REJECT in body:
                            st.c["user_rejections"][name] += 1
                            tail = body.split("the user said:", 1)[1] if "the user said:" in body else ""
                            if tail.strip():
                                st.ex("rejection_reasons", f"{name}: {snip(tail)}")
                            continue
                        m = CLASSIFIER_DENY.search(body)
                        if m:
                            st.c["classifier_denials"][m.group(1)] += 1
                            if name == "Bash":
                                st.ex(f"denied:{m.group(1)}", snip(first_line(inp.get("command", "")), 120), 4)
                            continue
                        if c.get("is_error"):
                            st.c["tool_errors"][name] += 1
                            if name == "Bash":
                                head = cmd_head(str(inp.get("command", "")))
                                st.c["failing_bash_heads"][head] += 1
                                nf = NOT_FOUND.search(body)
                                if nf:
                                    st.c["not_found"][nf.group(1)[:60]] += 1
                        if name == "Bash" and CATEGORIES["test"].search(first_line(inp.get("command", ""))):
                            last_test = (not c.get("is_error"), snip(first_line(inp.get("command", "")), 80))
                    continue
                if d.get("isMeta") or d.get("isSidechain"):
                    continue
                text = text_of(content)
                if INTERRUPT in text:
                    st.c["interrupts"][proj] += 1
                    after_interrupt = True
                    continue
                if not text.strip() or NOISE_PROMPT.match(text):
                    continue
                st.c["prompts"][proj] += 1
                if first_prompt is None:
                    first_prompt = text
                if after_interrupt:
                    st.ex("after_interrupt", snip(text), 25)
                    after_interrupt = False
                if kind == "interactive" and CORRECTION.search(text) and len(text) < 1500:
                    st.ex("corrections", snip(text), 60)
                    st.c["correction_words"][CORRECTION.search(text).group(1).lower()] += 1
    if first_prompt:
        st.c["opening_prompts"][snip(first_prompt, 70).lower()] += 1
    if last_test is not None and not last_test[0]:
        st.c["sessions_ending_with_failed_test"][proj] += 1
        st.ex("ended_with_failed_test", f"{proj}: {last_test[1]}", 8)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--days", type=int, default=30, help="only sessions modified in the last N days (default 30)")
    ap.add_argument("--project", action="append", default=[], help="substring of the encoded project folder; repeatable")
    ap.add_argument("--include-automated", action="store_true", help="also scan SDK runs and sessions in temporary folders")
    ap.add_argument("--max-sessions", type=int, default=2000, help="stop after this many scanned sessions (newest first)")
    ap.add_argument("--top", type=int, default=25, help="entries kept per counter")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    cutoff = time.time() - a.days * 86400
    files = []
    for f in glob.glob(os.path.join(ROOT, "*", "*.jsonl")):
        if a.project and not any(p in f for p in a.project):
            continue
        try:
            if os.path.getmtime(f) >= cutoff:
                files.append(f)
        except OSError:
            pass
    files.sort(key=os.path.getmtime, reverse=True)

    st = Stats()
    started = time.time()
    i = 0
    for i, f in enumerate(files, 1):
        scan_file(f, st, a.include_automated)
        if st.sessions["interactive"] + st.sessions["automated"] >= a.max_sessions:
            break
        if i % 1000 == 0:
            print(f"  scanned {i}/{len(files)} files", file=sys.stderr)

    report = {
        "scope": {"days": a.days, "projects_filter": a.project, "include_automated": a.include_automated,
                  "files_in_window": len(files), "files_read": i, "seconds": round(time.time() - started, 1)},
        "sessions": dict(st.sessions),
        "counts": {k: dict(v.most_common(a.top)) for k, v in sorted(st.c.items())},
        "examples": dict(st.examples),
    }
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w") as fh:
        json.dump(report, fh, indent=1, ensure_ascii=False)
    print(f"wrote {a.out}: {st.sessions.get('interactive', 0)} interactive, "
          f"{st.sessions.get('automated', 0)} automated, {st.sessions.get('skipped_automated', 0)} automated skipped "
          f"in {report['scope']['seconds']}s")


if __name__ == "__main__":
    main()
