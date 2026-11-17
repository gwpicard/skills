# Hook mechanics

Checked against https://code.claude.com/docs/en/hooks.md on 17 November 2026. Hooks change often: before proposing a field marked with a version, or any field not listed here, fetch that page and check it.

## Where hooks live

| Location | Scope | Use for |
|---|---|---|
| `~/.claude/settings.json` | every project, this user | personal habits: notifications, logging, general guards |
| `.claude/settings.json` | one project, committed | team rules: formatters, project test gates |
| `.claude/settings.local.json` | one project, not committed | personal rules for one project |
| plugin `hooks/hooks.json` | while the plugin is enabled | hooks that belong to a skill set you ship |
| skill frontmatter `hooks:` | from the skill's first invocation to the end of the session (`once: true` removes a hook after its first run) | checks tied to one workflow |
| subagent frontmatter `hooks:` | while that subagent runs (`Stop` becomes `SubagentStop`) | checks on one subagent's work |

Shape: `{"hooks": {"<Event>": [{"matcher": "<filter>", "hooks": [<handler>, ...]}]}}`.

Matcher: only letters, digits, `_`, `-`, spaces, commas and `|` → exact names, case-sensitive (`Edit|Write`). Any other character → JavaScript regex, unanchored (`mcp__github__.*`). Empty or `*` → everything. To match every tool of an MCP server, `.*` is required: `mcp__memory__.*`; a bare `mcp__memory` is an exact name and matches nothing. MCP tools are `mcp__<server>__<tool>`; plugin MCP servers are `mcp__plugin_<plugin>_<server>__<tool>`.

Handler fields: `type` (`command`, `http`, `mcp_tool`, `prompt`, `agent`), `command`, `args` (exec form, no shell), `timeout` (seconds), `if` (permission-rule syntax such as `Bash(git push *)`, tool events only; filters before the process starts), `async` (runs in the background, cannot block), `statusMessage`, `onFailure` (`"block"` makes a crashed guard block; v2.1.295+), `once` (skills only).

## Handler types

A hook does not have to be a shell script. Pick the type that fits the job:

| Type | What runs | Good for |
|---|---|---|
| `command` | a shell command; event JSON on stdin | deterministic checks, files, CLIs |
| `http` | POST of the event JSON to `url` (`headers`, `allowedEnvVars`); JSON response | webhooks: phone notifications, chat channels, team dashboards |
| `mcp_tool` | a tool on a configured MCP server (`server`, `tool`, `input`); text result read like stdout | acting in connected apps (Drive, Notion, Slack, Calendar, a database) without a script |
| `prompt` | one model call with `prompt` (`$ARGUMENTS` = event JSON; optional `model`); answers `{"ok": true}` or `{"ok": false, "reason": "..."}` | judgment: tone, completeness, privacy, "does this answer the question" |
| `agent` | a subagent that can Read, Grep and Glob before answering in the same format; experimental | judgment that needs the files: "does the doc match the brief", "are sources cited" |

`mcp_tool` details: `server` is the configured server name (plugin servers: `plugin:<plugin>:<server>`); string values in `input` accept `${path}` substitution from the event JSON, such as `"${tool_input.file_path}"`. A tool result with `isError: true` is a non-blocking error, except on PreToolUse, where an unreadable answer refuses the call.

Which events accept which types:
- all five: PreToolUse, PostToolUse, PostToolUseFailure, PostToolBatch, PermissionDenied, Stop, SubagentStop, UserPromptSubmit, UserPromptExpansion, TaskCreated, TaskCompleted, TeammateIdle;
- PermissionRequest: all except `agent`;
- `command`, `http`, `mcp_tool` only: Notification, PreCompact, PostCompact, SessionEnd, SubagentStart, FileChanged, CwdChanged, ConfigChange, InstructionsLoaded, MessageDisplay, StopFailure, WorktreeCreate, WorktreeRemove, PreModelSwitch, PostModelSwitch, Elicitation, ElicitationResult, DirectoryAdded;
- SessionStart: `command` and `mcp_tool` only, and `mcp_tool` is skipped at launch (MCP servers are not ready), running only after `/clear` or compaction; Setup: `command` only.

`try_hook.py` runs only `command` hooks. Test the other types live after installing (`claude --debug`), and say so in the proposal.

Default timeouts: 600 s for command, http and mcp_tool; 30 s for prompt; 60 s for agent. UserPromptSubmit is capped at 30 s. The SessionEnd hooks share 1.5 s unless a hook sets a longer timeout (maximum 60 s).

Variables: `$CLAUDE_PROJECT_DIR`, `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}`; SessionStart and CwdChanged can append `export` lines to `$CLAUDE_ENV_FILE`.

## Events most proposals use

| Event | Matcher matches | Can block | Typical use |
|---|---|---|---|
| SessionStart | `startup`, `resume`, `clear`, `compact`, `fork` | no | stdout is added to Claude's context |
| UserPromptSubmit | none | yes | add context; reject a prompt |
| PreToolUse | tool name | yes | guard, rewrite input, auto-approve |
| PermissionRequest | tool name | via `decision` JSON only | answer a permission dialog |
| PostToolUse | tool name | no (tool already ran) | format, lint, feed problems back, replace output |
| PostToolUseFailure | tool name | no | log failures |
| Stop | none | yes (Claude continues) | test gates, completeness checks |
| SubagentStop | agent type | yes | check a subagent's result |
| Notification | `permission_prompt`, `idle_prompt`, … | no | desktop alerts |
| PreCompact / PostCompact | `manual`, `auto` | Pre only | backups; PreCompact stdout steers the summary |
| SessionEnd | exit reason | no | cleanup, logging |
| FileChanged | literal file names joined by `\|` | no | react to edits made outside Edit/Write |

Other events exist (Setup, UserPromptExpansion, PostToolBatch, PermissionDenied, MessageDisplay, SubagentStart, TaskCreated, TaskCompleted, TeammateIdle, InstructionsLoaded, ConfigChange, CwdChanged, DirectoryAdded, WorktreeCreate, WorktreeRemove, PreModelSwitch, PostModelSwitch, Elicitation, ElicitationResult, StopFailure). Check the reference before using one.

## Input on stdin

Always: `session_id`, `transcript_path`, `cwd`, `permission_mode`, `hook_event_name`; inside a subagent also `agent_id`, `agent_type`.
PreToolUse: `tool_name`, `tool_input`, `tool_use_id`. PostToolUse adds `tool_response`. UserPromptSubmit: `prompt`. Stop: `stop_hook_active`, `last_assistant_message`. SessionStart: `source`. PreCompact: `trigger`, `custom_instructions`.

## Output

Exit codes: `0` success, stdout parsed as JSON if it starts with `{`. `2` blocking error, stderr is the reason, **stdout JSON ignored**. Anything else: non-blocking error, the action proceeds (unless `onFailure: "block"`).

Exit 2 blocks PreToolUse, UserPromptSubmit, Stop, SubagentStop, PreCompact, ConfigChange and a few others. On PostToolUse it only shows stderr to Claude. On SessionStart and SessionEnd it only shows stderr to the user. PermissionRequest ignores it.

Plain stdout reaches Claude only on SessionStart and UserPromptSubmit (as context) and PreCompact (as summary instructions).

JSON:
- Any event: `continue: false` (stops Claude entirely), `stopReason`, `suppressOutput`, `systemMessage` (shown to the user).
- PreToolUse: `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow|deny|ask|defer", "permissionDecisionReason": "...", "updatedInput": {...}, "additionalContext": "..."}}`. `updatedInput` replaces the whole input: copy unchanged fields. `allow` skips the prompt but does not override deny rules. `deny` applies even in bypassPermissions mode.
- PostToolUse: `{"decision": "block", "reason": "..."}` feeds the reason to Claude; `hookSpecificOutput.updatedToolOutput` replaces the result; `additionalContext` adds context.
- Stop / SubagentStop: `{"decision": "block", "reason": "..."}`; the reason becomes Claude's next instruction. Claude Code overrides a Stop hook after 8 consecutive blocks with no tool call in between (`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`).
- PermissionRequest: `{"hookSpecificOutput": {"hookEventName": "PermissionRequest", "decision": {"behavior": "allow|deny", "message": "..."}}}`.
- Prompt and agent hooks answer `{"ok": true}` or `{"ok": false, "reason": "..."}`. On Stop, `ok: false` makes Claude continue. On PreToolUse and PostToolUse a prompt hook's `ok: false` ends the turn unless `continueOnBlock: true`; an agent hook always behaves as if `continueOnBlock` were true. Tell the model to answer with raw JSON only: JSON wrapped in Markdown is not read, and the hook gives no verdict.

## Execution

All matching handlers run in parallel and each runs to completion; a deny from one does not cancel side effects in another. Identical handlers from several settings files run once. On PreToolUse the most restrictive result across hooks wins (deny > defer > ask > allow). A timed-out PreToolUse hook does not block unless `onFailure: "block"`. Hooks run with the user's full permissions. Project hooks need folder trust. Cloud sessions do not read `~/.claude/settings.json`; Cowork runs plugin hooks but not user-settings hooks. `disableAllHooks` and `allowManagedHooksOnly` switch hooks off silently. Debug with `claude --debug`; `/hooks` lists what is loaded.
