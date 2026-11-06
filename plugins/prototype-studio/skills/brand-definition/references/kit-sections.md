# Kit sections

The sections a `SPEC.md` can contain, sized for an organisation without a design team. Use only the sections the organisation needs: a consultancy with no product UI needs no component states; a firm that publishes no numbers needs no data palette. Each section states rules with numbers and shows each breakable rule as a rendered do/don't pair.

Patterns here draw on public brand kits, notably GitHub's brand toolkit (brand.github.com), IBM's Carbon design system (carbondesignsystem.com) and Dropbox Brand (brand.dropbox.com). They are adapted, not copied.

## Header

Version (semver), date, owner, and how to propose a change (an entry in `decisions.md`). State precedence: "Where an earlier note disagrees, this file wins."

## Logo

- Variants and when each is used: full lockup, mark only, a solid version for small sizes, reversed.
- Minimum size in px for each variant, and the size at which the small version takes over.
- Clear space as a unit taken from the mark itself (for example "the height of the mark"), so it scales.
- Approved colours for each background, and backgrounds it must not sit on (busy photographs, low-contrast fills).
- Four to six rendered don'ts: stretching, rearranging, recolouring, effects, outlines, busy backgrounds.
- A co-brand rule if partners are likely: the two marks are about the same optical size and centred.
- Generate every output (favicon sizes, social images, app icons) from one source file.

## Colour

- Proportion as a rule, not only a palette: "mostly neutral, with small moments of accent".
- One meaning per colour, written next to its role token.
- Text, fill and stroke usage: which roles may carry text.
- Measured contrast for every text and accent pair on each theme (`scripts/colour_check.py`).
- Keep the palette small: a neutral ramp of about eight steps, one or two accents, and status colours only if the product shows status.

## Type

- At most eight named styles (for example `display`, `h1`–`h3`, `body`, `body-small`, `label`, `mono`), each with family, size, line height, weight, tracking, case, fallback chain and use.
- Whether each size is fixed or fluid, and the fluid range.
- A scale and minimum size for each medium produced (web, slides, documents). Never shrink type below the minimum to make content fit; choose another layout or split the content.
- Rules the typeface implies: do not track a typeface that has tracking built in; reserve alternate widths or weights for named uses.

## Layout and grid

- Base unit (for example 8 px), a spacing scale of at most ten steps, and the rule for changing step at a breakpoint rather than inventing a value.
- Columns, margins and gutters for two or three breakpoints.
- Allowed image ratios (for example 1:1, 3:2, 16:9).
- A one-sentence construction rule, such as "type aligns to the box padding" or "show the grid with rules at most twice per page, then use it invisibly".
- One annotated construction drawing for each key layout (hero, section, card, slide).
- Layout contracts for templates: required and optional slots, maximum lines, reading order and what happens on overflow.

## Imagery

One system, divided by job, so each kind of image has a reason to exist:

| Kind | Job | Size tier | Rules to state |
|---|---|---|---|
| UI icons | Label actions and states | 16–32 px | Grid, stroke, corner rule borrowed from the typeface, contrast equal to text, 44 px touch target |
| Pictograms or spot art | Mark a concept or section | 48 px and up | Never used as UI icons or as the logo |
| Illustration | Explain abstract ideas, soften errors | Hero, spot, mini | The drawing rules from the asset-style studies; light, projection, accent use |
| Photography | Show real people, work and customers | — | Subject, light, crop, treatment (for example greyscale next to illustration) |
| Diagrams | Explain structure or data | — | No illustration or gradients inside; colour only for grouping |

Give each asset a rights entry (see spec-and-tokens.md).

## Motion

Only if the brand moves:

- Three or four durations tied to use: feedback about 70–110 ms, small changes 150–240 ms, large changes about 400 ms.
- One signature easing curve, with entrance and exit variants.
- Two to four principles, at least one concrete enough to check ("a wink, not confetti").
- A reduced-motion rule: what is shown instead.

## Data

Only if the organisation publishes numbers: a categorical sequence of four to six colours in a fixed order, checked for contrast between neighbours; one sequential ramp; a status set; and the rule "never colour alone" (add labels, patterns or position).

## Accessibility

Text at least 4.5:1 (large text 3:1); icons at the contrast of their text; a defined focus style; 44 px targets; alt text for every meaningful image; no autoplay sound and no flashing; a reduced-motion version of anything that moves.

## Expression levels

Two or three levels of loudness (for example quiet, standard, loud), which surfaces use which, and which elements each level may use. A product screen is quiet; a launch page or event can be loud. This lets the brand stretch without a second identity.

## Applications

`applications.md` lists three to six real surfaces the brand must serve (website hero, slide, social card, document, email signature, proposal), each with a rendered example, its template file and its layout contract. For a small team, templates do more than guidance: people copy a working file.

## What not to build

Enterprise kits carry overhead a small organisation does not need: component-level tokens with every interaction state, four or more themes, five breakpoints with fluid type sets, separate guides per product and event, custom variable typefaces, interactive demo microsites, 14-colour palettes and 20-step grey ramps, and sign-off committees. Add brand architecture (sub-brands, product lockups) only when a second product exists. Show the range a rule permits with `templates/compare.html`, not with a bespoke site.
