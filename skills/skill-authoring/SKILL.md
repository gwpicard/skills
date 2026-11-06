---
name: skill-authoring
description: >
  Best practices for creating, improving, and organizing Claude Code skills.
  Use when the user asks to "create a skill", "write a SKILL.md", "improve a skill",
  "organize skills", "skill best practices", "fix my skill", "why isn't my skill triggering",
  or needs guidance on skill structure, progressive disclosure, descriptions, or evaluation.
  Also triggers when asked to "interview me about a skill" or "help me design a skill".
---

# Skill Authoring

Guide for creating effective Claude Code skills. Based on official Anthropic documentation, the Agent Skills open standard, and the skill-creator reference implementation.

## Skill Interview Workflow

Before writing any skill, gather sufficient context through a structured interview. Do NOT jump straight to writing SKILL.md — insufficient context produces vague, unhelpful skills.

### Phase 1: Understand Intent

Ask these foundational questions (use AskUserQuestion tool):

1. **What should this skill enable Claude to do?** — Get the core capability in one sentence.
2. **When should it trigger?** — Exact phrases users would say, and contexts where it should activate.
3. **What's the expected output?** — Format, files created, side effects.
4. **Who invokes it?** — User-only (`disable-model-invocation: true`), Claude-only (`user-invocable: false`), or both (default).
5. **Which category?** — Helps choose the right structural pattern:
   - **Document & Asset Creation** — Consistent, high-quality output (reports, code, designs). Key techniques: embedded style guides, templates, quality checklists.
   - **Workflow Automation** — Multi-step processes with consistent methodology. Key techniques: step-by-step validation gates, templates, iterative refinement loops.
   - **MCP Enhancement** — Workflow guidance on top of MCP tool access. Key techniques: coordinating multiple MCP calls, embedding domain expertise, error handling for common MCP issues.

Capture answers in a **use case definition**:
```
Use Case: [name]
Trigger: User says "[phrase 1]" or "[phrase 2]"
Steps:
1. [action]
2. [action]
Result: [concrete outcome]
```

### Phase 2: Research and Scope

Before writing, investigate:

- **What does Claude already know?** — Don't document what Claude handles well without the skill. Test without the skill first if possible.
- **What are the failure modes?** — What goes wrong today? The skill should address specific gaps.
- **Problem-first or tool-first?** — "I need to set up a project workspace" (problem-first: skill orchestrates the right tools) vs "I have Notion MCP connected" (tool-first: skill teaches best practices for existing tools). Most skills lean one direction.
- **Are there fragile operations?** — Database migrations, deployments, API calls with side effects need exact scripts, not general guidance.
- **Are there existing patterns?** — Check the codebase for conventions, existing scripts, or related skills.
- **Composability** — Skills load simultaneously. Design yours to work well alongside others, not as the only capability available.

**Pro tip**: Iterate on a single challenging task until Claude succeeds, then extract the winning approach into a skill. This provides faster signal than broad testing.

### Phase 3: Draft and Validate

1. Write a minimal SKILL.md addressing the identified gaps
2. Create 2-3 realistic test prompts covering normal use, edge cases, and should-not-trigger scenarios
3. Test with and without the skill — compare behavior
4. Iterate based on observed failures

### Interview Anti-patterns

- **Skipping the interview** — Writing a skill from a one-line request produces generic instructions
- **Over-interviewing** — 3-5 targeted questions suffice; don't turn it into a 20-question survey
- **Accepting vague answers** — "It should help with deployment" needs follow-up: which deployment target? what steps? what can go wrong?

## Skill Anatomy

```
skill-name/
├── SKILL.md              # Required: frontmatter + instructions (<500 lines)
├── references/           # Optional: detailed docs loaded on demand
│   └── api-reference.md
├── scripts/              # Optional: executable utilities
│   └── validate.py
├── examples/             # Optional: working code samples
│   └── basic-example.sh
└── assets/               # Optional: templates, images for output
    └── template.html
```

### What goes where

| Location | Purpose | Loaded when |
|----------|---------|-------------|
| Frontmatter `description` | Trigger matching (~100 words max) | Always in context |
| SKILL.md body | Core instructions, workflows, quick reference | When skill triggers |
| `references/` | Detailed API docs, schemas, edge cases | Claude reads as needed |
| `scripts/` | Deterministic utilities, validators, generators | Executed, not loaded into context |
| `examples/` | Complete, runnable code samples | Claude reads as needed |
| `assets/` | Templates, images used in output | Used in output, not loaded |

**Rule**: Information lives in SKILL.md OR references, never both. Keep SKILL.md under 500 lines / ~2,000 words. Move anything beyond that to `references/`.

## Frontmatter Reference

```yaml
---
name: my-skill-name           # Lowercase, numbers, hyphens. Max 64 chars. Must match directory name.
description: >                 # Max 1024 chars. CRITICAL for discovery.
  Processes Excel files and generates reports. Use when working with
  Excel files, spreadsheets, tabular data, or .xlsx files.

# --- Optional fields ---
argument-hint: "[filepath]"              # Autocomplete hint for arguments
disable-model-invocation: true           # Prevent auto-triggering (manual /invoke only)
user-invocable: false                    # Hide from / menu (background knowledge only)
allowed-tools: Read, Grep, Glob          # Auto-approve these tools when skill is active
model: sonnet                            # Override model (opus, sonnet, haiku)
context: fork                            # Run in isolated subagent context
agent: Explore                           # Subagent type when context: fork
hooks:                                   # Hooks scoped to this skill's lifecycle
  skill_start:
    - command: echo "skill started"
---
```

### Invocation control matrix

| Frontmatter | User can invoke | Claude can invoke | Context behavior |
|---|---|---|---|
| (default) | Yes | Yes | Description always loaded, body loads on invoke |
| `disable-model-invocation: true` | Yes | No | Description NOT in context, body loads when user invokes |
| `user-invocable: false` | No | Yes | Description always loaded, body loads on invoke |

### String substitutions

| Variable | Description |
|----------|-------------|
| `$ARGUMENTS` / `$0`, `$1`... | Arguments passed when invoking the skill |
| `$ARGUMENTS[N]` | Access specific argument by 0-based index |
| `${CLAUDE_SKILL_DIR}` | Absolute path to this skill's directory |
| `${CLAUDE_SESSION_ID}` | Current session ID |

### Dynamic context injection

Prefix a backtick-wrapped shell command with `!` (no space) to inject its output before Claude sees the content.

Example in your SKILL.md:
```
## Current state
- Git status: !`git status --short`
- Branch: !`git branch --show-current`
```

Commands execute during preprocessing. Claude only sees the output, not the command.

### Extended thinking

Include the word "ultrathink" anywhere in skill content to enable extended thinking mode.

## Writing Effective Descriptions

The description is the PRIMARY triggering mechanism. Claude uses it to choose from potentially 100+ skills.

### Formula

```
[What it does] + [When to use it] + [Key capabilities]
```

### Rules

1. **Third person** — "Processes Excel files..." not "Use this to..." or "I can help you..."
2. **Specific trigger phrases** — Include exact phrases users would say
3. **State WHAT and WHEN** — What the skill does + when to use it
4. **Be pushy about activation** — Mention contexts where users might not explicitly request the skill but would benefit from it
5. **Use negative triggers when needed** — "Do NOT use for simple data exploration (use data-viz skill instead)" prevents over-triggering
6. **Mention file types if applicable** — ".fig files", ".xlsx", ".csv"
7. **No XML angle brackets** (`<` or `>`) in frontmatter — security restriction since frontmatter appears in system prompt

### Good vs Bad

```yaml
# Good — specific, actionable, includes triggers
description: >
  Analyzes Figma design files and generates developer handoff documentation.
  Use when user uploads .fig files, asks for "design specs", "component
  documentation", or "design-to-code handoff".

# Good — clear value proposition with scope boundaries
description: >
  PayFlow payment processing for e-commerce. Handles account creation,
  payment setup, and subscription management. Use when user says "onboard
  new customer", "set up subscription", or "create PayFlow account".
  Use specifically for online payment workflows, not for general
  financial queries.

# Bad — too vague
description: Helps with documents

# Bad — missing triggers (too technical, no user phrases)
description: Implements the Project entity model with hierarchical relationships.

# Bad — wrong person
description: Use this to process PDFs
```

### Trigger evaluation

Create 20 eval queries: 10 should-trigger, 10 should-not-trigger. The most valuable should-not-trigger cases are **near-misses** — adjacent domains sharing keywords. Make queries realistic with specifics (file paths, column names, context).

**Debugging trick**: Ask Claude "When would you use the [skill name] skill?" — Claude will quote the description back. Adjust based on what's missing or misleading.

## Writing the Skill Body

### Use imperative form

```markdown
# Good
Configure the MCP server with authentication.
Validate settings before use.

# Bad
You should configure the MCP server.
You need to validate settings.
```

### Only add what Claude doesn't know

Don't explain what PDFs are or how standard libraries work. Add only:
- Project/domain-specific knowledge (schemas, conventions, business rules)
- Specific tool choices and configurations
- Non-obvious workflows and sequences
- Guardrails for fragile operations

### Be specific and actionable

```markdown
# Good
Run `python scripts/validate.py --input {filename}` to check data format.
If validation fails, common issues include:
- Missing required fields (add them to the CSV)
- Invalid date formats (use YYYY-MM-DD)

# Bad
Validate the data before proceeding.
```

### Prevent instructions from being ignored

If Claude loads the skill but doesn't follow instructions:
1. **Too verbose** — Keep instructions concise; use bullet points and numbered lists
2. **Instructions buried** — Put critical instructions at the top; use `## Important` or `## Critical` headers
3. **Ambiguous language** — "Make sure to validate things properly" vs "Before calling create_project, verify: project name is non-empty, at least one team member assigned, start date is not in the past"
4. **Model laziness** — For critical validations, bundle a script rather than relying on language instructions (code is deterministic; language interpretation isn't)

### Match freedom to fragility

**High freedom** (multiple valid approaches):
```markdown
## Code review
1. Analyze code structure
2. Check for bugs or edge cases
3. Suggest readability improvements
```

**Low freedom** (fragile, exact sequence):
```markdown
## Database migration
Run exactly: `python scripts/migrate.py --verify --backup`
Do not modify the command or add flags.
```

### Explain the why, not just the what

Help the model understand reasoning rather than enforcing rigid rules. "We use snake_case because the codebase convention..." is better than "ALWAYS use snake_case."

**Yellow flag**: If you're writing ALWAYS or NEVER in all caps, or using rigid structures, reconsider. Explain the reasoning instead.

## Structural Patterns

### Pattern 1: High-level guide with references
```markdown
# PDF Processing
## Quick start
[Core instructions — essential content only]
## Advanced features
For complete API details, see [reference.md](references/reference.md)
```

### Pattern 2: Workflow with checklist
```markdown
## Deployment workflow
- [ ] Run test suite
- [ ] Build application
- [ ] Deploy to staging
- [ ] Verify deployment
- [ ] Promote to production
```

### Pattern 3: Feedback loop
```markdown
## Edit process
1. Make edits
2. Validate: `python ${CLAUDE_SKILL_DIR}/scripts/validate.py output/`
3. If validation fails, fix issues and validate again
4. Only proceed when validation passes
```

### Pattern 4: Conditional workflow
```markdown
## Determine approach
**Creating new?** Follow "Creation workflow" below
**Editing existing?** Follow "Editing workflow" below
```

### Pattern 5: Visual output generation
Bundle a script that generates interactive HTML (tree views, dependency graphs, reports). The skill orchestrates; the script does the heavy lifting. See [references/patterns.md](references/patterns.md) for a complete example.

## Where Skills Live

| Scope | Path | Applies to |
|-------|------|------------|
| Enterprise | Managed settings | All users in org |
| Personal | `~/.claude/skills/<name>/SKILL.md` | All your projects |
| Project | `.claude/skills/<name>/SKILL.md` | This project only |
| Plugin | `<plugin>/skills/<name>/SKILL.md` | Where plugin is enabled |

Priority: enterprise > personal > project. Plugin skills use `plugin-name:skill-name` namespace.

**Automatic discovery**: Skills in nested `.claude/skills/` directories are discovered when working in subdirectories (supports monorepos). Skills from `--add-dir` directories are also loaded with live change detection.

## Subagent Integration

Use `context: fork` to run a skill in an isolated subagent. The skill content becomes the subagent's task prompt. It won't have conversation history.

```yaml
---
name: deep-research
description: Research a topic thoroughly
context: fork
agent: Explore
---
Research $ARGUMENTS thoroughly:
1. Find relevant files using Glob and Grep
2. Read and analyze the code
3. Summarize findings with file references
```

The `agent` field accepts: `Explore`, `Plan`, `general-purpose`, or any custom subagent from `.claude/agents/`.

**Warning**: `context: fork` only works for skills with explicit tasks. Guidelines-only skills ("use these conventions") produce nothing useful in a subagent.

## Permissions and Restrictions

Control which skills Claude can use:

```text
# In /permissions deny rules:
Skill                    # Deny all skills
Skill(deploy *)          # Deny specific skill
Skill(commit)            # Deny exact match

# Allow rules:
Skill(review-pr *)       # Allow with any args
```

If many skills exceed the description budget (2% of context window, fallback 16,000 chars), run `/context` to check for warnings. Override with `SLASH_COMMAND_TOOL_CHAR_BUDGET` env var.

## Agent Skills Open Standard

Skills follow the [Agent Skills](https://agentskills.io) open standard, supported by 30+ AI tools (Cursor, VS Code Copilot, Gemini CLI, Goose, Roo Code, etc.). Additional standard fields:

| Field | Description |
|-------|-------------|
| `license` | License name or reference to bundled file |
| `compatibility` | Environment requirements (max 500 chars) |
| `metadata` | Arbitrary key-value pairs (author, version) |

The `name` must match the parent directory name per the standard.

## Success Criteria

Define these before building (aspirational targets, not precise benchmarks):

**Quantitative**:
- Skill triggers on 90% of relevant queries (test with 10-20 eval queries)
- Workflow completes in fewer tool calls than without the skill
- 0 failed API/MCP calls per workflow

**Qualitative**:
- Users don't need to prompt Claude about next steps
- Workflows complete without user correction
- Consistent results across sessions
- New users accomplish the task on first try with minimal guidance

## Key Rules

- **References one level deep** — SKILL.md can reference files, but those files should not reference further files
- **Structure long reference files with TOC** — Files over 100 lines need a table of contents
- **Name files descriptively** — `form_validation_rules.md` not `doc2.md`
- **Use forward slashes** — `scripts/helper.py` works everywhere
- **One default approach** — Mention alternatives only when the default won't work
- **Consistent terminology** — Pick one term, stick with it throughout
- **Scripts should solve, not punt** — Handle errors explicitly; document magic numbers
- **No README.md inside skill folder** — All documentation goes in SKILL.md or `references/`. (Use a repo-level README for GitHub distribution only.)
- **Security**: No XML angle brackets (`<` `>`) in frontmatter. No "claude" or "anthropic" in skill name (reserved).

## Naming Conventions

**Prefer gerund form**: `processing-pdfs`, `analyzing-spreadsheets`, `testing-code`

**Acceptable**: `pdf-processing`, `process-pdfs`

**Avoid**: `helper`, `utils`, `tools`, `documents`, `data` (too vague)

**Name must**: be lowercase, hyphens only (no spaces/underscores/capitals), max 64 chars, match folder name, no consecutive hyphens, not start/end with hyphen.

## Checklist

### Before shipping:

**Structure**
- [ ] Valid YAML frontmatter with `name` and `description`
- [ ] `name` matches directory name (lowercase, hyphens, max 64 chars)
- [ ] SKILL.md body under 500 lines
- [ ] Detailed content in separate reference files
- [ ] References one level deep; all referenced files exist

**Description**
- [ ] Third person ("Processes X..." not "Use this to...")
- [ ] Includes specific trigger phrases users would say
- [ ] States what the skill does AND when to use it
- [ ] Under 1024 characters

**Content**
- [ ] Imperative writing style
- [ ] Only adds context Claude doesn't already have
- [ ] Explains the why, not just rigid rules
- [ ] Consistent terminology; no time-sensitive information
- [ ] Forward slashes for all paths

**Testing**
- [ ] Tested with real usage scenarios (with and without skill)
- [ ] Verified triggering works (and doesn't over-trigger)
- [ ] Tested with target models if cross-model support needed

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Never triggers | Add specific trigger phrases matching user language to description |
| Triggers too often | Narrow description; add negative triggers ("Do NOT use for...") or `disable-model-invocation: true` |
| Claude ignores bundled files | Explicitly reference files in SKILL.md with guidance on when to read |
| Instructions not followed | Too verbose (use bullets), buried (put critical info first), or ambiguous (be specific). For critical checks, bundle a validation script |
| Context too large | Move detailed content to `references/`; keep SKILL.md under 500 lines / 5,000 words |
| Skills excluded from context | Check `/context` for warnings; trim descriptions; consider skill "packs" for related capabilities |
| Subagent skill returns nothing | Ensure skill has an explicit task, not just guidelines |
| Skill won't upload | File must be exactly `SKILL.md` (case-sensitive); verify with `ls -la` |
| Invalid frontmatter | Ensure `---` delimiters present; no unclosed quotes; no XML angle brackets |
| MCP calls fail | Test MCP independently first ("Use [Service] MCP to fetch my projects"); verify tool names are case-sensitive and match MCP docs |

### Iteration signals

**Undertriggering** (skill doesn't load when it should, users manually enabling it):
→ Add more detail and trigger keywords to description

**Overtriggering** (skill loads for irrelevant queries, users disabling it):
→ Add negative triggers, be more specific about scope

**Execution issues** (inconsistent results, API call failures, user corrections):
→ Improve instructions, add error handling, bundle validation scripts

## Sources

- [The Complete Guide to Building Skills for Claude](https://anthropic.com) (Anthropic PDF guide)
- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills)
- [Agent Skills Open Standard](https://agentskills.io/specification)
- [Anthropic skill-creator reference](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md)
- For MCP-specific patterns and distribution, see [references/patterns.md](references/patterns.md)
