# Product PRD Template & Guidance

Use this template as a structural guide when writing a full product PRD. Adapt sections based on relevance — not every product needs every section, but consider each one before omitting it.

---

## 1. Product Overview

A concise elevator pitch. Cover:
- What is this product?
- Who is it for?
- What problem does it solve?
- What makes it different from existing solutions?

Keep this to 3-5 sentences. Anyone reading just this section should understand the product.

## 2. Problem Statement

Go deep on the problem:
- Describe the current state (how do users solve this today?)
- What's painful, slow, expensive, or broken about the status quo?
- Quantify the problem where possible (time wasted, money lost, error rates)
- Include user quotes or research findings if available

## 3. Goals & Success Metrics

Define what success looks like with measurable targets:

| Goal | Metric | Target | Timeframe |
|------|--------|--------|-----------|
| e.g., Reduce onboarding friction | Time to first value | < 5 minutes | Launch + 30 days |
| e.g., Drive adoption | Weekly active users | 1,000 WAU | Launch + 90 days |

Include both **leading indicators** (early signals) and **lagging indicators** (ultimate outcomes).

## 4. Target Audience

Define your users with specificity:
- **Primary persona** — Who is the #1 user? Role, context, goals, frustrations, technical skill level.
- **Secondary personas** — Who else uses this? How do their needs differ?
- **Anti-personas** — Who is this explicitly NOT for? (Prevents scope creep)

## 5. Jobs To Be Done (JTBD)

Frame user needs as jobs:

> When [situation], I want to [motivation], so I can [expected outcome].

List 3-7 core jobs. Prioritize them (must-have vs nice-to-have).

## 6. User Stories

Translate JTBD into implementable user stories:

> As a [persona], I want to [action], so that [benefit].

Group by feature area. Each story should be independently deliverable and testable.

## 7. User Flows

Describe the key journeys through the product as narrative scenes:

### Flow: [Name]
**Trigger:** What initiates this flow?
**Actor:** Which persona?

1. **Scene 1: [Name]** — Describe what the user sees, does, and feels. Include system responses.
2. **Scene 2: [Name]** — Continue the narrative...
3. **Resolution** — What state is the user in when this flow completes?

**Edge cases:**
- What if [X fails]?
- What if [user does Y instead]?

Cover at minimum:
- First-time / onboarding flow
- Core usage loop (the thing users do daily)
- Error / recovery flows

## 8. Core Features

List each feature with:

### Feature: [Name]
**Priority:** Must-have / Should-have / Nice-to-have
**Description:** What it does and why it matters.

**Acceptance Criteria:**
- [ ] Given [context], when [action], then [result]
- [ ] Given [context], when [action], then [result]

**Edge Cases:**
- What happens when [boundary condition]?
- What happens when [error state]?

Group features by area. Be thorough on acceptance criteria — this is what engineers and QA will build and test against.

## 9. Pages / Screens as Scenes

Describe each major view as a scene rather than a wireframe spec:

### Scene: [Name]
**Purpose:** Why does this scene exist? What job does it serve?
**Entry points:** How does the user arrive here?
**Key elements:** What must be present? (List, don't layout)
**Interactions:** What can the user do here?
**Emotional tone:** How should this scene feel? (e.g., calm and focused, energizing, reassuring)
**Exit points:** Where can the user go from here?

This approach is AI-implementation-friendly and focuses on intent over pixel-level prescription.

## 10. Edge Cases & Error Handling

Consolidate edge cases that span multiple features:

| Scenario | Expected Behavior | User Communication |
|----------|-------------------|-------------------|
| Network lost mid-action | Queue action, retry on reconnect | "Saved offline — will sync when connected" |
| Session expired | Redirect to login, preserve state | "Your session expired. Sign in to continue where you left off" |
| Invalid input | Inline validation | Specific, actionable error message |

Think about:
- Empty states (no data yet)
- Overloaded states (too much data)
- Permission boundaries
- Concurrent editing
- Rate limiting
- Internationalization edge cases

## 11. Emotional Thesis

Define the emotional core of the product:

**Core feeling:** [One sentence describing how the product should make users feel]

**Emotional principles:**
1. [Principle] — [How it manifests in the product]
2. [Principle] — [How it manifests in the product]
3. [Principle] — [How it manifests in the product]

This section drives design, copy, and interaction decisions. Reference it when making tradeoffs.

## 12. Design System Direction

Establish the visual and interaction language:

### Typography
- What personality should the type convey? (e.g., modern & clean, warm & approachable, technical & precise)
- Hierarchy needs (headline, body, caption, code)

### Color
- Mood and associations (e.g., trust = blues, energy = warm tones)
- Functional color needs (success, warning, error, info)
- Accessibility requirements (contrast ratios)

### Layout
- Density preference (spacious vs compact)
- Responsive strategy (mobile-first? desktop-primary?)
- Grid and spacing philosophy

### Motion & Animation
- When to use motion (transitions, feedback, delight)
- Speed and easing preferences (snappy vs smooth)
- Accessibility considerations (reduced-motion support)

### Voice & Tone
- How does the product speak? (casual, professional, playful, authoritative)
- Tone shifts by context (error messages vs celebrations vs onboarding)
- Examples of good and bad copy for this product

## 13. UX Principles

3-5 guiding principles for design decisions:

1. **[Principle name]** — [Description and what it means in practice]
2. **[Principle name]** — [Description]
3. **[Principle name]** — [Description]

These should be specific to this product, not generic ("be intuitive" is too vague).

## 14. Accessibility Requirements

- WCAG compliance level target (AA minimum recommended)
- Keyboard navigation requirements
- Screen reader considerations
- Color contrast requirements
- Motion sensitivity accommodations
- Any domain-specific accessibility needs

## 15. Functional Requirements

Technical capabilities the system must have, organized by area:

### [Area]
- FR-001: The system shall [requirement]
- FR-002: The system shall [requirement]

Use "shall" for requirements, "should" for preferences, "may" for optional.

## 16. Non-Functional Requirements

### Performance
- Page load time targets
- API response time targets
- Concurrent user capacity

### Security
- Authentication method
- Authorization model
- Data encryption requirements
- Compliance requirements (GDPR, SOC 2, HIPAA, etc.)

### Reliability
- Uptime target (e.g., 99.9%)
- Backup and recovery requirements
- Disaster recovery plan

### Scalability
- Expected growth trajectory
- Scaling strategy (horizontal, vertical)

## 17. Data Model

Describe key entities and their relationships:

### [Entity Name]
- Key attributes and their types
- Relationships to other entities
- Constraints and validations

Include an entity relationship overview (describe in words, or use mermaid diagrams if helpful).

## 18. Technical Architecture

High-level technical direction:
- Frontend framework / approach
- Backend architecture (monolith, microservices, serverless)
- Database choices
- Third-party integrations
- Infrastructure and deployment
- API design approach (REST, GraphQL, etc.)

Note: Keep this directional, not prescriptive. Engineers should own the detailed technical design.

## 19. Roadmap

### MVP (Launch)
- Features included and why
- What's explicitly excluded and why
- Target date or timeframe

### V1 (Post-launch iteration)
- Features to add based on MVP learnings
- Known gaps to fill

### V2 (Growth phase)
- Larger features deferred from V1
- Expansion opportunities

### Future Considerations
- Long-term vision items
- Platform / ecosystem plays

## 20. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| [Risk description] | High/Med/Low | High/Med/Low | [Mitigation strategy] |

Consider:
- Technical risks
- Market / competitive risks
- User adoption risks
- Resource / timeline risks
- Regulatory / compliance risks

## 21. Open Questions

Track unresolved decisions:

- [ ] [Question] — Owner: [who], Due: [when]
- [ ] [Question] — Owner: [who], Due: [when]

Don't bury uncertainty — surface it explicitly so it gets resolved.

## 22. Appendix

Include supporting materials:
- Research findings
- Competitive analysis details
- Technical spike results
- User interview summaries
- Reference designs or inspiration

---

## Writing Guidance

When filling in this template:

1. **Start with the emotional thesis** (section 11) even though it appears mid-document — it informs everything else.
2. **Be specific.** Replace every vague word with a concrete one. "Fast" → "< 200ms". "Easy" → "completable in under 2 minutes without documentation".
3. **Write acceptance criteria as given/when/then** for testability.
4. **Describe scenes, not wireframes.** Focus on what the user experiences, not pixel positions.
5. **Include the unhappy path.** For every flow, ask "what goes wrong?" and document the answer.
6. **Mark assumptions.** If you're guessing, tag it `[ASSUMPTION]` so it gets validated.
7. **Prioritize ruthlessly.** Everything can't be must-have. Use MoSCoW or similar.
8. **Keep it alive.** A PRD is a living document — flag sections that need revisiting as the product evolves.
