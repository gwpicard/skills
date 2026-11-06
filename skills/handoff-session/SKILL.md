---
name: handoff-session
description: >
  Writes a handoff so work resumes later without re-deriving decisions. In a
  Claude Code repo it measures live git, PR, CI and issue state and prints a
  paste-able continuation prompt plus a reference document; for any other
  conversation (no repo, claude.ai, ideas, research, decisions) it writes a
  standalone document a zero-context reader can continue from. Either way it
  captures the decisions, reasoning and lessons that exist only in the
  conversation. Use when the user says "handoff", "hand this off", "continue in
  a new session", "give me a prompt to continue", "pick this up tomorrow",
  "let's stop here", "capture this", "save the context", "write this up so I
  can come back to it", "make this portable", or wants to pass the conversation
  to another AI. Offer it when the context window passes about 60-65%, before
  compaction discards the reasoning. Do NOT use for a quick in-chat recap, or
  for a handover or onboarding document written for a team or a new joiner.
argument-hint: "[optional: what to emphasise]"
license: MIT
metadata:
  version: "0.2.0"
  author: "Guillaume Picard"
---

# Handoff

Hand a conversation's work to whoever picks it up next: a new Claude Code
session, another AI, or the user on another day. The output is either a
**session handoff** (a coding session in a git repo) or a **conversation
handoff** (everything else). Both rest on the same rules; they differ in what
can be measured and in who reads the document.

## Critical

**The bar: a competent stranger can continue.** Someone who was not in the
conversation should be able to read the handoff and carry on without asking a
question. That rules out "as discussed above", "the earlier approach" and any
other reference whose referent is not in the document itself.

**Measure state, never recall it.** A SHA, PR number or CI status recalled from
earlier in the session is routinely already wrong, and a wrong one sends the
next session hunting for something that no longer exists. When there is a repo,
run the gather script even when you think you know the answer.

**Capture what only this conversation knows.** Git history and open issues are
re-derivable in thirty seconds. What is genuinely lost is *why*: decisions and
their reasoning, alternatives rejected, bugs found and how, process lessons.
That is the valuable half and the part that takes judgement. Quote load-bearing
material (decisions, numbers, named concepts, the user's sharp phrasings)
rather than paraphrasing it; drifted paraphrase becomes the next reader's truth.

**Never restate the repo's own documentation.** If `CLAUDE.md` or `README.md`
already says it, link to it. Duplicated conventions rot.

**Never write a secret.** The next reader takes the document verbatim, and a
session handoff lives in `~/.claude/plans/`, outside any repo's `.gitignore`.
Name the variable or secret store that holds the value, never the value: "the
token in `FAL_KEY` expires every 24h" carries everything useful and leaks
nothing. The checker in step 4 is a backstop, not permission to be careless.

**No manufactured closure.** Record what is broken, half-done, or uncertain. An
honest "this is untested and I am not sure the approach holds" saves more time
than a tidy summary.

## Which kind of handoff

Run the gather script first; its first line decides the branch.

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/gather-state.sh
```

| Situation | Branch | Reader | Output |
|---|---|---|---|
| Inside a git repo, work on code | **Session handoff** | A new Claude Code session that can run commands | `~/.claude/plans/<project>-handoff.md` plus a paste-able prompt |
| No repo, no shell (claude.ai), or the conversation was ideas, research, a decision, drafting or learning | **Conversation handoff** | Another AI, or the user later, with no context | One standalone markdown document (or a small package) |

If you cannot run shell commands at all, you are on the conversation branch.
A coding conversation in a repo that also produced a design debate is still a
session handoff; fold the debate into its decisions.

## When compaction is the right call

`/compact` is the cheaper move when you are **staying in this session and only
need room**: it preserves your intent, costs one turn, and leaves nothing to
clean up. Reach for it when the work is going well and the context is mostly
finished business.

A handoff earns its cost when the *reasoning* has to survive: a design that
changed its mind twice, an approach abandoned for a reason that is not in the
diff, a bug found by accident. That is precisely what compaction summarises
away. So: going well and just full, `/compact`. Went wrong somewhere, or
stopping for the day, handoff.

## Offer it before compaction, not after

The trigger is **context pressure**, not session end, and it has to fire early,
because once compaction has run the reasoning is already gone. When the context
window passes about 60-65%, say so and offer a handoff in one sentence. Offer at
a natural boundary (a merged PR, a passing suite, a completed step), never
mid-task. If the user declines, do not ask again.

## Session handoff (git repo)

### 1. Measure

The gather script above is read-only and takes seconds. It reports branch, HEAD,
uncommitted files, recent commits, open PRs **with CI status**, recently merged
PRs, open issues, the next free issue number, existing plan files, and whether a
handoff for this project already exists.

**Do not run the test suite.** It can take minutes and can fail for environment
reasons unrelated to the work. Cite the last count measured in this session and
say when: "450 passing as of the last run, before the current uncommitted
changes."

If the script reports an existing handoff for this project, the previous one
was never picked up or never deleted. Overwrite it. Never leave two.

### 2. Decide depth

Match the document to the work, not to a template.

- **A short or single-task session**: often no document at all. A few sentences
  in the reply may be the whole handoff. Say so rather than manufacturing
  structure.
- **A substantial session** (several commits, a design that evolved, bugs
  found): the full document.

### 3. Write the document

Structure and section-by-section guidance:
[references/handoff-template.md](references/handoff-template.md)

Open it with the deletion instruction, so the next session removes it on pickup
and handoffs never accumulate:

```markdown
> **Delete this file once you have read it and started work.**
> It is a snapshot, and a stale one is worse than none.
```

### 4. Check

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/check-handoff.sh ~/.claude/plans/<project>-handoff.md
```

`<project>` is the `project:` line from step 1's output, not a guess.

Read-only. It catches what fails silently: a secret in the document, a missing
delete-header, an empty heading left by a section with nothing in it, and a repo
path that no longer exists. Exit 2 means it could not read the file; check the
path before assuming the document is fine.

Fix every `FAIL` before step 5: a handoff is read once, unquestioned, by a
session that cannot tell the difference. Take each `WARN` as a question worth
answering rather than a box to tick.

### 5. Print the prompt

Short; the reader is pasting it, not studying it. It needs only:

1. The repo path and the handoff file to read first.
2. The single immediate next action.
3. The one or two things that would bite in the first ten minutes.
4. The one or two skills to reach for, if any are worth naming.
5. The instruction to delete the handoff after reading.

Show it as a quoted block so it is obvious what to copy.

### What belongs in a session document

Ordered by how expensive it is to reconstruct, most expensive first.

| Include | Why |
|---|---|
| Decisions and their reasoning | Unrecoverable. The next session will otherwise re-litigate settled questions. |
| Bugs found and how they surfaced | Especially ones a test suite passed straight through. |
| Process lessons | "Verify a new guard fails when the thing it guards is broken." Cheap to write, expensive to relearn. |
| Invariants discovered | Constraints not obvious from the code and easy to break. |
| Environment gotchas | Anything that cost time and will cost it again. |
| In-flight uncommitted work, and what is *verified* about it | The next session inherits the working tree and trips over it first. |
| Ordered next actions, with decisions already made | So the next session executes rather than re-designs. |
| Suggested skills, and when to reach for them | Otherwise the next session rediscovers its own tooling. |
| Measured state, with when | SHA, PRs, CI, test count. |

Leave out anything the next session can get from `git log`, the issue tracker,
or the repo's own docs in under a minute.

## Conversation handoff (no repo, or not about code)

There is no state to measure, so the whole document is the judgement half.

### 1. Read the conversation and infer its shape

Identify what it was substantively about. The invocation message, your setup
questions and the user's answers are scaffolding, not content. Assign a primary
shape (idea exploration, research, decision, drafting, debugging, learning, or
short note) and decide whether sub-threads with different futures need
separate documents. Heuristic, per-shape body structures and splitting rules:
[references/conversation-shapes.md](references/conversation-shapes.md)

### 2. Ask only what the conversation has not answered

At most four questions, in this order, and skip any the conversation already
settles:

- **Shape and split.** "This looks like an idea exploration that included a
  landscape scan; one handoff covers it. Does that match, or should I split it?"
- **Depth.** Comprehensive or lightweight.
- **External material.** "You referenced X and pasted Y. Include them?"
- **Title.** Propose a specific one.

If the user only said "capture this", confirm the title and take sensible
defaults for the rest. If the user overrides the shape, redo the inference from
scratch; different shapes surface different material.

### 3. Write the document

Every conversation handoff has, in order: a specific **title** ("Handoff" is not
a title); a **BLUF** of three short sentences (what this is, where it stands,
what to do first), which must work as the opening message of a new
conversation; a one-line **shape marker**; the **body** in that shape;
**unresolved items**; **action items**; and **cross-references** and **external
references** only when real. Omit any section with nothing in it rather than
writing "none".

Write argument and reasoning as prose; keep bullets for genuine lists. Match
the user's voice, and attribute ideas the user took forward to the conversation
("the conversation landed on X"), not to the assistant. Capture dates and
numbers verbatim.

Where it goes: on claude.ai, a downloadable markdown file. In Claude Code
outside a repo, the location the user names, or the working directory if they
name none. Worked examples of each shape:
[references/examples.md](references/examples.md)

### 4. Check

If you can run shell commands:

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/check-handoff.sh --record <path-to-handoff.md>
```

`--record` drops the delete-header and repo-path checks, because a
conversation handoff is a durable record the user decides when to retire.
Without a shell, apply the same checks by reading: no secrets, no empty
headings. Then reread it as the stranger: is anything implicit, any reference
ungrounded, any conclusion resting on reasoning not in the document? Fix it.

## Anti-patterns

- **A narrative of the session.** Nobody needs the chronology, except the
  hypothesis chain in a debugging handoff. They need the state and the
  decisions.
- **Recalled numbers.** If it was not measured, do not assert it.
- **Restating CLAUDE.md.** Link.
- **Inventing structure for a small conversation.** Three sentences is a valid
  handoff.
- **Burying the next action.** It goes near the top and in the prompt.
- **Flattening the user's voice** into neutral consultant prose. The user has
  to trust that the thinking in the document is their own.
- **Keeping scaffolding.** Options the assistant offered and the user moved past
  without using are not content.

## Resuming from a handoff

When a session begins by reading a session handoff: read it, verify the state it
claims, do the work it points at, and **delete the file**. It described a moment
that has now passed, and a stale handoff read as current is worse than none.
A conversation handoff is the user's record; do not delete it.

## A note on this skill's own design

Do not add `context: fork`. The machine-checkable half could run in a subagent,
but the valuable half (decisions, reasoning, lessons) exists only in the
conversation this skill is invoked from. A forked handoff would confidently
produce the half that was never the problem.
