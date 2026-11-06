# Choosing the asset style with studies

The asset style covers icons, illustration, drawing language, 3D, photography and motion. It is chosen by controlled studies, not by successive full redesigns.

## One variable per round

- Fix the subjects (the same five objects or scenes) and vary only the style. When a round changes both, the user's feedback cannot be attributed; in one run, a request for a "pen-like" drawing style produced architectural subjects instead, because the brief let the subject vary.
- Then fix the style and vary the subject.
- Show levels of one property: line from clean to textured (L0–L3), objects from matte to rendered, colour from none to full. Render on real subjects, beside the real headline, on both backgrounds.
- The user's pick comes with a limit ("no cleaner than L2"). Write the limit into the spec.

## Translate taste words into visible properties

| Word | Properties |
|---|---|
| "computer line", "too digital" | constant stroke width, perfect joins, no pressure taper, no overshoot, no tonal hatching |
| "hand-drawn", "pen-like" | pressure taper at stroke ends, slight overshoot at corners, controlled irregularity in straightness, hatching for tone, a weight hierarchy (contour, detail, hatch) |
| "precise", "Japanese-inspired" | fine consistent line, generous empty space, one restrained accent used like a seal; tradition of craft, not motifs |
| "human", "not robotic" | real-world scale, believable motion and gait, curvature, small imperfection |
| "gimmicky" | the brand motif used as building blocks for every concept; novelty rendering |

Build the properties as parameters so a level study is a parameter change, not a redraw.

## Two builders, different techniques

Give two model families the same brief in isolated folders, and have each use a different technique: for example, one draws with an image model and traces to vectors, the other generates geometry procedurally. Compare side by side and combine strengths; in one run the adopted language was one builder's drawn feel on the other's exact geometry.

Two builders on the same storyboard with the same technique converge; use the pair for divergence.

## Find the real source of character before amplifying it

When a style feels flat, find what carries the character before turning anything up. Texture is a common false lead: in one run heavy stroke texture was added, codified and then removed ("a bit scrappy"), once it was clear the character came from the objects, the projection, the weight hierarchy and the figures, not from the stroke.

## Motifs, accents and scale

- Use the brand motif as a hint (an angle, a proportion, one part), not as the building blocks of everything. Cubes used for every icon read as a construction toy.
- Keep the accent rare so it keeps its meaning: once per scene, on the thing that matters.
- Set physical references for illustration: real dimensions for people and furniture in one shared scale file, published gait curves for walking figures, structural logic for buildings.
- Use the right generator for the scale: image models for exploration and large illustrations; code or vectors for icons, small sizes and sets. At 48 px only the silhouette survives, so draw small versions separately.
- Treat image-model output as a concept target. It invents impossible structure and does not hold projection or registration across a set.
- In a drawn brand, draw. A photoreal 3D model will clash with drawn assets, however well it is made.

## Brief template for a study round

```
# Round N: <property under study>
What changed since round N-1 (the user's words):
> "..."
This overrides: <earlier instruction>
Fixed: <subjects, sizes, palette, backgrounds>
Varies: <one property, levels 0–3>
Technique: <builder A> / <builder B>; do not open each other's folders
Check before reporting: render, inspect close crops at real size on both backgrounds, list limits honestly
Deliver: one comparison page, one note per level
```
