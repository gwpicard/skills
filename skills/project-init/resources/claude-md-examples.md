# CLAUDE.md Examples

Real-world CLAUDE.md examples for different project types. Use these as reference -- never copy verbatim. Every CLAUDE.md should be tailored to its specific project.

---

## Example 1: Next.js Full-Stack App

```markdown
# TaskFlow

A task management app with real-time collaboration, built with Next.js and Supabase.

## Quick Commands

```bash
pnpm dev                    # Start dev server (localhost:3000)
pnpm build                  # Production build
pnpm test                   # Run Vitest
pnpm test:e2e               # Run Playwright e2e tests
pnpm lint                   # ESLint + Prettier check
pnpm db:push                # Push schema to Supabase
pnpm db:generate            # Generate Prisma client
pnpm db:studio              # Open Prisma Studio
```

## Tech Stack

**Frontend**: Next.js 15 (App Router), React 19, TypeScript
**Styling**: Tailwind CSS + shadcn/ui
**State**: TanStack Query for server state, Zustand for UI state
**Backend**: Next.js API Routes + Server Actions
**Database**: Supabase (PostgreSQL) with Prisma ORM
**Auth**: Supabase Auth (email + Google OAuth)
**Deployment**: Vercel + Supabase Cloud

## Project Structure

```
src/
├── app/              # Next.js app router pages and layouts
├── components/       # Shared UI components (shadcn/ui based)
├── features/         # Feature modules (tasks/, teams/, settings/)
│   └── [feature]/
│       ├── components/   # Feature-specific components
│       ├── hooks/        # Feature-specific hooks
│       ├── actions/      # Server actions
│       └── types.ts      # Feature types
├── lib/              # Shared utilities (supabase client, utils)
├── hooks/            # Shared custom hooks
└── types/            # Global TypeScript types
```

## Code Conventions

- Named exports only, no default exports
- Server Components by default, 'use client' only when needed
- Server Actions for mutations, TanStack Query for reads
- Zod schemas for all input validation (shared between client/server)
- Error boundaries at feature level, not component level
- All database queries go through Prisma, never raw SQL

## Critical Rules

1. Never commit .env or .env.local
2. All API inputs validated with Zod before processing
3. Check Supabase RLS policies when modifying database access patterns
4. Run `pnpm build` before pushing -- catches SSR issues that dev mode misses
5. Real-time subscriptions must be cleaned up in useEffect return

## Dev Workflow

- Feature branches from `main`, squash merge via PR
- `/dev-docs [feature]` before starting anything non-trivial
- `/code-review` before creating PR
- `/build-and-fix` if CI fails

## Environment Setup

```bash
cp .env.example .env.local
# Fill in NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY
pnpm install
pnpm db:generate
pnpm dev
```
```

---

## Example 2: Python Backend API

```markdown
# DataPipeline API

REST API for data ingestion, transformation, and delivery. Handles 50k+ records/day.

## Quick Commands

```bash
uv run fastapi dev                    # Start dev server
uv run pytest                         # Run all tests
uv run pytest -x -v tests/test_api/   # Run API tests, stop on first failure
uv run ruff check .                   # Lint
uv run ruff format .                  # Format
uv run alembic upgrade head           # Run migrations
uv run alembic revision --autogenerate -m "description"  # Create migration
```

## Tech Stack

**Runtime**: Python 3.12
**Framework**: FastAPI + Uvicorn
**Database**: PostgreSQL 16 via SQLAlchemy 2.0 (async)
**Migrations**: Alembic
**Task Queue**: Celery + Redis
**Testing**: pytest + httpx (async test client)
**Package Management**: uv

## Project Structure

```
src/
├── api/              # FastAPI routers (one file per resource)
├── core/             # Config, security, dependencies
├── models/           # SQLAlchemy models
├── schemas/          # Pydantic request/response schemas
├── services/         # Business logic layer
├── repositories/     # Database access layer
├── tasks/            # Celery background tasks
└── utils/            # Shared utilities
tests/
├── test_api/         # API endpoint tests
├── test_services/    # Service layer tests
└── conftest.py       # Shared fixtures
```

## Architecture

- **Layered architecture**: Router -> Service -> Repository -> Database
- Routers handle HTTP concerns only (parsing, status codes)
- Services contain all business logic
- Repositories handle all database queries
- Never skip layers (no direct DB access from routers)

## Code Conventions

- Type hints on all function signatures
- Pydantic models for all API input/output
- Dependency injection via FastAPI Depends()
- Async by default for all I/O operations
- Structured logging with structlog (never print())

## Critical Rules

1. All endpoints require authentication via JWT middleware
2. Database sessions must use async context managers (no manual commit/rollback)
3. Background tasks go through Celery, never threading
4. Alembic migrations must be reversible (include downgrade)
5. Never use `SELECT *` -- always specify columns
```

---

## Example 3: Simple Static Site / Script

```markdown
# Portfolio

Personal portfolio site built with Astro.

## Commands

```bash
pnpm dev        # localhost:4321
pnpm build      # Build to dist/
pnpm preview    # Preview production build
```

## Stack

Astro 4, Tailwind CSS, MDX for blog posts. Deployed on Netlify.

## Structure

```
src/
├── pages/        # Astro pages (.astro)
├── layouts/      # Page layouts
├── components/   # UI components
├── content/      # MDX blog posts and project descriptions
└── styles/       # Global CSS
```

## Conventions

- Content in MDX with frontmatter for metadata
- Images optimized with Astro Image
- No client-side JS unless absolutely necessary
- Mobile-first responsive design
```

---

## Key Takeaways

1. **Scale the CLAUDE.md to the project's complexity** -- a portfolio site needs 30 lines, a full-stack app needs 150
2. **Only include real commands** -- never leave `[placeholder]` text in a shipped CLAUDE.md
3. **Architecture decisions matter most** -- "Server Components by default" saves more rework than any style guide
4. **Critical Rules prevent the biggest mistakes** -- these are the rules that if broken cause real problems
5. **Keep updating** -- add a rule every time you find yourself correcting the same mistake twice
