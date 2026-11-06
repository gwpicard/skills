# Template: Onboarding Guide
<!-- output: .claude/repo-onboarding-guide.md -->
<!-- agents: D1, D4, D5, D9 -->

## Synthesis Instructions

Optimize for **time-to-first-PR**: every section should help a new developer make their first meaningful contribution faster. Include **verification checkpoints** after every setup step (not "run X" but "run X — you should see Y"). Mine the codebase for gotchas by grepping for `HACK`, `WORKAROUND`, `NOTE`, `XXX`, `WARNING` comments. Suggest **first tasks** by finding easy-tagged issues, small `TODO`s, or simple files.

## Template Structure

```markdown
# Developer Onboarding Guide: {project_name}
> Goal: Get you from zero to your first PR.

## 1. What This Project Is (2 min read)

{Product summary from D4 — what it does, who uses it, key value proposition}

**Core domain concepts you'll encounter:**
| Term | Meaning | Where in Code |
|------|---------|---------------|
| {domain term} | {plain language definition} | `{primary file/module}` |
| ... | ... | ... |
{Extract from D4 business glossary. 5-8 most important terms.}

## 2. Architecture at a Glance (5 min read)

```mermaid
{Architecture diagram from D1}
```

**Key architectural decisions:**
- **{Pattern}**: We use {pattern} because {why}. See `{example file}`.
- **{Convention}**: {description}. See `{example file}`.
- **{Boundary rule}**: {e.g., "Never import from src/db/ in route handlers — always go through repositories"}
{3-5 key patterns from D5. Focus on the "why" — these are the things a new dev will violate first.}

## 3. Life of a Request

{Trace a single user action through the entire system — this is the single most effective onboarding technique. Pick the most representative flow (e.g., "user creates a task" or "API processes a payment").}

```
User clicks "Create Task"
  → Browser: POST /api/tasks (src/app/api/tasks/route.ts)
    → Auth middleware validates JWT (src/middleware/auth.ts)
    → Validation: Zod schema checks body (src/validators/task.ts)
    → Service: TaskService.create() (src/services/task.ts)
      → Repository: taskRepo.insert() (src/repositories/task.ts)
        → Database: INSERT into tasks table
      → Event: emits "task.created" (src/events/task.ts)
    → Response: 201 with created task
  → Browser: Adds task to board state
```

{Annotate with actual file paths from the analysis. This gives the new dev a mental model of how everything connects.}

## 4. Getting Your Dev Environment Running

{Every step has a verification checkpoint. Format:}

### Prerequisites
- {runtime} {version} — check: `{command} --version` → should show `{expected}`
- {database} {version} — check: `{command} --version` → should show `{expected}`

### Setup Steps

**Step 1: Clone and install**
```bash
{clone command}
cd {project}
{install command}
```
Verify: `{check command}` → {expected output, e.g., "no errors, 0 vulnerabilities"}

**Step 2: Configure environment**
```bash
cp .env.example .env
```
{List which env vars MUST be changed for local dev vs which can use defaults}
Verify: all required vars are set

**Step 3: Set up database**
```bash
{migrate command}
{seed command, if available}
```
Verify: `{check command}` → {expected, e.g., "X tables created" or "seed data loaded"}

**Step 4: Start the dev server**
```bash
{dev command}
```
Verify: Open {URL} → you should see {what}

**Step 5: Run the test suite**
```bash
{test command}
```
Verify: All tests pass (expected: {N} tests, {N} suites). If tests fail, see Gotchas section below.

## 5. Codebase Map

| Directory | What's In It | When You'd Change It | Entry Point |
|-----------|-------------|---------------------|-------------|
| {dir} | {description} | {trigger} | `{key file to read first}` |
| ... | ... | ... | ... |
{From D1. Include "Entry Point" column — the ONE file to read first to understand that directory.}

**If you're looking for where something happens:**
| "I need to..." | Start here |
|----------------|-----------|
| Add a new API endpoint | `{path}` |
| Add a new page/view | `{path}` |
| Change business logic | `{path}` |
| Modify the database schema | `{path}` |
| Add a new test | `{path}` |
| Change CI/CD | `{path}` |
{From D5/D9 patterns. Map common developer intents to starting files.}

## 6. Key Patterns & Conventions

{From D5. Only include patterns a new dev NEEDS to know to avoid mistakes.}

### Do This / Not That
| Instead of... | Do this... | Why |
|---------------|-----------|-----|
| {anti-pattern} | {correct pattern} | {reason} |
| {anti-pattern} | {correct pattern} | {reason} |
{3-5 most important conventions. Derive from D5 patterns and D8 quality findings.}

### Code Style
- {Formatter}: `{command}` (runs on save / on commit)
- {Linter}: `{command}` — fix with `{fix command}`
- {Other conventions: naming, file organization, import ordering}

## 7. Common Development Tasks

{Step-by-step recipes for the 3-4 most common tasks. Derive from D5 patterns.}

### Adding a new {most common task type, e.g., "API endpoint"}
1. {Step with file path}
2. {Step with file path}
3. {Step with file path}
4. Run tests: `{command}`
5. Verify: {how to check it works}

### Adding a new {second most common task type}
{Same format}

## 8. Who Owns What
{From D10. If git history is available, map code areas to knowledge owners.}

| Area | Primary Owner | Key Files |
|------|--------------|-----------|
| {area} | {contributor from git history} | {files} |
| ... | ... | ... |
{If no git history: "See team documentation for ownership information."}

## 9. Gotchas & Tips

{Mine from code comments: grep for HACK, WORKAROUND, NOTE, XXX, WARNING. Also from D8 quality findings.}

- **{Gotcha}**: {explanation + workaround}
- **{Gotcha}**: {explanation + workaround}
- **{Tip}**: {helpful shortcut or debugging technique}
{5-10 items. These save hours of confusion.}

## 10. Suggested First Tasks

{Help the new dev find a good first contribution:}

| Task | Difficulty | File(s) | Why It's Good for Onboarding |
|------|-----------|---------|------------------------------|
| {TODO from code} | Easy | `{file:line}` | Touches one file, clear scope |
| {Simple improvement from D8} | Easy | `{file}` | Learn the test patterns |
| {Small feature/fix} | Medium | `{files}` | Touches the main code path |
{Find from: TODO/FIXME comments with small scope, D8 quality quick wins, simple test coverage gaps}
```
