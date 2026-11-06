# Eval Implementations

Concrete implementation patterns with code examples.

---

## Level 1: Assertion-Based Tests

### Python pytest Pattern

```python
import pytest
import json
from your_system import generate_response

# --- Format & Structure Checks ---

def test_response_is_valid_json():
    """Verify output parses as valid JSON when JSON is expected."""
    response = generate_response("List the top 3 features")
    parsed = json.loads(response)  # Fails if not valid JSON
    assert isinstance(parsed, dict)

def test_no_pii_leaked():
    """Check that PII patterns don't appear in output."""
    import re
    response = generate_response("Summarize the customer's issue")
    # SSN pattern
    assert not re.search(r'\b\d{3}-\d{2}-\d{4}\b', response)
    # Email (shouldn't leak customer emails)
    assert not re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', response)

def test_no_internal_ids_leaked():
    """Ensure internal UUIDs/IDs don't appear in user-facing output."""
    import re
    response = generate_response("What's the status of my order?")
    assert not re.search(
        r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
        response
    )

def test_response_length_reasonable():
    """Guard against degenerate outputs (empty or absurdly long)."""
    response = generate_response("Explain our return policy")
    assert 50 < len(response) < 5000

# --- Schema Validation ---

def test_structured_output_schema():
    """Validate structured output matches expected schema."""
    from jsonschema import validate
    schema = {
        "type": "object",
        "required": ["answer", "sources"],
        "properties": {
            "answer": {"type": "string", "minLength": 1},
            "sources": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 1
            }
        }
    }
    response = generate_response("What is our refund policy?")
    parsed = json.loads(response)
    validate(instance=parsed, schema=schema)

# --- Feature x Scenario Matrix ---

TOPICS = ["billing", "technical_support", "account_management"]
COMPLEXITIES = ["simple", "multi_step"]
TONES = ["polite", "frustrated"]

@pytest.mark.parametrize("topic", TOPICS)
@pytest.mark.parametrize("complexity", COMPLEXITIES)
def test_handles_topic_and_complexity(topic, complexity, test_cases):
    """Test across feature dimensions."""
    query = test_cases[topic][complexity]  # Load from fixtures
    response = generate_response(query)
    assert len(response) > 0
    assert "error" not in response.lower()
    # Add domain-specific assertions per topic
    if topic == "billing":
        assert any(term in response.lower() for term in ["invoice", "charge", "payment", "refund"])
```

### TypeScript / Vitest Pattern

```typescript
import { describe, it, expect } from 'vitest'
import { generateResponse } from './your-system'

describe('LLM Output Validation', () => {
  it('returns valid JSON when expected', async () => {
    const response = await generateResponse('List the top 3 features')
    const parsed = JSON.parse(response)
    expect(parsed).toBeDefined()
    expect(typeof parsed).toBe('object')
  })

  it('does not leak PII', async () => {
    const response = await generateResponse("Summarize the customer's issue")
    expect(response).not.toMatch(/\b\d{3}-\d{2}-\d{4}\b/) // SSN
    expect(response).not.toMatch(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/) // Email
  })

  it('stays within reasonable length', async () => {
    const response = await generateResponse('Explain our return policy')
    expect(response.length).toBeGreaterThan(50)
    expect(response.length).toBeLessThan(5000)
  })
})
```

### Acceptable Pass Rates

Not every eval needs 100% pass rate. This is a **product decision**:
- Format/schema compliance: 100% (non-negotiable)
- PII/safety checks: 100% (non-negotiable)
- Task completion on synthetic data: 85-95% is often acceptable to start
- Edge case handling: Track and improve over time, set realistic baselines

### Synthetic Test Case Generation Prompt

```
You are generating test cases for a {system_description}.

Create {count} test cases covering these dimensions:
- Topics: {topics}
- Complexity levels: {complexity_levels}
- Edge cases: {edge_cases}

For each test case, provide:
1. Input query
2. Expected behavior (what a good response should do)
3. What would make a response fail

Format as JSON array.
```

---

## Level 2: LLM-as-Judge

### Binary Pass/Fail Judge Prompt

```
You are evaluating the quality of an AI system's response.

## Task Context
{task_description}

## Input
{user_input}

## System Output
{system_output}

## Additional Context (if applicable)
{retrieved_documents_or_conversation_history}

## Evaluation Criteria
{specific_criteria_for_this_eval_dimension}

## Instructions
Evaluate whether the system output PASSES or FAILS based on the criteria above.

First, write a brief critique (2-3 sentences) explaining your reasoning.
Then, on a new line, write exactly one of: PASS or FAIL

Critique:
```

### Dimension-Specific Judge Examples

**Faithfulness (RAG):**
```
## Evaluation Criteria
The response must ONLY contain information that is directly supported by the retrieved documents.
A response FAILS if it:
- States any fact not present in the retrieved documents
- Makes claims that go beyond what the documents support
- Invents statistics, dates, or details not in the source material

A response PASSES if every claim it makes can be traced to the retrieved documents,
even if it doesn't cover everything in the documents.
```

**Task Completion (Chatbot):**
```
## Evaluation Criteria
The conversation should result in the user's goal being achieved.
A conversation FAILS if:
- The user's core question was not answered
- The user was given incorrect information
- The conversation ended without resolution and without appropriate escalation

A conversation PASSES if the user's primary goal was addressed,
even if the conversation took extra turns or included minor imperfections.
```

### The Alignment Process ("Phillip Spreadsheet")

1. **Collect 25-50 traces** with diverse outcomes (mix of good and bad)
2. **Domain expert labels each** as PASS or FAIL with a written critique
3. **Run the LLM-as-judge** on the same traces
4. **Create a comparison spreadsheet**:

| Trace | Human Label | Human Critique | Judge Label | Judge Critique | Agreement |
|-------|-------------|----------------|-------------|----------------|-----------|
| 1     | PASS        | Clear, complete | PASS       | Accurate...     | Yes       |
| 2     | FAIL        | Fabricated stat | PASS       | Seems correct   | **No**    |
| 3     | FAIL        | Wrong topic     | FAIL       | Off-topic       | Yes       |

5. **Calculate True Positive Rate and True Negative Rate** (not raw agreement):
   - TPR = (judge correctly identifies PASS) / (total human PASS)
   - TNR = (judge correctly identifies FAIL) / (total human FAIL)
   - Both should be >80% before deploying the judge
6. **Iterate on the judge prompt** using the disagreement cases
7. **Re-run alignment** after any judge prompt changes

### Key Rules for LLM-as-Judge
- **Start with the most capable model** (Claude Opus, GPT-4o). Optimize cost later.
- **Only invest in LLM-as-judge for persistent failure categories** you iterate on repeatedly. Don't build a judge for a one-time analysis.
- **Weekly maintenance required.** As your system improves, failure modes shift. The judge prompt may need updates.
- **Never trust the judge blindly.** Periodically spot-check judge decisions against expert opinion.

---

## Guardrails vs. Evaluators

Two distinct patterns — don't conflate them:

### Guardrails (Inline, Synchronous)
- Run BEFORE or AFTER generation, in the response path
- Must be fast and deterministic
- Block or modify responses that violate rules
- Examples: regex for PII, keyword blocklists, JSON schema validation, token length limits
- Implementation: middleware in your generation pipeline

### Evaluators (Async, Post-Generation)
- Run AFTER generation, outside the response path
- Can be slow and expensive (LLM calls are fine)
- Feed dashboards and monitoring, don't block responses
- Examples: LLM-as-judge for faithfulness, coherence scoring, task completion checks
- Implementation: background job processing logged traces

```python
# Guardrail example (inline)
def guardrail_no_pii(response: str) -> str:
    """Strip PII before returning to user."""
    import re
    response = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN REDACTED]', response)
    return response

# Evaluator example (async)
async def evaluate_faithfulness(trace: dict) -> dict:
    """Run async after response is sent. Log result for monitoring."""
    judge_prompt = build_faithfulness_prompt(
        context=trace["retrieved_docs"],
        response=trace["response"]
    )
    result = await llm_judge(judge_prompt)
    log_eval_result(trace_id=trace["id"], dimension="faithfulness", result=result)
    return result
```

---

## CI/CD Integration

### CI Datasets
- **Size**: 100+ test cases minimum
- **Composition**: Purpose-built from error analysis findings. Each test case targets a known failure mode.
- **Checks**: Deterministic assertions (Level 1). LLM-as-judge only for critical dimensions with aligned judges.
- **Trigger**: Run on every PR / commit that touches prompts, models, or generation logic.

### CI Pipeline Example

```yaml
# .github/workflows/evals.yml
name: LLM Evals
on:
  pull_request:
    paths:
      - 'prompts/**'
      - 'src/generation/**'
      - 'src/retrieval/**'
      - 'evals/**'

jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements-eval.txt
      - run: pytest evals/ -v --tb=short --junitxml=eval-results.xml
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: eval-results
          path: eval-results.xml
```

### Production Eval Loop
1. **Log all traces** in production (input, output, intermediate steps, metadata)
2. **Sample traces** for async evaluation (random + signal-based sampling)
3. **Run evaluators** as background jobs on sampled traces
4. **Track metrics over time** with confidence intervals
5. **Production failures feed back into CI datasets** — when you find a new failure mode in prod, add it as a test case

```python
# Production sampling and async eval
import random

async def maybe_evaluate(trace: dict):
    """Sample and evaluate production traces."""
    # 10% random sample
    if random.random() < 0.10:
        await evaluate_faithfulness(trace)
        await evaluate_relevance(trace)

    # Always evaluate traces with negative user signals
    if trace.get("user_feedback") == "negative":
        await evaluate_all_dimensions(trace)
```

---

## Custom Annotation Tools

**This is often the most impactful eval investment.** A simple tool that lets a domain expert review and label system outputs.

### Minimal Gradio Annotation App

```python
import gradio as gr
import json
from pathlib import Path

# Load traces to annotate
traces = json.loads(Path("traces.json").read_text())
annotations = {}
current_idx = 0

def show_trace(idx):
    trace = traces[idx]
    return (
        f"**Input:** {trace['input']}",
        f"**Output:** {trace['output']}",
        f"**Context:** {trace.get('context', 'N/A')}",
        f"Trace {idx + 1} of {len(traces)}"
    )

def annotate(label, critique, idx):
    annotations[traces[idx]["id"]] = {
        "label": label,
        "critique": critique,
        "trace_id": traces[idx]["id"]
    }
    Path("annotations.json").write_text(json.dumps(annotations, indent=2))
    next_idx = min(idx + 1, len(traces) - 1)
    return (*show_trace(next_idx), next_idx, "")

with gr.Blocks() as app:
    idx_state = gr.State(0)
    gr.Markdown("# Trace Annotation Tool")

    with gr.Row():
        input_display = gr.Markdown()
        output_display = gr.Markdown()

    context_display = gr.Markdown()
    progress = gr.Markdown()

    critique = gr.Textbox(label="Critique (why pass/fail?)", lines=3)

    with gr.Row():
        pass_btn = gr.Button("PASS", variant="primary")
        fail_btn = gr.Button("FAIL", variant="stop")

    pass_btn.click(
        fn=lambda c, i: annotate("PASS", c, i),
        inputs=[critique, idx_state],
        outputs=[input_display, output_display, context_display, progress, idx_state, critique]
    )
    fail_btn.click(
        fn=lambda c, i: annotate("FAIL", c, i),
        inputs=[critique, idx_state],
        outputs=[input_display, output_display, context_display, progress, idx_state, critique]
    )

    app.load(fn=lambda: (*show_trace(0), 0), outputs=[input_display, output_display, context_display, progress, idx_state])

app.launch()
```

### What Makes Annotation Tools Effective
- **Show the full trace** — input, output, intermediate steps, retrieved documents — all visible at once
- **Binary labels** with a required free-text critique field
- **One-click labeling** — minimize friction, maximize throughput
- **Progress indicator** — domain experts should know how many are left
- **Export to JSON/CSV** — feed directly into judge alignment spreadsheets
- **Don't over-build** — a working tool today beats a perfect tool next month
