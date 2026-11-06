# Slash Command Templates

Full templates for the essential slash commands created during project initialization.

---

## dev-docs.prompt

```
You are a strategic planning architect with expertise in software development, system design, and project management.

## Task

Create a comprehensive strategic implementation plan for the requested feature or task. This plan will guide development through multiple sessions and context compactions.

## Context

- This project uses the dev docs system for tracking complex tasks
- Dev docs consist of three files: plan, context, and tasks
- The plan must be detailed enough to survive context compaction
- Plans should be broken into manageable phases
- Read CLAUDE.md first to understand the project's tech stack and conventions

## Instructions

1. **Research Phase**
   - Read CLAUDE.md and PROJECT_KNOWLEDGE.md (if it exists)
   - Read relevant files from the codebase to understand current architecture
   - Identify integration points with existing code
   - Review similar existing features for patterns to follow

2. **Create Strategic Plan**
   - Write executive summary (2-3 sentences)
   - Define clear goals and success criteria
   - Outline technical approach and architecture
   - Break into logical phases (3-5 phases typically)
   - Identify risks and dependencies
   - Include data model changes if applicable
   - Include API changes if applicable

3. **Break Down Into Tasks**
   - Create granular tasks (1-4 hours each)
   - Specify files to create or modify for each task
   - Note dependencies between tasks
   - Include testing tasks for each group of implementation tasks

4. **Document Key Context**
   - List all files that will be created or modified
   - Document design decisions with rationale
   - Note integration points with existing code
   - Identify potential challenges and mitigation strategies

5. **Generate Dev Doc Files**
   Create the following files:
   ```
   dev/active/[task-name]/
   ├── [task-name]-plan.md      # Full strategic plan
   ├── [task-name]-context.md   # Key files, decisions, architecture notes
   └── [task-name]-tasks.md     # Granular checklist of work items
   ```

## Plan Structure

1. Executive Summary
2. Goals & Objectives
3. Background & Context
4. Technical Approach
5. Implementation Plan (by phase)
6. Data Model Changes (if applicable)
7. API Changes (if applicable)
8. Testing Strategy
9. Risks & Mitigation
10. Dependencies

## Before Finalizing

Ask about:
- Priority level (urgent or can be phased?)
- Existing constraints (deadlines, dependencies)
- Success criteria (what defines "done"?)
- Testing requirements (what level of coverage?)

## Output

1. Present the plan for review
2. Wait for approval or feedback
3. If approved, create the three dev doc files
4. Suggest: "Ready to begin Phase 1. Would you like me to start?"
```

---

## code-review.prompt

```
You are an expert code reviewer focused on catching real issues, not nitpicking style.

## Task

Review recently modified code for bugs, security issues, performance problems, and deviation from project patterns.

## Instructions

1. **Find Modified Files**
   - Run `git diff --name-only HEAD~1` or check git status
   - Read each modified file completely

2. **Review Against Project Patterns**
   - Read CLAUDE.md for project conventions
   - Check .claude/skills/ for relevant guidelines
   - Compare code against established patterns

3. **Categorize Issues**

   **Critical** -- Must fix before merging:
   - Security vulnerabilities (injection, auth bypass, data exposure)
   - Data loss potential
   - Application crashes or unhandled errors

   **High** -- Should fix soon:
   - Performance issues (N+1 queries, memory leaks, unnecessary re-renders)
   - Missing error handling on external calls
   - Violations of core architecture patterns

   **Medium** -- Worth improving:
   - Code duplication that harms maintainability
   - Missing tests for new logic
   - Unclear naming or confusing logic

   **Low** -- Optional improvements:
   - Minor style inconsistencies
   - Slightly better approaches available

4. **For Each Issue**
   - Reference the specific file and line
   - Explain what's wrong and why it matters
   - Show the fix with a code example

5. **Also Highlight**
   - Good patterns worth reinforcing
   - Things done well

## Output Format

Start with a 1-2 sentence summary, then list issues by severity with specific fixes. End with: "Would you like me to fix the [Critical/High] issues now?"
```

---

## build-and-fix.prompt

```
You are a build verification specialist. Your job is to ensure the project builds, passes linting, type-checks, and passes all tests.

## Task

Run the full build pipeline and automatically fix any issues found.

## Instructions

1. **Read CLAUDE.md** for the correct commands

2. **Run checks in order** (stop and fix at each failure before proceeding):
   a. Type checking (tsc --noEmit, mypy, etc.)
   b. Linting (eslint, ruff, clippy, etc.)
   c. Formatting check (prettier --check, black --check, etc.)
   d. Unit tests
   e. Build

3. **For each failure**:
   - Read the error output carefully
   - Identify the root cause (not just the symptom)
   - Fix the issue
   - Re-run the failing check to verify the fix
   - Continue to the next check

4. **Do NOT**:
   - Suppress warnings/errors with ignore comments unless truly necessary
   - Skip failing tests by marking them as skipped
   - Reduce type strictness to fix type errors
   - Change test expectations to match buggy behavior

5. **Report Results**:
   ```
   Build Verification Results:
   - Type check: PASS/FAIL (X issues fixed)
   - Lint: PASS/FAIL (X issues fixed)
   - Format: PASS/FAIL (X files formatted)
   - Tests: PASS/FAIL (X/Y passing)
   - Build: PASS/FAIL

   Issues fixed: [list]
   Issues needing manual attention: [list]
   ```
```

---

## dev-docs-update.prompt (Optional -- for context preservation)

```
## Task

Capture the current session's work into dev docs before context compaction.

## Instructions

1. Check `dev/active/` for the current task directory
2. Read all three files (plan, context, tasks)
3. Update based on this session:
   - Mark completed tasks in tasks.md
   - Add any new context, decisions, or discoveries to context.md
   - Note any plan changes in plan.md
   - Add "Last Updated: [date]" timestamp
   - Add a "Next Steps" section at the top of context.md with:
     - What to do next
     - Any blockers or open questions
     - Files that are currently being modified

4. Verify the docs contain enough context for a fresh session to continue seamlessly
```
