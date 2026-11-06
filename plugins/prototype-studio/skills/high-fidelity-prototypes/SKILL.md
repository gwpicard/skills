---
name: high-fidelity-prototypes
description: Creates and iterates on high-fidelity interactive product prototypes from rough ideas, screenshots, references or wireframes, with a deliberate visual direction instead of agent defaults. Use when the user wants to visualise and test an application's screens and behaviour, says "prototype this", "mock up", "clickable demo", "make it look real", "it looks generic", or wants a landing page, tool or flow they can click through for research, alignment or a pitch. Reads a brand kit when one exists and runs the brand-definition skill's lite mode when the look matters and none exists. Does not imply production backend integration or public deployment.
---

# High-fidelity prototypes

Produce a runnable product experience that helps the user evaluate the idea. Fidelity covers coherent behaviour, believable content and visible state as well as appearance. Match the depth to the task: a focused component or one-screen experiment need not become an application.

## Frame the work

- Recover the audience, core job, intended artifact, platform, existing code or design system, and earlier product decisions from the conversation and workspace before asking questions.
- Name who the prototype is for (research, alignment, engineering handoff, a pitch) and the decision it should support. Record what is in scope, what is simulated and what is excluded. A role switcher demonstrates permissions; it does not establish authorisation.
- Ask only consequential missing questions, one at a time during exploratory work, and continue independent work while waiting. If the user asks you to build with reasonable assumptions, build.
- Look for a brand kit: a `brand/` folder with `tokens.json`, `SPEC.md` and `never.md` (see the brand-definition skill). If one exists, take every colour, type style and drawing rule from it, use role tokens (`color.text.primary`, not a hex value), respect the rules in `rules.yaml`, and note the kit version the prototype used. If none exists and the look matters to the evaluation, run brand-definition in lite mode first. If the look does not matter, use a plainly neutral style and say that it is a placeholder.
- Distinguish reusable configuration or library spaces from the flow of creating or editing an instance. Distinguish an entity's create, view, edit, review and history states where relevant; do not present each interaction state as an unrelated navigation destination.
- Choose a realistic worked scenario from the user's own domain and the few representative objects needed to demonstrate it end to end. Common, concrete examples beat specialised or invented ones. Separate records keep separate data. Preserve earlier user decisions as the prototype evolves.
- For an application, list the in-scope capabilities as a capability matrix before scaling screens: each with its role, entry point, main behaviour, failure path, data effects and how you will know it works. A capability that exists only as a screen label is not in the prototype. Start from user goals and derive screens; do not draw a navigation and invent features to fill it.
- For work that spans several rounds, keep a compact brief, the capability matrix and a decision list in project documentation (for example `BRIEF.md` and `COVERAGE.md`). Reuse established files; do not add scaffolding for a small change.

## Set the visual bar before the first visual build

Read [references/visual-direction.md](references/visual-direction.md) and [references/agent-defaults.md](references/agent-defaults.md) before choosing a look.

- Define "good" with examples the user picks, not with adjectives. If the user gives adjectives ("clean", "premium", "not generic"), ask for three to eight sites or products that have the quality, and ask what they like in each. A wrong guess here costs a full round.
- Keep references visual through the build. Measure them (grid, column widths, type sizes, spacing, colour count) and put screenshots beside your build in every review. Do not reduce a reference to a sentence and then build from the sentence.
- Treat the agent-defaults list as a gate, never as the quality bar. A page that avoids every listed pattern can still be generic; avoiding tells removes problems but adds no identity.
- Take identity from what this product owns: its real content and scenario, the user's own sketches and artefacts, its real data and its point of view. Styling alone changes the costume, not the skeleton.
- Give each accent colour or mark one meaning, and use it only where that meaning applies.
- For an application, judge a direction on a dense view, a form, a detail view and an empty or error state, not on a spacious hero. A direction that works only on the hero is not yet a direction for the product.
- Settle the asset style (drawn, photographic, 3D, iconographic) before polishing screens or story. Polishing a story in a style that is later rejected wastes the polish.

## Design the experience

Read [references/interaction-patterns.md](references/interaction-patterns.md) for editing, comments, AI proposals, inspectors, libraries and history. Apply only the patterns relevant to the product.

- Establish the information architecture, core journey and major states before polishing isolated screens. Prefer familiar conventions when they reduce effort.
- Put actions at their real scope: application, collection, record, page, element or selection. Show the current scope. Anchor contextual feedback to its target, with an equivalent keyboard path.
- Use real product labels and plausible content. Never invent metrics, chart values, testimonials or slogans the user did not supply; mark placeholders as placeholders. Keep prototype explanations and simulation caveats in the handoff, not in the product.
- Cut copy until the interface explains itself. A disabled button, the layout or a state change should carry meaning that would otherwise need an instruction, legend or label.
- Make the next action discoverable. Distinguish editing, requesting a proposal, reviewing it and committing it when those are separate operations.
- For design specifications, render the claimed properties: a type specimen uses its declared family, size, weight, line height and tracking at a stated scale. Flag a missing font or asset rather than implying a substitute is exact.

## Work with the user in rounds

- When the user is still shaping the direction, propose before implementing. Show options side by side on one comparison page (see `templates/compare.html` in brand-definition) rather than describing them; users decide by comparing and combining.
- Change one variable per round and hold the rest fixed. If the subject and the style both change, the user cannot tell which one they reacted to.
- Open each round's brief with the user's feedback quoted word for word, and state what it overrides.
- When the user says the result is generic or wrong without naming a target, stop. Diagnose the cause, ask for an example of what right looks like, and only then build again.
- Ask for decisions as a short numbered list, each with your recommendation, so the user can answer "1 yes, 2 recommended, 3 no".
- Give one place to look: the exact URL or file, and what changed there. Keep one status record so the user never has to ask what came out of a review.

## Build for iteration

- Work in the existing stack where practical. For a standalone experiment, plain HTML, CSS and JavaScript are often enough. Do not impose hosting or deployment unless asked.
- Take every visual value from one source (tokens or a single stylesheet). Hand-copied values drift; copies of the same colour in three files will disagree.
- Treat demo data as product design. Read [references/data-and-simulation.md](references/data-and-simulation.md) when the prototype has records, roles, services or more than one screen sharing data. Define the domain model first, compute totals from the records, and use a fixed seed and reference date.
- Use a single clear source of state with stable identifiers and explicit events. Keep rendering, domain rules and simulated services separate, so an action updates every view that shows its data.
- Build one vertical slice first: entry, action, processing, success, failure, recovery, persistence and reset, all working. Then expand to the remaining capabilities with the same patterns.
- Give every visible control an observable result in the worked scenario, an explained unavailable state, or remove it. Simulate unavailable services with bounded, repeatable fixtures, with controllable latency and failure rather than randomness, and say so in the handoff. Do not claim to have read a file, validated compliance or produced an export when that did not happen.
- Preserve entered text, selection and review decisions across navigation. Version any stored state and offer one reset that clears storage, reseeds fixtures and returns to a known entry point. Keep reviewer controls (scenario presets, reset, role switcher) visibly separate from the product.
- Snapshot a reviewed round before patching it, so a regression can be compared and reversed.
- Refactor as the concept stabilises. Do not accumulate overrides, appended scripts or duplicate renderers after each round of feedback.
- Treat image-model output as a concept target, not a final asset: it does not hold exact geometry, projection or registration across a set.

## Verify and refine

Read [references/verification.md](references/verification.md) before handoff or a substantial iteration.

- Run the worked scenario, including return navigation and recovery. Inspect the rendered result in a browser at the primary viewport and one narrow width, with close crops at real size. Syntax checks and state tests cannot establish visual quality; if no browser is available, say that visual verification is incomplete.
- Exercise the states the scenario touches: empty versus no matches, permission denied versus missing data versus service error, slow and failed operations, long and dense content.
- Measure what can be measured: text and accent contrast on every background, and colour difference between surfaces that must read as distinct. Use WCAG 2.2 AA as the default accessibility target; an automated scan supports that review but never establishes conformance.
- For a substantial round, get a fresh-context review through the design-critique skill: a perception review of what a first-time visitor would conclude, and a blind tell count when several builds exist. Critics find tells; the user makes the taste call.
- Repair the underlying pattern behind feedback rather than patching one label. Group feedback by product area, preserve accepted decisions and retest affected dependencies.
- Hand off with a working link or file, a short scenario guide (presets, entry routes, reset), coverage against the capability matrix, concise verification results and limitations, and the assumptions that still need testing with people. Another person should be able to open, explore and reset the prototype without you.
