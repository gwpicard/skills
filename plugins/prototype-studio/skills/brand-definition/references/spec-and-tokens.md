# Spec, tokens and the never list

## When to codify

Write the spec at the first sign of drift, or once three or so assets are approved, whichever comes first. Assets tuned one by one drift apart: in one project an audit of 62 elements found 33 had drifted from the approved examples and 13 were outside the language altogether.

## SPEC.md

- Build it from approved examples. Crop the approved assets and state the rules they follow.
- Use numbers: stroke weights and their ratios, a formula for weight against size, projection angles, spacing steps, radii, colour roles. "Medium weight" is not a rule.
- State precedence: "Where an earlier note disagrees, this file wins."
- Version it, with a short history entry for each change and the decision that caused it.
- Include usage and exceptions with rendered examples, and a short "Never" section of drift patterns found by the audit.

## tokens.json

- One file holds every colour, type style, spacing and radius value. Mark it as the source of truth.
- Give every colour its role, its text variant where it carries text, and its value on each background (light and dark).
- Add a token the moment a new colour is needed. A builder inventing a value in a prototype is drift.
- Generate assets from source (icons from a generator, washes from the tokens). Do not edit or recolour generated files by hand.
- Propagate brand changes to every output: favicon sizes, social images, reduced-motion versions, print.

## Colour

- One meaning per colour. Write the meaning next to the token.
- Neutral at rest, colour as a signal, is a strong default; illustrations can stay ink at rest and take realistic material colour only on hover or focus.
- Measure, do not eyeball. Run `scripts/colour_check.py` on the tokens: WCAG contrast for every text and accent pair on every background, and CIEDE2000 (ΔE00) between surfaces that must read as distinct. Problems like a 1.01:1 accent on a dark background or a ΔE00 of 1.2 between two materials look like taste problems until measured.

## never.md

Keep three lists, because they relax differently:

1. **Design tells.** Agent defaults and generic patterns found in your builds, each with the count that justified it. These can be relaxed deliberately, with a written reason.
2. **Drift patterns.** Ways assets departed from the spec, found by the audit.
3. **Honesty rules.** No invented numbers, testimonials, case results or slogans; approved names are not changed; claims match evidence. These never relax.

The never list is a gate. Passing it removes problems and adds no identity.

## Audit

Capture every element (icons, illustrations, components, pages) and compare each with the spec and the approved crops. Give each a verdict: consistent, drifted (fix to spec) or off-language (redraw or remove). Re-run the audit after each round that touches assets.
