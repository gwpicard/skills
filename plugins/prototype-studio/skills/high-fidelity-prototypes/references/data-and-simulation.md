# Data, scope and simulation

Use this file when the prototype has records, roles, services or several screens that share data. A one-screen experiment needs little of it. The data decides whether the prototype feels plausible and whether its layouts survive real use; random names pasted into idealised cards are not enough.

## Fidelity contract

Decide each dimension before building, and write down what is excluded.

| Dimension | Decide |
|---|---|
| Visual | Intended appearance, brand source, type, icons, imagery, density |
| Interaction | Which controls, navigation, forms, selection and keyboard paths really work |
| Content | Real labels, errors, long text, domain language |
| Data | Entities, relationships, totals, timestamps, distributions |
| State | Initial, populated, empty, loading, success, error, permission and recovery, where they apply |
| Persistence | What survives navigation, reload and a reopened session |
| Services | What is local, simulated, intercepted or actually integrated |
| Evaluation | What was checked automatically, inspected by eye and tested with people |

A simulated payment can show entry, pending, failure and confirmation without a real transaction. Say so in the handoff.

## Capability matrix

One row per in-scope capability. The rows below are examples, not assumed requirements.

| ID | Capability | Role | Entry | Main behaviour | Failure or alternative | Data effects | Evidence | Status |
|---|---|---|---|---|---|---|---|---|
| C01 | Create a project | Editor | Project list | Create, open detail, see it in the list | Invalid name; save fails; cancel | New project and activity entry | Journey run | Planned |
| C02 | Filter projects | Viewer | Project list | Combine filters, clear, return | No matches; reload; browser Back | Filters in the URL | Interaction check | Planned |

For each journey behind a row, know the entry point and prerequisites, the starting data and permissions, the feedback during processing, the downstream effects of success, and the routes for cancel and recovery.

Questions often missed:

- Can a user start from a deep link rather than the home screen?
- What happens when they leave and return? Do Back and Forward behave predictably?
- Is an empty product different from a search with no matches?
- Is permission denied different from missing data or a service error?
- What happens when an item changes status while the user is viewing it?
- Can a user abandon a process without losing data by accident?
- Does "done" mean the same thing in the list, the detail, the dashboard and notifications?

## Data rules

- Define the domain model first: entities, IDs, relationships, roles, statuses, timestamps and derived values.
- Curate a small, coherent narrative dataset for the worked scenario. Add generated records only for volume and edge cases.
- Compute summaries, counts and totals from the records. A hardcoded dashboard will contradict the list behind it, and its numbers are invented.
- Use a fixed seed and a fixed reference date. Relative dates ("3 days ago") drift otherwise, and a reviewer cannot reproduce what you saw.
- Use realistic distributions of status, text length, missing values and amounts for the domain.
- Include hard content: long names and translations, missing images, large numbers, many records.
- Use synthetic personal data and safe example contact details (`example.com`, reserved phone ranges). Never send anything to a generated address.
- Bundle essential assets so the demonstration does not depend on external images.
- Fix the units, timezone, locale and currency, and write them down.

## Scenario presets

Offer the presets the evaluation needs, from a reviewer control that is visibly separate from the product.

| Preset | Shows |
|---|---|
| First use | No records; a clear starting action |
| Everyday use | A plausible populated state |
| Dense use | Many records, long labels |
| Attention required | Overdue, failed, incomplete or conflicting records |
| Restricted role | Read-only behaviour and permission boundaries |
| Slow service | Pending feedback and repeated-click handling |
| Recoverable failure | An explanation, preserved input, retry or alternative |
| Locale stress | Long strings, other number and date formats, right-to-left text when in scope |

A preset must not change the behaviour under study by accident.

## Simulation layering

Keep these concerns separate enough that behaviour stays consistent across screens. This need not become a backend.

| Concern | Holds |
|---|---|
| Domain | Entities, allowed status transitions, permissions, calculations |
| Fixtures | Narrative data, stress data, scenario presets |
| Service layer | Reads, writes, simulated responses, deterministic latency and failure |
| Application state | Session, selected role, drafts, transient UI state |
| Routes | Reachable screens, deep links, filters and selection in the URL where useful |
| UI | Components, layout, feedback |

A small adapter object is enough for most prototypes. Intercept real HTTP requests (for example with MSW) only when the existing code already makes them. Write workflows with more than a few states as an explicit transition table; reach for a state-machine library only when branching, retries or concurrent work make plain state hard to follow.

## Functional integrity

- An action changes the right record and every view that shows it, including counts, activity and notifications.
- Validation follows real rules and gives actionable errors.
- A pending action cannot create duplicates.
- A failure preserves the user's work; an optimistic update rolls back when the simulated call fails.
- Search, sort, filters and pagination work on the same data.
- Reload, deep links and browser history behave deliberately.
- Long-running work has pending, completed, failed and cancelled states where relevant.
- Upload, export, invitations, sign-in and payment state their simulation boundary.

## Reset and persistence

State where data lives: memory, browser storage or a service. Provide one reset that clears storage, reseeds fixtures, resets simulated services and returns to a known entry point. Version stored data, so state left by an old build cannot silently break a new one.
