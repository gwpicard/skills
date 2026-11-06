# Starting from existing material

Use this in a rebrand, or when an organisation has guidelines, templates, decks or a site that already carry decisions. The aim is to keep what is decided, find what is contradicted, and never let a model fill a gap with an invented value.

## 1. Collect

List every source in `sources.md`: guideline documents, templates, recent decks and documents the organisation considers good, the live site, logo and font files. Record a checksum or date for each, so later claims can point at a fixed version. Check font licences now: desktop, web and embedding permissions decide what the kit may use.

## 2. Extract claims with quotes

For each statement the sources make about the brand, record a claim:

```yaml
- claim: "Logo clear space equals the height of the mark"
  strength: hard          # "must", "never", "always" -> hard; "should", "prefer" -> soft
  source: "guidelines-2023.pdf, p. 12"
  quote: "Always leave clear space equal to the height of the symbol."
```

Discard any claim without a verbatim quote. Aspirational statements ("be bold", "feel premium") are not rules; keep them as rubric questions for critics. When two sources disagree, record both as one ambiguity.

## 3. Measure what the material actually does

Measure approved documents and pages: margins, type sizes, colours in use, logo sizes, spacing (`scripts/measure_reference.mjs` for web pages). Practice often differs from the guidelines. A regularity the guidelines never state becomes a proposed soft rule, not a hard one.

## 4. Turn disagreements into questions

Every conflict between sources, or between a source and practice, becomes a numbered question with both sides shown, ideally as crops side by side:

```
Q3. The guidelines set body text at 11 pt; nine of the twelve recent documents use 10 pt. Which is right?
    1. 11 pt (guidelines)  2. 10 pt (practice)  3. Other
```

Questions that block a rule stop that rule from entering the kit until answered.

## 5. Decide what to keep

With the answers, mark each element keep, adjust or replace, and record it in `decisions.md`. Then run the stages as usual: positioning and lines still come first, and the existing visual elements become inputs to the studies rather than settled facts.
