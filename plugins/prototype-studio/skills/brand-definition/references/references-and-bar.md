# References and the quality bar

Negative feedback ("generic", "not quite") without a positive target is the most expensive state a brand project can be in. Every round produces a new rejection and nothing converges. Define the target with examples the decision-maker chooses.

## Collect the picks

1. Ask for three to eight references with the quality wanted, and one line on what the user likes in each.
2. If the user gives adjectives, turn each into a question about a specific element: "Whose navigation feels expensive to you?", "Which site handles a long story well?"
3. Offer a pick sheet when the user has no list: twelve to twenty candidates in a grid, chosen across the categories below, with the user picking their top five.
4. Confirm the kind of target. A request for "not generic" has meant "polished commercial sites with character" as often as "experimental, abstract work". Show two contrasting candidates and ask which is closer before building.

Categories worth covering:

- direct peers (to know what to avoid as much as what to take);
- adjacent commercial products with craft (the most common real target);
- craft outside the web: print, architecture, product manuals, information design, explorable explanations.

## Capture and measure

Run `scripts/capture.mjs` for viewport strips and section crops at 1440 px and 390 px. Run `scripts/measure_reference.mjs` for the computed anatomy: content width, columns, type sizes and weights in use, letter-spacing, line length, section spacing, radii, colour count, and counts of common agent tells.

Measurements change decisions in a way that descriptions do not. "Generous whitespace" is an opinion; "section spacing 160 px against our 96 px" is a fix.

## Write one note per reference

In `references/<name>.md`:

```
What to take: headline 64/68, weight 500, left-aligned on a 7-of-12 column measure; one image per section, full bleed.
What not to take: their purple accent; the product screenshots (we have no product UI).
Element it informs: home hero, section rhythm.
```

Map every reference to the element of your work it informs. A reference with no element is mood, and mood references give no structure.

## Keep the references visual through the work

The common failure is to read the references, write sentences about them, and then build from the sentences. The references drop out and the build drifts back to defaults. Instead:

- put the reference crop beside the matching element of the build in every review;
- overlay the measured grid on your build;
- cite the reference note in the brief for each element.
