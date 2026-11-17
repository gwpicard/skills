---
name: agent-instructions-review
description: Reviews agent instruction files (CLAUDE.md, AGENTS.md, CLAUDE.local.md, .claude/rules) and gives line-level suggestions. Checks best practice and finds content that belongs elsewhere - changelogs and history, prohibitions with no alternative, and rules a hook, permission rule, linter or CI should enforce instead of the model (e.g. "never push to main"). Each suggestion quotes the line and gives a rewrite, a move or a ready-to-use hook or settings snippet. Reviews one project, or many projects with one subagent each, finding rules to move to the user level. Use when the user says "review my CLAUDE.md", "review AGENTS.md", "audit my agent instructions", "why does Claude ignore my CLAUDE.md", "clean up CLAUDE.md", or "review CLAUDE.md across all my projects". Do NOT use to write a first CLAUDE.md for a new project (use project-init) or to review a SKILL.md (use eval-skill).
argument-hint: "[repo-path | global | folder-of-repos]"
---

# Agent instructions review

Instruction files load into every session, so every line costs context and competes for attention. Studies find that their measured value lies in what the agent cannot work out alone: the exact commands, the project's own tools and the conventions that differ from defaults. Overviews and generated text add cost without improving results. The review keeps the lines that change what an agent does, and moves everything else to the place that handles it better: a hook, a permission rule, a linter, git history, a README, a skill or a path-scoped rule.

The review reports. It does not edit until the user approves.

## Scope

- **This project (default).** Review the repository you are in, or the path in `$ARGUMENTS`. Follow steps 1-5 below.
- **Global.** When the user asks for "all my projects", "global", "across projects" or names a folder of repositories, follow [references/global-mode.md](references/global-mode.md). It finds the projects, reviews each one in its own subagent so their contents stay out of this context, and adds the findings only a cross-project view shows: rules to move up to `~/.claude/CLAUDE.md` and one user-level hook in place of the same prose rule in many projects.

If the request is ambiguous ("review my CLAUDE.md" from the home directory, with no repository), ask which scope.

## 1. Collect

Run the scanner on the repository root (or the path in `$ARGUMENTS`):

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/scan_instructions.py <repo-root>
```

Add `--user` only when the user asks to include their personal `~/.claude/CLAUDE.md`.

The scanner reports:
- every instruction file (CLAUDE.md, AGENTS.md, GEMINI.md, Copilot files, `.claude/rules/`) with when it loads: at startup, on demand (nested, including under template or fixture folders), or for other agents only;
- the **per-session load**: what a Claude Code session started at the repository root loads (startup files and their imports), plus files the instructions say to read before any work. Use this total in the report summary;
- warnings: length limits, directory trees, template files named like live instructions, an AGENTS.md Claude Code does not read, and personal files not git-ignored;
- the settings files, and allow rules that may contradict the instructions;
- broken `@imports`, paths and package scripts that exist nowhere in the repository, passages repeated across files, and flagged passages.

Flags are candidates found by keyword. Judge each one; a flag is not a finding, and many real findings have no flag (the best ones in testing did not).

Then read, in full:
- every instruction file and every file it imports;
- `.claude/settings.json` and `.claude/settings.local.json`, to see which hooks and permission rules already exist. Both are in scope; label a finding in the local file as affecting only that user's sessions;
- `~/.claude/settings.json` as context only: its permission mode (auto mode, for example) and settings such as `attribution` change how a project finding plays out. Report findings about the user's own files only when the user includes them (`--user`);
- enforcement code the repository already has, including hooks and scripts it ships to others (a secrets guard in a project template, say). Reusing it is usually the cheapest code fix;
- any document the instructions say the settings mirror (a list of blocked commands, say);
- the tooling that already enforces rules: formatter and linter configs, `.pre-commit-config.yaml` or `.husky/`, CI workflows, `package.json` scripts or `Makefile`;
- how a file that ships to users is packaged (release manifest, plugin folders), if the repository ships one.

If `gh` is available and the repository has a GitHub remote, collect the server-side state too. It is read-only, and it often decides a finding:

```bash
gh repo view --json visibility,isPrivate
gh api repos/{owner}/{repo} --jq .security_and_analysis    # secret scanning, push protection
gh api repos/{owner}/{repo}/rulesets                         # rulesets: check these, not only classic protection
gh api repos/{owner}/{repo}/branches/main/protection         # classic protection; "not protected" can be wrong if rulesets apply
```

A public repository with secret scanning or push protection off is a top finding, whatever the instruction files say. Rulesets and required checks count as "already enforced".

Knowing the tooling decides many findings. "Use 2-space indentation" is redundant when Prettier already enforces it, and it becomes a hook suggestion when nothing does.

## 2. Judge

Read [references/checks.md](references/checks.md) and test every instruction against it. Its first table says how strong the evidence is for each check; state each finding with matching confidence. [references/evidence.md](references/evidence.md) holds the studies, vendor quotes and incidents; read it when the user asks why or disputes a finding.

**A. Best practice.** The main test: would the agent get this wrong without the line? Delete overviews, directory trees and anything else the agent can read from the repository, and prune text that `/init` or a template generated. Then check that the line is specific and checkable, gives a reason when the reason is not obvious, and does not conflict with another file. Check that the commands and project-specific tools are present, the file is under the size limits with the important rules first, and CLAUDE.md and AGENTS.md share one source. Check that the settings agree with what the file says, that nested or template instruction files cannot load as live instructions, and that "read X before any work" is scoped to the work that needs X.

**B. Content in the wrong place.**
- **History.** Changelogs, dated entries, "we switched from X to Y" and migration stories belong in git history, release notes or an ADR. Keep only the current state, plus a warning if old patterns still appear in the code ("`src/legacy/` still uses Jest; write new tests with Vitest").
- **Prohibitions with no alternative.** "Don't use axios" leaves the agent guessing. Name what to do instead and why: "Use the `http` client in `src/lib/http.ts` instead of axios; it adds auth and retries."
- **Rules the model should not enforce.** Move a rule to a tool when it has no exceptions, a program can check it, it keeps being missed (emphasis on the line is the sign), or breaking it is irreversible. Instructions are advice the model may decide does not apply; a hook, permission rule, linter, CI check or branch protection applies every time. Keep preferences with exceptions as instructions. Read [references/enforcement.md](references/enforcement.md) to pick the mechanism and copy the snippet.

## 3. Verify before reporting

Every finding is a claim about the repository, and one wrong claim costs the user's trust in the rest. Re-check each finding before showing it; drop or downgrade any that fails:

1. **The quote is real.** The quoted text exists at that file and line.
2. **The facts are checked.** Every path, command, file count or "nothing enforces this" claim was confirmed by reading the repository, not inferred. Search for an existing check (CI, required checks, rulesets, git hooks, validators) before saying a rule is unenforced. In particular:
   - **Loading claims:** name the exact way a file gets loaded (a nested CLAUDE.md, an `@import`), and reproduce it when that is cheap: read a file in that folder and see which instruction files the harness loads. A reproduction is cheap when it runs in a scratch folder, touches nothing in the repository or online, and takes about a minute; a `claude -p` run with a small model counts (enforcement.md shows one).
   - **Rename or move costs:** search for the exact file you would rename, not its folder.
   - **Suggested tests:** confirm the repository's tests actually cover the file before telling the user to run them.
3. **The fix is verified.** Every settings key, hook event, permission syntax and CLI flag in a snippet appears in enforcement.md, in the current official documentation, or in a settings file that already works. Otherwise mark it "unverified: check the documentation" or leave it out.
4. **The fix addresses something present.** No rule for a file, tool or service the repository does not have, and no guard on a route nobody uses (an ask rule for `gh release create` when releases go through a workflow).
5. **A step before commit or push earns its place.** This covers a proposed pre-commit or pre-push hook and an existing instruction to "run X before pushing". Check whether required CI already runs the same check, and time the command. A hook that only saves an occasional red CI run is padding; one that takes more than a few seconds gets bypassed, and a slow instruction gets skipped.
6. **The repository has not already decided it.** If a document explains an intended trade-off (a deny rule that over-blocks on purpose, say), it is not a finding. A list that a validator or test pins to an exact set is not a decision against changing it: propose the change together with the matching edit to the validator.
7. **A rewrite keeps the rule's scope.** Change only the part the finding is about. A rewrite that narrows or widens another part of the rule ("read A before changing commands; for other work, read B" when B applied to all work) is a new, unreviewed change.
8. **The basis is stated.** Each finding says whether it rests on a measured result, vendor guidance or inference (the table at the top of checks.md).
9. **Code first for rules that must hold; the enforced set stays small for the rest.** For a rule that meets the B3 test, the fix is code, not better prose: check that no finding settles it by weakening a setting to match the text (removing an allow rule restores a prompt, and under auto mode a prompt is not guaranteed), or leaves part of it to prose while code for that part exists. Then look at all "move to a tool" findings together. The small-set counter-rule applies to preferences and rules with exceptions; it never argues against enforcing a rule with no exceptions whose breach cannot be undone (merging, force pushes, secrets, data).

Then cut padding: a finding whose fix is marginal (a hook that prints `git status`) goes, even if it is correct.

## 4. Report

Lead with a two-line summary: the files reviewed, the per-session load from the scanner (say what it includes), and the one change that matters most.

Then list findings in three groups, most valuable first within each:
- **Act:** the facts are verified and the fix is clear.
- **Decide:** the fix depends on the user's intent or a trade-off only they can judge (a personal setting that may be deliberate, how much protection the repository should have). Say what the decision is and give your pick. When the rule meets the B3 test, list the code option first and explain any reason not to pick it.
- **Notes:** correct but lower value; one line each.

Report a finding only when the fix improves the agent's behaviour or removes cost; skip taste-level rewording. Twelve findings is a sensible ceiling; if there are more, group the small ones ("8 lines restate what Prettier enforces: L12-L19").

For each finding:

```
### <n>. <file>:<line> - <short label>
> <quoted line or lines>

Problem: <what goes wrong, in one or two sentences>
Basis: <measured / vendor guidance / inference>, <verified / partly verified>
Fix: <the action: Rewrite / Delete / Move to hook / Move to permission rule /
     Move to linter or CI / Move to .claude/rules/<name>.md / Move to README / Add>
<the exact replacement text, or the snippet, or the destination>
```

When a rule moves to a hook or permission rule, also say what the instruction file should say afterwards. Usually that is nothing. Keep a short positive line only when it tells the agent the workflow to follow ("Work on a feature branch and open a pull request"), so it does not first try the blocked action and then recover.

After the findings, list in one or two lines what already passes and what is already enforced, so the user knows those were checked. End with an **Add** section only for missing essentials you can fill from the repository (a test command found in `package.json`, say). Do not invent content you cannot verify.

## 5. Apply on request

Take the Decide findings one at a time: the decision in one sentence, the options with their cost, your pick, then wait for the answer. Then ask which Act findings to apply. When applying:

- Edit instruction files in place, keeping the author's structure and tone.
- When a fix reaches beyond instruction files and settings (renaming a shipped template, changing scripts, release or upgrade machinery), draft an issue instead of editing: why, what changes, how to check it, written so that someone with no access to this review can act on it. Use the repository's issue templates if it has them, and create the issue only when the user says so.
- Add hooks and permission rules to `.claude/settings.json` (shared) unless the user wants them only for themselves (`.claude/settings.local.json`). Put hook scripts in `.claude/hooks/` and make them executable.
- Test every hook before removing the prose it replaces: pipe a sample tool input into the script and check the exit code and message (examples in enforcement.md). Remove the prose only after the test passes.
- Run the scanner again and report what changed: lines and tokens before and after, and any finding left open.
