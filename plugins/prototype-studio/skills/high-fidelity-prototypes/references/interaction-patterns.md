# Patterns for coherent interaction

Read only the sections relevant to the task. These are decision aids, not a feature list to implement in every prototype.

## Navigation and configuration

An entity's create form, saved overview, editable settings and version history are related views of that entity. Reusable settings, assets and templates typically live outside an instance-creation flow. A creation flow can select existing configuration and offer a contextual route to create more. A recent-item card should reopen that item's saved state; it must not open a new-item form or a different record with a changed title.

Make global navigation distinguish destinations from local states. Avoid exposing every prototype screen as a sequence of product tabs when the real application has a different structure.

## Contextual and direct editing

Choose an explicit interaction grammar: what a click, text selection, blank-canvas click, drag and Escape mean. Keep a small persistent toolbar when modes or frequently used actions would otherwise be hidden. Expose selected mode and target; hover alone is insufficient.

A scoped inspector can expose actions for the selected component without showing every application function. Select controls by the user's goal: a user requesting another graph style may need alternatives and an instruction field, not a spreadsheet of values. Consider the complete component, including labels, source, captions, child elements and semantics.

For spatial insertion: choose Add → indicate mode → click a location → choose an approved component → place there → allow adjustment and exit the mode. Store the location and actually render the object there. Preserve a keyboard route with an equivalent result. Account for bounds and overlapping content.

## Comments and task queues

Keep scopes distinct: whole artifact, page/record, element, text range. Show the scope near the composer and keep it stable until explicitly changed. Scope a comment to stable object IDs or text anchors; page coordinates alone can become invalid after reflow.

Use a visible anchor/selection state and a related thread. Clicking a pin should select its target and reveal its thread. Keep whole-artifact discussion separate from the selected-element thread, while providing a clear total backlog. Handle removed targets by retaining an unanchored comment rather than attaching it to an unrelated object.

Differentiate direct edits, instructions and proposed changes using more than color. Do not infer that a comment was approved merely because a user navigated away. Preserve draft comments during relevant navigation; avoid rerendering away keyboard focus after every keystroke.

## Generated proposals and review

Decide when the system acts from the product requirements: immediate, after an explicit review, or after a scheduled operation. Do not apply one timing model universally.

When reviewing proposals, distinguish the saved source, proposed revision, accepted decisions and committed result. Let users browse without deciding. Show pending/accepted/rejected counts, a navigable list, and current location. Retain decisions when switching views or returning to the editor.

Start with a small number of understandable views, e.g. Compare and Revised, with an optional highlight toggle. Put highlights on the actual artifact. Text diffs can explain wording; they cannot locate a chart or alignment change. Keep a complete artifact preview when overall flow matters. Identify added, deleted, moved, data, wording and layout changes accurately.

Group changes that depend on one another when rejecting them independently would create an impossible result. Direct human edits must not be lost because an unrelated AI proposal was rejected. Rebuild the result from decisions and display unresolved constraints honestly.

## Async processing and AI

Preserve the last usable artifact during generation. Show meaningful states, preserve inputs on failure, and provide a recovery action. Do not fabricate exact progress or estimates. In a simulated prototype, deterministic phase transitions can demonstrate the intended experience; describe that simulation in the handoff.

Separate automatic formatting/validation corrections from proposed meaning changes where appropriate to the product. Record automatic corrections if users need auditability. State which feedback affects the current output, a future session, a shared rule or a model. Do not silently promote a one-off preference to a shared organizational rule.

If user-supplied sources matter, show source interpretation and allow correction. Known fixtures can carry believable descriptions; arbitrary uploaded files must not receive invented analyses. A file name or extracted text preview is not evidence of full content understanding.

## Libraries, rules and specimens

Separate an individual asset, its variants, a layout, a master and a full template when users need those distinctions. Group by task or role. Include actual previews; named roles; relevant properties; usage/avoidance; provenance; and version information where useful.

Edit structured rules with structured controls. Store method, scope, parameters, severity and action separately from explanatory prose. A dictionary substitution, a regular expression and an AI assessment are different types of rules. Link a displayed validation rule to its actual definition; avoid duplicate lists that can drift.

Render typography at declared settings, indicate canvas scale, and use real assets when available. If a font or asset is unavailable, identify the fallback. A table listing sizes beside uniformly sized text is not a type specimen.

## Recovery and history

Undo/redo covers local actions; saved versions capture meaningful snapshots; an activity log explains events. Model these separately if the user needs all three. Tie an event to its affected object and, when possible, a visual before/after rather than abstract prose alone.

A restore should preserve access to the current state by creating a new version or checkpoint. Handle unsaved edits and comments explicitly. A version label alone is not version history. For reusable configuration, retain change notes, author/origin and configuration snapshots; distinguish suggested lessons from approved rule changes.
