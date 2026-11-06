# Template: Documentation Plan
<!-- output: .claude/repo-documentation-plan.md -->
<!-- agents: D1, D2, D3, D4, D9 -->

## Synthesis Instructions

Use the Diataxis framework (Tutorials, How-To Guides, Reference, Explanation) to classify docs. Assess quality using a 0-3 scale (0=placeholder, 1=skeletal, 2=functional, 3=comprehensive). Assess freshness by comparing doc last-modified dates to related code changes.

## Template Structure

```markdown
# Documentation Plan: {project_name}
> Generated on {date}

## Documentation Health Score: {score}/100
| Dimension | Score | Weight |
|-----------|-------|--------|
| README Quality | {X}/25 | 25% |
| API Documentation | {X}/25 | 25% |
| Architecture Documentation | {X}/15 | 15% |
| Inline Documentation | {X}/15 | 15% |
| Guides & Tutorials | {X}/10 | 10% |
| Operational Docs | {X}/10 | 10% |

## Current Documentation Inventory
| Document | Diataxis Type | Location | Quality (0-3) | Freshness | Issues |
|----------|-------------|----------|-------------|-----------|--------|
| README.md | Mixed | / | ... | Fresh/Aging/Stale | ... |
| ... | Tutorial/How-To/Reference/Explanation | ... | ... | ... | ... |

## Inline Documentation Coverage
- Public API doc coverage: ~{X}% of exported symbols have doc comments
- Undocumented complex functions: {list top 5}
- Modules with lowest doc coverage: {list}

## Gap Analysis

### Critical Gaps (blocking adoption/onboarding)
| # | Document | Diataxis Type | Target Audience | Why Critical | Effort |
|---|----------|-------------|----------------|-------------|--------|
| ... | ... | ... | ... | ... | {X}h |

### Important Gaps (reducing productivity)
| # | Document | Current State | Specific Gap | Effort |
|---|----------|--------------|-------------|--------|
| ... | ... | {exists but incomplete} | {what's missing} | {X}h |

### Nice-to-Have Gaps (improves experience)
| # | Document | Purpose | Effort |
|---|----------|---------|--------|
| ... | ... | ... | {X}h |

## Freshness Report
{Flag docs that reference deleted files, old API signatures, outdated dependency versions, or haven't been updated despite significant related code changes}

## Prioritized Action Plan

### Immediate (Week 1)
{Top 3-5 items with: what to write, where to put it, estimated effort, why it matters}

### Short-Term (Month 1)
{Next tier of items}

### Ongoing Maintenance
{Recommendations for keeping docs fresh: triggers for updates, review cadence}

## Documentation Architecture Recommendation
{Based on Diataxis: recommended directory structure}

```
docs/
  getting-started/     # Tutorials
  guides/              # How-To Guides
  reference/           # API and config reference
  architecture/        # Explanation + ADRs
  contributing.md
  changelog.md
```

## README Draft Structure
{Recommended sections based on analysis, with notes on what content goes where. Detect project type (library/app/CLI/API) and adjust emphasis accordingly.}

## API Documentation Outline
{Endpoints/functions to document, grouped by area. Note which are undocumented vs. partially documented. For each: method, path, auth, what needs documenting.}

## Architecture Guide Outline
{Recommended C4 model levels: System Context (always), Container (if multi-component), Component (for complex modules). Include Mermaid diagrams from D1 analysis.}

## Tooling Recommendations
{Based on detected tech stack: suggest specific doc tools — Docusaurus, Sphinx, mdBook, Storybook, Redoc, etc. Only recommend tools not already in use.}
```
