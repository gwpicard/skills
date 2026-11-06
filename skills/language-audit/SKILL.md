---
name: language-audit
description: Review any text for AI writing antipatterns, hollow language, and structural problems. Use when polishing a document, post, slide deck, email, or markdown file before sharing. Input can be pasted text or a file path. Produces a numbered list of specific flagged phrases with suggested rewrites, followed by a pass/revise verdict.
---

# Language Audit

Review the provided text and flag every instance of the patterns in this file. For each issue: quote the exact phrase, name the pattern, and give a concrete rewrite. Do not give general advice. Do not summarise the text. Work through it systematically.

## Output format

Produce a numbered list. Each item:

> **Quote:** "exact phrase from the text"
> **Pattern:** name of the antipattern
> **Fix:** a specific rewrite

After the list, add one line: the total number of issues found, and either "Ready to share" or "Needs revision."

If no issues are found, confirm that the text passed review and name the patterns you checked.

---

## Structural antipatterns

### Em dashes used as connectors or commas

Flag em dashes where a period, colon, or comma would be cleaner.

Bad: "Skills are saved prompts only — no file input, no batch"
Fix: "Skills are saved prompts only. No file input, no batch."

Bad: "The system connects to Shopify — pulling products automatically"
Fix: "The system connects to Shopify and pulls products automatically."

Do not flag every em dash. Parenthetical uses are fine: "New York — a city I visited once — surprised me." Flag the ones doing work a punctuation mark should do.

### Contrastive reframes

Flag "not X, it's Y" and "this isn't about X, it's about Y" constructions. Also flag the same pattern split across sentences.

Bad: "It's not about automation. It's about intelligence."
Bad: "This isn't a tool. It's a workflow."
Fix: Rewrite as a direct statement of what it actually is.

### Triplets for rhetorical effect

Flag lists of three adjectives or qualities used for rhythm rather than substance.

Bad: "innovative, scalable, and transformative"
Bad: "fast, reliable, and easy to use"
Fix: Pick the one that actually matters. If all three matter, say why each one does.

### Dangling participial phrases

Flag sentence endings that add empty interpretation instead of stating a fact.

Bad: "...improving team outcomes"
Bad: "...driving growth across the organisation"
Bad: "...enabling teams to move faster"
Fix: State the specific result, or cut the phrase entirely.

### Significance inflation

Flag phrases that connect a specific thing to a grand broader trend.

Bad: "marking a pivotal moment in"
Bad: "part of a broader shift toward"
Bad: "as the industry continues to evolve"
Bad: "in today's rapidly changing landscape"
Fix: State the specific claim without the inflation.

### Short parallel sentences used for rhythm

Flag sequences of three or more short sentences with the same structure used for dramatic effect.

Bad: "Progress stalls. Funding dries up. Teams lose faith."
Fix: Rewrite as prose. If the sequence is genuinely useful, vary the sentence lengths.

---

## Openers and closers

### Throat-clearing

Flag phrases that delay the point.

- "It's worth noting that..."
- "It's important to remember that..."
- "One of the most important things to consider is..."
- "Before we get into X, it's worth understanding Y..."

Fix: Delete the preamble. Start with the point.

### Compulsive summaries

Flag summary openers in short pieces where the content speaks for itself.

- "Overall,"
- "In summary,"
- "In conclusion,"
- "To summarise,"

Flag at the start of any paragraph or section in a document shorter than 1,000 words.

### Closing meta-statements

Flag sentences that cash out the meaning of what was just said. If the writing did its job, the point is already there.

Bad: "That is what this project is about."
Bad: "This is why X matters."
Bad: "Understanding X requires taking Y seriously."
Fix: Delete the sentence.

### Chatbot openers

- "Certainly!"
- "Great question!"
- "I'd be happy to"
- "Of course!"
- "Absolutely!"

### Landscape openers

- "In today's rapidly evolving..."
- "As X continues to navigate..."
- "In an era of..."

---

## Word-level patterns

### Banned words

Flag any of the following regardless of context. See references/banned-words.md for the full list with suggested replacements.

Core banned list: delve, intricate, tapestry, pivotal, underscore, landscape (metaphorical), foster, testament, enhance, crucial, robust, seamless, vibrant, nestled, thriving, leverage (as a verb), commence, navigate (metaphorical), unlock, game-changer, comprehensive, paradigm shift, watershed moment, transformative, groundbreaking, empower, synergy, holistic, streamline, cutting-edge, best-in-class

### Copula avoidance

Flag "serves as", "functions as", "acts as" used instead of "is".

Bad: "This document serves as a reference guide."
Fix: "This document is a reference guide."

### Vague attribution

Flag claims attributed to unnamed sources.

- "experts suggest"
- "many researchers argue"
- "studies show"
- "research indicates"

Fix: Name the source or rewrite the claim as a direct statement you can stand behind.

### Promotional admiration

Flag adjectives that express admiration without content.

- "incredible"
- "amazing"
- "world-class"
- "powerful" (when used to mean "good")
- "exciting" (when used about your own work)

---

## Formatting antipatterns

These apply when reviewing documents and slides, not plain prose.

### Bullet lists with bolded headers

Flag bullet lists where each item follows the pattern: **Bold label:** explanation text.

Bad:
- **Speed:** The tool processes requests in under a second.
- **Accuracy:** Results are verified against three sources.

Fix: Rewrite as prose, or as plain bullets without the bold label.

### Excessive bolding

Flag bold text used for general emphasis rather than for key terms, headings, or UI labels. If more than one word in five is bold, flag the section.

---

## Notes on judgment calls

- Quote the exact phrase. Do not paraphrase the problem.
- If the same pattern appears multiple times, list each instance separately.
- Some patterns (em dashes, parallel sentences) require judgment. When in doubt, flag and explain why, then let the author decide.
- This skill checks language patterns only. It does not check factual accuracy, grammar, spelling, or tone.
- Do not rewrite the entire document. Produce fixes only for the flagged phrases.
