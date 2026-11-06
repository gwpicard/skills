---
name: brand-definition
description: Defines a brand from the ground up — positioning, vocabulary, voice, lines, a reference bar the decision-maker chooses, one core idea, the visual asset style, and a binding spec with tokens — through gated stages run with AI builders and fresh-context critics. Use when the user says "define our brand", "brand identity", "rebrand", "visual identity", "logo, palette or type direction", "our site looks generic", "we need a design language", or when a prototype needs a look and no brand kit exists (lite mode). Produces a brand/ kit that the high-fidelity-prototypes skill reads. Not for checking copy against an existing brand guide.
---

# Brand definition

A brand is defined in words before pixels, and its identity comes from what the organisation owns: its record of work, its point of view, the founder's sketches, its real customers' world. Styling cannot supply identity; it can only express it. This skill runs the work as gated stages, each producing a file, so decisions survive across sessions and agents.

## Choose a mode

- **Lite** (one sitting, for a prototype): a one-line position and audience, three to eight reference picks with measurements, a palette and type pair in `tokens.json`, and `never.md`. Skip the stages marked full.
- **Full** (several sessions): all seven stages. Tell the user the stage you are in and what its gate is.

If the user only wants copy checked against an existing guide, this skill does not apply.

## The brand kit

Write everything to one `brand/` folder (or the project's existing brand folder). Other skills and agents read it.

| File | Holds | Stage |
|---|---|---|
| `positioning.md` | Audience, problem, position, point of view, vocabulary | 1 |
| `voice.md` | Voice rules, banned words, before/after pairs | 1 |
| `lines.md` | Adopted lines, and every rejected line with its reason | 2 |
| `references/` | Picked references, captures, measurements, one note each | 3 |
| `concept.md` | The core idea and its storyboard | 4 (full) |
| `studies/` | Level studies and their outcomes | 5 (full) |
| `SPEC.md` | Binding visual rules with numbers, versioned | 6 |
| `tokens.json` | The single source of every colour, type style and spacing value | 6 |
| `never.md` | Design tells, drift patterns, honesty rules | 6 |
| `decisions.md` | Numbered decisions, their status, what each replaced | all |

## Stages

Each stage ends at a gate. Do not start the next stage's visual work until the gate holds; most rework in brand projects comes from iterating visuals on an unsettled brief.

1. **Ground the position in evidence.** Read [references/positioning-and-lines.md](references/positioning-and-lines.md). Build the position from the organisation's real work: past projects, delivery records, sales conversations, competitor teardowns, the founder's own frameworks. Fix the vocabulary and point of view early; they become the content that styling cannot fake. *Gate:* the user agrees the position in their own words.
2. **Write lines that take a stance.** Same reference. Test each candidate with the opposite test and the swap test, and keep every rejected line with its reason in `lines.md`; give that file to every generator. *Gate:* one adopted line that fails neither test.
3. **Let the decision-maker set the bar.** Read [references/references-and-bar.md](references/references-and-bar.md). Collect the user's picks, confirm what kind of target they are, capture and measure them with `scripts/capture.mjs` and `scripts/measure_reference.mjs`. *Gate:* a pick sheet the user has confirmed, with one concrete move per reference.
4. **Find one core idea** (full). Read [references/concept.md](references/concept.md). Start from the user's sketch or the customer's real world, storyboard it before building, and reject diagrams of the offer. *Gate:* the user can say the idea in one sentence and it could not belong to a competitor.
5. **Choose the asset style with one-variable studies** (full). Read [references/asset-style-studies.md](references/asset-style-studies.md). Fix the subject, vary one property in levels, use two builders with different techniques, and translate taste words into visible properties. *Gate:* the asset style is chosen on real subjects, with stated limits.
6. **Codify.** Read [references/spec-and-tokens.md](references/spec-and-tokens.md). Write `SPEC.md` from approved examples, put every value in `tokens.json`, generate assets from source, and write `never.md`. Do this at the first sign of drift, not at the end. *Gate:* every asset can be audited against the spec.
7. **Review as a visitor.** Use the design-critique skill: audit every element against the spec, measure colour, and ask a fresh reviewer what a first-time visitor concludes. Extend the brand language into the layout, or distinctive assets end up on template furniture. *Gate:* the perception review earns the adjectives the user asked for, or the gap is a recorded decision.

## Working with the decision-maker

- The user is the taste arbiter. AI critics find tells and measure; they do not decide taste.
- Show, do not describe. Put options side by side on one page built from `templates/compare.html`, with real content, and let the user pick or combine.
- Ask for decisions as a numbered list with a recommendation each. Record answers in `decisions.md`.
- Quote the user's feedback word for word at the top of the next brief, and say what it overrides.
- When the user says "generic" or "not right" without a target, stop building. Diagnose, ask for an example, and change the brief before the next round.
- Mark anything not yet approved as a proposal. Never present invented numbers, slogans or claims as brand facts.
- Archive before replacing: keep each superseded version in a dated folder with a note on why it was replaced. Reversals are common and should be cheap.
- Keep one review location and one status record. Tell the user exactly where to look.

## Where the time goes

These patterns cost the most rounds in practice; watch for them:

- rejecting outputs as "generic" for several rounds before anyone defines a positive target;
- turning references into sentences and building from the sentences;
- varying subject and style in the same round, so feedback cannot be attributed;
- polishing a story or screen in an asset style that is later rejected;
- overcorrecting: adding heavy texture after "too clean", then removing it again;
- hand copies of values drifting from the source;
- reviewing the artefact in isolation instead of the visitor's first screens.
