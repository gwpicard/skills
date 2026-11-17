# Field notes: what practitioners run, keep and remove

Researched on 17 November 2026 by four agents reading the official docs, Anthropic's plugins, community repositories and practitioner write-ups. Most pages were read through a summarising fetch, so quotes may not be verbatim; contested points were rechecked against the raw hooks reference. Claims from search results only are left out. Use these notes to judge a candidate, then cite the source in the proposal when it helps the user decide.

Evidence labels: **strong** (several independent users or an official example), **some** (one detailed user report or an official plugin), **docs only** (supported by the docs, little real use found).

## What survives in practice

The hooks practitioners keep are few and quiet. Several write-ups converge on the same short list: a formatter, a destructive-command guard, a short SessionStart context and a completion notification. "The hooks that died were loud": per-edit test runs, context-window warnings, bundle-size checks and commit-message enforcers. **(strong)**
- rentierdigital, hooks survival guide (2026-04-02): https://rentierdigital.xyz/blog/claude-code-hooks-survival-guide
- disler, claude-code-hooks-mastery (about 4k stars): https://github.com/disler/claude-code-hooks-mastery
- examples collection: https://www.web-developpeur.com/en/blog/claude-code-hooks-exemples

Consequence for proposals: prefer fewer, quieter hooks; propose a noisy check only with strong evidence; offer a warn-only first version for anything that might misfire.

## Coding

| Pattern | Evidence | Notes and sources |
|---|---|---|
| Format after Edit/Write | strong | Lead example of the official guide. `npx` start-up costs time on every edit; when formatting fights Claude's next edit, format at Stop or PostToolBatch instead. https://code.claude.com/docs/en/hooks-guide.md |
| Type-check feedback (`tsc --noEmit`, truncated, exit 2) | some | The one quality hook rentierdigital kept. Always truncate output. |
| Batch checks once per parallel batch (PostToolBatch) | docs only | Fires once per batch and can block. https://agentpatterns.ai/tool-engineering/posttoolbatch-hook-batch-boundary/ |
| Full test suite after every edit | anti-pattern | 4–8 s per save; removed by its author. Run tests at Stop, gated on "files changed". https://dev.to/subprime2010/claude-code-hooks-auto-format-auto-lint-auto-test-on-every-save-4ani |
| Destructive-command guard | strong | hooks-mastery blocks `rm -rf` and `.env` access; rentierdigital's git guard caught a force-push on day one. Regex guards are bypassable (`$(...)`, aliases, scripts). |
| TDD enforcement | some | nizos/tdd-guard (about 2.4k stars) starts a separate Claude session per edit: real model cost and latency. https://github.com/nizos/tdd-guard |
| Rewrite commands (`updatedInput`) | some | Most practitioners block with a message instead ("use pnpm") so Claude sees what ran. Rewrite only when trivially safe. |

## Knowledge work

Real-world use outside coding is thin. Prefer command hooks; use prompt or agent hooks only for a judgment-based correction that recurs in the user's sessions.

| Pattern | Evidence | Notes and sources |
|---|---|---|
| Prose lint on document edits (command, exit 2) | strong | slop-linter: Vale rules tuned against about 3,900 comments. https://github.com/thrash-d/slop-linter. hookify: regex warn/block rules. https://github.com/anthropics/claude-plugins-official/tree/main/plugins/hookify. Start in warn mode. |
| Allowlist guard for a browser or MCP tool | some | A Playwright guard limiting navigation to localhost: https://mythos.one/me/brianswichkow/149777. A default-deny Bash allowlist inside a Slack-posting skill: https://quickchat.ai/post/claude-code-skill-watches-coding-sessions-shares-to-slack |
| Context at UserPromptSubmit, transcript backup at PreCompact | some | Anthropic's own article: https://claude.com/resources/articles/how-to-configure-hooks |
| `mcp_tool` hook after edits or at Stop (scan, tracker update) | some | https://dev.to/speedy_devv/mcp-tool-hooks-in-claude-code-24f6. Fails open if the server is disconnected; never starts an OAuth flow. |
| Prompt hook on Stop for tone or unsupported claims | docs only | Narrow criteria only. Trail of Bits notes that a small model can wrap its JSON in Markdown and the hook then fails silently; say "answer with raw JSON only". https://github.com/trailofbits/claude-code-config |
| Agent hook that checks citations or glossary against files | docs only | The only handler that can read files; 30–60 s; experimental. |
| Gate on outbound MCP sends | docs only | Start with `permissionDecision: "ask"`; add a prompt hook with `continueOnBlock: true` later. |
| Research source log (WebFetch/WebSearch, async) | docs only | Zero context cost. |

Cowork caveat: plugin `hooks/hooks.json` loads in Cowork, but hooks in `~/.claude/settings.json` do not fire there (issue closed as not planned): https://github.com/anthropics/claude-code/issues/63360. Hooks are ignored in claude.ai chat: https://claude.com/docs/plugins/platform-support

## Safety and audit

- **Fail closed.** A guard that crashes or lacks `jq` lets the action through. Use `onFailure: "block"` or end the guard with `|| exit 2`. **(strong, docs)**
- **Most restrictive wins, side effects still happen.** On PreToolUse the strictest result across hooks wins (deny > defer > ask > allow), but a deny does not stop another hook's side effects. **(docs)**
- **Hooks are not a sandbox.** The docs call Bash argument patterns fragile and the `if` field best-effort; hard bans belong in permission deny rules and the sandbox. Edit/Write guards miss writes made through Bash. https://code.claude.com/docs/en/permissions.md
- **Do not duplicate auto mode.** The auto-mode classifier already blocks force-pushes, unreviewed merges, production deploys, `curl | bash` and credential exposure; auto mode pauses after 3 consecutive or 20 total blocks. Propose a guard only for determinism, a user-specific rule, a tool the classifier does not cover, a content check, an audit trail, or enforcement that must survive bypassPermissions and `-p`. https://code.claude.com/docs/en/permission-modes.md
- **Secret scan before writes.** Anthropic's security-guidance plugin combines pattern rules on Edit/Write with a review at Stop. https://github.com/anthropics/claude-plugins-official/tree/main/plugins/security-guidance; https://aitmpl.com/blog/security-hooks-secrets **(some)**
- **Audit logs.** Log at PreToolUse to include denied calls; log metadata, not content; run async. A full observability example sends events over HTTP to a local server and UI: https://github.com/disler/claude-code-hooks-multi-agent-observability **(some)**
- **Costs and usage:** use the built-in OpenTelemetry metrics rather than hooks. https://code.claude.com/docs/en/monitoring-usage.md
- **Hooks are code from whoever wrote them.** A disclosed flaw let a hook in a repository's shared project settings run a command when the repository was opened (fixed before disclosure, 2026-02-25): https://blog.checkpoint.com/research/check-point-researchers-expose-critical-claude-code-flaws/. Treat project, plugin and skill hooks as code to review. Do not echo untrusted content into `additionalContext`.

## Context, sessions and loops

- **Keep SessionStart small.** Advice converges on a few hundred tokens; plugin hooks can quietly add about 2K tokens per session, and UserPromptSubmit injection pays on every turn. Inject facts, not instructions; static rules belong in CLAUDE.md. https://www.mindstudio.ai/blog/session-start-hooks-claude-code-force-context; https://dev.to/pponali/after-the-skill-vault-3-more-hidden-token-sinks-in-claude-code-32ek **(some)**
- **Compaction memory.** A self-reported system over 1,300 sessions uses PreCompact, PostCompact and SessionStart together: https://dev.to/mikeadolan/claude-code-compaction-kept-destroying-my-work-i-built-hooks-that-fixed-it-2dgp **(some)**
- **Phone notifications** through ntfy, with Tailscale notes; never send prompt text to a public topic. https://dev.to/felipeelias/perfect-claude-code-notifications-setup-with-tailscale-and-ntfy-1ii1; https://pypi.org/project/claude-code-ntfy-notification-hook/ **(some)**
- **Stop loops.** The official ralph-loop plugin uses a state file, a completion tag, a maximum iteration count and a session check: https://github.com/anthropics/claude-plugins-official/tree/main/plugins/ralph-loop. Critics argue that in-session loops fill the context window and a shell loop with fresh context works better: https://www.aihero.dev/why-the-anthropic-ralph-plugin-sucks. Bound any loop with a verifier, an iteration cap and a halt when there is no diff: https://gautamkhorana.com/blog/claude-code-bounded-agent-loops/; https://codingwithroby.substack.com/p/the-stop-hook-that-wont-let-claude **(some)**
- **Agent teams.** TaskCreated, TaskCompleted and TeammateIdle can act as quality gates (exit 2 keeps work going). Agent teams are experimental. https://code.claude.com/docs/en/agent-teams.md **(docs only)**

## Hooks as a learning instrument

- Log skill use asynchronously: PostToolUse with matcher `Skill`, UserPromptExpansion for slash commands, and a weekly report that also flags streams with zero events. https://ytrofr.github.io/claude-code-guide/docs/guide/part5-advanced/03-self-telemetry.html **(some)**
- Count Skill tool calls and direct SKILL.md reads, de-duplicated by session and tool-use ID, as Shopify's AI Toolkit hook does: https://cdn.jsdelivr.net/npm/@shopify/ai-toolkit@1.8.2/hooks/README.md **(some)**
- Log InstructionsLoaded to find instruction files that load every session but never matter. **(docs only)**
- Log names and sizes, not content; write files with mode 0600; keep them local.
- `/skill-doctor` already reports skill usage and context cost without a hook. Check it before proposing telemetry.
