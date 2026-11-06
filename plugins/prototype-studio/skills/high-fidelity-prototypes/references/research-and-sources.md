# Research that informs a prototype

Use this file when references or UX evidence would resolve a design decision. The links are starting points, not a mandatory reading list. Verify current URLs and page contents when using them. Do not describe every reference as applicable to every product.

## Small research loop

1. Name the uncertainty: e.g. selecting an object versus commenting on a page, browsing pending proposals, or displaying a type hierarchy.
2. Choose relevant primary product guidance, standards, or original UX research. Inspect shipped products when available, using their actual detail pages and interactions.
3. Capture the observed pattern, why it fits the user's task, the specific adaptation, and the limit of the evidence. Keep observed facts distinct from recommendations.
4. Implement the relevant behavior and evaluate it in the worked scenario. A familiar pattern is a starting hypothesis, not proof of usability.

For dynamic sites inspect navigation, tabs, controls, hover/selected states, editable specimens, overlays, and linked examples as relevant. Inspect visual assets and embedded previews when they carry information absent from extracted text. Source/CSS inspection can clarify mechanisms; it does not establish rendered behavior, accessibility, or motion quality. Report unavailable live inspection explicitly.

## General interaction and accessibility

- [Nielsen Norman Group: usability heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/): use as a lens for state visibility, familiar language, recovery, recognition, and unnecessary complexity. Turn a heuristic into a concrete observation, not a vague quality claim.
- [W3C WAI-ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/): interaction and keyboard conventions for custom widgets. Prefer native elements where they suffice.
- [WCAG quick reference](https://www.w3.org/WAI/WCAG22/quickref/): keyboard access, focus, contrast, status announcements, and non-color cues. A prototype inspection is not a conformance certification.
- [W3C ATAG overview](https://www.w3.org/WAI/standards-guidelines/atag/): for authoring tools, evaluate both access to the editor and support for accessible output.
- [Carbon Design System](https://www.carbondesignsystem.com/): find the specific component or pattern; inspect its states, usage and accessibility guidance. Do not copy a web-component taxonomy into a different product without adapting it.

## Generative and asynchronous systems

- [Microsoft Research: human-AI interaction guidelines](https://www.microsoft.com/en-us/research/blog/guidelines-for-human-ai-interaction-design/): invocation, dismissal, correction, uncertainty, cautious adaptation, and understandable consequences.
- [Google PAIR Guidebook](https://pair.withgoogle.com/guidebook-v2/chapters): mental models, feedback/control, and graceful failure. Especially relevant to what the system knows, what feedback changes, and what happens after an error.

Apply these when AI is part of the task. They do not imply adding chat, approval gates, confidence scores, or an AI sidebar to ordinary applications.

## Detailed visual specifications and libraries

These are valuable when a product contains brand management, design systems, reusable components or visual inspectors:

- [GitHub Brand Toolkit](https://brand.github.com/): foundations, annotated layout constructions, usage examples, and applications. Inspect [typography](https://brand.github.com/foundations/typography) and [layouts](https://brand.github.com/graphic-elements/layouts) for specimens rather than metadata alone.
- [Carbon typography](https://www.carbondesignsystem.com/building-blocks/foundations/typography/overview): named styles and coherent hierarchy. [Type sets](https://www.carbondesignsystem.com/building-blocks/foundations/typography/type-sets) documents role, family, size, leading, weight and tracking.
- [Mozilla Protocol](https://protocol.mozilla.org/): variants, rendered component previews, guidance and implementation definitions. Its .html detail/preview routes may expose specimens more clearly than extracted navigation.
- [Dropbox Brand](https://brand.dropbox.com/): expressive demonstrations, interactive typography, and distinct asset families. Borrow meaningful exploration; avoid adding spectacle that obstructs a business task.
- [NHS identity guidelines](https://www.england.nhs.uk/nhsidentity/identity-guidelines/): permitted uses, exceptions, practical font alternatives and real-world applications. Some pages may require a browser verification flow.

Synthesis for an inspector: specimen → properties → usage and exceptions → checks → source → history. Use this when the user needs to inspect a specification; it is not a mandatory page layout for all prototypes.

## Review, provenance and versions

- [Adobe Acrobat: document comparison](https://helpx.adobe.com/acrobat/using/compare-documents.html): highlighted content, paired views, navigation between changes and change-type filtering.
- [Figma: version history](https://help.figma.com/hc/en-us/articles/360038006754-View-a-file-s-version-history): previewing snapshots in context and restoring versions while preserving access to later history.
- [Vale: structured rules](https://docs.vale.sh/topics/styles): check method, scope, severity, message, source link and correction action. Useful when designing rule configuration; do not label judgment-based checks deterministic.

These references support product decisions. They do not require installing the referenced products or libraries.
