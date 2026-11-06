# Spec, tokens, rules and specimens

## When to codify

Write the spec at the first sign of drift, or once three or so assets are approved, whichever comes first. Assets tuned one by one drift apart: in one project an audit of 62 elements found 33 had drifted from the approved examples and 13 were outside the language altogether.

## SPEC.md

- Build it from approved examples. Crop the approved assets and state the rules they follow.
- Use numbers: stroke weights and their ratios, a formula for weight against size, projection angles, spacing steps, radii, colour roles. "Medium weight" is not a rule.
- Organise it by the sections in kit-sections.md, using only those the organisation needs. `templates/SPEC.md` is a starting skeleton.
- Open with a header: version (semver), date, owner, how to propose a change, and "Where an earlier note disagrees, this file wins."
- Show each rule that can be broken visibly as a rendered do/don't pair.
- Keep a changelog at the end: each version, what changed, and the decision that caused it.

## tokens.json

`templates/tokens.json` is a starting file. It uses two tiers:

- **Primitives**: the raw palette and scales (`gray.10`–`gray.90`, `clay.50`). Nothing outside the tokens file refers to them.
- **Roles**: what a value is for (`color.text.primary`, `color.surface.raised`, `color.accent.signal`, `color.border.subtle`, `color.focus`). Each role references a primitive for each theme, and carries its meaning and where it may be used (text, fill, stroke). Name tokens by role, never by appearance: `color.accent.signal`, not `color.orange`.

Themes keep the role names and swap the primitives: a light and a dark theme map `color.text.secondary` to different greys. Builds use role tokens only.

The file also holds the type styles (family, size, line height, weight, tracking, case, fallback, use), the spacing scale, radii and, if the brand moves, durations and easing curves.

- Add a token the moment a new value is needed. A builder inventing a value in a prototype is drift.
- Generate assets from source (icons from a generator, colour washes from the tokens). Do not edit or recolour generated files by hand.
- Propagate changes to every output: favicon sizes, social images, reduced-motion versions, print, templates.
- Version the file with the spec, and note in each prototype or template which kit version it used.

## Colour

- One meaning per colour. Write the meaning next to the role.
- Neutral at rest, colour as a signal, is a strong default; illustrations can stay ink at rest and take realistic material colour only on hover or focus.
- Measure, do not eyeball. Run `scripts/colour_check.py`: WCAG contrast for every text and accent pair on every theme, and CIEDE2000 (ΔE00) between surfaces that must read as distinct. Problems like a 1.01:1 accent on a dark background or a ΔE00 of 1.2 between two materials look like taste problems until measured.

## rules.yaml

Prose in SPEC.md explains; `rules.yaml` makes each rule checkable and traceable. `templates/rules.yaml` shows the format:

```yaml
- id: R-012
  rule: "The accent appears at most once per screen"
  strength: hard          # hard = must/never; soft = should/prefer
  severity: error         # error | warning | info
  check: deterministic    # deterministic | measured | judgement
  how: "count elements using color.accent.* per viewport; must be <= 1"
  do: specimens/accent-do.png
  dont: specimens/accent-dont.png
  source: "decisions.md D7; studies/round3/l2.png"
  status: active          # proposed | active | retired (keep, with reason)
```

- Every rule has a source: a decision, an approved crop or a quoted guideline. A rule with no source is a bug.
- A measurement alone never creates a hard rule; it creates a proposed soft rule for the user to confirm.
- Judgement rules ("feels calm") are not pass/fail checks. They become rubric questions for critics (`rubric.md`).
- Retire rules instead of deleting them, with the reason and date.
- A new rule must pass every gold exemplar and flag every anti exemplar before it becomes active.

## Specimens and exemplars

The specimen sheet is the gate for stage 6. Render `specimens/` from fixed placeholder content so it can be re-rendered after every change:

- every type style in context, on light and dark;
- every colour pair with its measured contrast;
- every logo variant at its minimum size and on each allowed background;
- icons at each size tier;
- key layouts under stress: a long title, dense content, many items, empty optional slots.

Show the sheet beside the approved references, and ask the user to approve it. Approved crops become `exemplars/gold/`. Rejected outputs go to `exemplars/anti/`, each with one line saying why. The two sets turn taste decisions into test cases for later rounds and for new rules.

## Rights and licences

- `fonts/LICENSES.md`: for each font, the licence, whether desktop, web and document embedding are permitted, the source and a checksum.
- `assets/catalogue.yaml`: for each logo file, illustration or photograph, its kind, alt text, allowed crops, rights (licence, owner, expiry, restrictions) and source, with `confirmed: false` until the user confirms the rights. Never ship an asset whose rights are unconfirmed.

## never.md

Keep three lists, because they relax differently:

1. **Design tells.** Agent defaults and generic patterns found in your builds, each with the count that justified it. These can be relaxed deliberately, with a written reason.
2. **Drift patterns.** Ways assets departed from the spec, found by the audit.
3. **Honesty rules.** No invented numbers, testimonials, case results or slogans; approved names are not changed; claims match evidence. These never relax.

The never list is a gate. Passing it removes problems and adds no identity.

## Audit

Capture every element (icons, illustrations, components, pages, templates) and compare each with the spec, the rules and the gold exemplars. Give each a verdict: consistent, drifted (fix to spec) or off-language (redraw or remove). Re-run the audit after each round that touches assets, and run deterministic checks before asking critics: the cheapest check that can decide a rule should decide it.
