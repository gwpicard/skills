# Template: README Draft
<!-- output: .claude/repo-readme-draft.md -->
<!-- agents: D1, D2, D3, D4, D9 -->

## Synthesis Instructions

Generate an actual README draft with real content extracted from the analysis. Apply the **30-second test**: a reader should understand What, Why, and How to get started within the first screenful. Detect **project type** (library, application, CLI tool, API service, framework/plugin) and adjust structure accordingly — libraries emphasize installation/API reference, applications emphasize setup/features, CLI tools emphasize usage examples, APIs emphasize endpoints/authentication.

Every command must be **copy-pasteable** (no placeholders in shell commands unless unavoidable — use realistic defaults). Every setup step must have a **verification step** (how to confirm it worked). Mark sections needing human input with `<!-- TODO: description of what to fill in -->` (HTML comments that render as invisible in markdown previews, not `[FILL]` which looks broken).

Target length: 100-300 lines. Shorter READMEs are better — link to detailed docs rather than inlining everything.

## Template Structure

```markdown
# {project_name}

> {one-line description — what it does in plain language, not marketing speak}

{badges — auto-detect from repo: CI status, npm/PyPI version, license, coverage if available. Only include badges that have real backing data.}

{If visual: screenshot or demo GIF placeholder}
<!-- TODO: Add screenshot or demo GIF showing the main interface -->

## Features

- **{Feature 1}** — {what it does, one line}
- **{Feature 2}** — ...
- **{Feature 3}** — ...
{5-7 features max. Derive from D4 product analysis. List by user value, not by technical component.}

## Quick Start

### Prerequisites
{Only list what's actually required. Include version constraints found in configs.}
- {runtime} {version from .nvmrc, .python-version, go.mod, etc.}
- {database if required}
- {other services if required}

### Installation

{Detect project type and provide appropriate install commands:}

**For libraries:**
```bash
npm install {package-name}
# or
yarn add {package-name}
# or
pip install {package-name}
```

**For applications:**
```bash
git clone {repo-url}
cd {project-name}
{copy .env command}
{install dependencies command}
{setup command — db migrate, etc.}
{start command}
```

### Verify It Works
{A concrete check — not "it should work" but "you should see X at Y"}
```bash
{verification command, e.g., curl localhost:3000/health}
# Expected output: {"status": "ok"}
```
{Or: "Open http://localhost:3000 — you should see the login page"}

## Usage

{For libraries: 2-3 code examples showing the most common use cases}
{For CLI tools: 3-5 most common commands with realistic arguments}
{For applications: skip this section or link to user docs}
{For APIs: 2-3 curl examples for the most important endpoints}

## Environment Variables

{Only include if the project uses env vars. Derive from .env.example or grep results.}
| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| ... | ... | Yes/No | ... |

## Architecture

{Include Mermaid diagram from D1 if the project has multiple components. Skip for simple libraries.}

```mermaid
{diagram}
```

{2-3 paragraphs explaining the high-level architecture. Focus on "why" decisions, not just "what" exists.}

## API Reference

{For APIs/libraries: summary table of endpoints or main functions. Link to full docs if extensive.}
{For applications: skip or link to separate API docs}

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| ... | ... | ... | ... |

## Development

```bash
{dev server command}      # {what it does}
{test command}            # {what it does}
{lint command}            # {what it does}
{build command}           # {what it does}
{other common commands}   # {what they do}
```

## Project Structure

```
{project-name}/
├── {dir}/          # {purpose — one line}
├── {dir}/          # {purpose}
├── {dir}/          # {purpose}
└── {config files}  # {purpose}
```
{Keep to 2-3 levels deep. Only show directories that help navigation, not every file.}

## Contributing

{If CONTRIBUTING.md exists: "See [CONTRIBUTING.md](./CONTRIBUTING.md)"}
{If not: brief section with branch strategy, PR process, and test requirements from D9/D5 analysis}
<!-- TODO: Review and expand contributing guidelines -->

## License

{Detected license from D6, or:}
<!-- TODO: Add license information -->
```
