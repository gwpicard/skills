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
- An empty product, a search with no matches, permission denied, missing data and a service error each look different.
- A deep link opens the right record and state; Back and Forward behave predictably.
- A repeated click during a pending action creates no duplicate; a simulated failure rolls back any optimistic change.
- Every scenario preset is reachable, and reset returns to the same starting point each time.

Apply the relevant subset. Do not create irrelevant review or AI features to satisfy a checklist.

## Rendered inspection

Use an available supported browser/testing tool to inspect the actual running interface. Capture and examine the main screens, an active/contextual state, and a narrow viewport. Inspect overflow, long labels/content, dialogs, real font rendering, empty states, focus, and scroll position.

Stress the interface with long text, empty data, dense data, slow responses, failures, browser zoom and system preferences. Check widths near layout breakpoints, not only the two main ones, and confirm that menus, tooltips, dialogs and sticky elements do not hide important content.

Exercise keyboard navigation and a complete primary action without relying on hover. Compare claimed visual properties against actual specimens. Verify a visual change appears at the correct location in comparison/history, not merely in text below the artifact. If export parity is a product claim, compare exported output rather than assuming browser print matches.

When browser inspection is unavailable, perform syntax, route/render and state-transition checks if useful. Clearly state what was verified and that visual verification is incomplete. A VM test with a mocked DOM cannot establish DOM event behavior, layout, accessibility or screenshot fidelity.

## Accessibility

Use WCAG 2.2 AA as the default target unless the project sets another. Record what you checked; never call the prototype compliant on the strength of an automated scan.

- Native elements before ARIA; every control has a meaningful accessible name.
- Full keyboard operation in a logical order, with focus visible and not hidden under sticky content or overlays.
- Dialogs trap focus and return it to the control that opened them.
- Labels, hints and errors are associated with their inputs.
- Status is not carried by colour alone; important asynchronous updates are announced without constant interruption.
- Text and non-text contrast meet the WCAG criteria. Do not substitute another contrast model when checking WCAG.
- The layout reflows at 400% zoom and with larger text; reduced motion is respected; gestures have alternatives.
- Targets are comfortably sized; inputs use suitable types and autocomplete and permit paste.
- Headings, landmarks, page titles, image alternatives, and labels for charts and tables make sense.

Run axe on every meaningful state at each viewport the prototype supports, including an open dialog and a form with errors, not only the default view. `scripts/axe_states.mjs` does this with Playwright and `@axe-core/playwright` (installed in a scratch folder, run from there):

```bash
cd <scratch> && npm i playwright @axe-core/playwright
node <skill>/scripts/axe_states.mjs --states states.json --viewports 1440x900,390x844 --json axe.json
```

`states.json` names each state by its URL (preset, deep link) and the steps that reach it, for example `{ "name": "invite dialog", "url": "index.html#team", "steps": [{ "click": "#invite" }] }`; the script header shows the full format. It prints violations per state and viewport, with the rule and the element. Set `CHROME_PATH` to an installed Chrome to skip Playwright's browser download. Then do the keyboard and zoom checks by hand: an automated scan finds only some failures and does not establish conformance. For authoring tools, distinguish accessibility of the application from accessibility of the exported artifact. Screen-reader testing with real assistive technology is a separate step; say whether it happened.

## Visual and perception review

Interaction checks do not show whether the prototype looks right or says the right thing. For a substantial visual round:

- Inspect close crops at real size, not only full-page screenshots. Small defects (halos, cut-off lines, stray marks, objects passing through each other in motion) are invisible at thumbnail scale.
- Measure contrast for text and accents on every background and in each colour mode. Measure the colour difference between surfaces that must read as distinct.
- Run the agent-defaults gate (agent-defaults.md). When several builds exist, count each pattern across them. `measure_reference.mjs` in brand-definition counts the common ones; `npx impeccable detect --json <path-or-url>` is an optional second counter (see the design-critique skill for its limits).
- Ask a fresh-context reviewer what a first-time visitor would conclude in five seconds: what the product is, who it is for, and which adjectives it earns. Compare those adjectives with the ones the user asked for. The design-critique skill has the prompts.
- Review motion frame by frame when motion carries meaning: movements should be believable, loops should make sense, and nothing should appear from nowhere.
- Hold the critic's verdict apart from the user's. AI critics agree on tells but disagree on taste; the user makes the taste call.

If you keep screenshot baselines, review each one before approving it: a regression test can faithfully preserve a poor design.

When tuning stalls after two or three passes, ask a fresh agent to diagnose the cause from scratch before trying another fix.

## Review feedback as evidence

Keep what was seen apart from what it means:

| Type | Example |
|---|---|
| Observation | Four participants opened Billing while looking for team permissions |
| Interpretation | The navigation grouping may conflict with their expectations |
| Proposed change | Move permissions under Team and retest the label |
| Uncertainty | Small sample; the task wording may have steered them |

Translate each observation into the underlying issue: destination/state confusion, ambiguous scope, undiscoverable action, incorrect data model, weak visual hierarchy, missing recovery, or absent specimen detail. Repair the pattern and its affected instances; avoid isolated wording patches.

After a substantial iteration, remove obsolete code and controls, consolidate duplicate renderers, and run the changed journey plus its affected dependencies. Do not repeatedly rerun unrelated checks without new evidence.

## Handoff

Provide the actual runnable URL or local file and a short scenario guide: entry routes, presets, how to reset, and the interactions worth trying. Report coverage against the capability matrix, checks completed, concrete limitations and which services and data are simulated. Say which design decisions rest on observation of users, standards, convention or preference, and list the assumptions that still need testing with people; if asked, draft neutral task scripts for that testing. Another person should be able to open, explore and reset the prototype without the builder present. Keep these notes outside normal product UI unless they affect a user's decision within the flow. Do not claim production readiness, successful export, accessibility conformance or visual QA without supporting verification.
