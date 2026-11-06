---
name: harvest-learnings
description: Reads Claude Code and Codex session logs (and a project's own records) from a real project, reconstructs how the work went, and proposes general learnings as edits to this repository's skills, with evidence and with everything project-specific removed. Use when the maintainer says "harvest learnings from <project>", "port the lessons from these sessions", "what did we learn that the skills should know", or after a long project that used these skills. Maintainer tool; not shipped in any plugin.
---

# Harvest learnings

Turn a finished or long-running project into improvements to the skills, without carrying the project's private details into a public repository.

## 1. Find and extract the logs

Run `scripts/extract_logs.py` with the project's folder names and a date range. It finds:

- Claude Code sessions in `~/.claude/projects/<encoded-path>/*.jsonl`, matched by path substring;
- Codex sessions in `~/.codex/sessions/YYYY/MM/DD/*.jsonl`, matched by the `cwd` in each session's first line.

It writes one Markdown file per session with the user's messages and the longer assistant messages, without tool output or images, into an output folder outside the repository (default: a temporary folder). Codex approval-review and subagent sessions repeat other transcripts; the script marks sessions whose working folder is a temporary folder so you can read them last.

```
python3 scripts/extract_logs.py --match my-project --match my-project-lab --since 2026-09-01 --out /tmp/harvest
```

Also read the project's own records: decision logs, specs, briefs, archive notes, memory files. They record the reasons that logs only imply.

## 2. Read in parallel slices

Split the extracts by date and source into slices of roughly 400–900 KB of text, and give each slice to a fresh reader agent with the same instructions:

1. a dated chronology of what was attempted and decided;
2. the user's corrections and rejections, and what landed, with short quotes;
3. process techniques that worked and those that wasted time;
4. candidate general learnings, each backed by evidence.

Readers focus on the user's messages: they carry the decisions, corrections and approvals.

## 3. Synthesise and filter

Merge the readers' reports. Keep a learning only if it passes the four tests in `CONTRIBUTING.md`: general, evidenced, actionable, placed. Check each main claim against the extract before relying on it.

Remove: client and brand names, people's names, real taglines and product names, prices, paths, private decisions, and anything a reader could use to identify the client. Replace examples with neutral ones that show the same point.

## 4. Propose the edits

For each learning, present to the maintainer:

- the instruction as it would read in the skill;
- the file and section it changes, or the new reference file;
- the evidence line for `LEARNINGS.md`.

Prefer sharpening an existing instruction over adding a new one. Present the edits as a numbered list and apply only the ones the maintainer approves. Then add the `LEARNINGS.md` entries and bump the plugin versions.

## Privacy

Never copy extracts, screenshots or quotes that identify the client into the repository. Keep extracts outside it, and delete them when the harvest is done unless the maintainer wants them kept.
