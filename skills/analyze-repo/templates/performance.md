# Template: Performance Optimization Plan
<!-- output: .claude/repo-performance-plan.md -->
<!-- agents: D1, D2, D5, D9 -->

## Synthesis Instructions

**Critical framing**: Static analysis can identify performance *patterns* and *anti-patterns* but cannot measure actual performance. Every finding is a hypothesis until measured. Structure the output around this principle: identify patterns → recommend measurements → prioritize fixes based on measurement results.

Use a **3-tier confidence framework**:
- **Confirmed Pattern**: Code clearly shows a known anti-pattern (e.g., N+1 query in a loop, synchronous blocking call)
- **Likely Issue**: Pattern suggests a problem but impact depends on data volume/usage (e.g., missing index on a column used in WHERE clauses)
- **Recommended Practice**: Not necessarily a problem today, but a best practice gap (e.g., no caching layer, no connection pooling config)

Use **ICE-M scoring** for prioritization: Impact (1-5) × Confidence (1-5) × Ease of Fix (1-5), divided into tiers.

## Template Structure

```markdown
# Performance Optimization Plan: {project_name}
> Generated on {date} | Method: Static Analysis

## Methodology Note
This plan is based on static code analysis — identifying known performance patterns and anti-patterns. **No runtime measurements were taken.** All impact estimates are hypotheses that should be validated with profiling before committing to optimization work. The "Measurement Plan" section provides specific steps to validate each finding.

**Guiding principle**: Measure first, optimize second. The #1 recommendation is to set up observability (Section 6) before acting on specific findings.

## Executive Summary
- **Findings**: {count} total ({confirmed} confirmed patterns, {likely} likely issues, {recommended} recommended practices)
- **Highest-impact area**: {e.g., "Database queries — 3 confirmed N+1 patterns in high-traffic endpoints"}
- **Observability readiness**: {None / Basic / Good / Comprehensive}
- **Estimated quick wins**: {count} items achievable in < 1 day with measurable impact

## Current State Assessment

| Area | Status | Confidence | Key Finding |
|------|--------|-----------|-------------|
| Database queries | {OK / WARNING / CRITICAL} | {Confirmed/Likely} | {one-line summary} |
| Caching strategy | {OK / WARNING / NONE} | ... | ... |
| Frontend bundle | {OK / WARNING / CRITICAL / N/A} | ... | ... |
| API design | {OK / WARNING} | ... | ... |
| Async/Background processing | {OK / WARNING / NONE / N/A} | ... | ... |
| Connection management | {OK / WARNING / MISSING} | ... | ... |
| Observability | {None / Basic / Good} | Confirmed | ... |

## Prioritized Findings

### Tier 1: High Impact, High Confidence (act on these)

| # | Finding | Confidence | Location | Pattern | Fix | ICE-M | Effort |
|---|---------|-----------|----------|---------|-----|-------|--------|
| P-1 | {e.g., N+1 query in task list endpoint} | Confirmed | `{file:line}` | {anti-pattern name} | {specific fix} | {score} | {T-shirt} |
| P-2 | ... | ... | ... | ... | ... | ... | ... |

{For top 3-5 findings, include detail:}

### [P-1] {Finding Title}
- **Confidence**: Confirmed Pattern
- **Location**: `{file:line}`
- **Evidence**: {code snippet showing the pattern}
- **Why this matters**: {explain the scaling behavior — e.g., "Issues N+1 queries where N = number of tasks on the board. With 50 tasks, this is 51 DB queries per page load."}
- **Fix**:
  ```{language}
  // Before
  {problematic code}

  // After
  {fixed code}
  ```
- **How to measure improvement**: {specific command or metric — e.g., "Enable query logging, load a board with 50 tasks, compare query count before/after"}

### Tier 2: Likely Issues (validate then fix)

| # | Finding | Confidence | Location | Pattern | Recommended Action | ICE-M | Effort |
|---|---------|-----------|----------|---------|-------------------|-------|--------|
| ... | ... | Likely | ... | ... | {Measure first, then fix if confirmed} | ... | ... |

### Tier 3: Best Practice Gaps (plan for)

| # | Finding | Category | Current State | Recommended Practice | Effort |
|---|---------|---------|--------------|---------------------|--------|
| ... | ... | {Caching / Indexing / Pooling / etc.} | {what exists today} | {what should exist} | ... |

## Framework-Specific Findings

{Detect framework and apply framework-specific checks:}

{For Next.js: RSC vs client components, dynamic imports, Image optimization, ISR/SSG usage}
{For Django: select_related/prefetch_related usage, queryset evaluation, N+1 in templates}
{For Rails: eager loading, counter caches, background jobs for heavy work}
{For Express/Fastify: middleware ordering, streaming responses, compression}
{For any ORM: query count per request, missing eager loading, raw query opportunities}

| # | Framework-Specific Check | Status | Location | Recommendation |
|---|------------------------|--------|----------|---------------|
| ... | ... | ... | ... | ... |

## Database Performance

{If the project uses a database:}

### Query Patterns
| Pattern | Occurrences | Risk | Locations |
|---------|------------|------|-----------|
| N+1 queries (query in a loop) | ... | HIGH | ... |
| Missing eager loading | ... | MEDIUM | ... |
| Full table scans (no WHERE/missing index) | ... | MEDIUM | ... |
| Large result sets without pagination | ... | MEDIUM | ... |
| String-based query building | ... | LOW | ... |

### Index Recommendations
{From schema analysis — columns used in WHERE, JOIN, ORDER BY that lack indexes}
| Table | Column(s) | Used In | Recommended Index |
|-------|----------|---------|------------------|
| ... | ... | `{file:line}` | `CREATE INDEX ...` or ORM equivalent |

## Caching Inventory

| What | Cached? | TTL | Invalidation | Recommendation |
|------|---------|-----|-------------|---------------|
| {frequently accessed data} | Yes/No | ... | {strategy or "none"} | ... |
| ... | ... | ... | ... | ... |

## Measurement Plan

**Before optimizing anything, set up these measurements:**

### Quick Setup (< 1 hour)
| # | What to Measure | How | Tool/Command |
|---|----------------|-----|-------------|
| 1 | DB query count per request | {enable query logging} | {specific config} |
| 2 | API response times | {add timing middleware} | {specific code or tool} |
| 3 | {Framework-specific metric} | ... | ... |

### Deeper Profiling (when needed)
| # | What to Measure | When to Do This | Tool |
|---|----------------|----------------|------|
| 1 | Memory usage under load | Before Tier 1 fixes | {tool} |
| 2 | Bundle analysis | If frontend is slow | {tool, e.g., webpack-bundle-analyzer} |
| 3 | Database slow query log | After basic logging shows issues | {config} |

## Observability Setup

{Rate current observability and recommend specific improvements:}

**Current level**: {None / Basic / Good / Comprehensive}

| # | Action | What It Gives You | Priority | Effort |
|---|--------|------------------|----------|--------|
| 1 | {e.g., Add structured request logging} | Response times, error rates | HIGH | {time} |
| 2 | {e.g., Add DB query logging in dev} | Query count, slow queries | HIGH | {time} |
| 3 | {e.g., Add health check endpoint} | Basic uptime monitoring | MEDIUM | {time} |
| 4 | {e.g., Add metrics collection} | Dashboards, alerting | MEDIUM | {time} |
| ... | ... | ... | ... | ... |

## Quick Wins

{Items that are low-effort AND high-confidence — can be done immediately:}

- [ ] {Quick win 1} (`{file}`) — {what to change} — {expected improvement}
- [ ] {Quick win 2} — ...
- [ ] {Quick win 3} — ...

## Positive Observations
{2-3 things the codebase already does well for performance — acknowledge good patterns}
```
