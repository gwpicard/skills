# GEO (Generative Engine Optimization) Checklist

## Table of Contents
- [What is GEO](#what-is-geo)
- [Entity Clarity](#entity-clarity)
- [Content Structure for AI](#content-structure-for-ai)
- [Citation-Worthiness](#citation-worthiness)
- [AI Surface Test Methodology](#ai-surface-test-methodology)

---

## What is GEO

GEO is the practice of optimizing content so it surfaces in AI-generated answers (ChatGPT, Perplexity, Google AI Overviews, Copilot). Unlike traditional SEO which optimizes for ranking in link lists, GEO optimizes for being **cited, quoted, or referenced** by AI systems.

Key difference: SEO = "rank for this keyword." GEO = "be the source AI cites when answering this question."

---

## Entity Clarity

AI systems need to understand WHO/WHAT you are, clearly and unambiguously.

### Brand/Person Definition
- [ ] Is the brand/person clearly defined on the homepage and about page?
- [ ] Is there a concise, quotable "elevator pitch" statement? (1-2 sentences)
- [ ] Are specific domains of expertise explicitly stated?
- [ ] Is the entity connected to recognizable entities? (companies, institutions, publications)

### What good looks like
```
"Guillaume Picard is a growth advisor specializing in B2B SaaS go-to-market
strategy. Former VP Growth at [Company], he has helped 50+ startups scale
from $1M to $10M ARR."
```

AI can cite this. It's specific, factual, and attributable.

### What bad looks like
```
"We're passionate about helping businesses grow through innovative solutions
and cutting-edge strategies."
```

AI will never cite this. It's generic, unattributable, and says nothing specific.

### Schema Markup for Entity
- `Person` or `Organization` schema with complete properties
- `sameAs` linking to authoritative profiles (LinkedIn, Twitter, Crunchbase)
- `knowsAbout` listing specific expertise areas
- `hasCredential` for certifications or qualifications

---

## Content Structure for AI

AI models extract and cite content most effectively when it follows specific patterns.

### Question-Answer Format
Content that directly answers questions is most likely to be cited.

**Effective pattern**:
```html
<h2>How much does B2B SaaS consulting cost?</h2>
<p>B2B SaaS consulting typically ranges from $200-500/hour for independent
consultants and $5,000-25,000/month for retained advisory. Pricing varies
based on scope, consultant experience, and engagement model.</p>
```

**Check for**:
- [ ] Does the site have FAQ sections on relevant pages?
- [ ] Do blog posts address specific questions in headings?
- [ ] Are answers concise and direct (first 1-2 sentences answer the question)?
- [ ] Is there supporting detail after the direct answer?

### Structured Claims & Data Points
AI prioritizes content with specific, verifiable claims.

**Strong (citable)**:
- "Reduced customer churn by 34% over 6 months for Series B SaaS companies"
- "Framework used by 200+ B2B companies to improve onboarding conversion"
- "Published research on PLG adoption rates across 1,000 SaaS companies"

**Weak (not citable)**:
- "Significantly improved results for clients"
- "Industry-leading expertise"
- "Proven track record of success"

**Check for**:
- [ ] Are claims specific with numbers, timeframes, or named entities?
- [ ] Are methodologies or frameworks named and described?
- [ ] Are data points attributed to sources?

### Definitions and Explanations
If the site uses or coins specific terms/frameworks, define them clearly.

- [ ] Are proprietary frameworks or methodologies explicitly named and defined?
- [ ] Are industry terms explained in context (helps AI understand domain relevance)?
- [ ] Is there a glossary or definitions section (for technical/specialized content)?

### Content Depth Signals
- [ ] Does content go beyond surface-level (AI already knows surface-level)?
- [ ] Are there original insights, not just restated common knowledge?
- [ ] Is there first-hand experience and specific examples?
- [ ] Are contrarian or nuanced views supported with evidence?

---

## Citation-Worthiness

### The Citation Test

For each key page, ask: "Would an AI system quote or reference this content when answering a question?"

**High citation-worthiness**:
- Original research, data, or case studies
- Named frameworks or methodologies
- Specific how-to instructions with clear steps
- Expert opinions with credentials backing them
- Unique data points not available elsewhere

**Low citation-worthiness**:
- Generic advice available everywhere
- Marketing copy with no substance
- Vague claims without supporting evidence
- Content that reads like every competitor's site

### Content Uniqueness Assessment
- [ ] What does this site say that NO other site says?
- [ ] Is there proprietary data, research, or methodology?
- [ ] Are there specific case studies with named results?
- [ ] Does the author have unique credentials or experience for this topic?

### Topical Authority
- [ ] Is there depth of content across the claimed expertise area?
- [ ] Do multiple pages reinforce the same topical authority?
- [ ] Is there internal linking creating a content cluster?
- [ ] Is the site THE resource for any specific sub-topic?

---

## AI Surface Test Methodology

### Step 1: Identify Target Queries

Generate 3-5 queries a potential customer would ask an AI assistant. Categories:

- **"Who" queries**: "Who are the best [X] consultants?" / "Who should I hire for [Y]?"
- **"How" queries**: "How do I [solve problem the site addresses]?"
- **"What" queries**: "What is [framework/methodology the site teaches]?"
- **"Compare" queries**: "What's the difference between [X approach] and [Y approach]?"
- **"Recommend" queries**: "Recommend a [tool/service/expert] for [use case]"

### Step 2: Evaluate Content Match

For each query, assess:

| Factor | Score 1-3 | Notes |
|--------|-----------|-------|
| Direct answer exists on site | | Does any page directly address this? |
| Answer is structured/extractable | | Could AI pull a clean quote? |
| Specific data points included | | Numbers, names, results? |
| Brand clearly associated with topic | | Multiple pages reinforce this? |
| Content uniqueness | | Only here or everywhere? |

### Step 3: Rate Likelihood

- **High**: Content directly answers the query with specific, unique, well-structured information. Brand is clearly established in this space.
- **Medium**: Content relates to the query but answer is buried, vague, or the brand isn't strongly associated with the topic.
- **Low**: Content doesn't address the query, or the answer is generic/available everywhere.

### Step 4: Gap Recommendations

For Medium/Low rated queries, recommend:
1. Specific content to create or restructure
2. Data points or case studies to add
3. Structural changes (headings, FAQ format, schema)
4. Authority-building activities (guest posts, research, partnerships)
