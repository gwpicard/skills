# D8: Code Quality & Testing

Analyze this repository for CODE QUALITY & TESTING.

Your task:

STEP 1 — Determine the recommended test model based on project type:
- Library/package/utility → Test Pyramid (70% unit, 20% integration, 10% E2E)
- Web frontend (React/Vue/Angular) → Testing Trophy (40% integration, 25% unit, 25% static, 10% E2E)
- Microservices → Testing Honeycomb (large integration layer, contract tests at boundaries)
- Monolith → Modified Pyramid (fat integration layer)
- CLI tool → Test Pyramid

STEP 2 — Inventory tests:
1. Glob for test files using the CONTEXT test file patterns
2. Classify each test file by type using heuristics:
   - Unit: imports single module, mocks dependencies, tests functions in isolation
   - Integration: uses real/in-memory DB, tests multiple modules together, API endpoint tests
   - E2E: browser automation (Playwright/Cypress/Selenium), full-stack HTTP tests
3. Count and compute distribution vs. recommended model
4. Map source files to test files — flag source files with NO corresponding test file
5. For unmapped source files, weight the gap by: cyclomatic complexity (branches, loops, conditionals) and git change frequency (frequently changed + untested = CRITICAL gap)

STEP 3 — Assess test quality (read 2-3 test files for the most critical/changed modules):
6. Check for anti-patterns:
   - Excessive mocking: >5 mocks per test
   - Testing implementation details: assertions on private members, internal state, exact call counts
   - Hardcoded dates/times: date literals without clock mocking
   - Weak assertions: only toBeDefined/toBeTruthy/not.toBeNull
   - Giant tests: >50 lines or >10 assertions per test block
   - Snapshot overuse: snapshot files >500 lines
   - Missing error path tests: source has try/catch but tests only cover happy path
   - Shared mutable test state: let/var at describe scope modified in test blocks
7. Read linter/formatter configs using the CONTEXT config file patterns

STEP 4 — Inventory technical debt:
8. Using the CONTEXT language patterns, grep for and count:
   - TODO / FIXME / HACK / XXX / WORKAROUND comments
   - Debug statements (from CONTEXT debug patterns) in source (not test) files
   - Type suppressions (from CONTEXT type_suppress patterns)
   - Lint suppressions (from CONTEXT lint_suppress patterns)
9. Find very long files (>500 lines of code) — report as complexity hotspots
10. Look for dead code: large commented-out blocks, unused exports, unreferenced functions
11. Check for code duplication patterns (similar function signatures, copy-paste indicators)
12. Categorize all debt into: Code Debt, Architectural Debt, Test Debt, Documentation Debt, Dependency Debt, Infrastructure Debt

Use the Quality Rubric (appended below this prompt) to assign ratings. Each rating MUST follow the rubric criteria exactly. If no rubric is appended, rate based on your best judgment but note "rubric unavailable" in the justification.

Return your findings as a markdown section starting with `## Code Quality & Testing`. Include:
- Quality scorecard table (use the rubric — cite which criteria level each rating matches):

| Dimension | Rating (1-5) | Justification |
|-----------|-------------|---------------|
| Type Safety | | {cite rubric criteria met} |
| Test Coverage | | {cite rubric criteria met} |
| Error Handling | | {cite rubric criteria met} |
| Documentation | | {cite rubric criteria met} |
| Code Organization | | {cite rubric criteria met} |
| Security Posture | | {cite rubric criteria met} |
| Observability | | {cite rubric criteria met} |

- Test distribution analysis (Current: X% unit, Y% integration, Z% E2E vs. Recommended model for this project type)
- Test summary (framework, file count, types, patterns, anti-patterns found with counts)
- Coverage gap analysis (top 5-10 untested modules ranked by risk = complexity × change frequency)
- Linting/formatting setup
- Technical debt inventory (categorized into 6 debt types, with counts and file references)
- Complexity hotspots (top 5-10 files by estimated complexity that are frequently changed)
- Dead code candidates
- Positive observations: 2-3 things the codebase does well

Keep your output under 250 lines. Focus on the most important findings.
