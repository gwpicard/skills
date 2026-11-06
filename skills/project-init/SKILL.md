---
name: project-init
description: Comprehensive project initialization skill that sets up CLAUDE.md, .claude/ infrastructure, dev docs workflow, and creates a full development plan. Use when starting a new project, onboarding to an existing codebase, or when a user says "init", "initialize", "set up project", or "bootstrap".
---

# Project Initialization Skill

A comprehensive, interactive skill for initializing any project with a production-grade Claude Code setup. By the end, the user will have a complete CLAUDE.md, .claude/ infrastructure, and a phased development plan.

## When to Use This Skill

- User says "init", "initialize project", "set up project", "bootstrap"
- User starts working in a new or empty project directory
- User asks to create a CLAUDE.md or set up Claude Code for a project
- User wants to create a development plan for a new project
- User is onboarding to an existing codebase and needs structure

## Process Overview

This skill runs through **6 phases** interactively. Each phase gathers information from the user, performs analysis, and produces artifacts. Always confirm outputs with the user before moving to the next phase.

```
Phase 1: Discovery & Analysis
Phase 2: CLAUDE.md Generation
Phase 3: .claude/ Infrastructure Setup
Phase 4: Project Knowledge Base
Phase 5: Development Plan & Task Breakdown
Phase 6: Verification & Summary
```

---

## Phase 1: Discovery & Analysis

### Step 1.1: Determine Project State

First, determine if this is a **new project** or an **existing codebase**:

**For existing codebases:**
- Read `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Gemfile`, `pom.xml`, `build.gradle`, `composer.json`, or equivalent
- Scan the directory tree structure (top 3 levels)
- Identify frameworks, libraries, and tools already in use
- Check for existing CI/CD configs (`.github/workflows/`, `Dockerfile`, etc.)
- Check for existing linting/formatting configs (`.eslintrc`, `.prettierrc`, `biome.json`, etc.)
- Check for existing test setup (`__tests__/`, `tests/`, `spec/`, test configs)
- Check for `.env.example` or `.env.local` files
- Check for existing documentation (`README.md`, `docs/`)
- Run `git log --oneline -20` to understand recent activity

**For new projects:**
- Ask the user what they want to build (high-level description)
- Ask about target tech stack preferences
- Ask about deployment target (Vercel, AWS, self-hosted, etc.)
- Ask about team size and experience level

### Step 1.2: Gather Project Information

Ask the user the following questions (skip any that are already answered by analysis). Present these as a structured interview, not a wall of questions. Group them logically and ask in batches of 2-3:

**Project Identity:**
- Project name
- One-sentence description of what it does
- Who are the users/audience?

**Technical Decisions:**
- Tech stack (frontend, backend, database, styling, state management)
- Package manager preference (npm, pnpm, yarn, bun)
- Monorepo or single-repo?
- TypeScript or JavaScript? (Recommend TypeScript)
- Testing framework preference
- Deployment target

**Architecture:**
- What are the main features/modules?
- Any external APIs or services to integrate?
- Authentication requirements?
- Real-time requirements (WebSockets, SSE)?

**Workflow Preferences:**
- Git branching strategy (trunk-based, gitflow, simple feature branches)?
- PR review workflow?
- CI/CD requirements?
- How much autonomy should Claude have? (conservative vs autonomous)

### Step 1.3: Produce Discovery Summary

Create a brief summary document and present it to the user for confirmation before proceeding:

```markdown
## Project Discovery Summary

**Project**: [Name] - [Description]
**Stack**: [Frontend] / [Backend] / [Database]
**Key Features**: [List]
**Architecture**: [Monolith/Microservices/Serverless]
**Deployment**: [Target]

Proceed with this understanding? (y/n)
```

---

## Phase 2: CLAUDE.md Generation

Generate a tailored `CLAUDE.md` at the project root. This file is loaded into EVERY conversation, so it must be **concise but comprehensive**. Target 100-200 lines. Do NOT pad with placeholder content -- only include what is real and relevant to this project.

### CLAUDE.md Structure

```markdown
# [Project Name]

[One-sentence description]

## Quick Commands

```bash
# Development
[actual commands for this project's package manager and scripts]

# Testing
[actual test commands]

# Database (if applicable)
[actual database commands]

# Deployment (if applicable)
[actual deployment commands]
```

## Tech Stack

**Frontend**: [Specific framework + version, styling, state management]
**Backend**: [Runtime, framework, ORM]
**Database**: [Type + name]
**Infrastructure**: [Hosting, CI/CD, monitoring]

## Project Structure

```
[Actual directory tree - only list directories that exist or will exist]
src/
├── [dir]/    # [purpose]
└── [dir]/    # [purpose]
```

## Architecture Decisions

- [Decision 1 with brief rationale]
- [Decision 2 with brief rationale]

## Code Conventions

- [Convention 1 - e.g., "Use named exports, not default exports"]
- [Convention 2 - e.g., "Error handling: all async operations wrapped in try/catch"]
- [Convention 3 - e.g., "Naming: camelCase for functions, PascalCase for components/types"]

## Critical Rules

1. [Rule 1 - e.g., "Never commit .env files"]
2. [Rule 2 - e.g., "All API endpoints must validate input with Zod"]
3. [Rule 3 - e.g., "Run tests before committing"]

## Dev Workflow

### Starting a New Feature
1. Create feature branch from `main`
2. Enter planning mode or use `/dev-docs [feature]`
3. Implement with tests
4. Run `/code-review` before PR
5. Create draft PR for review

### Task Tracking
- Active tasks: `./dev/active/[task-name]/`
- Each task has: plan.md, context.md, tasks.md
- Update task files before context compaction

## Environment Setup

```bash
[Actual setup steps for this project]
```

## External Services

- [Service 1]: [What it's used for, how to configure]
- [Service 2]: [What it's used for, how to configure]
```

### Important CLAUDE.md Principles

- **Be concise**: Every line consumes context tokens in every conversation
- **Be specific**: "Use Zod for validation" not "validate inputs"
- **Be actionable**: Include actual commands, not placeholders
- **Skip sections** that don't apply rather than leaving placeholder text
- **No emojis** unless the user specifically wants them
- **Update regularly**: Add instructions here only when you find yourself repeating them

Present the CLAUDE.md to the user for review and edits before writing it.

---

## Phase 3: .claude/ Infrastructure Setup

Set up the `.claude/` directory at the project root with the following structure. Only create what's relevant to the project:

```
.claude/
├── skills/              # Project-specific skills
│   └── [as needed]
├── slash-commands/      # Custom prompt shortcuts
│   ├── dev-docs.prompt
│   ├── code-review.prompt
│   └── build-and-fix.prompt
└── hooks/               # Automation hooks (optional)
```

### 3.1: Slash Commands

Create these essential slash commands as `.prompt` files:

**`dev-docs.prompt`** -- Strategic planning for new features/tasks:
- Researches codebase before planning
- Creates plan.md, context.md, tasks.md in `./dev/active/[task-name]/`
- Breaks work into phases with granular tasks (1-4 hours each)
- Identifies risks, dependencies, and testing strategy
- Waits for user approval before proceeding

**`code-review.prompt`** -- Architectural code review:
- Reviews recently modified files against project patterns
- Categorizes issues by severity (Critical/High/Medium/Low)
- Suggests specific fixes with code examples
- Highlights good patterns too

**`build-and-fix.prompt`** -- Build verification and auto-fix:
- Runs build, lint, type-check, and tests
- Automatically fixes issues it finds
- Reports what was fixed and what needs manual attention

See `resources/slash-command-templates.md` for full templates.

### 3.2: Project Skills (If Needed)

Only create project-specific skills if the project has:
- A complex frontend with specific component patterns to follow
- A backend with layered architecture patterns
- Database operations requiring safety guardrails
- Domain-specific conventions that Claude should always follow

Each skill should have a `SKILL.md` under `.claude/skills/[skill-name]/`.

### 3.3: Add to .gitignore

Ensure `.claude/` config is committed but local state is not:
```
# Claude Code local state (don't commit)
dev/active/
dev/completed/
```

The `.claude/` directory itself SHOULD be committed so the team shares skills and commands.

---

## Phase 4: Project Knowledge Base

### 4.1: Create Dev Directory Structure

```bash
mkdir -p dev/active dev/completed
```

### 4.2: Create PROJECT_KNOWLEDGE.md (If Complex Project)

Only create this for projects with significant complexity. This file supplements CLAUDE.md with deeper architectural context that doesn't need to be in every conversation but can be referenced:

```markdown
# Project Knowledge Base

## Architecture Overview
[Detailed architecture description with data flow]

## Key Integration Points
[How systems connect, API contracts, event flows]

## Domain Concepts
[Business domain terminology and rules]

## Historical Decisions
[Why certain technical choices were made -- for future context]

## Known Limitations
[Current technical debt, workarounds, constraints]

## Troubleshooting
[Common issues and their solutions]
```

### 4.3: Create TROUBLESHOOTING.md (Optional)

Only if the project has known gotchas:

```markdown
# Troubleshooting Guide

## [Issue Category]
**Symptom**: [What you see]
**Cause**: [Why it happens]
**Fix**: [How to resolve]
```

---

## Phase 5: Development Plan & Task Breakdown

This is the most critical phase. Help the user create a comprehensive development plan.

### 5.1: Define Project Scope

Work with the user to define:
- **MVP features** -- What's the minimum viable version?
- **V1 features** -- What's the full first release?
- **Future features** -- What's explicitly out of scope for now?

### 5.2: Create Phased Implementation Plan

Break the project into logical phases. Each phase should be independently deployable or testable:

```markdown
# Development Plan: [Project Name]

## Phase 0: Foundation (Do First)
- Project scaffolding and configuration
- Development environment setup
- CI/CD pipeline setup
- Database schema design
- Authentication setup (if needed)

## Phase 1: Core Data Layer
- Database models/schema
- API endpoints (CRUD)
- Input validation
- Error handling patterns
- Unit tests for data layer

## Phase 2: Core UI
- Layout and navigation
- Core pages/views
- Component library foundation
- Connect to API
- Basic responsive design

## Phase 3: Feature - [Feature Name]
- [Specific tasks]
- Tests for this feature

## Phase 4: Feature - [Feature Name]
- [Specific tasks]
- Tests for this feature

## Phase N: Polish & Launch
- Performance optimization
- Error monitoring setup
- Documentation
- Deployment configuration
- Launch checklist
```

### 5.3: Break Into Granular Tasks

For each phase, create detailed task files with:

```markdown
# Tasks: Phase [N] - [Phase Name]

## Prerequisites
- [ ] [What must be complete before starting this phase]

## Tasks

### [Task Group 1]
- [ ] [Specific task] -- Files: `path/to/file.ts`
- [ ] [Specific task] -- Files: `path/to/file.ts`
- [ ] Write tests for [task group]

### [Task Group 2]
- [ ] [Specific task]
- [ ] [Specific task]
- [ ] Write tests for [task group]

## Verification
- [ ] All tests pass
- [ ] Build succeeds
- [ ] [Feature-specific verification]

## Notes
- [Any important context for this phase]
```

### 5.4: Create the Plan Files

Write the plan to `dev/active/project-init/`:
- `project-init-plan.md` -- The full phased plan
- `project-init-context.md` -- Key files, decisions, architecture
- `project-init-tasks.md` -- Granular task checklist for Phase 0

### 5.5: Present for Approval

Present the full plan to the user. Ask:
- Does the phasing make sense?
- Are any features missing or misplaced?
- Should any phase be split or merged?
- Is the task granularity right?
- What should we start building first?

---

## Phase 6: Verification & Summary

### 6.1: Verify Everything Was Created

Check that all files exist and are valid:
- [ ] `CLAUDE.md` at project root
- [ ] `.claude/` directory with appropriate contents
- [ ] `dev/active/project-init/` with plan files
- [ ] `.gitignore` updated
- [ ] Any supporting docs (PROJECT_KNOWLEDGE.md, etc.)

### 6.2: Present Summary

```markdown
## Project Initialization Complete

### Created Files:
- `CLAUDE.md` -- Project context for Claude Code
- `.claude/slash-commands/dev-docs.prompt` -- Planning workflow
- `.claude/slash-commands/code-review.prompt` -- Code review workflow
- `.claude/slash-commands/build-and-fix.prompt` -- Build verification
- `dev/active/project-init/project-init-plan.md` -- Development plan
- `dev/active/project-init/project-init-context.md` -- Key context
- `dev/active/project-init/project-init-tasks.md` -- Phase 0 tasks

### Quick Start:
1. Review the CLAUDE.md and adjust anything that doesn't look right
2. Start Phase 0: `Let's begin Phase 0 of the project plan`
3. For new features later: `/dev-docs [feature description]`
4. Before PRs: `/code-review`
5. Before merging: `/build-and-fix`

### Tips:
- Start fresh conversations for each new topic
- Use `/compact` when context gets long, or write a handoff doc first
- Keep CLAUDE.md concise -- add instructions only when you repeat yourself
- Update dev docs before context compaction to preserve state
```

### 6.3: Offer Next Steps

Ask the user:
- "Would you like to start Phase 0 now?"
- "Want to adjust anything in the plan?"
- "Should I set up any project-specific skills for [detected framework]?"

---

## Important Principles

1. **Interactive, not automatic** -- Always confirm with the user before writing files. Present drafts, get feedback, then write.
2. **Concise over comprehensive** -- A 150-line CLAUDE.md that's all signal beats a 500-line one padded with boilerplate.
3. **Skip what doesn't apply** -- Don't create placeholder skills or empty sections. Only create artifacts the project actually needs.
4. **Existing projects need audit, not scaffolding** -- For existing codebases, analyze what's there and fill gaps rather than overwriting.
5. **The plan is the product** -- The development plan should be detailed enough that someone could pick it up and start working with minimal context.
6. **Fresh context is king** -- Design all artifacts to survive context compaction. Plans, tasks, and context docs should be self-contained.
7. **Token economy matters** -- CLAUDE.md is loaded every conversation. Keep it tight. Put detailed reference material in PROJECT_KNOWLEDGE.md or skills instead.

## Resources

For detailed templates and examples, see:
- `resources/slash-command-templates.md` -- Full slash command prompt templates
- `resources/claude-md-examples.md` -- CLAUDE.md examples for different project types
- `resources/planning-patterns.md` -- Planning patterns and task breakdown strategies
