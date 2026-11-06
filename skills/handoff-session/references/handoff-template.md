# Handoff document structure

Guidance, not a form to fill in. Drop any section the session did not produce
content for — an empty heading is worse than an absent one.

## Contents

1. [Header](#header)
2. [What this is](#what-this-is)
3. [State](#state) — including [In flight](#in-flight)
4. [Do next](#do-next)
5. [Suggested skills](#suggested-skills)
6. [Conventions](#conventions)
7. [Environment gotchas](#environment-gotchas)
8. [Process lessons](#process-lessons)
9. [Invariants](#invariants)
10. [Start by](#start-by)

---

## Header

Always first, so it is read before anything else:

```markdown
> **Delete this file once you have read it and started work.**
> It is a snapshot, and a stale one is worse than none.

Repo: `/absolute/path`
Plan: `~/.claude/plans/<name>.md` — read this first, it carries the design
decisions for everything still to do.
```

Link the plan only if one exists. If the session had no plan file, the handoff
carries the decisions itself and should say so.

Write the repo path as it is *now*, from the gather script — not as it was when
an earlier handoff was written. Projects move.

## What this is

Two or three sentences. Enough for someone who has never seen the project to
follow the rest. Not a README — link that instead.

## State

Everything here comes from the gather script, never from memory.

```markdown
`main` is at `abc1234`. **450 tests pass** (`uv run pytest -q`, ~3 min) as of
the last run, before the uncommitted changes on `feat/x`.

Merged this session: #64 ... · #65 ... · #66 ...

**Open: PR #74 `feat/x`** — CI pending. Check before merging.
```

State the test count *and when it was measured*. "450 passing" is a claim about
a moment; without the moment it is a claim about now, and probably wrong.

### In flight

The next session inherits the working tree, so uncommitted work is the first
thing it trips over. Give it its own heading whenever the tree is dirty.

Say four things, in this order:

1. **What is modified** — the diffstat, not a description of it.
2. **What it is trying to do**, and whether the approach is coherent.
3. **What is actually verified about it, separated from what is assumed.** This
   is the part that gets skipped and the part that matters.
4. **The one command that would settle it.**

```markdown
Checked out on **`feat/edit-reporting`** are **181 uncommitted lines** across
three files, written outside the session that produced this handoff:

    src/storygen/cli.py      | 49 ++
    src/storygen/edit.py     | 87 ++
    src/storygen/evaluate.py | 59 ++-

It implements the plan's reporting increment: a `--rebalance` flag, an
`edl-stale` **fail** finding, and — the substantive change — `evaluate`
measuring over `edit.timeline(sl)` instead of `sl.shots`.

**What is not known:** whether it is finished, whether it has tests, whether the
suite passes. It imports cleanly, and that is the only thing verified about it.
**Run `uv run pytest -q` before building on it**, and treat a green suite as the
first real signal.
```

The honest "what is not known" paragraph is the point. A confident summary of
work you did not verify is worse than no summary, because the next session
builds on it.

## Do next

The most important section. Numbered, in order, each with **the decisions already
made** so the next session executes rather than re-designs.

A good entry carries the constraint that is not obvious from the code:

```markdown
5. **`feat/handheld-drift`** (#58) — filter specified verbatim in FINDINGS §6.3.
   **It cannot go in `realism_chain()`** — that runs once over the concatenated
   timeline and §6.3 requires per-shot phase. It belongs in `normalize_clip`,
   phase derived deterministically from the shot id.
```

Without that second sentence, the next session writes it into `realism_chain()`,
discovers the problem, and redesigns. That paragraph is the handoff earning its
existence.

## Suggested skills

What the next session should reach for, so it does not rediscover its own
tooling. One line each, saying **when** to use it — not what it is.

```markdown
- `/commit-message` — before every commit. This repo wants a multi-paragraph
  rationale ending with the test count; the default one-liner will be rejected.
- `/code-review high` — before opening the PR. The last two PRs both came back
  with findings that this would have caught.
- `storygen:render-check` (project skill) — after any change to `assemble`.
```

Include only skills this session actually earned the right to recommend: ones it
used, or ones whose absence cost it something. A generic list of what is
installed is noise — the next session can run `/help` for that. If nothing
qualifies, drop the section.

## Conventions

Only project-specific ones, and only those actually discovered — commit message
shape, branch naming, changelog format, staging discipline, label taxonomy.

If they are already in `CLAUDE.md` or `CONTRIBUTING.md`, link and stop. Include
only what the session learned by observation and is written down nowhere.

## Environment gotchas

Anything that cost time and will cost it again: a broken venv, a tool that must
be a specific build, a flaky external dependency, an auth quirk.

Say what fixes it, and what looks like a fix but is not — a workaround that was
tried and failed is as valuable as one that worked, because it stops the next
session spending the same hour.

**Never write the credential itself.** Describe the auth quirk and name the
variable or secret store that holds the value — `FAL_KEY`, `gh auth token`, the
`.env` the repo already documents. A handoff lives in `~/.claude/plans/`, outside
any repo's `.gitignore`, and the next session reads it verbatim. "The token in
`FAL_KEY` expires every 24h; re-run `fal auth login`" carries everything useful
and leaks nothing.

## Process lessons

How to work on this, learned the hard way. Short, imperative, each earned by
something that actually went wrong:

```markdown
- **Verify every new guard fails when the thing it guards is broken.** Two tests
  this session were green for the wrong reason.
- **Never queue a background command that switches branches.** One ran
  `git checkout main` mid-work and a commit landed on the wrong branch.
```

Include the evidence clause. "Verify guards fail" reads as generic advice; "two
tests this session were green for the wrong reason" makes it credible and
memorable.

## Invariants

Constraints that must not break and are not obvious from reading the code. These
are the things a well-meaning change quietly violates:

```markdown
- **The audio timeline never moves.** Captions are word-aligned to the voiceover.
  Picture may be re-cut; the soundtrack may not.
- **Measurements, not flags.** A status field can be stale about its own subject.
```

## Start by

Three or four commands that re-establish context and verify the state above is
still true. Ending with the immediate next action closes the loop between the
document and the work.

```bash
cd /path/to/repo
git fetch origin && git log --oneline origin/main -3
gh pr checks 74
```
