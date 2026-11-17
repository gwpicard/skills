#!/usr/bin/env python3
"""List every hook Claude Code would load for a project, with its source.

Reads user, project and local settings, plus hooks.json from enabled plugins.
Skill and subagent frontmatter hooks are not listed: they load on invocation.

Usage: python3 hooks_inventory.py [--project DIR] [--json]
"""
import argparse
import json
import os

HOME = os.path.expanduser("~")


def load(path):
    try:
        with open(path) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def rows_from(hooks, source):
    rows = []
    for event, groups in (hooks or {}).items():
        for g in groups or []:
            for h in g.get("hooks") or []:
                target = h.get("command") or h.get("url") or h.get("prompt") or h.get("tool") or ""
                rows.append({
                    "source": source, "event": event, "matcher": g.get("matcher", ""),
                    "type": h.get("type", "command"), "if": h.get("if", ""),
                    "async": bool(h.get("async")), "timeout": h.get("timeout"),
                    "target": " ".join(str(target).split())[:160],
                })
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=os.getcwd())
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    rows, enabled, notes = [], {}, []
    settings_files = [
        ("user", os.path.join(HOME, ".claude/settings.json")),
        ("user-local", os.path.join(HOME, ".claude/settings.local.json")),
        ("project", os.path.join(a.project, ".claude/settings.json")),
        ("project-local", os.path.join(a.project, ".claude/settings.local.json")),
    ]
    for label, path in settings_files:
        d = load(path)
        if not d:
            continue
        rows += rows_from(d.get("hooks"), f"{label}: {path.replace(HOME, '~')}")
        enabled.update(d.get("enabledPlugins") or {})
        for flag in ("disableAllHooks", "allowManagedHooksOnly"):
            if d.get(flag):
                notes.append(f"{flag} is set in {path.replace(HOME, '~')}")

    installed = (load(os.path.join(HOME, ".claude/plugins/installed_plugins.json")) or {}).get("plugins", {})
    for plugin_id, on in enabled.items():
        if not on:
            continue
        for inst in installed.get(plugin_id, []):
            if inst.get("scope") in ("local", "project") and inst.get("projectPath") and \
                    os.path.abspath(inst["projectPath"]) != os.path.abspath(a.project):
                continue
            d = load(os.path.join(inst.get("installPath", ""), "hooks/hooks.json"))
            if d and d.get("hooks"):
                rows += rows_from(d.get("hooks"), f"plugin: {plugin_id}")
            elif d and d.get("modules"):
                notes.append(f"plugin {plugin_id} registers function-hook modules {d['modules']}; "
                             "read them to see which events they handle")
            break

    if a.json:
        print(json.dumps({"hooks": rows, "notes": notes}, indent=1))
        return
    if not rows:
        print("No hooks configured.")
    for r in rows:
        extra = " ".join(x for x in [f"if={r['if']}" if r["if"] else "", "async" if r["async"] else ""] if x)
        print(f"{r['event']:<18} matcher={r['matcher'] or '*':<20} {r['type']:<8} {extra}\n    {r['target']}\n    from {r['source']}")
    for n in notes:
        print("NOTE:", n)


if __name__ == "__main__":
    main()
