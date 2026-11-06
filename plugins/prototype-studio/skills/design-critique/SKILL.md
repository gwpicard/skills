---
name: design-critique
description: Runs fresh-context design reviews of a brand, prototype or site — blind tell counts across several builds, a first-visitor perception review, an audit against a brand spec, measured colour checks and frame-by-frame motion review — and reports findings the user can act on without letting critics make the taste call. Use when the user says "review the design", "is this generic", "critique these options", "what would a visitor think", "audit against the spec", "blind review", or after a substantial visual round in the brand-definition or high-fidelity-prototypes skills. For a loop that keeps building until the work beats a reference, use a gauntlet-loop skill if one is installed.
---

# Design critique

A builder cannot see its own defaults. Critique works when a reviewer with fresh context looks at the rendered result through one named lens, measures what can be measured, and reports in a fixed shape. The user makes the taste call; critics supply evidence.

## Pick the lenses

Use only the lenses the question needs. Run independent lenses in parallel.

| Lens | Question it answers | Input |
|---|---|---|
| Blind tells | Which patterns repeat across these builds, and which build is whose? | Screenshots and HTML of two or more builds, labels randomised |
| Perception | What does a first-time visitor conclude in five seconds, and which adjectives does it earn? | The first screens at desktop and phone width; the target adjectives |
| Spec audit | Which elements follow the spec, which drifted, which are off-language? | `SPEC.md`, approved crops, crops of every element |
| Colour | Do text and accents meet contrast on every background, and do distinct surfaces read as distinct? | Tokens; `colour_check.py` from brand-definition |
| Art direction | Is there one idea, a clear hierarchy and owned content, or is it styling on a template? | Screenshots plus the brief and references |
| Motion | Is every movement believable, every loop logical, and nothing appearing from nowhere? | Frames at 2× (for example every 100 ms), plus the code |
| Domain | Would someone in this field find the content correct and the examples real? | The content and the scenario |

Prompts for each lens are in [references/critic-prompts.md](references/critic-prompts.md). In Claude Code, the `blind-critic`, `perception-reviewer` and `spec-auditor` agents carry these prompts; in other tools, paste the prompt into a fresh session.

## Rules for every critic

- Fresh context: the critic sees the rendered output and the files it needs, not the build conversation.
- When the brand kit has a `rubric.md`, critics judge only its questions and answer pass or fail with evidence. A finding outside the rubric is dropped or proposed as a new question for the user to accept. This keeps reviews comparable from round to round.
- Run deterministic checks (contrast, token use, sizes) before asking critics. The cheapest check that can decide a rule should decide it.
- Optionally, add a second counter: `npx impeccable detect --json <path-or-url>` ([pbakaus/impeccable](https://github.com/pbakaus/impeccable), Apache-2.0) runs 62 deterministic rules for agent tells and quality problems, with no LLM and no API key, and lists each finding with its rule, severity and evidence. A URL gets more checks (contrast, text size) than source files; add `--viewport 390x844` for a phone-width pass. It sits beside `measure_reference.mjs` and `colour_check.py`; it does not replace them. Some of its rules are taste preferences (for example, it flags Inter as an overused font), so pass its hits to critics as evidence, not as verdicts, and drop any that contradict a fixed decision. Use only `detect`: `install` adds skills and hooks to the agent setup, and live mode can run agents with permissions bypassed. Prefix `IMPECCABLE_NO_TELEMETRY=1` to turn off its usage ping. Exit code 2 means findings, not a failure.
- Blind where it matters: randomise labels; never reveal which model or round built what.
- List the fixed decisions the critic must not challenge (approved palette, stage names, the headline), so its suggestions can be built.
- Ask for evidence: counts, measurements, the element and where it is. No praise; no general quality claims.
- Ask for a fixed number of moves (usually three), each buildable from the fixed decisions and owned assets, under a word limit.
- Keep honesty findings (invented numbers, slogans, changed names) separate and at the top. They are never matters of taste.

## Report to the user

1. Honesty findings, if any.
2. What the critics agree on, with counts. Agreement on tells is reliable.
3. Where they disagree. Disagreement on quality is normal; present it as options, not as a verdict.
4. A short numbered list of proposed changes, each with a recommendation, for the user to answer by number.

Check the critics' main claims yourself against the screenshots before reporting them.

## When tuning stalls

After two or three unsuccessful passes on one problem, ask a fresh agent to diagnose the cause from scratch, with published reference data where it exists (gait curves, type scales, contrast standards). Ask for "what you see and why" before any fix; a diagnosis without code changes is a valid result.
