#!/usr/bin/env python3
"""Run a hook command against a sample event and report what Claude Code would do.

Builds the event JSON (common fields plus the fields you pass), pipes it to the
command through `sh -c`, and prints the exit code, timing, stdout, stderr and
the decision it implies. Use it on every proposed hook before installing it.

Examples:
  python3 try_hook.py --event PreToolUse --tool Bash --input '{"command":"rm -rf build"}' \
      --command 'bash ~/.claude/hooks/guard.sh'
  python3 try_hook.py --event PostToolUse --tool Write --input '{"file_path":"/tmp/x.ts"}' \
      --response '{"success":true}' --command 'bash ~/.claude/hooks/format.sh'
  python3 try_hook.py --event Stop --extra '{"stop_hook_active":false}' --command 'bash stop.sh'
"""
import argparse
import json
import os
import subprocess
import time

BLOCKING_EXIT2 = {"PreToolUse", "UserPromptSubmit", "UserPromptExpansion", "Stop", "SubagentStop",
                  "PreCompact", "ConfigChange", "PostToolBatch", "TaskCreated", "TaskCompleted",
                  "TeammateIdle", "PreModelSwitch"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--event", required=True)
    ap.add_argument("--command", required=True, help="the hook's command string, exactly as it will be configured")
    ap.add_argument("--tool", help="tool_name for tool events")
    ap.add_argument("--input", default="{}", help="tool_input as JSON")
    ap.add_argument("--response", help="tool_response as JSON (PostToolUse)")
    ap.add_argument("--extra", default="{}", help="other event fields as JSON, e.g. prompt, source, stop_hook_active")
    ap.add_argument("--cwd", default=os.getcwd())
    ap.add_argument("--timeout", type=float, default=60)
    a = ap.parse_args()

    event = {"session_id": "try-hook-test", "transcript_path": "/dev/null", "cwd": a.cwd,
             "permission_mode": "default", "hook_event_name": a.event}
    if a.tool:
        event.update(tool_name=a.tool, tool_input=json.loads(a.input), tool_use_id="toolu_test")
    if a.response:
        event["tool_response"] = json.loads(a.response)
    event.update(json.loads(a.extra))

    env = dict(os.environ, CLAUDE_PROJECT_DIR=a.cwd)
    start = time.time()
    try:
        p = subprocess.run(["sh", "-c", a.command], input=json.dumps(event), capture_output=True,
                           text=True, cwd=a.cwd, env=env, timeout=a.timeout)
        code, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT after {a.timeout}s: Claude Code treats this as a non-blocking error.")
        return
    ms = int((time.time() - start) * 1000)

    print(f"event: {a.event}   exit: {code}   time: {ms} ms")
    print("stdout:", out.strip()[:2000] or "(empty)")
    print("stderr:", err.strip()[:2000] or "(empty)")

    verdict = []
    if code == 2:
        if a.event in BLOCKING_EXIT2:
            verdict.append(f"BLOCKS ({a.event}); stderr is the reason Claude sees")
        elif a.event in ("PostToolUse", "PostToolUseFailure"):
            verdict.append("tool already ran; stderr is fed back to Claude")
        else:
            verdict.append(f"exit 2 does not block {a.event}")
        if out.strip().startswith("{"):
            verdict.append("WARNING: JSON on stdout is ignored when the exit code is 2")
    elif code == 0:
        s = out.strip()
        if s.startswith("{"):
            try:
                j = json.loads(s)
                hso = j.get("hookSpecificOutput") or {}
                if hso.get("permissionDecision"):
                    verdict.append(f"permissionDecision={hso['permissionDecision']}")
                if "updatedInput" in hso:
                    verdict.append("rewrites tool input (replaces the whole object)")
                if j.get("decision") == "block":
                    verdict.append("decision=block")
                if j.get("continue") is False:
                    verdict.append("continue=false: stops Claude entirely")
                if hso.get("additionalContext"):
                    verdict.append("adds context for Claude")
                if hso.get("hookEventName") and hso["hookEventName"] != a.event:
                    verdict.append(f"WARNING: hookEventName is {hso['hookEventName']}, expected {a.event}")
                verdict = verdict or ["valid JSON, no decision: normal flow"]
            except ValueError:
                verdict.append("WARNING: stdout starts with { but is not valid JSON; it will be ignored")
        elif s:
            verdict.append("plain stdout: added to context on SessionStart/UserPromptSubmit, "
                           "used as summary instructions on PreCompact, otherwise only in the debug log")
        else:
            verdict.append("no output: normal flow")
    else:
        verdict.append(f"exit {code} is a non-blocking error: the action proceeds (unless onFailure is 'block')")
    if ms > 2000:
        verdict.append(f"SLOW: {ms} ms on every matching event; consider async, an `if` filter or a narrower matcher")
    print("means:", "; ".join(verdict))


if __name__ == "__main__":
    main()
