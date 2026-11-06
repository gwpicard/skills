# Feature PRD Template & Guidance

Use this template when writing a PRD for a specific feature within an existing product. It's lighter-weight than the full product PRD but still demands precision and thoroughness.

---

## 1. Feature Summary

One paragraph covering:
- What is this feature?
- Which product does it belong to?
- Why are we building it now?

## 2. Problem / Opportunity

Describe what's driving this feature:
- What user problem does it solve, or what opportunity does it capture?
- How do users cope today without this feature?
- What evidence do we have that this matters? (user feedback, data, research)
- What happens if we don't build this?

## 3. Goals & Success Metrics

| Goal | Metric | Target | Timeframe |
|------|--------|--------|-----------|
| e.g., Reduce support tickets about X | Tickets tagged "X" per week | 50% reduction | 30 days post-launch |

Define 2-4 metrics. Each must be:
- **Measurable** — Can you actually track this?
- **Specific** — Includes a numeric target
- **Time-bound** — When do you expect to hit the target?

## 4. User Stories & JTBD

### Jobs To Be Done
> When [situation], I want to [motivation], so I can [expected outcome].

### User Stories
> As a [persona], I want to [action], so that [benefit].

List all relevant stories. Mark priority: Must / Should / Could.

## 5. Detailed Requirements

### Functional Requirements

Group by sub-area if the feature is complex:

- FR-001: The system shall [requirement]
  - **Acceptance Criteria:**
    - [ ] Given [context], when [action], then [result]
    - [ ] Given [context], when [action], then [result]

- FR-002: The system shall [requirement]
  - **Acceptance Criteria:**
    - [ ] Given [context], when [action], then [result]

### Non-Functional Requirements

- **Performance:** Response time, throughput targets
- **Security:** Access control, data handling
- **Scalability:** Expected load, growth considerations
- **Compatibility:** Browser/device/OS requirements

## 6. User Flow

Describe the step-by-step journey for this feature:

### Flow: [Primary Use Case Name]
**Trigger:** What initiates this flow?
**Actor:** Which user/persona?

1. **[Step]** — What the user sees/does and what the system responds with
2. **[Step]** — Continue...
3. **[Resolution]** — End state

### Alternate Flows
- **[Variation name]:** Describe how the flow differs under [condition]

## 7. Edge Cases

| Scenario | Expected Behavior | User Communication |
|----------|-------------------|-------------------|
| [Empty state] | [Behavior] | [Message to user] |
| [Error condition] | [Behavior] | [Error message] |
| [Boundary condition] | [Behavior] | [Feedback] |

Think through:
- What if there's no data yet?
- What if there's too much data?
- What if the user lacks permission?
- What if a dependency is unavailable?
- What if the user does something unexpected?
- What if the action is performed concurrently by multiple users?

## 8. Design Direction

### Emotional Tone
How should this feature feel? (Reference the product's emotional thesis if one exists.)

### Key Interactions
- Describe important interactions (hover states, transitions, feedback moments)
- Note any motion or animation requirements

### Design Constraints
- Must it follow an existing design system? Which patterns to reuse?
- Any new patterns this feature introduces?
- Mobile / responsive considerations

### Copy & Messaging
- Key labels, button text, empty states, error messages
- Tone guidance for this feature's context

## 9. Dependencies & Risks

### Dependencies
- **Upstream:** What must exist before this feature can be built?
- **Downstream:** What other features or teams are affected by this?
- **External:** Any third-party services, APIs, or integrations required?

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| [Risk] | High/Med/Low | High/Med/Low | [Mitigation] |

## 10. Rollout Plan

### Release Strategy
- Big bang / phased / feature flag / beta?
- Who gets access first?

### Rollout Phases
1. **Phase 1:** [Scope, audience, duration]
2. **Phase 2:** [Expanded scope]
3. **General availability**

### Rollback Plan
- How do we roll back if something goes wrong?
- What data considerations exist for rollback?

### Communication
- How will users learn about this feature? (changelog, in-app, email, docs)

## 11. Open Questions

- [ ] [Question] — Owner: [who], Due: [when]
- [ ] [Question] — Owner: [who], Due: [when]

---

## Writing Guidance

When filling in this template:

1. **Anchor to the product.** Reference the product's existing design system, emotional thesis, and patterns rather than reinventing them.
2. **Be thorough on acceptance criteria.** This is what engineers build against and QA tests against. Ambiguity here becomes bugs later.
3. **Cover the unhappy paths.** Edge cases and error states are where features break in production.
4. **Keep scope tight.** A feature PRD should be implementable in one sprint or release cycle. If it's too big, break it into multiple feature PRDs.
5. **Mark assumptions.** Use `[ASSUMPTION]` for anything you're not certain about.
6. **Include rollout thinking.** How the feature ships is as important as what it does.
