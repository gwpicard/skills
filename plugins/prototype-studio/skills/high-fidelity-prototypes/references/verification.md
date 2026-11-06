# Verification and iteration

Use proportionate checks for the prototype's scope. Pick the critical journey and actual risks; do not add a heavyweight testing program for a cosmetic edit.

## Define success as observable behavior

Write a small scenario from the user's goal, e.g. open saved item → edit content → request a revision → inspect changes → reject one → commit the rest → reopen → restore. Substitute the actual product's actions. Test resulting state, not whether implementation text contains certain words.

For a substantial prototype, cover the relevant invariants:

- Two saved records retain independent contents, comments and history.
- Selecting a target updates controls and feedback to the right scope.
- Editing an object and commenting on it are distinguishable operations.
- Navigating back preserves the relevant inputs and decisions.
- Pending and completed counts match the actual queue.
- Accept/reject decisions produce the expected artifact and do not discard direct edits.
- Add, remove, undo and restore have observable, recoverable results.
- An interrupted operation retains the last usable state and input.
- Reload preserves expected state; a reset permits another walkthrough.
- Export, parsing, validation or external integration claims match what actually runs.

Apply the relevant subset. Do not create irrelevant review or AI features to satisfy a checklist.

## Rendered inspection

Use an available supported browser/testing tool to inspect the actual running interface. Capture and examine the main screens, an active/contextual state, and a narrow viewport. Inspect overflow, long labels/content, dialogs, real font rendering, empty states, focus, and scroll position.

Exercise keyboard navigation and a complete primary action without relying on hover. Check that primary controls have accessible names and that status changes are perceivable. For authoring tools, distinguish accessibility of the application from accessibility of the exported artifact.

Compare claimed visual properties against actual specimens. Verify a visual change appears at the correct location in comparison/history, not merely in text below the artifact. If export parity is a product claim, compare exported output rather than assuming browser print matches.

When browser inspection is unavailable, perform syntax, route/render and state-transition checks if useful. Clearly state what was verified and that visual verification is incomplete. A VM test with a mocked DOM cannot establish DOM event behavior, layout, accessibility or screenshot fidelity.

## Visual and perception review

Interaction checks do not show whether the prototype looks right or says the right thing. For a substantial visual round:

- Inspect close crops at real size, not only full-page screenshots. Small defects (halos, cut-off lines, stray marks, objects passing through each other in motion) are invisible at thumbnail scale.
- Measure contrast for text and accents on every background and in each colour mode. Measure the colour difference between surfaces that must read as distinct.
- Run the agent-defaults gate (agent-defaults.md). When several builds exist, count each pattern across them.
- Ask a fresh-context reviewer what a first-time visitor would conclude in five seconds: what the product is, who it is for, and which adjectives it earns. Compare those adjectives with the ones the user asked for. The design-critique skill has the prompts.
- Review motion frame by frame when motion carries meaning: movements should be believable, loops should make sense, and nothing should appear from nowhere.
- Hold the critic's verdict apart from the user's. AI critics agree on tells but disagree on taste; the user makes the taste call.

When tuning stalls after two or three passes, ask a fresh agent to diagnose the cause from scratch before trying another fix.

## Review feedback as evidence

Translate each observation into the underlying issue: destination/state confusion, ambiguous scope, undiscoverable action, incorrect data model, weak visual hierarchy, missing recovery, or absent specimen detail. Repair the pattern and its affected instances; avoid isolated wording patches.

After a substantial iteration, remove obsolete code and controls, consolidate duplicate renderers, and run the changed journey plus its affected dependencies. Do not repeatedly rerun unrelated checks without new evidence.

## Handoff

Provide the actual runnable URL or local file and brief directions for the important interactions. Report checks completed, concrete limitations and which services/data are simulated. Keep these notes outside normal product UI unless they affect a user's decision within the flow. Do not claim production readiness, successful export, accessibility conformance or visual QA without supporting verification.
