# Prototype Studio

Define a brand and build high-fidelity prototypes that do not look agent-made.

Coding agents share a house style. Ask two model families for six differently styled homepages and most of them come back with the same cream background, the same tight headline tracking and the same accent word in the headline. Style prompts change the surface and leave the structure alone. This plugin works on the inputs that agents cannot generate for themselves: the organisation's real work and point of view, references the decision-maker chooses, one core idea, and visual rules written down with numbers.

## Skills

- **brand-definition** defines positioning, vocabulary, voice and lines, a reference bar, a core idea, the asset style and a binding spec with tokens, in seven gated stages. Its lite mode produces what a prototype needs in one sitting. Output: a `brand/` kit.
- **high-fidelity-prototypes** builds interactive prototypes with coherent behaviour, believable content and visible state, and takes its look from the brand kit or from references the user picks.
- **design-critique** runs fresh-context reviews: blind tell counts across builds, a first-visitor perception review, a spec audit, colour measurement and frame-by-frame motion review.

## Agents (Claude Code)

`blind-critic`, `perception-reviewer` and `spec-auditor`. In other tools, the same prompts are in `skills/design-critique/references/critic-prompts.md`.

## Scripts and templates

In `skills/brand-definition/`:

- `scripts/capture.mjs`: viewport strips, section crops or a full page, for references and builds;
- `scripts/measure_reference.mjs`: computed anatomy of one or more pages as a comparison table, including counts of common agent defaults;
- `scripts/colour_check.py`: WCAG contrast and CIEDE2000 colour difference for a set of checks, no dependencies;
- `templates/compare.html`: one review page for a round of options, with picks, notes and a "Copy decisions" button;
- `templates/tokens.json`, `rules.yaml`, `SPEC.md`, `rubric.md`: starting files for a brand kit (role-named tokens with light and dark themes, rules as records, a spec skeleton, a closed review rubric).

The two `.mjs` scripts need Puppeteer (`npm i puppeteer` in a scratch folder, or set `PUPPETEER_PATH`).

## Principles

1. Identity comes from what the organisation owns, not from styling.
2. Define "good" with examples the decision-maker picks.
3. Keep references visual: measure them and show them beside the build.
4. Change one variable per round.
5. Write the spec from approved examples as soon as drift appears, and generate everything from one source.
6. Measure colour and contrast.
7. Critics find tells; the user makes the taste call.
8. Honesty rules never relax: no invented numbers, slogans or claims.

## Install

Claude Code:

```bash
claude plugin marketplace add gwpicard/skills
claude plugin install prototype-studio@gwpicard-skills
```

Codex and other agents:

```bash
npx skills add gwpicard/skills
```

## Status

Version 0.2.0. The guidance comes from one long brand and website project run with Claude and Codex, generalised. [LEARNINGS.md](../../LEARNINGS.md) records each lesson, its evidence and where it lives in the skills. The scripts have been run locally; the skills have not yet been evaluated against a baseline.
