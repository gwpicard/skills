# Setting a visual direction for a prototype

Use this when the look of the prototype affects the user's judgement of it. For a full brand, use the brand-definition skill; this file covers what a prototype needs.

## 1. Get a target the user chose

1. Ask for three to eight references with the quality the user wants. If they offer adjectives only, translate each adjective into a question: "Which product's navigation feels expensive to you?"
2. Ask what they like in each reference, in one line.
3. Check what kind of target it is. "Not generic" has meant "polished commercial products with character" as often as "experimental portfolio". Confirm with one or two candidate examples before building.
4. If the user has a sketch, canvas or rough image of the idea, start from it. One founder sketch has ended a run of a dozen rejected agent concepts.

## 2. Measure the references

Capture each reference at the primary viewport and one narrow width. Record measurable anatomy: content width and columns, hero height, type sizes and weights in use, line lengths, section spacing, number of colours, radius, and how much of the page is text. The brand-definition skill provides `scripts/measure_reference.mjs` and `scripts/capture.mjs`.

For each reference, write one concrete move to take ("headline set at 64 px, left-aligned on a 12-column grid with a 7-column measure") and one thing not to take.

## 3. Turn taste words into visible properties

Feedback words describe a perception. Translate them into properties you can change, then vary those properties.

| The user says | Properties to examine |
|---|---|
| "generic", "template" | Agent-default layout and type (see agent-defaults.md); missing owned content; no point of view |
| "cheap", "bootstrappy" | Stock components, default shadows and radii, uniform spacing, weak type contrast |
| "computer-made line" | Constant stroke width, perfect joins, no taper, no overshoot, no variation in tone |
| "scrappy", "messy" | Too much texture or wobble, inconsistent weights, stray marks |
| "robotic" (motion or figures) | Even timing, no anticipation, unnatural stride or scale, everything moving at once |
| "gimmicky" | A motif used as the building blocks of everything, novelty rendering, decoration with no meaning |
| "too dense", "crowded" | Copy volume, number of elements per screen, labels that repeat the layout |
| "faint", "doesn't pop" | Contrast with the background, colour saturation relative to line weight |

## 4. Choose one axis per round

Show three to five levels of one property on the same subject: for a line, clean to textured; for an object, matte to rendered; for a layout, quiet to dense. Render them on real content beside the real headline. The user's choice then comes with a limit ("no cleaner than level 2"), which becomes a rule.

## 5. Colour and accents

- One accent colour per meaning. If the accent appears on ten kinds of element, it has ten meanings and none.
- Neutral at rest, colour where it signals something, is a reliable default for interface and illustration alike.
- Measure contrast for text and accents on every background, in both light and dark modes if both exist. Measure the colour difference between surfaces that must read as separate; a ΔE00 below about 3 looks like one colour.
- Put every colour decision into the tokens at once, with its text variant and its dark-mode value.

## 6. Match the medium to the scale

- Image models are good for exploring a direction and for large illustrations reviewed by eye.
- Code or vector geometry suits icons, small sizes and anything that must stay consistent across a set.
- At small sizes only the silhouette survives; draw separate small versions instead of shrinking detail.
