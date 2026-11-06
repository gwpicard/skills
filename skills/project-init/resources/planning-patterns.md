# Planning Patterns & Task Breakdown Strategies

Patterns for creating effective development plans and breaking work into manageable tasks.

---

## The Phased Approach

Every project plan should follow the principle: **each phase is independently testable and deployable**.

### Standard Phase Template

```
Phase 0: Foundation     -- Scaffolding, config, CI/CD, core setup
Phase 1: Data Layer     -- Models, database, API endpoints, validation
Phase 2: Core UI        -- Layouts, navigation, core pages, component library
Phase 3-N: Features     -- One phase per major feature
Phase N+1: Polish       -- Performance, monitoring, documentation, launch prep
```

### Why This Order Works

1. **Foundation first** ensures everyone can run the project and CI catches issues early
2. **Data layer before UI** means the UI has real data to connect to, no mocking needed
3. **Core UI before features** establishes patterns that features follow consistently
4. **Features in parallel** are possible once foundation + data + core UI are stable
5. **Polish last** because you can't optimize what doesn't exist yet

---

## Task Granularity

### The 1-4 Hour Rule

Every task should be completable in 1-4 hours. If it's bigger, break it down further.

**Too big:**
```
- [ ] Implement user authentication
```

**Right size:**
```
- [ ] Set up auth provider configuration (NextAuth/Supabase Auth)
- [ ] Create login page UI with email + password form
- [ ] Implement login server action with validation
- [ ] Create signup page UI
- [ ] Implement signup server action with email verification
- [ ] Add OAuth provider buttons (Google)
- [ ] Implement OAuth callback handling
- [ ] Create auth middleware for protected routes
- [ ] Add session management (refresh tokens)
- [ ] Write tests for auth flows
```

### Task Specification Format

Each task should specify:
```markdown
- [ ] [What to do] -- Files: `path/to/file.ts`, `path/to/test.ts`
```

Including file paths helps:
- Estimate scope quickly
- Identify conflicts between parallel tasks
- Resume work after context compaction

---

## The Checkpoint Pattern

Insert verification checkpoints between phases to catch issues early:

```markdown
## Phase 1: Data Layer

### Tasks
- [ ] Create database schema
- [ ] Implement User model
- [ ] Implement Task model
- [ ] Create API routes for CRUD operations
- [ ] Add input validation with Zod
- [ ] Write tests for all endpoints

### CHECKPOINT: Verify Data Layer
- [ ] All tests pass
- [ ] Can create, read, update, delete via API
- [ ] Validation rejects invalid input
- [ ] Error responses have correct status codes and messages
- [ ] Database migrations run cleanly on fresh database

> Do NOT proceed to Phase 2 until all checkpoint items pass.
```

---

## Dependency Mapping

For complex projects, explicitly map dependencies between tasks:

```markdown
## Dependency Graph

Phase 0: Foundation ──→ Phase 1: Data Layer ──→ Phase 2: Core UI
                                                       │
                                              ┌────────┼────────┐
                                              ▼        ▼        ▼
                                          Phase 3  Phase 4  Phase 5
                                          (Auth)   (Tasks)  (Teams)
                                              │        │        │
                                              └────────┼────────┘
                                                       ▼
                                                  Phase 6: Polish
```

### Parallel Execution Opportunities

When phases have no dependencies, they can be worked on in parallel (different branches, different sessions):

```markdown
## Can Run in Parallel
- Phase 3 (Auth) and Phase 4 (Tasks) -- after Phase 2 is complete
- Frontend tests and Backend tests -- always independent
- Documentation and Bug fixes -- always independent
```

---

## Context Document Patterns

### context.md Template

```markdown
# Context: [Task Name]

**Last Updated**: [Date]
**Status**: In Progress -- Phase [N]

## Next Steps (Read This First)
1. [Immediate next action]
2. [Following action]
3. [Any blockers or open questions]

## Key Files
| File | Purpose | Status |
|------|---------|--------|
| `src/features/auth/login.tsx` | Login page | Complete |
| `src/features/auth/signup.tsx` | Signup page | In Progress |
| `src/lib/auth.ts` | Auth utilities | Not Started |

## Architecture Decisions
1. **[Decision]**: [Rationale]
2. **[Decision]**: [Rationale]

## Discoveries During Implementation
- [Something unexpected found during work]
- [Workaround applied and why]

## Open Questions
- [ ] [Question needing user input]
- [ ] [Technical question to investigate]
```

### The "Next Steps" Section is Critical

This is the most important part of context.md. When a fresh session loads this file, the "Next Steps" section tells it exactly where to pick up. Always update this before context compaction.

---

## Risk Identification

Every plan should identify risks. Common categories:

### Technical Risks
- Third-party API limitations or rate limits
- Database performance at scale
- Complex state management
- Real-time synchronization conflicts
- Browser compatibility requirements

### Scope Risks
- Feature creep during implementation
- Underestimated complexity
- Unclear requirements that need user clarification
- Dependencies on external teams or services

### Mitigation Strategies
```markdown
## Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Supabase rate limits | High | Medium | Implement caching layer, batch operations |
| Complex form state | Medium | High | Use react-hook-form + Zod, prototype early |
| Unclear notification UX | Low | High | Build MVP notification, iterate with feedback |
```

---

## The Handoff Document Pattern

When a task will span multiple sessions, write a handoff document before ending:

```markdown
# Handoff: [Task Name] -- [Date]

## What Was Accomplished
- [Completed item 1]
- [Completed item 2]

## Current State
- [File X] is partially implemented -- [what's done, what's remaining]
- Tests are passing for [scope]
- Build is [passing/failing] because [reason]

## What to Do Next
1. [Specific next step with file path]
2. [Specific next step with file path]

## What Didn't Work (So You Don't Repeat It)
- Tried [approach] but it failed because [reason]
- [Library/tool] doesn't support [feature] -- use [alternative] instead

## Open Questions for User
- [Question 1]
- [Question 2]
```

To continue in a fresh session: "Read `dev/active/[task-name]/[task-name]-context.md` and continue from where we left off."

---

## Estimation Heuristics

While we avoid giving time estimates, these heuristics help with task breakdown:

- **CRUD endpoint** (model + route + validation + tests): ~4 tasks
- **UI page with data** (page + components + hooks + API connection): ~6 tasks
- **Authentication** (full flow with OAuth): ~10 tasks
- **File upload** (UI + storage + validation + processing): ~5 tasks
- **Search/filtering** (UI + API + database queries + pagination): ~6 tasks
- **Real-time feature** (WebSocket/SSE + state sync + UI): ~8 tasks

Each "task" maps roughly to one focused Claude Code session.
