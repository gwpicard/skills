# Template: Refactoring Plan
<!-- output: .claude/repo-refactoring-plan.md -->
<!-- agents: D5, D7, D8, D10 -->

## Synthesis Instructions

Every item must have: specific file/line references, the refactoring technique to apply, effort estimate (T-shirt size: XS <1h, S 1-4h, M 4h-2d, L 2d-1w, XL 1w+), risk assessment, and a suggested PR scope. Use `change_frequency × complexity` as the primary hotspot metric. Include before/after code examples for the top 3-5 items and for repeated patterns.

## Template Structure

```markdown
# Refactoring Plan: {project_name}
> Generated on {date}

## Executive Summary
- **Health score**: {composite from D8 scorecard}
- **Total items identified**: {count} across {N} categories
- **Estimated total effort**: {range}
- **Top 3 highest-impact items**: {one-line each}

## Codebase Health Dashboard
| Metric | Value | Assessment |
|--------|-------|-----------|
| Complexity hotspots (functions with estimated CC >15) | ... | ... |
| Files >500 lines | ... | ... |
| TODO/FIXME/HACK count | ... | ... |
| Type/lint suppressions | ... | ... |
| Untested critical modules | ... | ... |
| Code duplication indicators | ... | ... |

## Complexity Hotspots
{Top 10 files ranked by change_frequency × estimated_complexity. These are where refactoring provides the most relief.}

| File | Function/Area | Complexity Indicator | Changes (6mo) | Test Coverage | Priority Score |
|------|-------------|---------------------|---------------|---------------|---------------|
| ... | ... | {deep nesting, long function, many branches} | ... | {Has tests / No tests} | ... |

## Phase 0: Quick Wins (can start immediately)

Present as a checklist — each item should be independently actionable:

- [ ] **{What}** ({effort size}, ~{time estimate})
  File: `{file:line}`
  Action: {specific refactoring technique, e.g., "Extract method", "Apply guard clauses", "Remove dead code"}
  {Before/after code example if non-obvious}

## Phase 1: Foundation ({estimated effort range})
{Items that make subsequent refactoring safer: add characterization tests, fix CI, extract interfaces}

| # | What | Where | Technique | Effort | Risk | PR Scope |
|---|------|-------|-----------|--------|------|----------|
| ... | ... | file:line | {Extract Interface, Add Tests, etc.} | XS-XL | Low/Med/High | "{suggested PR title}" |

## Phase 2: Core Refactoring ({estimated effort range})
{Depends on Phase 1. Main structural improvements.}

| # | What | Where | Technique | Effort | Risk | Depends On | PR Scope |
|---|------|-------|-----------|--------|------|------------|----------|
| ... | ... | ... | ... | ... | ... | Phase 1 #N | "..." |

## Phase 3: Strategic Refactors ({estimated effort range})
{Larger architectural improvements. Each should be a separate workstream.}

| # | What | Scope | Why | Effort | Risk | Business Value |
|---|------|-------|-----|--------|------|---------------|
| ... | ... | {N files, N modules} | ... | L/XL | ... | {connects to business impact: "reduces time to add new X from Y to Z"} |

## Risk Assessment
| Item | Breaking Change | Regression Risk | Blast Radius | Reversibility | Overall |
|------|---------------|----------------|-------------|--------------|---------|
| ... | None/Low/Med/High | Low/Med/High | Isolated/Contained/Widespread | Easy/Moderate/Difficult | LOW/MED/HIGH |

## Technical Debt Inventory
{Categorized into 6 types with counts and top file references}

| Category | Count | Top Locations | Severity |
|----------|-------|-------------|----------|
| Code Debt (smells, complexity) | ... | ... | ... |
| Architectural Debt (coupling, missing abstractions) | ... | ... | ... |
| Test Debt (coverage gaps, brittle tests) | ... | ... | ... |
| Documentation Debt | ... | ... | ... |
| Dependency Debt (outdated, vulnerable) | ... | ... | ... |
| Infrastructure Debt (CI/CD, build) | ... | ... | ... |

## Quality Scorecard
{Include the full scorecard from D8}

## Positive Observations
{2-3 things the codebase does well — acknowledge good patterns}
```
