# Advanced Skill Patterns Reference

Detailed patterns and examples for skill authoring. Referenced from SKILL.md.

## Table of Contents

- [Skills + MCP Relationship](#skills--mcp-relationship)
- [MCP Workflow Patterns](#mcp-workflow-patterns)
- [Visual Output Generation](#visual-output-generation)
- [Before/After Examples](#beforeafter-examples)
- [Anti-patterns](#anti-patterns)
- [Evaluation Workflow](#evaluation-workflow)
- [Description Optimization](#description-optimization)
- [Distribution and Sharing](#distribution-and-sharing)
- [Cross-Platform Compatibility](#cross-platform-compatibility)

## Skills + MCP Relationship

**The kitchen analogy**: MCP provides the professional kitchen (tools, ingredients, equipment). Skills provide the recipes (step-by-step instructions on how to create something valuable).

| MCP (Connectivity) | Skills (Knowledge) |
|---|---|
| Connects Claude to your service (Notion, Asana, Linear, etc.) | Teaches Claude how to use your service effectively |
| Provides real-time data access and tool invocation | Captures workflows and best practices |
| What Claude *can* do | How Claude *should* do it |

**Without skills**: Users connect MCP but don't know what to do next; each conversation starts from scratch; inconsistent results because users prompt differently.

**With skills**: Pre-built workflows activate automatically; consistent, reliable tool usage; best practices embedded in every interaction.

## MCP Workflow Patterns

### Pattern: Sequential workflow orchestration
**Use when**: Multi-step processes in a specific order.

```markdown
## Workflow: Onboard New Customer
### Step 1: Create Account
Call MCP tool: `create_customer`
Parameters: name, email, company
### Step 2: Setup Payment
Call MCP tool: `setup_payment_method`
Wait for: payment method verification
### Step 3: Create Subscription
Call MCP tool: `create_subscription`
Parameters: plan_id, customer_id (from Step 1)
### Step 4: Send Welcome Email
Call MCP tool: `send_email`
Template: welcome_email_template
```

Key techniques: explicit step ordering, dependencies between steps, validation at each stage, rollback instructions for failures.

### Pattern: Multi-MCP coordination
**Use when**: Workflows span multiple services.

```markdown
### Phase 1: Design Export (Figma MCP)
1. Export design assets from Figma
2. Generate design specifications
3. Create asset manifest
### Phase 2: Asset Storage (Drive MCP)
1. Create project folder in Drive
2. Upload all assets
3. Generate shareable links
### Phase 3: Task Creation (Linear MCP)
1. Create development tasks
2. Attach asset links to tasks
3. Assign to engineering team
### Phase 4: Notification (Slack MCP)
1. Post handoff summary to #engineering
2. Include asset links and task references
```

Key techniques: clear phase separation, data passing between MCPs, validation before moving to next phase.

### Pattern: Iterative refinement
**Use when**: Output quality improves with iteration.

```markdown
## Iterative Report Creation
### Initial Draft
1. Fetch data via MCP
2. Generate first draft report
3. Save to temporary file
### Quality Check
1. Run validation script: `scripts/check_report.py`
2. Identify issues (missing sections, formatting, data errors)
### Refinement Loop
1. Address each identified issue
2. Regenerate affected sections
3. Re-validate
4. Repeat until quality threshold met
### Finalization
1. Apply final formatting
2. Generate summary
3. Save final version
```

### Pattern: Context-aware tool selection
**Use when**: Same outcome, different tools depending on context.

```markdown
## Smart File Storage
### Decision Tree
1. Check file type and size
2. Determine best storage location:
   - Large files (>10MB): Use cloud storage MCP
   - Collaborative docs: Use Notion/Docs MCP
   - Code files: Use GitHub MCP
   - Temporary files: Use local storage
### Execute Storage
Based on decision:
- Call appropriate MCP tool
- Apply service-specific metadata
- Generate access link
### Provide Context to User
Explain why that storage was chosen
```

### Pattern: Domain-specific intelligence
**Use when**: Skill adds specialized knowledge beyond tool access.

```markdown
## Payment Processing with Compliance
### Before Processing (Compliance Check)
1. Fetch transaction details via MCP
2. Apply compliance rules:
   - Check sanctions lists
   - Verify jurisdiction allowances
   - Assess risk level
3. Document compliance decision
### Processing
IF compliance passed:
  - Call payment processing MCP tool
  - Apply appropriate fraud checks
  - Process transaction
ELSE:
  - Flag for review
  - Create compliance case
### Audit Trail
- Log all compliance checks
- Record processing decisions
- Generate audit report
```

## Visual Output Generation

Bundle a script that generates interactive HTML. The skill orchestrates; the script does the heavy lifting.

### Structure

```
codebase-visualizer/
├── SKILL.md
└── scripts/
    └── visualize.py
```

### SKILL.md

```yaml
---
name: codebase-visualizer
description: >
  Generate an interactive collapsible tree visualization of your codebase.
  Use when exploring a new repo, understanding project structure, or identifying large files.
allowed-tools: Bash(python *)
---

# Codebase Visualizer

Run the visualization script from the project root:

```bash
python ${CLAUDE_SKILL_DIR}/scripts/visualize.py .
```

This creates `codebase-map.html` and opens it in the browser.
```

The script scans the directory tree and generates a self-contained HTML file with collapsible directories, file sizes, and color-coded file types. It uses only Python built-in libraries.

This pattern works for: dependency graphs, test coverage reports, API docs, database schema visualizations.

## Before/After Examples

### Example 1: Vague skill made specific

**Before (bad)**:
```yaml
---
name: code-helper
description: Helps with code tasks
---
Help the user with their code. Be helpful and thorough.
```

Problems: vague name, vague description, no actual instructions, tells Claude what it already does.

**After (good)**:
```yaml
---
name: api-endpoint-review
description: >
  Review API endpoints for security, performance, and consistency with project conventions.
  Use when reviewing REST endpoints, API routes, or when the user asks to check an API.
---

# API Endpoint Review

When reviewing an API endpoint, check:

## Security
- Input validation on all parameters
- Authentication/authorization middleware applied
- No SQL injection or XSS vectors
- Rate limiting configured

## Performance
- Database queries use indexes (check schema)
- N+1 query patterns avoided
- Response pagination for list endpoints
- Appropriate caching headers

## Conventions
- Route follows `kebab-case` naming: `/api/v1/user-profiles`
- Response shape matches project standard: `{ data, meta, errors }`
- Error codes from `references/error-codes.md`

Read the endpoint handler, its tests, and the route configuration before reviewing.
```

### Example 2: Over-engineered skill simplified

**Before (too much)**:
```yaml
---
name: git-commit
description: Creates git commits
disable-model-invocation: true
---

# Git Commit Skill

## Prerequisites
- Ensure git is installed on your system
- Ensure you are in a git repository
- Ensure there are staged changes

## What is a commit?
A commit is a snapshot of your changes...

## Commit Message Format
### Header
The header should be...
### Body
The body should explain...
### Footer
The footer can reference...

## Step-by-step Process
1. First, check if git is installed by running `git --version`
2. Then check if you're in a repository...
[continues for 200 more lines]
```

Problems: explains what Claude already knows (git basics), too many prerequisites Claude handles naturally, 200+ lines for a simple task.

**After (right-sized)**:
```yaml
---
name: commit
description: Create a well-structured git commit following project conventions
disable-model-invocation: true
---

# Commit

Format: `<type>(<scope>): <description>`

Types: feat, fix, docs, refactor, test, chore
Scope: the module or area changed

1. Run `git diff --cached` to review staged changes
2. Write a commit message summarizing the actual changes (not the intent)
3. Body: explain WHY, not WHAT (the diff shows what)
4. Commit with `git commit`
```

## Anti-patterns

### 1. The Kitchen Sink
Cramming everything into SKILL.md instead of using references.

**Fix**: Keep SKILL.md to core workflow. Move API docs, schemas, and edge cases to `references/`.

### 2. The Parrot
Restating information Claude already has (library docs, language basics, common patterns).

**Fix**: Test without the skill first. Only add instructions for gaps.

### 3. The Drill Sergeant
All caps ALWAYS/NEVER rules with no explanation.

**Fix**: Explain reasoning. "Use snake_case because the existing codebase uses it consistently" > "ALWAYS use snake_case."

### 4. The Oracle
A skill that tries to handle every possible scenario with complex branching.

**Fix**: Handle the common case well. Let Claude's reasoning handle edge cases. Add guardrails only for genuinely fragile operations.

### 5. The Ghost
A skill with `context: fork` that contains only guidelines and no actionable task.

**Fix**: Forked skills need explicit tasks. For guidelines, use a regular skill that runs inline.

### 6. The Overreacher
A description so broad it triggers on unrelated requests.

**Fix**: Test with 10 should-not-trigger queries, especially near-misses from adjacent domains.

## Evaluation Workflow

### Step 1: Baseline
Run Claude on 3+ representative tasks WITHOUT the skill. Document what goes wrong.

### Step 2: Test scenarios
Create prompts that expose the documented failures:

```json
{
  "skill_name": "my-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "Realistic user request with specific details",
      "expected_output": "What success looks like",
      "files": ["any files needed for context"]
    }
  ]
}
```

### Step 3: Compare
Run the same prompts WITH the skill. Compare:
- Did the failure modes improve?
- Did any new problems appear?
- Is the output quality consistently better?

### Step 4: Iterate
- Read transcripts to find where the skill's instructions helped or were ignored
- Remove sections that aren't pulling their weight
- Add detail only where Claude still fails

### Step 5: Cross-model testing
If targeting multiple models, test with each. What works for Opus may need more detail for Haiku.

## Description Optimization

### Crafting eval queries

Create 20 queries: 10 should-trigger, 10 should-not-trigger.

**Good should-trigger queries** are realistic and substantive:
```
"I need to review the API endpoint in src/routes/users.ts — check for security issues and make sure it follows our patterns"
```

**Good should-NOT-trigger queries** are near-misses:
```
"Help me write a new API endpoint for user profiles"  # Creating, not reviewing
"Check my React component for accessibility issues"    # Different domain, similar "review" keyword
```

**Bad eval queries** (avoid):
```
"Review API"              # Too abstract — no real user talks like this
"Do something unrelated"  # Obviously won't trigger — not a useful test
```

### Iteration process
1. Run eval queries against the description
2. Check for false positives and false negatives
3. Adjust trigger phrases — be more specific where it over-triggers, add keywords where it under-triggers
4. Re-run and compare

## Distribution and Sharing

### How users get skills

1. Download the skill folder
2. Zip the folder (if needed)
3. Upload to Claude.ai via Settings > Capabilities > Skills
4. Or place in Claude Code skills directory (`~/.claude/skills/` or `.claude/skills/`)

### Organization-level deployment

Admins can deploy skills workspace-wide via managed settings. Provides automatic updates and centralized management.

### Using skills via API

For programmatic use cases (building applications, agents, automated workflows):

- `/v1/skills` endpoint for listing and managing skills
- Add skills to Messages API requests via the `container.skills` parameter
- Version control and management through the Claude Console
- Works with the Claude Agent SDK for building custom agents

| Use Case | Best Surface |
|---|---|
| End users interacting directly | Claude.ai / Claude Code |
| Manual testing and iteration | Claude.ai / Claude Code |
| Applications using skills programmatically | API |
| Production deployments at scale | API |
| Automated pipelines and agent systems | API |

### Positioning your skill

Focus on outcomes, not features when describing your skill:

```
# Good — outcome-focused
"The ProjectHub skill enables teams to set up complete project
workspaces in seconds — including pages, databases, and templates
— instead of spending 30 minutes on manual setup."

# Bad — implementation-focused
"The ProjectHub skill is a folder containing YAML frontmatter
and Markdown instructions that calls our MCP server tools."
```

### Highlight the MCP + skills story

```
"Our MCP server gives Claude access to your Linear projects.
Our skills teach Claude your team's sprint planning workflow.
Together, they enable AI-powered project management."
```

### Hosting on GitHub

1. Public repo with clear README (installation instructions, example usage, screenshots)
2. Link to skills from MCP documentation — explain the value of using both together
3. Create an installation guide:
   ```
   ## Installing the [Your Service] skill
   1. Download the skill: Clone repo or download ZIP from Releases
   2. Install in Claude: Open Claude.ai > Settings > skills, Upload skill
   3. Enable the skill: Toggle on [Your Service] skill; ensure MCP server is connected
   4. Test: Ask Claude "Set up a new project in [Your Service]"
   ```

## Cross-Platform Compatibility

Skills follow the [Agent Skills open standard](https://agentskills.io). For maximum portability:

### Standard fields (work everywhere)
- `name`, `description` — required by all implementations
- `license`, `compatibility`, `metadata` — optional standard fields

### Claude Code extensions (Claude Code only)
- `disable-model-invocation`, `user-invocable` — invocation control
- `allowed-tools` — tool auto-approval
- `model` — model override
- `context`, `agent` — subagent execution
- `hooks` — lifecycle hooks
- `argument-hint` — autocomplete hints
- String substitutions (`$ARGUMENTS`, `${CLAUDE_SKILL_DIR}`, etc.)
- Dynamic context injection (`!` backtick syntax)

### Portability tips
- Keep core instructions in standard markdown that any agent can follow
- Put Claude Code-specific features (subagent execution, hooks) behind clear context
- Use the `compatibility` field if your skill requires specific tools or environments
- Test with multiple agent products if distributing publicly
