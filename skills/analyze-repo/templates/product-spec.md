# Template: Product & Feature Spec
<!-- output: .claude/repo-product-spec.md -->
<!-- agents: D1, D2, D3, D4, D9 -->

## Synthesis Instructions

Use PRODUCT LANGUAGE throughout — translate code constructs into what they mean for users. For every extracted finding, note confidence: High (explicit in code/comments), Medium (inferred from patterns), Low (guessed from naming).

## Template Structure

```markdown
# Product Specification: {project_name}
> Reverse-engineered from codebase on {date} | Confidence levels noted per finding

## Product Overview
{What this product is, who it's for, what problem it solves — 3-5 sentences in business language}

## Target Users & Personas
| Role | Description | Key Permissions | How Detected |
|------|-------------|----------------|-------------|
| ... | ... | ... | RBAC/routes/auth scopes |

---

## Feature Map

### {Area Name} (e.g., Authentication & Access Control)
| Feature | Description | Criticality | Entry Point | Key Files | Confidence |
|---------|-------------|------------|-------------|-----------|-----------|
| ... | ... | Core/Supporting/Peripheral | ... | ... | High/Med/Low |

{Repeat per area}

---

## User Flows
{For each major flow: Mermaid flowchart (max 15-20 nodes) + step-by-step description + business rules. Show happy path first, then branch to errors.}

### Flow: {Name}
```mermaid
flowchart TD
    {diagram}
```
**Steps:** {numbered list in product language}
**Business rules:** {bullet list of rules governing this flow}
**Error states:** {what happens when things go wrong}

---

## Domain Model

### Entity Relationship Diagram
```mermaid
erDiagram
    {top 15-20 entities with labeled relationships}
```

### Core Entities
| Entity | Business Meaning | Key Fields | Rules | Confidence |
|--------|-----------------|-----------|-------|-----------|
| ... | ... | ... | ... | High/Med/Low |

### Business Glossary
| Term | Definition | Code Representation | Aliases/Inconsistencies |
|------|-----------|---------------------|------------------------|
| ... | ... | ... | {flag where same concept has different names} |

### Bounded Contexts (if applicable)
| Context | Core Entities | Integration Points |
|---------|--------------|-------------------|
| ... | ... | ... |

---

## State Machines
{Mermaid stateDiagram-v2 for each lifecycle pattern found}

## Discovered Business Constants
| Constant | Value | Likely Purpose | Location | Confidence |
|----------|-------|---------------|----------|-----------|
| ... | ... | ... | file:line | ... |

## Business Rules Catalog
| Rule | Category | Description | Trigger | On Violation | Location | Confidence |
|------|----------|-------------|---------|-------------|----------|-----------|
| ... | Validation/Auth/State/Calculation | ... | ... | ... | ... | High/Med/Low |

## Feature Flags & Experiments
| Flag/Experiment | Description | Controls | Default | Type |
|----------------|-------------|----------|---------|------|
| ... | ... | ... | On/Off | Release/Ops/Permission |

## Integrations
| Service | Category | Product Purpose | Data Flow | Failure Impact | Confidence |
|---------|---------|----------------|-----------|---------------|-----------|
| ... | Payment/Email/Auth/etc. | {in product terms} | In/Out/Bidirectional | Critical/Degraded/Invisible | ... |

---

## Requires Human Input
The following cannot be determined from code analysis alone:
- [ ] Product vision and strategic context
- [ ] Competitive positioning
- [ ] Feature prioritization rationale
- [ ] Success metrics / KPIs for each feature
- [ ] Deprecated features confirmation
- [ ] User segmentation beyond RBAC roles

## Detected Anomalies
{Dead code/features, inconsistent naming, undocumented endpoints, orphaned routes}
```
