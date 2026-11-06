---
name: what-do-you-need
description: Gives the user a short, clear status when much has happened and they lost the overview. Shows what is done, what Claude needs from the user, what the user must decide now, and what to check. Also explains one topic again if the user names it. Use when the user says "what do you need?", "what do you need from me", "I'm lost", "where are we", "what's left", "I lost track", "what do I need to decide", or "explain X again". Add "overall" or "everything" for a view across all sessions and worktrees.
---

# What do you need?

The user lost the overview. Give them a status they can read in 30 seconds. Add the context they do not have. Do not only cut words.

## Pick the scope

- **Default: this session.** Cover only the work done in this conversation.
- **Overall: only if the user says so** ("overall", "everything", "across all"). Cover all work so far. Check every worktree, branch, open PR, and recent session. Group the result by worktree or project.
- **Topic: if the user names a topic.** Explain that topic again. Find the first point the user does not understand and start there. That point can be older than your last message. Then give the status below, short.

## Rules

- Use the real state of the work. Check files, git, and task output. Do not guess from memory.
- Use the words in the project `CONTEXT.md`, if it exists.
- Put the most important item first in each section.
- Only report. Do not start work. Do not change anything.
- Leave out an empty section. Do not add filler.

## Output

Keep each item to one line when you can.

### Done
What is finished and checked. Name the result, not the steps.
- Mark anything not checked as "not checked".

### I need from you
Things only the user can give or do. Examples: access, a file, an answer, a test, an approval.
- Say what, and why it blocks the work.

### Decide now
Choices that change what happens next. For each one:
- **Question** in one sentence.
- **Options** with the trade-off of each.
- **My pick** and the reason. Mark it "(recommended)".

### Check these
Things the user must look at, because I did them without the user.
- **Decisions I made for you.** What I chose, and the other option I did not take.
- **Assumptions.** Things I took as true and did not confirm.
- **Not checked.** Things I did not test or verify.
- **Looks done, is not.** Work that seems finished but has a gap.

### Good to know
Context the user should have. Only list what applies.
- Work that waits on someone else.
- Risks, or actions that cannot be undone.
- A deadline, or what happens if the user does nothing.
- Something the user asked for earlier that I did not finish.
- Something that changed since the user last looked.

### Next step
One sentence. What I do first when the user answers.
