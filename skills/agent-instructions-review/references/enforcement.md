# Enforcement: where a rule goes instead of prose

Use this when a check B3 finding moves a rule out of an instruction file. Give the user the exact snippet, and test it before removing the prose. Sources are in evidence.md, section X.

## Contents

- Choosing the mechanism
- Permission rules
- PreToolUse hooks (blocking)
- PostToolUse hooks (formatting)
- Path-scoped rules
- Excluding nested instruction files
- Checking server-side controls
- Testing a hook or a permission rule

## Choosing the mechanism

| Rule | Mechanism | Why this one |
|---|---|---|
| Never push or merge to main, never force push | Branch protection or a ruleset on the remote, plus a PreToolUse hook | Only the remote control holds for every client and person; the hook gives the agent a clear message before it tries. Check rulesets first: they may already cover it |
| Never read or edit `.env`, secrets | Permission deny rules (`Read`, `Edit`); better, keep secrets off disk (injected env, a vault) | Deny rules miss `grep -r` and scripts that open files themselves |
| Don't edit `generated/`, migrations already on main | `Edit` deny rule or PreToolUse hook; CODEOWNERS for people | Built in, no script |
| Never run a dangerous command (`rm -rf`, `terraform apply`) | Sandbox (confines writes to the project), PreToolUse hook on Bash, deny rule as a first layer | Deny rules match command text only; a hook can inspect the whole command |
| Never touch production data | No production credentials in the development environment, separate environments, backups outside the system they protect | Every documented database-deletion incident happened despite instructions, and no agent-side control would have been enough |
| Ask before installing packages | Permission `ask` rule | Turns the instruction into a prompt |
| Indentation, quotes, import order, line length | Formatter config, plus a PostToolUse hook that runs it on edited files | The formatter decides; the agent never has to remember |
| Banned APIs, `any`, naming patterns | Linter rule (ESLint, Ruff, etc.), run in CI and pre-commit | Enforced for people and agents alike |
| Conventional commit messages | commitlint in a commit-msg git hook | Checked at commit time |
| Always run tests before finishing | A Stop hook that runs the fast test suite and blocks on failure; CI required check as the backstop | The agent cannot finish with failing tests unnoticed; keep the test command in the file too |
| Never commit secrets | A secret scanner in pre-commit (gitleaks, detect-secrets) and CI, GitHub push protection; git-ignore `.claude/settings.local.json` and `CLAUDE.local.md` | Catches it regardless of who commits |

Layering matters. Claude Code permission rules and hooks govern only Claude Code: they do not apply when Codex, Cursor or a person works in the repository, and they can be bypassed (see Permission rules). Git hooks and CI govern every contributor; branch protection, scoped credentials and push protection hold on every path. For a rule whose breach is irreversible, recommend a control outside the agent first, and the Claude Code layer for fast feedback. Cursor, Codex, Copilot and Gemini CLI have their own hook systems if the project uses them.

Keep the enforced set small. A hook that enforces a preference blocks legitimate work: a rule with real exceptions ("prefer named exports") stays an instruction. Use `command` hooks for enforcement; `prompt` and `agent` hooks ask a model to decide and are not deterministic.

## Permission rules

In `.claude/settings.json` (shared with the team) or `.claude/settings.local.json` (personal):

```json
{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Edit(./generated/**)",
      "Bash(git push --force *)",
      "Bash(git push origin main *)"
    ],
    "ask": [
      "Bash(npm install *)",
      "Bash(pnpm add *)"
    ]
  }
}
```

`*` matches any text; a rule with no `*` matches only that exact command. Bash deny rules match the command as written: they do not catch the same program called by full path or wrapped in `sh -c '...'`, and `git push` with no arguments on a main checkout slips past `Bash(git push origin main *)`. Variables (`URL=...; curl $URL`) and runners such as `npx` and `docker exec` slip past too. `Read` deny rules cover the built-in tools and the shell file commands Claude Code recognises, not `grep -r .` or a script that opens the file itself. Prefix rules also match only the exact word: `Bash(git push --force:*)` does **not** refuse `git push --force-with-lease` (tested in a scratch project), and options placed later in the command (`git push origin main --force`) are not covered either. Treat deny rules as a first layer and add a hook, the sandbox or a remote control for rules that must hold.

Permission modes change what an allow or ask rule means. Under auto mode a classifier decides many actions without a prompt, so removing an allow rule or adding an ask rule does not guarantee the person is asked (how ask rules behave under auto mode is unverified: check the documentation). A deny rule still refuses under auto mode (whether it holds when permissions are bypassed entirely is unverified). For a rule that must hold, use a deny rule or a hook, not the absence of an allow rule.

## PreToolUse hooks (blocking)

A PreToolUse hook runs before a tool call. It receives the call as JSON on stdin (`tool_name`, and `tool_input.command` for Bash). Exit code 2 blocks the call and sends stderr back to the agent as the reason, so write the message as an instruction: what to do instead.

Example: block pushes to main, including a bare `git push` while on main.

`.claude/hooks/block-push-to-main.sh`:

```bash
#!/usr/bin/env bash
# Blocks git pushes that target main or master.
cmd=$(jq -r '.tool_input.command // ""')
echo "$cmd" | grep -Eq '(^|[;&|[:space:]])git[[:space:]]+push' || exit 0

branch=$(git branch --show-current 2>/dev/null)
if echo "$cmd" | grep -Eq '(^|[[:space:]:])(main|master)([[:space:]]|$)' \
   || { [[ "$branch" == main || "$branch" == master ]] \
        && ! echo "$cmd" | grep -Eq 'git[[:space:]]+push([[:space:]]+-[^[:space:]]+)*[[:space:]]+[^-[:space:]]+[[:space:]]+[^-[:space:]]+'; }; then
  echo "Pushing to main is blocked. Create a branch (git switch -c <name>), push it, and open a pull request." >&2
  exit 2
fi
exit 0
```

`.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/block-push-to-main.sh" }
        ]
      }
    ]
  }
}
```

The script needs `jq`; if the project cannot assume it, write the hook in Python or Node and parse stdin there. Recent Claude Code versions also accept an `if` field with permission-rule syntax (for example `"if": "Bash(git push *)"`) to run the hook only for matching commands; it saves process launches but is optional, because the script checks the command itself.

The same pattern covers other command rules: change the `grep` test and the message. For a rule about file paths, match `Edit|Write` instead of `Bash` and read `tool_input.file_path`.

## PostToolUse hooks (formatting)

Runs the formatter on each file the agent edits, so style rules never need to be in prose:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write --ignore-unknown" }
        ]
      }
    ]
  }
}
```

Swap in the project's formatter (`ruff format`, `gofmt -w`, `rustfmt`). Suggest it only when the formatter is already a project dependency.

## Path-scoped rules

For check A10. A file in `.claude/rules/` loads only when the agent reads or edits a file matching `paths`:

```markdown
---
paths:
  - "src/api/**/*.ts"
---

# API handlers

- Validate request bodies with the zod schemas in `src/api/schemas/`.
```

A rules file without `paths` loads at startup like the root CLAUDE.md, so it splits the file without saving context. For a rule that other agents should also see, use a nested AGENTS.md in that directory instead.

## Excluding nested instruction files

For check A14, when a nested `CLAUDE.md` (a template, a fixture) should never load in this repository's Claude sessions:

```json
{
  "claudeMdExcludes": ["**/templates/foundation/CLAUDE.md"]
}
```

Patterns are globs matched against absolute paths, so start them with `**/`. The setting works in user, project, local and managed settings; put it in the shared `.claude/settings.json` so it covers every maintainer. It affects Claude Code only, and only this repository: if the folder ships to users, their projects load the file too. Renaming the file (`CLAUDE.md.tmpl`) fixes both. Confirmed in the Claude Code documentation in November 2026; recheck it if the snippet does not take effect.

## Checking server-side controls

Before proposing a hook for a rule about shared history, check what the remote already enforces (read-only):

```bash
gh api repos/{owner}/{repo}/rulesets --jq '.[] | {id, name, target, enforcement}'
gh api repos/{owner}/{repo}/rulesets/<id> --jq '{rules: [.rules[] | .type], bypass: .bypass_actors}'
gh api repos/{owner}/{repo}/branches/main/protection   # classic protection only
gh api repos/{owner}/{repo} --jq .security_and_analysis
```

The classic protection endpoint answers "Branch not protected" when protection comes from rulesets, so never conclude from it alone. A ruleset that blocks force-pushes and requires pull requests and checks on `main` already enforces most "never push to main" rules; the remaining gap is usually approval (a pull request that needs zero approvals) and feature branches. For a public repository, check that secret scanning and push protection are on. To turn them on (needs admin rights on the repository; field names confirmed in GitHub's REST documentation for "Update a repository", November 2026):

```bash
gh api -X PATCH repos/{owner}/{repo} \
  -f 'security_and_analysis[secret_scanning][status]=enabled' \
  -f 'security_and_analysis[secret_scanning_push_protection][status]=enabled'
```

Or in the repository's settings, under Code security. This changes an online setting, so it always needs the user's explicit yes.

## Testing a hook or a permission rule

Feed the hook a sample tool input and check the exit code before relying on it:

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"git push origin main"}}' \
  | .claude/hooks/block-push-to-main.sh; echo "exit $?"     # expect exit 2 and the message
echo '{"tool_name":"Bash","tool_input":{"command":"git push origin feature/x"}}' \
  | .claude/hooks/block-push-to-main.sh; echo "exit $?"     # expect exit 0
echo '{"tool_name":"Bash","tool_input":{"command":"git status"}}' \
  | .claude/hooks/block-push-to-main.sh; echo "exit $?"     # expect exit 0
```

Test one case that must be blocked, one near-miss that must pass, and one unrelated command.

To test how a permission rule matches, use a scratch project instead of guessing: put the rule in its `.claude/settings.json`, written against a harmless command of the same shape (`Bash(echo --force:*)` stands in for `Bash(git push --force:*)`), allow the plain command so that only the deny rule can refuse it (deny rules take precedence), and run a cheap non-interactive session that tries each spelling:

```bash
cd "$(mktemp -d)" && mkdir .claude
echo '{"permissions":{"deny":["Bash(echo --force:*)"]}}' > .claude/settings.json
claude -p --model claude-haiku-4-5-20251001 --allowedTools "Bash(echo:*)" "Run these one at a time and report which were refused: echo --force x; echo --force-with-lease x; echo x --force"
``` If the hook does not fire in the current session, open `/hooks` to check it is registered, or start a new session.
