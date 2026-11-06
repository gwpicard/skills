# D5: Implementation Patterns

Analyze this repository for IMPLEMENTATION PATTERNS.

Your task:
1. Read: core business logic files, utilities, middleware, hooks, services, type definitions, base classes
2. Grep for: design pattern indicators (factory, singleton, observer, strategy, repository, dependency injection), error handling patterns (try/catch, Result types, error boundaries, error classes), auth middleware/guards
3. Using the language-specific patterns from the CONTEXT block, identify:
   - Design patterns used (with specific file path examples)
   - Error handling strategy (how errors are created, propagated, caught, and reported to users)
   - Auth implementation approach (JWT, sessions, OAuth, API keys — how it works end to end)
   - Key abstractions and interfaces that structure the codebase
   - Data validation approach (schemas, validators, type guards, middleware)
   - Code conventions (naming, file organization, import patterns)
   - Complex or notable code paths worth understanding

4. Identify complexity hotspots: files/functions with deep nesting (>4 levels), long functions (>30 lines of logic), or many branches. For the top 5-10 hotspots, note the file:line and the specific complexity indicator.
5. Identify "seams" (per Michael Feathers) — places where behavior can be altered without editing the code in that place: interfaces, dependency injection points, strategy patterns, plugin systems. These are the safest entry points for refactoring.

Return your findings as a markdown section starting with `## Implementation Patterns`. Include:
- Patterns table (Pattern | Where Used | Example File)
- Error handling summary (approach, error types, user-facing vs internal)
- Auth approach summary
- Key abstractions list (interfaces, base classes, shared utilities)
- Complexity hotspots table (File | Function/Class | Indicator | Nesting Depth | Estimated Complexity)
- Seams/extension points for safe refactoring
- Notable code paths worth reading

Keep your output under 200 lines. Focus on the most important findings.
