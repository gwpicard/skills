---
name: gauntlet-loop
description: >
  Designs, sets up and launches a Gauntlet Loop (the method behind "Claude of
  Duty"): a lead agent splits a goal into pieces, builder subagents
  improve each piece, and blind critics with fresh context compare it A/B
  against a real reference until ours wins or the user stops the run. Chooses
  an inspectable quality bar, builds a reproducible capture step, writes the
  brief, critic rules and short lead prompt, then starts the loop after
  confirmation. Use when the user says "gauntlet loop", "set up a gauntlet",
  "loop until it beats X", "keep iterating until it is as good as X", "blind
  critic loop", or wants an agent to push any creative or engineering output
  (site, UI, 3D, game, writing, copy, code, campaign) far past "good enough".
  Do NOT use for a single review pass or a plain retry loop with no reference.
argument-hint: "[goal] [optional: reference or bar]"
---

# Gauntlet Loop

A Gauntlet Loop makes an agent keep improving work that it would otherwise
call "done". It has four parts:

1. **A real bar.** A concrete thing the agent can inspect and compare against.
   "The most recent Call of Duty", not "a great game".
2. **Split.** The lead agent breaks the goal into the smallest pieces that can
   be judged alone. Each piece gets its own builder.
3. **Blind critic.** A fresh subagent sees our piece and the reference with
   random labels. It picks the better one. If the reference wins, it names the
   biggest gap.
4. **No fixed end.** The loop runs until ours wins or the user stops it.

Source notes: `~/.claude/video-notes/he-built-call-of-duty-in-24-hours-with-this-ai-workflow-Sgas9rVHegc.md`.

Your job in this skill is to design the loop with the user, set it up so the
critic sees real output, and launch it. The design matters more than the
prompt. The original prompt is three paragraphs because the model does the rest.
The part that fails in practice is the setup: a weak bar, a critic that is not
really blind, or captures that the critic cannot trust.

## Step 1. Interview (short)

Get these facts. Take them from the request and the project first. Ask only
for what is missing, in one AskUserQuestion call with at most four questions.

- **Goal.** One sentence. What the finished thing is.
- **Bar.** A reference the user already has, or "find one".
- **Budget and stop rule.** How much time or money the run may use. Say the
  cost plainly: long runs with many subagents can use a large part of a
  subscription or hundreds of dollars.
- **Steering.** "Let it run" (experimental work) or "prescriptive" (real work:
  the user names what is good about the reference).

Also note: the project folder, the stack, and how the output can be looked at
(a browser page, an image, a text file, a test run).

## Step 2. Choose the bar

Read `references/bars.md`. It has the options for each kind of work.

A good bar passes four tests. Check each one out loud with the user:

1. **Inspectable.** The critic can look at it: pixels, text, test results,
   numbers. "Production-ready" fails.
2. **Comparable per piece.** Each piece can be set next to a matching
   reference piece: our gun next to a real gun, our opening paragraph next to
   a strong opening paragraph.
3. **Blind-safe.** Nothing except quality tells the critic which side is ours.
   Famous work fails this test: the model recognizes Stephen King. Match size,
   crop, format and length.
4. **Hard.** The bar does not need to be reachable. It must stop the agent
   from settling at "pretty good for AI".

When the user has no bar, propose two or three with one sentence each on why
they work. Let the user pick. When the thing does not exist yet, use a
reference with the same level of quality from another area, or generate
reference images until the user likes them.

If no blind A/B is possible (most backend code), use a measured bar (tests,
latency, a reference implementation) and keep a fresh critic that grades
against it. Say this to the user.

## Step 3. Build and test the capture step

The critic must inspect the real output, never a summary from the builder. So
before the loop starts, there must be a command that turns our current output
into the same format as the reference.

- Visual: a script that renders a named view and saves a screenshot at a
  fixed size (for example, Playwright headless, one fresh page per shot, a
  fixed wait or frame count).
- Writing: a script or rule that cuts the draft into units (paragraph,
  section) as plain text, same formatting as the reference units.
- Code: the test or benchmark command, with output saved to a file.

Test it now. Run it twice on the same input. If the two outputs differ, fix
that first (shared page state, timers, random seeds, clocks). If captures are
not reproducible, the critic compares noise. Then capture one reference item
and one of ours, and look at both. They must be in the same format.

Do not skip this step to launch sooner. It is the step that makes the loop
honest.

## Step 4. Write the loop files

Create `.gauntlet/` in the project:

```
.gauntlet/
  brief.md        goal, bar, the four bar checks, budget, stop rules, steering notes
  critic.md       copy of references/critic-brief.md, filled in for this task
  prompt.md       the lead prompt, from assets/lead-prompt.md
  capture.*       the capture command from step 3 (or a note on where it is)
  refs/           reference items, named by piece when possible
  pairs/          blind pairs the critics see (created during the run)
  workbench.md    live progress page (or workbench.html for visual work)
  log.jsonl       one line per verdict (written by the script)
```

Copy `scripts/blind_pair.py` into `.gauntlet/`. It puts ours and the
reference in random A/B order, and writes the key to
`~/.cache/gauntlet/<project>/keys/`, outside the project, so a critic cannot
find it. Usage is in the file header.

Fill `prompt.md` from `assets/lead-prompt.md`. Keep it short. Give the goal
and the bar. Do not give the architecture, the list of pieces, or a number of
rounds. The protocol details live in `brief.md` and `critic.md`, so the prompt
can stay short.

Read `references/lessons.md` and add to `brief.md` the lessons that apply to
this task. The most common: give coupled parts one owner, and let a builder
push back on a critic with evidence.

## Step 5. Confirm and launch

Show the user:
- the bar and why it is a good one, in one sentence,
- the full lead prompt,
- the cost warning and the stop rule,
- how to watch progress (`.gauntlet/workbench.md` or the HTML page).

Ask how to launch:

- **This session.** You become the lead agent. Follow `prompt.md`. Start each
  critic with the Agent tool as a new general-purpose subagent. Never use
  `fork` for a critic: a fork inherits your context, so it is not blind. For a
  large run, the user can say "ultracode" or "use a workflow" to allow the
  Workflow tool. Do not call Workflow without that opt-in.
- **New session.** Tell the user to open Claude Code in the project and paste
  `.gauntlet/prompt.md`. For large runs, recommend `/effort` set to
  ultracode.
- **Unattended.** Use `/loop` on the lead prompt so each round restarts.

Do not launch without a clear yes from the user.

## Step 6. While it runs (when you are the lead)

- Start a new critic for every judgment. Never reuse one. Give it only
  `critic.md` and the pair folder. Never give it builder notes or history.
- Run `blind_pair.py pair` before each judgment and `blind_pair.py reveal`
  after it. Only the reveal step tells you if ours won.
- Send the builder only the gap, not the verdict text about which side was
  which.
- After each wave, start one fresh smoothing agent. It checks that the
  pieces fit together. It does not redesign.
- Update the workbench after each round: before and after captures, win
  counts, the current biggest gaps.
- Stop when a stop rule in `brief.md` is met, or the user says stop. If a
  piece loses many rounds in a row with no progress, report it to the user
  and do not keep spending on it.
- At the end, write an honest assessment in the workbench: where ours won,
  where it still loses, and why.

## Files

| File | Use |
|---|---|
| `references/bars.md` | Bar options and blind-safety checks for each kind of work |
| `references/critic-brief.md` | Critic template: blind A/B rules and output format |
| `references/lessons.md` | What went wrong and right in real runs |
| `assets/lead-prompt.md` | Lead prompt template and the original prompt |
| `scripts/blind_pair.py` | Random A/B pairing, hidden key, verdict log, status |
