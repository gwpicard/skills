# D4: Product & User Experience

Analyze this repository for PRODUCT & USER EXPERIENCE. Your goal is to reverse-engineer a product requirements document (PRD) from the code. Use PRODUCT LANGUAGE, not code language — translate code constructs into what they mean for users.

Your task:
1. Read: routes/pages, navigation configs, form components, validation logic, middleware, landing pages, onboarding flows
2. Grep for: navigation items, menu definitions, form fields and validation rules, business rule implementations (guards, policies, permissions), integration SDK imports, pricing/plan logic, feature flag checks, analytics event names (these reveal product priorities)
3. Extract error messages — these are the most product-oriented text in the code and describe constraints in user-facing language
4. Identify:
   - What problem this product solves and for whom (target users/personas from RBAC roles, separate UI paths, auth scopes)
   - All features grouped by product area, classified as Core (critical path), Supporting (enhances core), or Peripheral (admin, edge-case)
   - Main user flows (signup, core workflows, admin tasks) — describe step by step in PRODUCT terms
   - Domain model in business terms (not just schema — what do the entities MEAN to users?)
   - State machines and lifecycle patterns (e.g., order statuses, task workflows) — search for status/state enums, transition methods, state machine libraries
   - Business rules (validation, limits, pricing tiers, permissions)
   - Discovered business constants — magic numbers and hardcoded values that represent business decisions (MAX_RETRIES, TRIAL_DAYS, FREE_TIER_LIMIT, etc.)
   - Feature flags and experiments — search for flag libraries, ENABLE_*/FF_* env vars, variant logic
   - External integrations and what they enable from a product perspective
5. Create Mermaid flowchart diagrams for the 2-3 most important user flows (limit each to 15-20 nodes max, show happy path first, then branch to errors)
6. Create Mermaid stateDiagram-v2 for any state machines found
7. If the codebase is large enough, identify bounded contexts (modules/services with distinct domain boundaries)

For each finding, assign a confidence level:
- **High**: Explicitly stated in code/comments
- **Medium**: Inferred from patterns and naming
- **Low**: Guessed from naming alone

Return your findings as a markdown section starting with `## Product & User Experience`. Include:
- Product overview (what, who, why — 3-4 sentences in product language)
- User personas/roles table (Role | Description | Key Permissions | Detection source)
- Feature map table by area (Feature | Description | Criticality | Entry Point | Key Files)
- Mermaid user flow diagrams (2-3 key flows with step descriptions and business rules per flow)
- Domain model in business terms (Entity | Business Meaning | Key Rules | Confidence)
- Business glossary: terms where the code uses specific domain language (Term | Definition | Code representation)
- State machines (Mermaid stateDiagram-v2 if found)
- Discovered business constants table (Constant | Value | Likely Purpose | Location)
- Business rules summary
- Feature flags / experiments (if found)
- Integrations table (Service | Category | Product Purpose | Data Flow Direction | Failure Impact)
- "Requires Human Input" section noting what the automated analysis cannot determine: strategic priorities, competitive context, success metrics, deprecation status

Keep your output under 300 lines. Focus on the most important findings.
