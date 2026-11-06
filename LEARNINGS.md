# Learnings

Each entry records a lesson, the evidence for it, and where it now lives. Evidence is anonymised: "the project" means the source project, not a named client or brand.

Format:

```
## L<number>. <Lesson as an instruction>
Source: <project type, date range, log or record>
Evidence: <what happened, with counts or the user's words>
Lives in: <skill/file>
```

## Source: a consultancy's brand and website, Sep–Nov 2026

Harvested on 6 November 2026 from 13 Claude Code sessions, 74 Codex sessions and the project's brand records.

## L1. Treat a never list as a gate, not as the quality bar
Evidence: two screens that broke none of the 47 never-list rules were still called "generic" by the founder and by critics ("Squarespace/Framer consultancy template").
Lives in: high-fidelity-prototypes/SKILL.md (Set the visual bar); agent-defaults.md; spec-and-tokens.md.

## L2. Expect agent defaults to converge across models and style prompts
Evidence: 18 homepages from two model families under six style prompts: 14 used the same cream ground, 18 used negative headline tracking, 15 put an accent word in the headline; models invented the same example names. Blind critics described "two template families wearing six identities".
Lives in: high-fidelity-prototypes/references/agent-defaults.md.

## L3. Define "good" with examples the decision-maker picks before the first visual build
Evidence: "generic" was said about five times over four versions before the founder supplied 13 reference sites. "Not generic" had been read as experimental when it meant polished commercial sites with character; the misread cost a round.
Lives in: high-fidelity-prototypes/SKILL.md; brand-definition/references/references-and-bar.md.

## L4. Keep references visual: measure them and show them beside the build
Evidence: the agent read the references, summarised them in sentences and built from the sentences; the founder asked "wasn't that the idea of having external references, so it's not just words to code?". Measured anatomy of the picked sites produced the first version judged "much better".
Lives in: references-and-bar.md; scripts/measure_reference.mjs.

## L5. Change one variable per round; fix the subject when testing style
Evidence: a brief asking for a "pen-like" drawing style let the subject vary, and builders drew roofs and vaults; the founder called it the wrong reading. The next round fixed the subjects and varied five line styles, and a decision followed on one grid. A four-level line study later settled texture in a day.
Lives in: asset-style-studies.md; high-fidelity-prototypes/SKILL.md (Work with the user in rounds).

## L6. Translate taste words into visible properties
Evidence: "every element just seems like a computer line, just with different thicknesses" became pressure taper, overshoot, irregularity and hatching, which the founder accepted. "Japanese-inspired" became precision, empty space and one seal-like accent, with no motifs.
Lives in: asset-style-studies.md; visual-direction.md.

## L7. Find the real source of character before amplifying it
Evidence: heavy stroke texture was added, codified over four spec versions, then removed as "a bit scrappy" once the character was traced to the objects, projection, weight hierarchy and figures.
Lives in: asset-style-studies.md.

## L8. Start from one core idea, ideally the decision-maker's own sketch
Evidence: about twelve agent concepts were rejected in six days ("thinking inside the box"); the founder's own rough concept image ended the search. The agent's diagnosis of the earlier work: "style changes the costume, not the skeleton".
Lives in: brand-definition/references/concept.md.

## L9. Ground metaphors in the customer's real world
Evidence: machines, trucks and a desk of paper ("looks like a school website") failed; a real office floor plan and AI shown as one step inside existing software landed.
Lives in: concept.md.

## L10. Settle the asset style before polishing the story
Evidence: about ten days of work on a 3D story were replaced in one day once the style question ("gimmicky", "minecraft") was finally asked.
Lives in: concept.md; high-fidelity-prototypes/SKILL.md.

## L11. Write the spec from approved examples at the first sign of drift, and audit every element
Evidence: after assets were tuned one at a time, an audit of 62 elements found 33 drifted and 13 off-language. The spec built from approved crops fixed them.
Lives in: spec-and-tokens.md; agents/spec-auditor.md.

## L12. Keep every value in one source and generate from it
Evidence: three copies of the same colour washes disagreed; a prototype invented a colour; the site kept old pen settings after the spec changed.
Lives in: spec-and-tokens.md; high-fidelity-prototypes/SKILL.md (Build for iteration).

## L13. Measure colour and contrast
Evidence: an accent at 1.01:1 on the dark background and a ΔE00 of 1.2 between two materials looked like taste problems until measured. The founder: "shouldn't this have been considered in the palette?"
Lives in: spec-and-tokens.md; scripts/colour_check.py.

## L14. Give each colour one meaning; colour as a signal, not a default
Evidence: a critic found the accent carried about ten meanings; the founder asked for "one style but different tints". The adopted rule kept illustrations ink at rest with realistic colour only on hover.
Lives in: visual-direction.md; spec-and-tokens.md.

## L15. Use image models to explore and code to ship a system
Evidence: image-model drawings varied in angle and invented impossible beams; exact tracing reached SSIM 0.994 but produced a 144 MB file that could not be animated. Production drawings were generated in code.
Lives in: asset-style-studies.md; high-fidelity-prototypes/SKILL.md.

## L16. In a drawn brand, draw
Evidence: a procedurally fitted 3D building was abandoned partly because it clashed with the drawn assets.
Lives in: asset-style-studies.md.

## L17. Use two builders with different techniques for divergence
Evidence: an image-model builder and a procedural builder on one brief produced complementary strengths, and the adopted language combined them. Two builders on the same storyboard with the same technique produced near-identical results.
Lives in: asset-style-studies.md.

## L18. Critics find tells; the decision-maker makes the taste call
Evidence: four blind critics agreed on the tells and disagreed on which build was best.
Lives in: design-critique/SKILL.md.

## L19. Review from a visitor's first screens
Evidence: a perception review scored a polished story 2/5 for "human" and found about 20 screens before any offer; moving the story to its own page cut it to 11.6 screens.
Lives in: design-critique (perception lens); agents/perception-reviewer.md.

## L20. Extend the brand language into the layout
Evidence: distinctive drawings sat on template navigation and cards ("bootstrappy, cheap") until the layout took the drawing system's grid and numbering.
Lives in: brand-definition/SKILL.md (stage 7).

## L21. Test lines with the opposite test and the swap test; keep rejected lines with reasons
Evidence: one added word ("only") turned a platitude into the adopted line. The rejected-lines brief stopped repeat suggestions, and a second model reached a line independently.
Lives in: positioning-and-lines.md.

## L22. Ground positioning in the record of work
Evidence: an audit called the selling "weak"; re-reading 19 past projects produced a specific value (experts' preparation time) the founder found "much more targeted".
Lives in: positioning-and-lines.md.

## L23. Show options side by side; propose before implementing
Evidence: a single palette and type comparison page led to a decision in about ten minutes; the founder asked about ten times for suggestions "before implementing any changes".
Lives in: templates/compare.html; high-fidelity-prototypes/SKILL.md.

## L24. Quote the user's feedback word for word in the next brief
Evidence: every round brief opened with the founder's words and what they overrode; corrections such as "the tracing was to convert it to something procedural, not chop it up" redirected the next round without loss.
Lives in: asset-style-studies.md (brief template); high-fidelity-prototypes/SKILL.md.

## L25. When the user says "generic", stop and diagnose
Evidence: the agent built on after the founder called a screen generic, and later wrote "I should have stopped there."
Lives in: high-fidelity-prototypes/SKILL.md; brand-definition/SKILL.md.

## L26. Give numbered decisions, one review location and one status record
Evidence: "where am I supposed to look?", "what came out of the review? I don't remember seeing that"; numbered decision lists got answers like "1 ok 2 recommended 3 only colour".
Lives in: high-fidelity-prototypes/SKILL.md; brand-definition/SKILL.md.

## L27. Set physical reference data for illustration and motion
Evidence: figures "too small relative to the furniture" were fixed by a shared scale file; "robot-like" walking was fixed by a fresh agent comparing the gait with published curves.
Lives in: asset-style-studies.md; design-critique (motion lens).

## L28. Bring in a fresh agent when tuning stalls; diagnose before fixing
Evidence: three tuning passes on a walk cycle failed; a fresh agent found seven causes and the founder approved at once. "Explain what you see before changing anything" found a stale depth map without code changes.
Lives in: design-critique/SKILL.md; verification.md.

## L29. Honesty rules never relax
Evidence: the worst bake-off failures were invented chart values and slogans, and changed names for approved stages. Design rules were later relaxed; honesty rules held.
Lives in: spec-and-tokens.md (never.md); high-fidelity-prototypes/SKILL.md; design-critique.

## L30. Archive before replacing
Evidence: dated archives with notes made many reversals cheap, including a story decision reversed after review.
Lives in: brand-definition/SKILL.md.
