# Template: Descriptive Report
<!-- output: .claude/repo-analysis.md -->
<!-- agents: all spawned agents -->

## Synthesis Instructions

This template is used for Full Analysis (all 10 agents) and Architecture Deep Dive (agents D1, D2, D3, D5). Adapt the structure based on which agents actually ran — skip sections for agents that weren't spawned.

### Executive Summary Guidelines
Write 3-4 paragraphs synthesizing ALL agent findings. Structure as:
1. **What it is**: Project identity, purpose, and tech stack (draw from D1 architecture, D4 product)
2. **How it's built**: Architecture patterns, key design decisions, data model (draw from D1, D2, D3, D5)
3. **Current health**: Quality scores from D8, security posture from D7, test coverage, tech debt levels. Lead with the most notable finding (good or bad).
4. **Team & trajectory**: Activity trends, bus factor, hotspots from D10. End with the single most important recommendation.

### Section Ordering
Include each agent's output as its own `##` section, in this order:
1. Architecture & Structure (D1)
2. Data Model & Storage (D2)
3. API Surface & Interfaces (D3)
4. Product & User Experience (D4)
5. Implementation Patterns (D5)
6. Dependencies & Integrations (D6)
7. Security Posture (D7)
8. Code Quality & Testing (D8)
9. DevOps & Infrastructure (D9)
10. Codebase Evolution & Team (D10)

Paste each agent's output verbatim as its section. Do NOT summarize or truncate agent outputs — include them in full. The executive summary and Key Observations sections are where you synthesize.

### Key Observations Guidelines
- **Strengths**: Look for high D8 quality scores (4-5), good security posture, strong test coverage, clean architecture patterns, active maintenance
- **Areas for Improvement**: Look for low D8 scores (1-2), missing tests, tech debt counts, missing documentation, no CI/CD
- **Risks & Concerns**: Look for critical security findings from D7, bus factor warnings from D10, architectural coupling from D5, missing error handling
- **Recommended Next Steps**: Prioritize by impact. Security fixes first, then quality/test gaps, then documentation, then nice-to-haves. Include specific file references.

## Template Structure

```markdown
# Repository Analysis: {project_name}
> Generated on {date} | Commit: {HEAD short hash if git} | Repository: {repo_root}

## Executive Summary
{3-4 paragraphs as described above}

---

{Each agent's output section in order, verbatim. Only include sections for agents that ran.}

---

## Key Observations

### Strengths
- {3-5 bullets with specific evidence from agent findings}

### Areas for Improvement
- {3-5 bullets with specific evidence and file references}

### Risks & Concerns
- {Prioritized list: security issues, bus factor, tech debt, scalability risks — with severity and file references}

### Recommended Next Steps
1. {Highest priority action — specific, with file references}
2. {Second priority}
3. {Third priority}
4. {Fourth priority, if warranted}
5. {Fifth priority, if warranted}
```
