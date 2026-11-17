# Global mode: review across projects

Use this when the user asks for a review across projects ("all my projects", "global", "across repos"). Each project is reviewed by its own subagent so that file contents, scanner output and repository reads stay out of the main context. The main agent holds only short summaries and does the cross-project analysis.

## 1. Pick the projects

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/discover_projects.py             # projects used in Claude Code, last 90 days
python3 ${CLAUDE_SKILL_DIR}/scripts/discover_projects.py --since 30  # narrower window
python3 ${CLAUDE_SKILL_DIR}/scripts/discover_projects.py --under ~/code  # every repo under a folder instead
```

The default source is Claude Code's session history, so it lists the projects the user actually works in, most recent first, with worktrees merged into their repository. Temporary and hidden locations are skipped; `--all` keeps them.

Show the table and ask which projects to include: all of them, or all except the numbers the user names. Leave out test fixtures and scratch repositories unless the user wants them. Above about 15 projects, suggest starting with the most recently used 10.

## 2. Read the user level yourself

Read `~/.claude/CLAUDE.md` and `~/.claude/settings.json` in the main context. They are short, and every subagent needs them to judge duplicates and conflicts. Review the user file with the same checks; it loads in every session of every project.

## 3. One subagent per project

Create a results folder (`mktemp -d`) and launch one general-purpose subagent per project, all in a single message so they run in parallel. Above 10 projects, launch in batches of 8. Use this brief, filled in:

```
Review the agent instruction files of the repository at <repo-path>. Report only; do not edit any file.

1. Run: python3 <skill-dir>/scripts/scan_instructions.py <repo-path>
2. Read every instruction file and import in full, .claude/settings.json and .claude/settings.local.json if present, and the repository's formatter, linter, pre-commit and CI configuration.
3. Read <skill-dir>/references/checks.md and <skill-dir>/references/enforcement.md, and test every instruction against the checks. Instruction files under template, fixture or example folders are material the project ships, not its own instructions: review them only for check A14 (can they load as live instructions?).
4. The user's global ~/.claude/CLAUDE.md, which loads in every project, contains:
   <paste the user file>
   User-level hooks and permission rules: <summary of ~/.claude/settings.json, or "none">.
   Flag project lines that repeat or contradict it.
5. Apply step 3 of <skill-dir>/SKILL.md (Verify before reporting) to every finding.
6. Write the full report to <results-dir>/<repo-name>.md in this format:
   <paste the finding format from SKILL.md, step 4 (Report), including the Act, Decide and Notes groups>
7. Reply with only this, under 250 words:
   SUMMARY: <files, per-session load from the scanner, the one change that matters most>
   FINDINGS: <count by check id, e.g. B1:2 B2:4 B3:3 A5:1>
   TOP: <the three most valuable findings, one line each, with file:line>
   PORTABLE: <rules that are personal preferences or general enough to apply to every project, quoted verbatim>
   ENFORCEABLE: <rules that should become a hook or permission rule, quoted verbatim, with the mechanism>
   CONFLICTS: <lines that repeat or contradict the user file>
```

Do not read the subagents' report files into the main context unless the user asks about a project.

## 4. Combine

From the replies, find what no single-project review can see:

- **Rules repeated across projects.** The same personal preference in three or more projects belongs in `~/.claude/CLAUDE.md` once; suggest the line for the user file and the lines to delete in each project. Keep a rule in the project when the team needs it too, since teammates do not get the user file.
- **One hook instead of many prose rules.** The same enforceable rule in several projects ("never push to main") becomes one hook or permission rule in `~/.claude/settings.json`, which applies in every project. Recommend branch protection in each shared repository as the control that also covers other contributors.
- **Conflicts with the user file.** Both files load, so the agent sees two contradicting instructions and may follow either. Make the project override explicit ("In this repository, use npm, not pnpm") or remove one of them.
- **Patterns.** A problem in most projects (history sections everywhere, AGENTS.md never imported by CLAUDE.md) points to a habit or a template; name it and fix the template if there is one.

## 5. Report

1. Two-line summary: projects reviewed, the per-session load of each (from the scanner) and their total, the single most valuable change.
2. **Across projects:** the combined findings above, each with the exact text to add to the user file or settings and the projects it cleans up.
3. **User file:** findings for `~/.claude/CLAUDE.md`.
4. **Per project:** one row each (project, lines, finding counts, top finding, path to the full report), worst first.

Offer to go deeper on one project (read its full report) or to apply changes. When applying across projects, edit the user-level files in the main context and launch one subagent per project with the approved findings for that project; each applies, tests any hook as in enforcement.md, and re-runs the scanner.
