# D1: Architecture & Structure

Analyze this repository for ARCHITECTURE & STRUCTURE.

Your task:
1. Read: manifest file, config files (from CONTEXT Language Patterns), any architecture docs (docs/architecture*, ARCHITECTURE.md, ADRs)
2. Use Glob to map directory structure 3 levels deep
3. Determine:
   - Primary language and version
   - Frameworks (frontend, backend, testing)
   - Architectural pattern (MVC, component-based, microservices, serverless, monolith, hexagonal, etc.)
   - Structure pattern (monorepo, single-app, multi-package)
   - Data flow pattern (SSR, SSG, SPA, API-first, hybrid, event-driven)
   - Database / ORM / data layer (if applicable)
   - Key module boundaries and how they communicate
4. Create an annotated directory tree (top 2-3 levels) showing what each directory contains
5. Create a Mermaid component diagram showing major modules and their relationships

Return your findings as a markdown section starting with `## Architecture & Structure`. Include:
- A stack summary table (Category | Technology | Version if known)
- The annotated directory tree
- A Mermaid component diagram
- A 2-3 sentence architecture summary

Keep your output under 200 lines. Focus on the most important findings.
