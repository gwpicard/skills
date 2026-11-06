# Error Analysis

Error analysis is the foundational practice of LLM evaluation. Everything else — assertions, LLM-as-judge, CI pipelines — is built on top of understanding HOW your system fails.

## Minimum Viable Setup

- **Time**: 30 minutes
- **Data**: 20-50 outputs from your system
- **People**: One domain expert (often you)
- **Tool**: Jupyter notebook, spreadsheet, or any way to view traces

That's it. You don't need a framework, a platform, or a team. You need one person looking at outputs.

## The Process: Open Coding → Axial Coding

### Open Coding (Discovery Phase)

1. Pull a random sample of traces (input → output, including intermediate steps if applicable)
2. Review each trace. For EACH one, write free-form notes about the **first failure** you observe
3. Don't use a predefined rubric — let the failure modes emerge from the data
4. Be specific: not "bad response" but "cited a document that wasn't in the retrieved set"

Example notes from a RAG system review:
```
Trace 1: Retrieved correct doc but answer ignored key paragraph
Trace 2: Good answer, passes
Trace 3: Query was ambiguous, retrieved docs for wrong interpretation
Trace 4: Answer fabricated a statistic not in any retrieved doc
Trace 5: Retrieved 3 relevant docs but only used info from first one
```

### Axial Coding (Categorization Phase)

1. Review all your open-coding notes
2. Group them into failure categories (a taxonomy)
3. Count frequency of each category
4. Rank by frequency — the most common failures are your top priority

Example taxonomy from the notes above:
```
Faithfulness violations (fabrication): 1 occurrence
Retrieval relevance (wrong interpretation): 1 occurrence
Incomplete synthesis (ignored relevant info): 2 occurrences
```

### Iterate Until Theoretical Saturation

- Keep reviewing more traces until you stop discovering NEW failure modes
- Typically requires ~100+ traces to reach saturation
- You'll still see failures, but they'll fall into categories you've already identified

## The Benevolent Dictator Model

One domain expert serves as the definitive judge of quality. Not a committee, not a vote — one person who deeply understands what "good" looks like for this specific use case.

Why:
- Eliminates inter-rater reliability problems
- Builds deep intuition about the system's failure modes
- Creates a single source of truth for the LLM-as-judge to align to
- Faster iteration cycles

This person should be doing the annotation themselves, not delegating it.

## Sampling Strategies

How to select which traces to review:

### Random Sampling
Always start here. Gives an unbiased view of system performance.

### Outlier Detection
Sort by response length, latency, token count — look at the extremes.

### User Feedback Signals
If available: thumbs down, repeated queries, abandoned conversations, escalations to human agents.

### Metric-Based Sorting
Once you have automated metrics, review cases near the decision boundary (scores between 0.4-0.6).

### Embedding Clustering
Embed your inputs, cluster them, sample from each cluster to ensure coverage across input types.

### Stratified Sampling
Sample proportionally from different user segments, input categories, or time periods.

## Synthetic Data Generation

When you don't have enough production data:

### Step 1: Define Dimensions
Identify the axes of variation that matter for your use case.

Example for a customer support bot:
- Topic: billing, technical, account, product
- Complexity: simple lookup, multi-step, ambiguous
- Tone: polite, frustrated, confused, terse

### Step 2: Create Tuples Manually
Write ~20 combinations by hand as (dimension1, dimension2, dimension3) tuples:
```
(billing, simple lookup, polite)
(technical, multi-step, frustrated)
(account, ambiguous, confused)
```

### Step 3: LLM-Generate More Tuples
Prompt an LLM to generate more combinations, especially edge cases you might not think of.

### Step 4: Convert to Natural Language (Two-Step)
First generate the tuples, THEN convert each to a natural language query in a separate step. This two-step process avoids the repetitive phrasing you get from single-step generation.

```
Tuple: (billing, multi-step, frustrated)
→ "I've been charged twice for my subscription AGAIN. Last time it took 3 emails to fix. Can someone just refund the duplicate and make sure it doesn't happen next month?"
```

## Cadence

- **Full error analysis cycle**: Every 2-4 weeks when making significant system changes
- **Lightweight review**: 10-20 traces weekly between full cycles
- **After every major change**: Prompt updates, model swaps, architecture changes — always re-check

## N-1 Testing for Multi-Turn Systems

For chatbots and agents with multi-turn conversations:

1. Take a real conversation of N turns
2. Provide the first N-1 turns as context
3. Test what the system produces at turn N
4. Compare against what actually happened (or what should have happened)

This isolates each turn's quality without cascading errors from previous turns affecting your evaluation.
