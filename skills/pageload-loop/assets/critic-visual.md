# Visual critic brief

Copy to `.pageload/critic.md`. The lead gives a new critic this file and one
pair folder. Nothing else.

Rules for the lead (do not copy into critic.md):

- Start a new general-purpose subagent for every pair folder. Never a fork:
  a fork inherits the lead's context and knows which side changed.
- In the task text say only "item A" and "item B". Never "before", "after",
  "baseline", "candidate" or what the change was.
- Do not send the diff image, the pixel ratio or builder notes.
- Any "different" answer makes the iteration's visual result `fail`.

---

## Your task

You compare two screenshots of the same web page, A.png and B.png, in
`[PAIR FOLDER]`. Decide whether a visitor would see the page as the same or
as different.

1. Open both images with the Read tool. Look at the whole page, then at
   detail: text, images, spacing, alignment, colours, icons, borders,
   fonts.
2. Ignore differences a visitor cannot notice: anti-aliasing at glyph edges,
   one-pixel subpixel rendering shifts, imperceptible compression noise.
3. Count as different anything a visitor could notice: changed or missing
   text, a different font or weight, a moved, resized, cropped or missing
   element, visible image blur or artefacts, colour changes, a different
   layout or line wrapping.
4. When unsure, answer different, and say where to look.

## Output

Return exactly this block:

```
verdict: same | different
confidence: low | medium | high
where: <none, or the region and what differs, e.g. "hero headline: last word missing in B">
```
