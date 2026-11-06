# D7: Security Posture

Analyze this repository for SECURITY POSTURE.

Your task:
1. Using the unsafe patterns from the CONTEXT block, grep for: injection vectors, unsafe operations, hardcoded secrets
2. Grep for: strings containing "key", "secret", "token", "password", "api_key" in assignments (NOT in .env files — those are expected). REDACT any actual secret values in your output — show only enough to identify (first 4 chars or variable name).
3. For injection findings, show the data flow where possible: source (user input) → transforms → sink (dangerous function)
4. Check:
   - Whether any .env files are committed (not in .gitignore)
   - Auth configuration: password hashing algorithm (accept bcrypt/argon2/scrypt; flag MD5/SHA-1/plaintext), JWT setup, session management
   - CSRF protection on state-changing endpoints
   - Rate limiting on auth and sensitive endpoints
   - Input validation and sanitization at API boundaries
   - Access control: are routes/endpoints properly protected? Look for missing auth middleware on sensitive routes.
   - IDOR (Insecure Direct Object References): do endpoints verify ownership before returning resources?
   - SQL/NoSQL injection: raw queries without parameterization
   - XSS vectors: unescaped user content in HTML (using CONTEXT unsafe patterns)
   - Dependency vulnerabilities: check if audit commands (npm audit, pip audit, cargo audit) exist in CI/scripts
   - Security headers (CSP, HSTS, X-Frame-Options) if applicable
   - Supply chain: are lockfiles committed with integrity hashes? Are registries pinned? Any post-install scripts?
5. Map each finding to an OWASP Top 10 (2021) category AND a specific CWE where applicable

For each finding, assign:
- **Severity**: Critical, High, Medium, Low, Informational (see calibration rules below)
- **Confidence**: High (structural certainty), Medium (likely but context-dependent), Low (possible, needs verification). Distinguish "definite vulnerability" from "security hotspot needing human review."
- **Effort**: Quick Fix (<1h), Moderate (1-8h), Significant (1+ days)

Severity calibration:
- CRITICAL: High confidence + direct path from user input to dangerous sink, OR exposed secrets, OR leads to data breach/RCE/full auth bypass
- HIGH: Confident vulnerability but exploitation requires specific conditions, OR missing control that would be trivially exploitable
- MEDIUM: Requires chained exploitation or insider access, OR defense-in-depth issue, OR high-impact but low confidence
- LOW: Best practice violation with no direct exploitation path
- INFO: Recommendations that improve posture but aren't vulnerabilities

Compute a priority tier for each finding:
- P0 (Immediate): Critical severity + easy to exploit + quick fix
- P1 (Urgent): High/Critical + exploitable, OR Critical + quick fix
- P2 (Planned): Medium severity, or High with low exploitability/high effort
- P3 (Backlog): Low/Info severity, or significant effort with moderate risk

Return your findings as a markdown section starting with `## Security Posture`. Include:
- Scope & limitations note: "This is a static analysis review, not a penetration test. It can detect code-level patterns but cannot detect business logic vulnerabilities, runtime issues, or infrastructure misconfigurations."
- Risk summary: counts by severity and by OWASP category
- Prioritized findings table: (Priority | Severity | Confidence | Finding | Location file:line | OWASP | CWE | Fix | Effort)
  - Group findings by OWASP category if multiple findings share the same category (reveals systemic patterns)
- Auth & authorization assessment as a checklist table (Control | Status PASS/FAIL/WARN | Details)
- Supply chain security summary (lockfile, integrity hashes, post-install scripts, pinning)
- Security infrastructure checklist (CSRF | Rate Limiting | Security Headers | Dependency Scanning | Input Validation — each with Present/Missing/Partial)
- Positive observations: 2-3 things the codebase does well from a security perspective
- Prioritized recommendations

Keep your output under 250 lines. Focus on the most important findings.
