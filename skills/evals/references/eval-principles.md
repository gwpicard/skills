# Eval Principles

## Why Evals Matter

The #1 reason LLM products fail is lack of evals. Teams iterate on prompts, swap models, change architectures — all without measuring whether things actually got better. This creates a cycle of whack-a-mole prompt engineering where fixing one thing breaks another.

## The Virtuous Flywheel

The core loop that makes LLM products improve:

```
Evaluate → Debug (error analysis) → Change behavior → Evaluate again
```

Every improvement must be measurable. If you can't measure it, you can't improve it. Evals aren't a separate phase — they ARE development.

## Remove ALL Friction From Looking at Data

This is the single most impactful principle. If it takes more than 30 seconds to look at what your system is producing, fix that first. Before writing a single eval, build the ability to:
- See inputs and outputs side by side
- Filter by quality signals
- Annotate with one click

The best eval investment is often a simple Gradio/Streamlit app that shows traces to a domain expert.

## Three Maturity Levels

### Level 1: Unit Tests / Assertions
**When**: From day one. Every project, no exceptions.
**What**:
- Assertion-based checks: format validation, required fields, no PII leaks, schema compliance
- Synthetic test cases covering key feature × scenario combinations
- Deterministic where possible — run on every code change
- Acceptable pass rate is a product decision (not always 100%)

**Key insight**: These catch regressions and obvious failures. They don't tell you if your system is "good" — they tell you it's not broken.

### Level 2: Human Eval + LLM-as-Judge
**When**: Once you have production traffic or enough synthetic data to analyze.
**What**:
- Trace logging — capture every input/output/intermediate step
- Domain expert reviews traces, applies binary pass/fail labels with written critiques
- Build an LLM-as-judge that replicates the domain expert's judgment
- Align the judge: create spreadsheet comparing judge vs human on 25-50 examples
- Measure True Positive Rate and True Negative Rate (not raw agreement)
- Start with the most capable model as judge, optimize cost later

**Key insight**: The domain expert IS the eval. The LLM-as-judge is an automation of the domain expert. If it disagrees with the expert, the judge is wrong.

### Level 3: A/B Testing
**When**: Only after product maturity — you need statistical significance and real user behavior.
**What**:
- Online experiments with real users
- Business metrics (retention, completion, satisfaction)
- Requires large sample sizes and careful experiment design

**Key insight**: Most teams should not be here yet. Get Level 1 and 2 right first.

## Anti-Patterns

### Whack-a-mole prompt engineering
Changing prompts based on individual failures without tracking whether the change helped overall. Feels productive, isn't.

### Generic eval frameworks / ready-to-use metrics
Off-the-shelf metrics (BLEU, ROUGE, generic "helpfulness" scores) give false confidence. Your eval dimensions must come from YOUR data and YOUR domain expert's understanding of quality.

### Likert scales (1-5 ratings)
Unreliable, inconsistent, and hard to act on. Use binary pass/fail with a written critique explaining why something failed. This forces clarity about what "good" means.

### Eval-driven development
Trying to anticipate every failure mode upfront and writing evals for them. You can't — the failure surface is infinite. Instead: deploy → observe failures → write evals for what actually breaks.

### Outsourcing annotation to non-experts
Labeling data is how you build understanding of your system. If the person labeling isn't the person who understands the domain, you lose the feedback loop that makes everything work.

### Buying tools before looking at data
Every eval tool vendor wants to sell you a dashboard. You don't need a dashboard — you need to look at 50 outputs in a spreadsheet. Buy tools only after you've outgrown spreadsheets.

## Evals ARE Development

Expect to spend 60-80% of your development time on error analysis and eval iteration. This isn't overhead — this IS the work. The quality of your LLM product is directly proportional to how much time you spend looking at what it produces.
