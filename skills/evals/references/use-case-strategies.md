# Use Case Strategies

Eval dimensions, approaches, metrics, and common failure modes for each use case type.

---

## RAG Pipelines

### Key Eval Dimensions (The RAG Triad)
1. **Context Relevance** — Did the retriever find relevant information?
2. **Groundedness / Faithfulness** — Does the response stick to retrieved facts? No fabrication?
3. **Answer Relevance** — Does the answer actually address the user's question?

### Recommended Approach
- **Evaluate retriever and generator independently.** A faithful answer from irrelevant documents is still wrong. A relevant document with a hallucinated answer is also wrong. Separate the failure modes.
- **Debug retrieval first, then generation.** If retrieval is broken, nothing downstream can save it.
- **Chunk size is a hyperparameter.** Large chunks for fixed-output tasks (extraction, classification). Small chunks for expansive tasks (research, synthesis). Test this empirically.

### Specific Metrics
- **Retriever**: Recall@k, Precision@k, MRR (Mean Reciprocal Rank)
- **Generator**: Faithfulness (binary — did it fabricate?), completeness (did it use all relevant info?), answer relevance (binary — does it answer the question?)

### Common Failure Modes
- Retriever returns tangentially related documents (keyword overlap but wrong topic)
- Generator ignores relevant retrieved content (especially when multiple docs are retrieved)
- Generator fabricates details not present in any retrieved document
- Query ambiguity leads to retrieving documents for the wrong interpretation
- Outdated documents retrieved when fresher information exists

### Synthetic Data
Create query-document pairs from your corpus:
1. Take a document chunk
2. Generate questions that SHOULD be answerable from that chunk
3. Generate questions that are SIMILAR but NOT answerable from that chunk
4. Use both as test cases for retrieval and generation

---

## Chatbots / Conversational AI

### Key Eval Dimensions
1. **Response Quality** — Is each individual response helpful and accurate?
2. **Conversation Coherence** — Does the conversation flow logically across turns?
3. **Persona Consistency** — Does the bot maintain its defined character/role?
4. **Safety** — Does it refuse appropriately? Does it avoid harmful content?
5. **Resolution Rate** — Does the conversation reach a successful outcome?
6. **Escalation Appropriateness** — Does it hand off to humans at the right time?

### Recommended Approach
- **Evaluate whole-conversation goal completion (pass/fail).** Not individual messages in isolation.
- **Focus on the first upstream failure.** In multi-turn conversations, downstream errors cascade. Find where things first went wrong.
- **Use N-1 testing** for isolating individual turn quality (see error-analysis.md).
- **Simulate users with LLMs** for synthetic multi-turn conversations.

### Specific Metrics
- Task completion rate (binary per conversation)
- Average turns to resolution
- Escalation rate (and appropriateness of each escalation)
- Safety violation rate
- Per-turn: response relevance (binary), persona adherence (binary)

### Common Failure Modes
- Losing context from earlier in the conversation
- Repeating information the user already provided
- Failing to ask clarifying questions when the request is ambiguous
- Breaking character or persona inconsistency
- Providing correct information but in a tone that doesn't match the brand
- Not knowing when to escalate vs. when to keep trying

---

## Agents / Tool Use

### Key Eval Dimensions

**Phase 1: End-to-End (Black Box)**
- Did the agent complete the task? (binary pass/fail)
- Was the result correct?
- How many steps / tokens / dollars did it take?

**Phase 2: Step-Level (Glass Box)**
- **Tool Selection Accuracy** — Did it pick the right tool at each step?
- **Parameter Extraction** — Did it pass correct parameters to tools?
- **Error Recovery** — When a tool call failed, did it recover gracefully?
- **Context Retention** — Did it maintain relevant information across steps?
- **Efficiency** — Did it take unnecessary steps or redundant tool calls?

### Recommended Approach
- **Start with end-to-end task success.** Does the agent complete the task? This is the only metric that matters initially.
- **Glass-box analysis for debugging.** When end-to-end fails, trace back to find the first step-level failure.
- **Transition failure matrices**: Create a matrix where rows = last successful state, columns = first failure state. This reveals which state transitions are fragile.
- **Include cost/token efficiency** as a dimension — an agent that succeeds but costs $5 per task may not be viable.

### Specific Metrics
- Task completion rate
- Average steps to completion
- Cost per task (tokens + tool call costs)
- Tool selection accuracy (per step)
- Error recovery rate

### Common Failure Modes
- Choosing the wrong tool for the task
- Passing malformed parameters to tools
- Getting stuck in loops (retrying the same failed action)
- Losing track of what's been accomplished across steps
- Over-planning (spending tokens on reasoning when action is needed)
- Not recovering from tool errors (treating them as fatal)

---

## Code Generation

### Key Eval Dimensions
1. **Functional Correctness** — Does the code do what was asked? (Execute it!)
2. **Syntax Validity** — Does it parse/compile without errors?
3. **Security** — No injection vulnerabilities, no hardcoded secrets, no unsafe patterns?
4. **Code Quality** — Readable, maintainable, follows conventions?
5. **Efficiency** — Reasonable time/space complexity?

### Recommended Approach
- **This is the most deterministic use case.** Execute the code. Run test suites. This is your primary eval.
- **Functional correctness is non-negotiable** and fully automatable — always test execution first.
- **Use LLM-as-judge only for readability/style.** Don't use it for correctness when you can just run the code.
- **Security checks can be partially automated** with static analysis tools (bandit, semgrep, eslint-security).

### Specific Metrics
- Pass@k (fraction of generated solutions that pass all tests)
- Compilation/parse success rate
- Security scan pass rate
- LLM-judge score for readability (binary: acceptable / needs improvement)

### Common Failure Modes
- Code that looks correct but fails on edge cases
- Using deprecated APIs or wrong library versions
- Generating code that works but is wildly inefficient
- Security vulnerabilities (SQL injection, XSS, command injection)
- Code that works in isolation but doesn't integrate with the existing codebase

---

## Classification / Extraction

### Key Eval Dimensions
1. **Accuracy** — Correct label / extracted value?
2. **Schema Adherence** — Output matches expected format/structure?
3. **Completeness** — All required fields extracted? No information missed?
4. **Consistency** — Same input produces same output across runs?

### Recommended Approach
- **Most amenable to traditional ML metrics.** Accuracy, F1, precision, recall — use them.
- **Clear ground truth = fully automatable.** If you have labeled data, you can run evals without human review.
- **Often no LLM-as-judge needed.** Exact match or fuzzy match against ground truth is sufficient.
- **Focus on edge cases and ambiguity.** The interesting failures are in ambiguous inputs where reasonable people might disagree.

### Specific Metrics
- Accuracy, Precision, Recall, F1 (per class and macro)
- Schema compliance rate
- Extraction completeness rate
- Run-to-run consistency (same input, same output?)

### Common Failure Modes
- Misclassifying ambiguous cases (the "borderline" inputs)
- Extracting partial information (getting the name but missing the title)
- Hallucinating extracted fields that aren't in the source
- Format inconsistency (sometimes returns JSON, sometimes plain text)
- Sensitivity to input phrasing (same info, different wording → different output)

---

## Content Generation (Summarization, Writing)

### Key Eval Dimensions
1. **Faithfulness** — Does the content accurately reflect source material? No fabrication?
2. **Coverage / Completeness** — Are all important points included?
3. **Conciseness** — Is it appropriately brief without losing meaning?
4. **Coherence** — Does it flow logically? Good structure?
5. **Tone / Style** — Does it match the intended voice and audience?

### Recommended Approach
- **LLM-as-judge is essential** for subjective quality dimensions (tone, style, coherence).
- **ROUGE/BERTScore as baselines only.** They correlate weakly with human judgment for most content tasks. Don't rely on them as primary metrics.
- **Pairwise A/B comparison** for style and tone preferences — easier for judges than absolute scoring.
- **Faithfulness is the one dimension that must be binary pass/fail.** Either it fabricated something or it didn't.

### Specific Metrics
- Faithfulness (binary pass/fail)
- Coverage score (fraction of key points included)
- LLM-judge: coherence (binary), tone match (binary)
- Pairwise preference rate (for A/B between versions)
- Length ratio (generated / target length)

### Common Failure Modes
- Fabricating facts or statistics not in the source
- Omitting critical information while including minor details
- Generating generic, "safe" content that lacks specificity
- Inconsistent tone (mixing formal and casual within same piece)
- Excessive hedging ("It's important to note that..." repeated)
- Not adapting to the target audience's knowledge level
