# Signal-to-hook catalog

Each entry names the signal in `signals.json` that justifies it, the hook, and its costs. Adapt the scripts to the user's tools; never propose an entry whose signal is absent or weak. Scripts assume `jq` (check `command -v jq`; otherwise write them in Python). Evidence and sources for each pattern are in `field-notes.md`.

Rules that apply to every guard: make it fail closed (`"onFailure": "block"`, or `|| exit 2` in the script), because a crashed guard lets the action through; keep hard bans in permission deny rules too, because regex guards are bypassable and Edit/Write guards miss writes made through Bash.

## 1. Format or lint after edits
**Signal:** `post_edit_followups`, `format_commands`, `lint_commands`; edited extensions in `edited_ext` match a formatter the project already uses.
**Hook:** PostToolUse, matcher `Edit|Write|MultiEdit`, project settings.
```bash
#!/bin/bash
f=$(jq -r '.tool_input.file_path // empty'); [ -z "$f" ] && exit 0
case "$f" in
  *.ts|*.tsx|*.js|*.jsx|*.css|*.json) npx --no-install prettier --write --log-level warn "$f" ;;
  *.py) ruff format -q "$f" && ruff check -q --fix "$f" ;;
esac
exit 0
```
**Costs:** latency on every edit (`npx` start-up included); only formats files written by Edit/Write, not by Bash. If formatting makes Claude's next edit fail to match, format at Stop or PostToolBatch instead. Never run the full test suite here. To return lint problems to Claude, print them on stderr and `exit 2`. Use the project's own formatter config; do not introduce a new formatter.

## 2. Guard a risky command
**Signal:** `risky_commands`, `classifier_denials` and `rejection_reasons` show a command the user does not want run, or keeps having to stop.
**Hook:** PreToolUse, matcher `Bash`, `if` narrowed to the command (for example `Bash(git push *)`), user settings.
```bash
#!/bin/bash
CMD=$(jq -r '.tool_input.command')
if echo "$CMD" | grep -qE 'git push\b.*(--force([^-]|$)| -f\b)'; then
  jq -n '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"deny",
    permissionDecisionReason:"Use --force-with-lease instead of --force."}}'
fi
exit 0
```
**Choose the decision:** `deny` when the action is never wanted; `ask` when it is sometimes wanted (the user gets a prompt even in auto mode); a rewrite with `updatedInput` when a safer equivalent exists. Do not duplicate what the auto-mode classifier already blocks (force-pushes, unreviewed merges, production deploys, `curl | bash`, credential exposure). Propose a guard only where it adds something: a deterministic result, a rule specific to this user, a tool the classifier does not cover, enforcement that must hold in bypassPermissions or `-p` runs, or a cheaper path than a denial that costs the user a round. Simple warn/block rules on a regex can also be written as `hookify` rules (official plugin) if the user has it.

## 3. Rewrite a command that keeps failing
**Signal:** `not_found` or `failing_bash_heads` shows the same wrong binary or flag repeatedly (for example `python` where only `python3` exists).
**Hook:** PreToolUse, matcher `Bash`, returning `updatedInput` with the corrected `command` (copy every other input field). Prefer fixing the environment or CLAUDE.md first if one line there would do; propose the hook only when the mistake recurs despite that.

## 4. Re-inject context after compaction
**Signal:** `compactions` per project is high, and the user repeats rules or context after long sessions.
**Hook:** SessionStart, matcher `compact`, project settings. Print a short reminder: the three or four rules that must survive, the current task file, `git status -s | head`.
**Costs:** context tokens on every compaction. Keep it under about 20 lines.

## 5. Session start briefing
**Signal:** `opening_prompts` show the user starting sessions with the same context ("read the handoff file", "what's next") or pasting the same block.
**Hook:** SessionStart, matcher `startup|resume`, printing the branch, uncommitted changes and the first lines of the handoff or plan file if it exists. If a skill already does this on demand, prefer the skill.

## 6. Test gate before Claude stops
**Signal:** `sessions_ending_with_failed_test`, or corrections such as "you didn't run the tests".
**Hook:** Stop, project settings, only in projects with a fast test command (under about 60 s).
```bash
#!/bin/bash
IN=$(cat)
git diff --quiet HEAD -- . 2>/dev/null && exit 0     # nothing changed: let Claude stop
OUT=$(npm test 2>&1) && exit 0
jq -n --arg r "Tests fail. Fix them before finishing:
$(echo "$OUT" | tail -30)" '{decision:"block",reason:$r}'
```
**Costs:** runs the suite at every stop, including stops after questions. Claude Code overrides the hook after 8 consecutive blocks. Exit early when `stop_hook_active` is true if one retry is enough. A `type: "prompt"` Stop hook ("are all requested tasks done?") is a cheaper alternative when there is no test suite.

## 7. Notifications when Claude waits
**Signal:** many `away_summary` events, `idle_prompt` waits, long `turn_duration`; and no notification hook in the inventory.
**Hook:** Notification, matcher `permission_prompt|idle_prompt`, user settings, `async: true`.
```bash
osascript -e 'display notification "Claude needs you" with title "Claude Code"'
```
Check first that nothing in the inventory already notifies (status apps, terminal integrations). osascript fails silently without notification permission for Script Editor.

## 8. Back up transcripts before compaction
**Signal:** many `compactions` and the user relies on old context (handoffs, "what did we decide").
**Hook:** PreCompact, user settings, `async: true`: copy `transcript_path` to a backup folder named by `session_id` and date.

## 9. Audit log
**Signal:** the user asks what an agent did, runs autonomous loops, or has many classifier denials.
**Hook:** PreToolUse (to log attempts, including denied ones) on `Bash`, `async: true`, appending a timestamp, `session_id`, `cwd` and the command to a JSONL file. This also produces cleaner data for the next run of this skill than transcripts do.

## 10. Protect files
**Signal:** `sensitive_edits` (lockfiles, `.env`, generated files), or corrections about editing a file that must not be edited.
**Hook:** PreToolUse, matcher `Edit|Write|MultiEdit`, deny with a reason that names the right way to change the file (for example "run `npm install`, do not edit package-lock.json").

## 11. Checks scoped to one skill or plugin
**Signal:** the user maintains skills or plugins, and a correction recurs only during one workflow.
**Hook:** in that skill's frontmatter `hooks:` or the plugin's `hooks/hooks.json`, so it ships with the skill. A skill's hooks stay registered from its first invocation to the end of the session; add `once: true` for a one-off check, or use a subagent's frontmatter when the check must end with the work. Propose it as an edit to the skill, not to settings.

## Knowledge work: writing, research, communication, connected apps

Hooks are not only for code. These use `prompt`, `agent`, `mcp_tool` and `http` handlers. Check `references/mechanics.md` for which events accept each type.

## 12. Writing standard on documents
**Signal:** most edits in `edited_ext` are `.md`, `.html` or `.txt`; corrections about tone, banned words or the glossary; the user greps their own drafts for a pattern.
**Hook:** PostToolUse, matcher `Edit|Write`, `if: "Edit(**/*.md)"` (add a second handler for `Write(**/*.md)`).
- Cheap: a `command` hook that greps the new text (`tool_input.new_string` or `tool_input.content`) for banned patterns and prints them on stderr with `exit 2`, so Claude fixes them.
- Judgment: a `prompt` hook: "Here is text just written: $ARGUMENTS. Return ok:false with the lines that break these rules: <the project's three to five writing rules>." Set `continueOnBlock: true` so Claude revises instead of ending the turn, and end the prompt with "Answer with raw JSON only". Start with the command version; it costs nothing and is what practitioners keep.
**Costs:** a model call per document edit with the prompt type; keep it to document paths.

## 13. Check before anything leaves the machine
**Signal:** `outbound_actions` (sends, shares, posts, comments, publishes through MCP tools, `gh` comments, artifacts); classifier denials such as External System Writes or Unsanctioned Communication; rejections of those calls.
**Hook:** PreToolUse, matcher naming those tools exactly (for example `mcp__claude_ai_Gmail__send_message|mcp__claude_ai_Slack__post_message`); to cover a whole server use `mcp__<server>__.*`, never a bare `mcp__<server>`.
- `prompt` hook: "This message is about to be sent: $ARGUMENTS. Return ok:false if it contains private client details, credentials, unverified claims, or a tone unsuitable for the recipient." Blocks with a reason Claude can act on.
- Or a `command` hook returning `permissionDecision: "ask"`, so the user always confirms, even in auto mode.

## 14. Answer quality before Claude stops
**Signal:** research or writing sessions (high WebSearch/WebFetch counts, many document edits) followed by corrections such as "you didn't answer", "where is the source", "that's not what I asked".
**Hook:** Stop, `prompt` hook: "Did the last answer address every part of the user's request, and is each factual claim tied to a source or marked as unverified? $ARGUMENTS". Use an `agent` hook instead when the check needs to open the files written. Claude Code overrides a Stop hook after 8 consecutive blocks.

## 15. Keep a sources log during research
**Signal:** many WebFetch/WebSearch or browser calls, and later requests to cite or find "that page from before".
**Hook:** PostToolUse, matcher `WebFetch|WebSearch`, `async: true`, a `command` that appends the date, `session_id`, URL or query to `research-log.jsonl` in the project. Zero context cost.

## 16. Act in a connected app at the right moment
**Signal:** the user repeatedly asks Claude to record something in another app after a step (log a decision, update a tracker, file a note), and the MCP server is configured.
**Hook:** `mcp_tool` handler on the event that marks the step, with `input` filled from the event, for example PostToolUse on `Artifact` that appends the published link to a tracker document, or Stop that adds a line to a work log. The tool's text result is read like stdout.
**Costs:** a write to an external system on every match: prefer a narrow matcher, and an append-only tool.

## 17. Reach the user away from the terminal
**Signal:** many `away_summary` events or long waits for input, and the user leaves sessions running.
**Hook:** Notification (matcher `permission_prompt|idle_prompt`) and optionally Stop, `http` handler posting to a push service or chat webhook (ntfy, a Slack incoming webhook). Put the URL in an environment variable and list it in `allowedEnvVars`; never write a secret into settings.

## 18. Guard browser automation
**Signal:** heavy `mcp__claude-in-chrome` (or other browser) use, plus rejections or classifier denials on form submissions, uploads or purchases.
**Hook:** PreToolUse on the browser tools that submit or upload (for example `mcp__claude-in-chrome__(form_input|file_upload)`), with `permissionDecision: "ask"` or a `prompt` hook that checks the target site and the data being sent.

## 19. Learn which skills and instructions are used
**Signal:** the user maintains skills, plugins or long instruction files, and wants to know which ones matter.
**Hook:** async command hooks appending one line per event to a local JSONL file (mode 0600): PostToolUse with matcher `Skill`, UserPromptExpansion for slash commands, InstructionsLoaded for instruction files. Log names, sizes and session IDs, not content. Check `/skill-doctor` first: it reports skill usage and context cost without a hook.

## Not hooks
Some signals call for something else. Say so instead of forcing a hook:
- a stable fact or preference → one line in CLAUDE.md;
- a repeated permission prompt for a safe command → an allow rule (`/fewer-permission-prompts`);
- a multi-step workflow the user starts by hand → a skill or slash command.
