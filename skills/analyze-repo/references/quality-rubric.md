# Quality Rubric

Agent D8 MUST use this rubric for all ratings. Each level has explicit criteria.

## Type Safety
| Rating | Criteria |
|--------|----------|
| 1 | No type system. Heavy use of `any`/`object`/`interface{}`. No validation at boundaries. |
| 2 | Types exist but inconsistently applied. Frequent type suppressions (>10). Many untyped functions. |
| 3 | Types used for most code. Some `any` usage (<10 instances). Basic validation present at API boundaries. |
| 4 | Strong typing throughout. Rare suppressions with justification (<5). Schema validation at boundaries. |
| 5 | Comprehensive types everywhere. No unjustified suppressions. Runtime validation at all boundaries. Generic types for reusability. |

## Test Coverage
| Rating | Criteria |
|--------|----------|
| 1 | No tests or only trivial smoke tests (<5 test files). |
| 2 | Some tests exist but major modules untested. Tests mostly check happy paths only. |
| 3 | Core business logic has tests. Mix of unit and integration. Some edge cases covered. |
| 4 | High coverage. Unit, integration, and some E2E tests. Edge cases and error paths tested. Test helpers/fixtures organized. |
| 5 | Comprehensive coverage. Property-based or fuzz testing present. Tests are fast, reliable, well-organized. Coverage enforcement in CI. |

## Error Handling
| Rating | Criteria |
|--------|----------|
| 1 | Errors silently swallowed or crash the app. No error boundaries or catch blocks. |
| 2 | Basic try/catch but inconsistent. Error messages unhelpful or generic. No recovery logic. |
| 3 | Consistent error handling in most paths. User-facing errors are meaningful. Some recovery logic. |
| 4 | Typed/structured errors with clear hierarchy. Errors propagated correctly. Good user-facing messages. Recovery where possible. |
| 5 | Comprehensive error types. Circuit breakers. Graceful degradation. Error monitoring/alerting integration. Retry with backoff where appropriate. |

## Documentation
| Rating | Criteria |
|--------|----------|
| 1 | No README or severely outdated README. No inline documentation. |
| 2 | README exists but minimal (just project name or basic description). Some scattered code comments. |
| 3 | Decent README with setup instructions. Some API/function documentation. |
| 4 | Comprehensive README with setup, usage, architecture. API docs present. Inline docs on complex logic. |
| 5 | Full documentation suite: README, API reference, architecture docs, contributing guide, examples/cookbooks. Docs are current. |

## Code Organization
| Rating | Criteria |
|--------|----------|
| 1 | No clear structure. God files/classes (>1000 lines with mixed concerns). No separation of concerns. |
| 2 | Some structure but inconsistent. Mixed patterns across modules. Some circular dependencies. |
| 3 | Clear directory structure. Consistent module pattern within areas. Reasonable separation of concerns. |
| 4 | Well-organized with clear boundaries. Consistent patterns throughout. Good separation of concerns. Dependency direction is clear. |
| 5 | Exemplary organization. Clear module boundaries enforced. Dependency injection/inversion. Easy to navigate, extend, and test in isolation. |

## Security Posture
| Rating | Criteria |
|--------|----------|
| 1 | Hardcoded secrets in code. No auth on sensitive endpoints. Raw SQL with string concatenation. No input validation. |
| 2 | Basic auth present but has flaws. Some input validation. Known vulnerability patterns present (XSS, injection). |
| 3 | Standard auth implementation. Input validated at API boundaries. No obvious critical vulnerabilities. Dependencies reasonably current. |
| 4 | Strong auth with proper session/token management. Security headers present. Rate limiting. Dependency scanning in CI. |
| 5 | Defense in depth. CSP + security headers. CSRF protection. Audit logging. Regular dependency scanning. Secrets management. Penetration tested. |

## Observability
| Rating | Criteria |
|--------|----------|
| 1 | No logging beyond console output. No monitoring. No health checks. |
| 2 | Basic logging exists but unstructured (free-form strings). No centralized monitoring. |
| 3 | Structured logging with levels. Basic health checks. Some metrics collection. |
| 4 | Structured logging with request context (IDs, user info). Distributed tracing. Metrics dashboards. Alerting configured. |
| 5 | Full observability stack: structured contextual logs, distributed tracing, metrics with dashboards, alerting with SLOs, error tracking service. |
