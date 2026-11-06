---
name: eval-skill
description: >
  Review and evaluate Claude Code skills against best practices. Analyzes SKILL.md files
  for description quality, structure, triggering effectiveness, instruction clarity, and
  adherence to the Agent Skills standard. Use when the user says "review my skill",
  "evaluate this skill", "check my skill", "audit my SKILL.md", "is my skill good",
  or wants feedback on a skill they've written or are improving.
argument-hint: "[skill-path]"
---

# Skill Evaluator

Review a skill against best practices and produce an actionable evaluation report.

## Evaluation Process

### Step 1: Locate and Read the Skill

If `$ARGUMENTS` is provided, read the SKILL.md at that path. Otherwise, ask which skill to evaluate.

Read the full skill directory structure (SKILL.md + any references/, scripts/, examples/, assets/) to understand the complete skill.

### Step 2: Run the Evaluation

Score each dimension below as PASS, WARN, or FAIL with specific evidence and fix suggestions. Do NOT give vague feedback — cite exact lines, quote exact text, and provide rewritten alternatives.

---

## Evaluation Dimensions

### 1. Frontmatter Quality

**name**:
- FAIL if: missing, has spaces/capitals/underscores, exceeds 64 chars, starts/ends with hyphen, has consecutive hyphens, contains "claude" or "anthropic"
- WARN if: doesn't match folder name, uses vague terms (helper, utils, tools)
- Check: name uses kebab-case, gerund form preferred (e.g., `processing-pdfs`)

**description**:
- FAIL if: missing, over 1024 chars, too vague ("Helps with projects"), wrong person ("I can help..." or "Use this to..."), contains XML angle brackets (`<` `>`)
- WARN if: missing trigger phrases, doesn't state WHEN to use it, missing file types if applicable, no key capabilities listed
- Check against formula: `[What it does] + [When to use it] + [Key capabilities]`
- Check: uses third person, includes specific user phrases, is "pushy" about activation contexts

**Other fields**:
- Check `disable-model-invocation` appropriateness (should be `true` for side-effect workflows like deploy, commit)
- Check `context: fork` has an explicit task in the body (not just guidelines)
- Check `allowed-tools` is minimal and appropriate

### 2. Structure and Organization

- FAIL if: SKILL.md exceeds 500 lines or ~5,000 words
- FAIL if: no SKILL.md file exists, or file is named incorrectly (skill.md, SKILL.MD)
- WARN if: detailed reference content is inlined instead of in `references/`
- WARN if: references go more than one level deep (SKILL.md → ref → another ref)
- WARN if: referenced files don't exist
- WARN if: README.md exists inside the skill folder (docs go in SKILL.md or references/)
- Check: reference files over 100 lines have a table of contents
- Check: files are descriptively named (`form_validation_rules.md` not `doc2.md`)
- Check: forward slashes used for all paths

### 3. Description Trigger Effectiveness

Generate 10 test queries (5 should-trigger, 5 should-not-trigger) based on the skill's stated purpose. The should-not-trigger queries must be **near-misses** — adjacent domains sharing keywords.

For each query, assess: would this description cause the skill to trigger appropriately?

Report:
- Estimated trigger accuracy
- False positive risks (queries that would incorrectly trigger)
- False negative risks (queries that should trigger but won't)
- Suggested description rewrites if accuracy is below 80%

### 4. Instruction Quality

**Clarity**:
- FAIL if: instructions are vague ("validate things properly", "make sure it works")
- WARN if: uses second person ("You should...") instead of imperative ("Configure...")
- WARN if: explains things Claude already knows (what git is, how Python works, basic library usage)
- Check: critical instructions are near the top, not buried

**Specificity**:
- WARN if: steps lack concrete commands, file paths, or expected outputs
- WARN if: error handling is missing for fragile operations
- Check: scripts are referenced with `${CLAUDE_SKILL_DIR}` for portability

**Freedom-to-fragility match**:
- WARN if: fragile operations (deployments, database changes, API calls with side effects) use vague guidance instead of exact scripts
- WARN if: flexible tasks (code review, analysis) are over-constrained with rigid rules
- Check: ALWAYS/NEVER in all caps is a yellow flag — reasoning should be explained instead

**Actionability**:
- WARN if: instructions say what to check but not what to DO about failures
- Good: "If validation fails, common issues include: missing fields (add them), invalid dates (use YYYY-MM-DD)"
- Bad: "Validate the data before proceeding"

### 5. Progressive Disclosure

- WARN if: all content is in SKILL.md with no supporting files for a complex skill
- WARN if: SKILL.md duplicates content from reference files
- Check: information lives in SKILL.md OR references, never both
- Check: SKILL.md references supporting files with guidance on WHEN to read them

### 6. Composability and Consistency

- WARN if: skill assumes it's the only capability available
- WARN if: terminology is inconsistent (alternating between "endpoint", "route", "URL", "path")
- WARN if: contains time-sensitive information ("If before August 2025...")
- Check: skill works alongside other skills without conflicts

### 7. Skill Category Fit

Identify the category and check category-specific best practices:

**Document & Asset Creation**: Does it have embedded style guides? Templates? Quality checklists?
**Workflow Automation**: Does it have step-by-step validation gates? Iterative refinement loops?
**MCP Enhancement**: Does it coordinate MCP calls? Embed domain expertise? Handle MCP errors?

---

## Step 3: Generate the Report

Output the evaluation in this format:

```
## Skill Evaluation: [skill-name]

### Summary
Overall: [PASS / NEEDS WORK / MAJOR ISSUES]
Category: [Document & Asset Creation / Workflow Automation / MCP Enhancement / Reference / Hybrid]

### Scorecard
| Dimension | Score | Key Issue |
|-----------|-------|-----------|
| Frontmatter | PASS/WARN/FAIL | [one-line summary] |
| Structure | PASS/WARN/FAIL | [one-line summary] |
| Trigger Effectiveness | PASS/WARN/FAIL | [one-line summary] |
| Instruction Quality | PASS/WARN/FAIL | [one-line summary] |
| Progressive Disclosure | PASS/WARN/FAIL | [one-line summary] |
| Composability | PASS/WARN/FAIL | [one-line summary] |

### Trigger Test Results
[Table of 10 test queries with expected vs predicted trigger behavior]

### Critical Fixes (FAIL items)
[Numbered list with exact rewrites]

### Recommended Improvements (WARN items)
[Numbered list with specific suggestions]

### What's Working Well
[List of strengths]
```

## Step 4: Offer to Fix

After presenting the report, ask if the user wants you to apply the critical fixes and recommended improvements directly to the skill files.

If yes, make the edits. Then re-run the evaluation on the updated skill to confirm improvements.
