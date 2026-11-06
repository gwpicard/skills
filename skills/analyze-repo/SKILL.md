---
name: analyze-repo
description: >
  Flexible multi-dimensional repository analysis with 9 presets and prescriptive output modes.
  Spawns specialized agents in parallel to analyze architecture, features, security, code quality,
  data model, API surface, performance, and more. Supports descriptive reports, security audits,
  product specs, refactoring plans, README drafts, onboarding guides, and other actionable outputs.
  Use when user says things like "analyze this repo", "understand this codebase", "what does this
  project do", "repo deep dive", "codebase analysis", "explain this project", "audit this codebase",
  "onboard me to this project", "product spec", "security audit", "code quality review",
  "write docs for this", "review performance", "help me understand the architecture".
---

# Skill: analyze-repo

Flexible, user-driven codebase analysis platform. Spawns specialized agents in parallel with support for 9 presets, 10 analysis dimensions, language-agnostic patterns, and prescriptive output modes.

## When to Use

- User says "analyze this repo", "understand this codebase", "what does this project do"
- User says "repo deep dive", "codebase analysis", "explain this project"
- User says "audit this codebase", "onboard me to this project"
- User says "product spec", "what does this product do", "reverse-engineer the features"
- User says "security audit", "check for vulnerabilities", "security review"
- User says "code quality review", "tech debt", "refactoring plan"
- User says "help me write docs", "documentation prep", "README draft"
- User says "architecture deep dive", "how is this structured"
- User says "performance review", "what's slow", "optimization plan"
- User asks for a comprehensive understanding of an unfamiliar codebase

## Instructions

**File paths**: All file references in this skill (e.g., `agents/d01-architecture.md`, `templates/security.md`, `references/language-patterns.md`) are relative to this skill's directory — the parent directory of this SKILL.md file. Resolve them to absolute paths when using the Read tool.

Execute the following phases in order.

---

## Phase Completion Protocol

Print these status lines as you complete each phase. Do NOT proceed to the next phase until the current phase is fully complete.

- Phase 0: `"Selected preset: {name} ({N} agents, {mode} mode)"`
- Phase 1: `"Recon complete. CONTEXT block assembled for {project_name} ({language}/{framework})"`
- Phase 2: `"All {N} agents complete. Proceeding to synthesis."`
- Phase 3: `"Report written to {file_path}"`

---

## Phase 0: Intent Detection & Preset Selection

Before any analysis, determine what the user wants. Use this mapping table:

| User says (or implies) | Auto-select preset |
|---|---|
| "analyze this repo", "understand this codebase", generic analysis request | None — ask user to choose |
| "what does this project do", "product spec", "reverse-engineer features", "what are the features" | Product & Feature Spec |
| "security audit", "check for vulnerabilities", "security review", "is this secure" | Security Audit |
| "help me understand this codebase", "explain this project", "deep dive" | Full Analysis |
| "I need to write docs", "documentation prep", "help me write docs", "README" | Documentation Prep |
| "onboard me", "I'm new to this project", "getting started" | Onboarding Package |
| "code quality", "tech debt", "refactoring plan", "review the code" | Code Quality Review |
| "architecture", "how is this structured", "system design" | Architecture Deep Dive |
| "performance", "what's slow", "optimize", "speed up" | Performance Review |

**If the user's intent clearly maps to a preset**: Auto-select it and confirm in one line (e.g., "I'll run a focused security analysis. Starting now."). Then proceed directly to Phase 1.

**If the user's intent is ambiguous or generic**: Use AskUserQuestion to narrow the scope. Since the tool supports max 4 options, use a two-step selection:

**Step 1** — Ask the category (AskUserQuestion, single-select, 4 options):

| Label | Description |
|---|---|
| Full repo analysis (Recommended) | Comprehensive analysis across all 10 dimensions |
| Understanding & documentation | Product spec, documentation prep, onboarding guide, or README draft |
| Quality & security | Security audit, code quality review, or performance review |
| Architecture deep dive | Structure, patterns, data flow, module boundaries |

**Step 2** — If the user selected "Understanding & documentation" or "Quality & security", ask a follow-up (AskUserQuestion, single-select, 3-4 options) to pick the specific preset:

For "Understanding & documentation":

| Label | Description |
|---|---|
| Product & feature spec | Reverse-engineer a PRD: features, user flows, domain model, business rules |
| Documentation prep | Analyze for README / API docs / guides with doc plan and drafts |
| Onboarding package | Architecture, workflows, key concepts for a new developer guide |

For "Quality & security":

| Label | Description |
|---|---|
| Security audit | Focused security analysis with prioritized remediation plan |
| Code quality review | Tech debt, testing, patterns with cleanup action plan |
| Performance review | Caching, queries, bundle size, observability with optimization plan |

If the user selects "Full repo analysis" or "Architecture deep dive" in Step 1, proceed directly — no Step 2 needed.

If the user selects "Other" at any step, treat it as the Custom option (see below).

### Preset Definitions

| Preset | Agents to spawn | Output mode | Template file |
|---|---|---|---|
| Full Analysis | D1-D10 | Descriptive | `templates/descriptive.md` |
| Product & Feature Spec | D1, D2, D3, D4, D9 | Product Spec | `templates/product-spec.md` |
| Security Audit | D1, D5, D6, D7 | Security | `templates/security.md` |
| Code Quality Review | D5, D7, D8, D10 | Refactoring | `templates/refactoring.md` |
| Documentation Prep | D1, D2, D3, D4, D9 | Documentation | `templates/documentation.md` |
| Onboarding Package | D1, D4, D5, D9 | Onboarding | `templates/onboarding.md` |
| Architecture Deep Dive | D1, D2, D3, D5 | Descriptive | `templates/descriptive.md` |
| Performance Review | D1, D2, D5, D9 | Performance | `templates/performance.md` |

### Custom Option

If the user selects "Custom", ask two follow-up questions:

1. **Scope** (multi-select): "Which areas should I analyze?" — list all 10 dimensions (D1-D10) with short descriptions.
2. **Output mode** (single-select): "What kind of output do you want?" — Descriptive report, Product spec, Security remediation plan, Refactoring action plan, README draft, Onboarding guide, Documentation plan, Performance optimization plan, Testing improvement plan, Migration plan.

---

## Phase 1: Enhanced Recon

Before spawning agents, gather context to pass to each one. Run these in parallel:

1. **`ls` the repo root** — get top-level files and directories
2. **Read the manifest file** — `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Gemfile`, `pom.xml`, `build.gradle`, `build.gradle.kts`, `composer.json`, `Package.swift`, or equivalent. Read whichever exists.
3. **Read README.md** (or README) if it exists — first 200 lines
4. **`git log --oneline -10`** — recent commits (skip if not a git repo)
5. **Glob `**/*` with 3 levels** — get a sense of the file tree structure

From this recon, determine:

### Project Identity
- **Project name** (from manifest or directory name)
- **One-sentence description** (from README or manifest)
- **Project type** (web app, mobile app, library, API service, CLI tool, framework, monorepo)
- **Maturity level** (prototype, MVP, production, mature — based on version, test presence, CI setup)
- **License** (from LICENSE file or manifest)
- **Version** (from manifest)

### Language Detection
From file extensions and manifest, determine the primary language(s). Count files by extension to identify dominant languages.

### Repo Size Classification
- **Small**: <500 source files — agents can explore broadly
- **Medium**: 500-5000 source files — agents should focus on key directories
- **Large**: >5000 source files — agents must sample strategically, focus on most-changed files from git

### Language-Specific Patterns
Read `references/language-patterns.md` and extract the pattern sets for ALL detected languages.

### CONTEXT Block Format

Assemble the CONTEXT block that every agent receives:

```
CONTEXT:
- Repo root: {path}
- Project: {name} — {one-sentence description}
- Type: {project type} | Maturity: {level} | License: {license} | Version: {version}
- Language(s): {primary}, {secondary if applicable}
- Framework(s): {detected frameworks}
- Key directories: {src/, lib/, app/, etc.}
- Repo size: {small/medium/large} ({file count} source files)
- Manifest: {manifest file path}

Language Patterns ({language}):
  Debug statements: {patterns}
  Type suppressions: {patterns}
  Lint suppressions: {patterns}
  Unsafe patterns: {patterns}
  Test files: {patterns}
  Config files: {patterns}
  Dependency files: {patterns}
  Module patterns: {patterns}
  Env access: {patterns}

{If multi-language, repeat Language Patterns block for each language}
```

---

## Phase 2: Spawn Agents

### Agent Dispatch Table

| Agent | File | Description |
|---|---|---|
| D1 | `agents/d01-architecture.md` | Architecture & Structure |
| D2 | `agents/d02-data-model.md` | Data Model & Storage |
| D3 | `agents/d03-api-surface.md` | API Surface & Interfaces |
| D4 | `agents/d04-product.md` | Product & User Experience |
| D5 | `agents/d05-patterns.md` | Implementation Patterns |
| D6 | `agents/d06-dependencies.md` | Dependencies & Integrations |
| D7 | `agents/d07-security.md` | Security Posture |
| D8 | `agents/d08-quality.md` | Code Quality & Standards (also needs `references/quality-rubric.md`) |
| D9 | `agents/d09-devops.md` | DevOps & Infrastructure |
| D10 | `agents/d10-evolution.md` | Codebase Evolution & Team |

### Two-Step Dispatch

**Step 2a**: Read all needed agent prompt files in parallel (one Read call per agent in the preset). For D8, also read `references/quality-rubric.md`.

**Step 2b**: Spawn all agents in a single message using the Agent tool. Each agent's prompt = CONTEXT block + the file contents read in Step 2a. For D8, append the quality rubric after the agent prompt.

All agents use `subagent_type: "general-purpose"`. Use `model: "sonnet"` for all agents for speed.

**Example composed prompt** (for a D7 agent):
```
CONTEXT:
- Repo root: /Users/alice/my-app
- Project: my-app — A task management API
- Type: API service | Maturity: production | License: MIT | Version: 2.1.0
- Language(s): TypeScript
- Framework(s): Express, Prisma
- Key directories: src/, tests/, prisma/
- Repo size: small (142 source files)
- Manifest: package.json

Language Patterns (TypeScript):
  Debug statements: console.log, console.debug, debugger
  Type suppressions: @ts-ignore, @ts-expect-error, as any, // @ts-nocheck
  Lint suppressions: eslint-disable, eslint-disable-next-line, eslint-disable-line
  Unsafe patterns: dangerouslySetInnerHTML, eval(, innerHTML =, document.write(
  Test files: *.test.*, *.spec.*, __tests__/
  Config files: tsconfig*, .eslintrc*, .prettierrc*, biome.json, vite.config.*, next.config.*, webpack*
  Dependency files: package.json, package-lock.json, yarn.lock, pnpm-lock.yaml, bun.lockb
  Module patterns: export default, export {, module.exports, import
  Env access: process.env., import.meta.env.

# D7: Security Posture

Analyze this repository for SECURITY POSTURE.

Your task:
1. Using the unsafe patterns from the CONTEXT block, grep for...
{... rest of d07-security.md contents ...}
```

**Example composed prompt for D8** (with quality rubric appended):
```
CONTEXT:
{... same CONTEXT block ...}

# D8: Code Quality & Testing
{... contents of d08-quality.md ...}

---

# Quality Rubric
{... contents of references/quality-rubric.md ...}
```

---

## Phase 3: Collect, Synthesize & Write Report

After all agents return:
- Collect each agent's output
- If any agent failed, note the section as "Analysis incomplete — agent encountered an error" and continue
- Do not let one failure block the entire report

### Create output directory

```bash
mkdir -p .claude
```

### Template Dispatch Table

| Output Mode | Template File |
|---|---|
| Descriptive | `templates/descriptive.md` |
| Product Spec | `templates/product-spec.md` |
| Security | `templates/security.md` |
| Refactoring | `templates/refactoring.md` |
| Documentation | `templates/documentation.md` |
| README | `templates/readme.md` |
| Onboarding | `templates/onboarding.md` |
| Performance | `templates/performance.md` |
| Testing | `templates/testing.md` |
| Migration | `templates/migration.md` |

Read the ONE template file for the selected output mode. Follow its structure exactly. The template contains:
- A metadata header with the output file path
- Synthesis instructions (follow these first)
- The full template structure (fill in with agent outputs)

Write the synthesized report to the file path specified in the template metadata header.

---

## Phase 4: Terminal Summary

Print a compact, scannable summary directly to the terminal. This MUST be readable in 30 seconds — keep it short.

**For Descriptive mode:**

```
## {project_name}

{one-sentence description} | {language} / {framework} | {type} | {maturity}

| Metric | Value |
|--------|-------|
| Source files | ~{count} |
| Dependencies | {count} prod, {count} dev |
| Test files | {count} |
| API endpoints | {count} (if applicable) |
| Contributors (6mo) | {count} |
| Project age | {duration} |

**Top findings:**
- {finding 1 — most important insight}
- {finding 2}
- {finding 3}
- {finding 4 — if significant}
- {finding 5 — if significant}

Full report: `.claude/repo-analysis.md`
```

**For Prescriptive modes:**

```
## {project_name} — {Preset Name}

{one-sentence summary of the prescriptive output}

**Key findings:**
- {top 3-5 most actionable findings, with file references where relevant}

Full report: `.claude/{output-file-name}.md`
```

---

## Phase 5: Contextual Follow-Up

After presenting the summary, use AskUserQuestion with options **derived from the actual findings**. Do NOT use a generic menu — look at what the analysis actually found and construct relevant options.

Guidelines for constructing follow-up options:
1. Look at the top 3-5 findings from the analysis
2. For each significant finding, create a follow-up option that lets the user act on it
3. Reference specific findings (e.g., "Fix the 2 critical security issues" not "Fix security issues")
4. Include a "Run a different analysis preset" option
5. Include a "Done for now" option

**Example follow-ups by preset:**

After **Full Analysis**:
- "Address the top security concerns" (referencing specific count/severity)
- "Clean up technical debt" (referencing specific counts of TODOs, suppressions, etc.)
- "Generate project documentation" (referencing what's missing)
- "Run a focused analysis on a specific area"
- "Done for now"

After **Security Audit**:
- "Fix the {N} critical issues now" (with specifics)
- "Set up automated security scanning in CI"
- "Dig deeper into {specific area that needs more investigation}"
- "Run a different analysis"
- "Done for now"

After **Product & Feature Spec**:
- "Write a comprehensive README based on this spec"
- "Create user documentation for the key features"
- "Generate API documentation"
- "Run a different analysis"
- "Done for now"

After **Code Quality Review**:
- "Start fixing the quick wins now"
- "Create tickets for the larger refactors"
- "Improve test coverage for {most critical gap}"
- "Run a different analysis"
- "Done for now"

After **Documentation Prep**:
- "Generate the README draft now"
- "Write API documentation"
- "Create the architecture guide"
- "Run a different analysis"
- "Done for now"

After **Onboarding Package**:
- "Set up missing dev tooling mentioned in the guide"
- "Create a CLAUDE.md with the key conventions"
- "Improve the getting started experience"
- "Run a different analysis"
- "Done for now"

---

## Edge Cases

- **Large repos (>5000 files)**: Agents sample strategically — focus on key directories, most-changed files from git history. Don't try to read everything.
- **Monorepos**: Analyze top-level structure + the 2-3 most active packages (by recent git activity).
- **Non-git repositories**: Skip D10 (Codebase Evolution & Team), note in the report that git history analysis was unavailable.
- **No README or manifest**: Report what can be determined from code, flag the documentation gaps explicitly.
- **Agent failure**: Note incomplete sections with "Analysis incomplete — agent encountered an error" and continue with all other agents.
- **No `.claude/` directory**: Create it with `mkdir -p .claude` before writing the report.
- **Multi-language repos**: Include language pattern sets for ALL detected languages in the CONTEXT block. Agents apply relevant patterns to relevant directories.
- **Empty or near-empty repos**: Report minimal findings, note the repo appears to be in early stages. Reduce agent count — skip D10, D2, D4 if insufficient code exists.
- **No test files found**: D8 should note this explicitly and rate Test Coverage as 1. Don't skip the agent.
- **Unfamiliar stack/framework**: Agents should report what they can determine from file structure and code patterns. Note uncertainty rather than guessing.
