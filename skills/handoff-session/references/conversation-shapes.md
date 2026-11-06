# Conversation handoff: shapes and content rules

For the conversation branch: a handoff with no repo state to measure. Guidance,
not a form. Drop any section the conversation did not produce content for.

## Contents

1. [Shape inference](#shape-inference)
2. [One handoff or several](#one-handoff-or-several)
3. [Body structure per shape](#body-structure-per-shape)
4. [What goes in and what stays out](#what-goes-in-and-what-stays-out)
5. [Comprehensive vs lightweight](#comprehensive-vs-lightweight)
6. [Single file vs package](#single-file-vs-package)
7. [Length](#length)

---

## Shape inference

Look for the dominant pattern and assign a primary shape:

| Signals | Shape |
|---|---|
| Seed idea, landscape exploration, refinement toward a design or plan | **Idea exploration** |
| Question posed, systematic investigation of sources, findings summarised | **Research or survey** |
| A specific choice weighed, options considered, reasons for the pick | **Decision** |
| An artifact produced (draft, outline, code, structured content) with reasoning alongside | **Design or drafting** |
| Problem stated, hypotheses tried, outcomes observed | **Debugging or problem-solving** |
| A concept explained, examples and analogies, the user building a mental model | **Learning or explanation** |
| Short exchange, a single question or small decision, under about 15 turns | **Short note** |

For a mix (an idea exploration that included some debugging), use the primary
shape as the overall structure and fold secondary material into its sections.

## One handoff or several

Split when sub-threads have different futures: they would be picked up on
different occasions, have different next moves, or go to different readers.
Combine when they are parts of the same work. When proposing a split, name each
document and say why.

Siblings get distinct subject titles, not "Part 1" and "Part 2". Each opens
with a line such as "This is one of three handoffs from the same conversation.
See also: [title 2], [title 3]." Never duplicate content across siblings; put it
in the most relevant one and cross-reference from the others.

## Body structure per shape

### Idea exploration

- **The seed**, in the user's original words. Short, unpolished; do not clean
  it up, because the user needs to recognise it.
- **Current state of the idea.** Two or three paragraphs on the sharpest
  version reached. What someone reads if they have thirty seconds.
- **Intellectual history.** The moves that mattered: reframings, pushback that
  sharpened things, changes of direction. Not a turn-by-turn log.
- **Landscape**, if one was explored: who else is in the space, what they do,
  where the gaps are, in enough detail that nobody redoes the scan.
- **Decisions.** For each: what, alternatives with reasoning, confidence
  (high/medium/low), status (proposed/accepted/superseded), consequences. Compact.
- **Open threads.** Tangents not followed up. These are re-entry points.
- **First concrete move.** One thing, not a plan.
- **Revival triggers.** "Pick this up if X happens; drop it if Y becomes true."
  Load-bearing for parked ideas, optional for active ones.

### Research or survey

- **The question.**
- **Findings**, each with a source specific enough to verify and a confidence
  with a sentence on why.
- **Sources consulted**, so the reader knows what has and has not been covered.
- **What remains unknown.**
- **What would change the picture.**

### Decision

- **The decision**, stated plainly.
- **Options considered**, each with reasoning for and against.
- **Reasoning behind the pick.** This rots fastest in memory; capture it fully.
- **Confidence and status.**
- **Consequences**: what it enables, forecloses, and any second-order effects.
- **What still needs to happen**: communicating, implementing, watching.

### Design or drafting

- **The artifact itself**, in full. Lean toward embedding over summarising.
- **Reasoning behind non-obvious choices**, as a careful editor's margin notes.
- **Revision history**, only where changes reflect real thinking.
- **Open points**: TKs, undecided phrasings, structural questions.
- **Next steps** to a finished state.

### Debugging or problem-solving

- **The problem**, in enough detail for someone unfamiliar with it.
- **What was tried**: each hypothesis, what was done, what happened. Keep the
  chronology here; the reader needs the causal chain.
- **Current hypothesis.**
- **Where to look next.**

If this was debugging code in a repo, use the session branch instead.

### Learning or explanation

- **The topic and the question that motivated it.**
- **The current mental model**, in the user's words where possible.
- **Examples or analogies that made it click**; the user re-anchors on these.
- **Remaining confusions.**
- **What to study next**, if discussed.

### Short note

Three to six lines, no sections beyond the BLUF. Do not inflate it.

## What goes in and what stays out

- **Engaged material is in.** If the user asked follow-ups, pushed back, built
  on it, or treated it as load-bearing, it stays, whoever originated it.
- **Unengaged material is in if it resolved a question** or was later used. A
  factual answer the user accepted and moved on from is still load-bearing.
- **Unengaged exploration is out.** Of three framings offered, the two the user
  did not pick are scaffolding.
- **Keep the user's voice.** Preserve sharp articulations and reframings in
  their words.
- **Quote, do not paraphrase,** decisions, framings, numbers, named concepts and
  settled wordings.

## Comprehensive vs lightweight

Comprehensive keeps the main argumentative lines and the supporting detail:
alternatives with reasoning, landscape, intellectual history, illustrative
specifics.

Lightweight keeps the main lines and drops the supporting detail. The test for
each piece: would removing it change the argument or the conclusion? If not,
cut. A lightweight decision handoff still says "we considered X, Y, Z and picked
X", without pros and cons for each. The BLUF, decisions, first move and
unresolved items always survive; only the supporting detail goes.

## Single file vs package

Default to one markdown file. Produce a folder (main handoff plus attachments)
when the conversation produced discrete artifacts that deserve their own files:
drafts longer than a few paragraphs, code longer than a snippet, unwieldy
structured data, or external documents the user asked to include. The main file
stays the entry point and references each attachment.

## Length

Let the content decide. A short note is under 200 words; a comprehensive idea
exploration for a substantial conversation may run 2,000-4,000 words. If a
section would be one sentence, make it one sentence.
