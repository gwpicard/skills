# Agent defaults: patterns that make a build read as machine-made

Coding agents converge on a shared house style. In one bake-off, two model families built 18 homepages from one brief under six different style prompts (brutalist, organic, playful, vibrant, dark, luxury). Blind critics could tell the model families apart, and the computed styles showed:

- 14 of 18 light pages used the same cream or paper background, often in a variable named `--paper`;
- all 18 headlines used tight negative letter-spacing;
- 15 of 18 put an accent-coloured word in the main headline;
- 17 of 18 used a full-width coloured band;
- several pages from different models invented the same example company names and wrote near-identical copy;
- a shared "frontend design" instruction file caused many of the tells it was meant to prevent.

Style prompts changed the surface and left the structure alone: "two template families wearing six identities".

## How to use this list

- Use it as a gate after a build, not as a target before one. Passing it is necessary and not sufficient.
- When several builds exist, count each pattern across them. A pattern present in most builds is a default, whatever the prompt asked for.
- A listed pattern can be right for a brand. Keep it deliberately, write down why, and make sure it carries meaning.
- Extend the list with tells you find in your own runs, each with the count that justified it.

## Layout

- A 50/50 hero with text left and an image or card right.
- The same container width and section rhythm on every section.
- Dense bento grids of equal cards; sibling cards each in a different colour.
- Pills or chips for every label, tag and button.
- An eyebrow label above every heading; numbered "01 / 02 / 03" sections by reflex.
- Breadcrumbs, step labels and helper text that repeat what the layout already shows ("Pick a business type to continue").
- A default floating or pill navigation with stock shadows; it reads as a template.

## Type

- Tight negative tracking on every headline.
- Monospaced, uppercase, widely tracked labels as decoration.
- The default display-serif plus grotesk pairing that agents reach for.
- An accent-coloured word inside the headline.

## Colour

- Cream or warm paper ground with a terracotta or clay accent.
- One hot accent used everywhere, so it means nothing.
- Purple or blue gradients, glows and grain overlays.
- Colour applied to every element by default rather than as a signal.

## Content

- Invented metrics, chart values, percentages and testimonials.
- Slogans and taglines the user never wrote; changed names for approved stages or products.
- Meta lines that say nothing ("Results are measured", "Built for teams").
- AI-sounding words: "real work", "seamless", "unlock", "empower", "leverage", "holistic", "groundwork", "supercharge".
- Instructions that a working interface would make unnecessary.

## Imagery

- Glowing brains, circuit nodes, robots, sparkles, random floating 3D shapes.
- A diagram of the offer presented as the visual concept.
- Literal props that do not belong to the customer's world.
- Toy-like 3D people or construction-kit blocks used for every concept.
- Image-model detail that cannot exist: impossible beams, melted text, inconsistent angles.
