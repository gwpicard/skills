# Template: Testing Improvement Plan
<!-- output: .claude/repo-testing-plan.md -->
<!-- agents: D5, D7, D8, D10 -->

## Synthesis Instructions

Determine the **recommended test model** based on project type: Testing Pyramid (libraries, backend services), Testing Trophy (frontend-heavy apps — more integration, fewer unit), or Testing Honeycomb (microservices — mostly integration). Use 7 coverage gap heuristics (source-to-test mapping, complexity × coverage, change frequency × coverage, public API coverage, error path coverage, critical path coverage, boundary coverage). Score priorities using: Business Criticality 30%, Bug Probability 25%, Blast Radius 20%, Change Frequency 15%, Effort 10%.

## Template Structure

```markdown
# Testing Improvement Plan: {project_name}
> Generated on {date}

## Executive Summary
- **Test framework**: {detected framework(s)}
- **Test files**: {count} files, ~{count} tests
- **Test types found**: {unit / integration / E2E / snapshot / property-based}
- **Estimated coverage**: ~{X}% (based on source-to-test file mapping)
- **Recommended test model**: {Pyramid / Trophy / Honeycomb} — because {one-line justification based on project type}
- **Top priority**: {one-line summary of the biggest testing gap}

## Current Test Distribution

| Test Type | Count | % of Total | Recommended % ({model}) | Gap |
|-----------|-------|-----------|------------------------|-----|
| Unit | ... | ... | ... | {Over/Under by X%} |
| Integration | ... | ... | ... | ... |
| E2E | ... | ... | ... | ... |
| Other (snapshot, property, etc.) | ... | ... | — | — |

{Visual representation:}
```
Current:      [===unit====][==integration==][E2E]
Recommended:  [====unit======][====integration====][==E2E==]
```

## Coverage Gap Analysis

### Source-to-Test Mapping
{Map each source module to its test file(s). Flag untested modules.}

| Module | Source Files | Test Files | Coverage | Priority Score | Gap |
|--------|-------------|-----------|----------|---------------|-----|
| {module} | {count} | {count} ({list}) | {None/Low/Medium/Good} | {weighted score} | {what's missing} |
| ... | ... | ... | ... | ... | ... |

**Priority scoring**: Business Criticality (30%) + Bug Probability (25%) + Blast Radius (20%) + Change Frequency (15%) + Effort (10%)

### Untested Critical Paths
{Identify the most important untested code paths:}

| # | Critical Path | Why Critical | Entry Point | Recommended Test Type | Effort |
|---|-------------|-------------|------------|---------------------|--------|
| 1 | {e.g., Payment processing flow} | {business criticality} | `{file:function}` | Integration | {hours} |
| 2 | {e.g., Auth middleware} | {security criticality} | `{file}` | Unit + Integration | {hours} |
| ... | ... | ... | ... | ... | ... |

### Untested Error Paths
{Identify error handling code with no test coverage:}

| # | Error Path | Location | What Could Go Wrong | Recommended Test |
|---|-----------|----------|--------------------|-----------------|
| ... | {e.g., "Database connection failure handling"} | `{file:line}` | {consequence if broken} | {test description} |

## Test Quality Assessment

### Anti-Patterns Found

| # | Anti-Pattern | Occurrences | Locations | Fix |
|---|-------------|------------|-----------|-----|
| 1 | **Excessive mocking** — mocking internals instead of boundaries | {count} | {files} | Mock at service/module boundaries, not internal functions |
| 2 | **Implementation detail testing** — tests break on refactor | {count} | {files} | Test behavior/output, not internal method calls |
| 3 | **Hardcoded dates/times** — tests will fail in future | {count} | {files} | Use frozen time utilities or relative dates |
| 4 | **Weak assertions** — `toBeTruthy()` / `assert result` without checking value | {count} | {files} | Assert specific values and shapes |
| 5 | **Giant test files** — test files >300 lines with poor organization | {count} | {files} | Split by behavior/feature, use describe blocks |
| 6 | **Snapshot overuse** — snapshots testing large objects/components | {count} | {files} | Replace with targeted assertions on key properties |
| 7 | **Missing error path tests** — only happy paths tested | {count} | {files} | Add tests for each error condition |
| 8 | **Shared mutable state** — tests depend on execution order | {count} | {files} | Isolate test state, use setup/teardown |
| 9 | **Flaky indicators** — sleep(), setTimeout(), race conditions | {count} | {files} | Use waitFor(), polling, or deterministic approaches |
| 10 | **Missing cleanup** — resources not cleaned up after tests | {count} | {files} | Add afterEach/afterAll cleanup |
{Only include anti-patterns that were actually found. Skip rows with 0 occurrences.}

### Test Helpers & Fixtures Assessment
- **Shared test utilities**: {exist / don't exist} — {quality assessment}
- **Test data factories/fixtures**: {exist / don't exist} — {recommendation}
- **Custom matchers**: {exist / don't exist}

## Phased Improvement Plan

### Phase 0: Infrastructure (do first — enables everything else)
| # | Action | Why | Effort |
|---|--------|-----|--------|
| 1 | {e.g., Add coverage reporting to CI} | Track progress, prevent regression | {hours} |
| 2 | {e.g., Set up test database/fixtures} | Consistent test data | {hours} |
| 3 | {e.g., Fix anti-patterns in existing tests} | Prevent false confidence | {hours} |

### Phase 1: Critical Coverage Gaps ({effort range})
{Highest-priority items from the gap analysis. Each should be a concrete, scoped task.}

| # | What to Test | Test Type | Module | Specific Tests to Write | Effort |
|---|-------------|-----------|--------|------------------------|--------|
| 1 | {e.g., Auth middleware — valid token, expired, missing, wrong role} | Unit | {module} | 4-6 tests | {hours} |
| 2 | {e.g., Core API endpoints — CRUD + auth + validation + errors} | Integration | {module} | 8-12 tests | {hours} |
| ... | ... | ... | ... | ... | ... |

### Phase 2: Coverage Expansion ({effort range})
| # | What to Test | Test Type | Module | Specific Tests to Write | Effort |
|---|-------------|-----------|--------|------------------------|--------|
| ... | ... | ... | ... | ... | ... |

### Phase 3: Advanced Testing ({effort range})
| # | What to Add | Why | Effort |
|---|-----------|-----|--------|
| 1 | {e.g., E2E tests for critical user flows} | Catch integration issues | {hours} |
| 2 | {e.g., Property-based tests for data transformations} | Catch edge cases | {hours} |
| 3 | {e.g., Performance regression tests} | Prevent degradation | {hours} |
{Only include if the project would benefit — don't recommend E2E for a library.}

## Effort Estimation by Test Type
{Help the team estimate capacity needed:}

| Test Type | Avg Effort per Test | Tests Needed | Total Effort |
|-----------|-------------------|-------------|-------------|
| Unit test (simple) | 15-30 min | ... | ... |
| Unit test (complex/mocked) | 30-60 min | ... | ... |
| Integration test | 1-2 hours | ... | ... |
| E2E test | 2-4 hours | ... | ... |
| **Total** | | | **{range}** |

## Recommended Test Structure
```
{Recommended directory layout based on detected patterns and conventions}
tests/
├── unit/
│   ├── {module}/        # Mirrors src/{module}/
│   └── ...
├── integration/
│   ├── {area}/
│   └── ...
├── e2e/                 # {only if recommended}
│   └── flows/
├── fixtures/            # Shared test data
├── helpers/             # Test utilities
└── setup.{ext}          # Global test setup
```

## Mutation Testing Consideration
{Only include if the project has >70% coverage and would benefit from deeper quality assessment:}
{Recommend if: mature test suite, critical business logic, team wants to move beyond coverage metrics}
{Skip if: low coverage (focus on writing tests first), simple CRUD app, small team}

## Positive Observations
{2-3 things the test suite does well — acknowledge good testing practices found}
```
