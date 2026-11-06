# Template: Security Remediation Plan
<!-- output: .claude/repo-security-audit.md -->
<!-- agents: D1, D5, D6, D7 -->

## Synthesis Instructions

Every finding must include: severity, confidence, effort estimate, OWASP category, CWE reference, and a specific fix recommendation (with before/after code where applicable). Redact actual secret values. Frame findings as prioritized remediation actions.

## Template Structure

```markdown
# Security Remediation Plan: {project_name}
> Generated on {date} | Commit: {HEAD short hash} | Method: Static Analysis

## Scope & Limitations
This report presents findings from automated static analysis of source code. It does NOT constitute a penetration test or comprehensive security audit. See appendix for full methodology notes.

Static analysis CAN detect: common vulnerability patterns, hardcoded secrets, known vulnerable dependency patterns, insecure configuration, missing security controls.
Static analysis CANNOT detect: business logic vulnerabilities, runtime-specific issues, infrastructure/network vulnerabilities, complex multi-step attack chains.

## Executive Summary
- **Overall risk rating**: {CRITICAL / HIGH / MODERATE / LOW}
- **Total findings**: {count} ({critical} critical, {high} high, {medium} medium, {low} low, {info} informational)
- **Top risk theme**: {e.g., "Injection vulnerabilities due to lack of input validation" — reveals systemic pattern}
- **Immediate actions needed**: {1-3 bullet points}

## Risk Summary

### By Severity
| Severity | Count |
|----------|-------|
| Critical | ... |
| High | ... |
| Medium | ... |
| Low | ... |
| Informational | ... |

### By OWASP Category
| OWASP Category | Count | Systemic? |
|---------------|-------|-----------|
| A01:2021 Broken Access Control | ... | {Yes if >2 findings} |
| A03:2021 Injection | ... | ... |
| ... | ... | ... |

## Prioritized Remediation Plan

### P0 — Immediate (fix within 48 hours)
| # | Finding | Severity | Confidence | Location | OWASP | CWE | Fix | Effort |
|---|---------|----------|-----------|----------|-------|-----|-----|--------|
| ... | ... | Critical | High/Med | file:line | A0X:2021 | CWE-XXX | {specific fix with code if possible} | Quick/Moderate/Significant |

### P1 — Urgent (fix within 1 week)
{Same table format}

### P2 — Planned (fix within 1 month)
{Same table format}

### P3 — Backlog
{Same table format}

## Detailed Findings
{For the top 3-5 most critical findings, provide expanded detail:}

### [F-001] {Finding Title}
- **Severity**: Critical | **Confidence**: High | **Effort**: Quick Fix
- **OWASP**: A03:2021 — Injection | **CWE**: CWE-89 (SQL Injection)
- **Location**: `file:line`
- **Description**: {what the issue is}
- **Evidence**: {code snippet or data flow: source → sink}
- **Impact**: {what could happen if exploited}
- **Remediation**:
  - Immediate fix: {before/after code snippet}
  - Proper fix: {architectural recommendation}
  - Prevention: {CI rule, linting, training}

## Authentication & Authorization Assessment
| Control | Status | Details |
|---------|--------|---------|
| Password hashing | PASS/FAIL/WARN | {algorithm used} |
| Session/token management | ... | ... |
| Rate limiting (auth) | ... | ... |
| MFA | ... | ... |
| Route protection | ... | {N routes missing auth middleware} |
| IDOR prevention | ... | {N endpoints lacking ownership checks} |
| RBAC implementation | ... | ... |
| Default deny | ... | ... |

## Supply Chain Security
- Total dependencies: {direct} direct, {transitive} transitive
- Lockfile committed: {Yes/No} | Integrity hashes: {Yes/No}
- Dependencies with post-install scripts: {list if any}
- Audit command in CI: {Yes/No}

## Security Infrastructure
| Control | Status | Notes |
|---------|--------|-------|
| CSRF Protection | {Present/Missing/Partial} | ... |
| Rate Limiting | ... | ... |
| Security Headers (CSP, HSTS, X-Frame-Options) | ... | ... |
| Dependency Scanning in CI | ... | ... |
| Input Validation at Boundaries | ... | ... |
| Secrets Management | ... | ... |

## Positive Observations
{2-3 things the codebase does well from a security perspective — builds credibility}

## Recommendations
{Prioritized: what to add to CI, policies to create, patterns to adopt, training to consider}
```
