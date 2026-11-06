# Conversation handoff examples

Worked examples for the conversation branch, one per shape. They are indicative,
not rigid templates. Session handoffs (git repo) have their examples inline in
`handoff-template.md`.

## Contents

1. [Idea exploration (comprehensive)](#example-1-idea-exploration-comprehensive)
2. [Decision (lightweight)](#example-2-decision-lightweight)
3. [Debugging (comprehensive)](#example-3-debugging-comprehensive)
4. [Research (lightweight)](#example-4-research-lightweight)
5. [Short note](#example-5-short-note)
6. [Notes on how these examples work](#notes-on-how-these-examples-work)

---

## Example 1: Idea exploration (comprehensive)

**Title:** Skills Workshop: Open-source project for creating and evaluating agent skills

**BLUF**

An open-source tool that helps people create agent skills (SKILL.md files), define what "good" means for each skill via test cases, and evaluate whether the skill holds up across the AI tools it's meant to run on. The idea is at the sketched-design stage with a V0.1 scope defined but no code written. If picked up now: pick one existing personal skill and hand-write its eval set as a calibration exercise before committing to V0.1.

**Shape**

This is a handoff for an idea exploration.

**The seed**

"I want to build an open source project that allows people to build, validate and iterate / improve their skills (agent skills). So you create a skill, then it helps you create evaluation criteria and examples, and then based on that help you improve the skill."

**Current state of the idea**

The project is a workshop covering the full lifecycle of an agent skill: create, evaluate, iterate, publish. The guiding framing is that the eval set is the canonical artifact and the SKILL.md is one implementation of it, reframing "eval" as a contract changes what the tool is and makes the differentiating features fall out of one coherent architecture.

The evaluation has three layers in V1 (static quality check, trigger/activation test, output quality test) with a fourth (instruction-following) deferred to V2. Cross-tool evaluation across Claude Code, Codex, Cursor, etc. is the main technical differentiator. Section-level contribution analysis and a shared eval library are secondary differentiators.

The project integrates with Vercel's `skills` CLI and `skills.sh` directory as the distribution layer, rather than building a competing one.

**Intellectual history**

Started as "does an eval framework for skills exist" (yes, Anthropic's skill-creator is the reference implementation). Sharpened by identifying what existing tools don't do: cross-tool testing, shared eval libraries, section-level contribution analysis, trust layer for published skills, SME-friendly UX. The framing shifted from "eval framework" (sounds like work, nobody wants it) to "workshop" (covers the full lifecycle, creation included). Creation was explicitly added to V0.1 rather than deferred because it's the moment authors have the most context, and because without it the project is an eval harness rather than something people actually want to use.

**Landscape**

Anthropic's `skill-creator`, reference implementation, Claude Code only, no cross-tool, per-author local setup, no shared evals, no trust layer. Apache 2.0.

Vercel's `skills` CLI and `skills.sh`, distribution backbone, 44+ tools, no eval.

Skilldex, package manager with compiler-style format checking and a "skillset" abstraction. Does static checks only.

mager.co's eval loop, combines trigger eval with promptfoo for output quality. Single-tool.

LangSmith, trace-based skill eval, commercial, tied to LangSmith infrastructure.

MLflow, LLM judges on execution traces. Checks instruction-following.

MindStudio Skills 2.0, commercial, batch eval, rubric management, A/B tests.

The gap: no tool combines cross-tool evaluation, shared eval libraries, and section-level ablation.

**Decisions**

- *Creation is in V0.1, not deferred.* Alternatives considered: ship as pure eval harness first, add creation later. Confidence: high. Status: accepted. Consequences: V0.1 scope is larger but positioning is coherent.
- *Instruction-following eval moves to V2.* Alternatives: ship all four layers in V1. Confidence: high. Status: accepted. Consequences: V0.1 ships faster; instruction-following layer has uneven support across tools anyway.
- *Integrate with Vercel's skills.sh rather than building competing distribution.* Alternatives: build own registry. Confidence: high. Status: accepted. Consequences: plug-in positioning as quality layer, not competing substrate.
- *XML-tagged sections required from V0.1.* Alternatives: retrofit later. Confidence: medium. Status: accepted. Consequences: imposes a small constraint on authors early; enables section-level analysis later.
- *CLI first, web UI in V0.5.* Alternatives: both at once. Confidence: high. Status: accepted. Consequences: developer adoption first, SME adoption later.
- *TypeScript as primary language.* Alternatives: Python. Confidence: medium. Status: accepted. Consequences: aligns with Vercel CLI and web UI ecosystem.

**Open threads**

- Whether trace access across AI tools is uniform enough to support the V2 instruction-following layer across all of them, or whether that layer will always be Claude-first.
- Whether the naming ("Skills Workshop" is a working title, nothing else) should be resolved before or after the first public write-up.
- Whether V0.4 (shared eval library) needs a separate contribution flow or can piggyback on GitHub conventions.

**First concrete move**

Take one existing personal skill and hand-write its eval set. Two activation tests, two output quality tests, two negative cases. If this feels tedious, the guided creation flow needs more substance than planned. If it feels obvious, the flow can be lighter.

**Revival triggers**

Pick up if Anthropic's skill-creator hasn't absorbed cross-tool support or shared eval libraries in the next six months. Drop (or reposition) if Anthropic ships both and does so well.

**Action items**

- Re-check the landscape before starting, fastest-moving piece is Anthropic's skill-creator.
- Technical spike on the AI tool adapter layer. Build Claude Code adapter first, sketch interface for Codex.
- Name the project.

**Cross-references**

- Trust Ladder thesis, conceptually adjacent, particularly on the reviewability property.
- Context Engineering work, the "eval set as contract" framing is related.

**External references**

- `skills-workshop-project-brief.md`, earlier version of this handoff, more detailed on version sequencing. Superseded by this document for main thinking but retains detail on V0.2-V1.1 planning.

---

## Example 2: Decision (lightweight)

**Title:** Database choice for internal tooling project

**BLUF**

Picked Postgres over SQLite for the internal tooling project, primarily because we need concurrent writes and cross-team access. Decision is final. If picking up now: spin up the Postgres instance, migrate the existing SQLite prototype.

**Shape**

This is a handoff for a decision.

**The decision**

Postgres.

**Options considered**

SQLite, rejected. Simple to set up, but single-writer model is a problem for the team use case, and we'd outgrow it fast.

Postgres, accepted. Handles the concurrency requirement, standard across the team's existing stack, tooling is mature.

DuckDB, considered briefly, set aside. Good fit for analytics but not for the transactional workload this project has.

**Reasoning**

Concurrency requirement is the decisive factor. Postgres being familiar across the team is a secondary factor that tips against any option requiring learning curve.

**Status and confidence**

Accepted. Confidence: high.

**What still needs to happen**

Infrastructure team to provision the instance. Migrate the prototype schema from SQLite. Update the connection code.

---

## Example 3: Debugging (comprehensive)

**Title:** Deploy failures on staging: intermittent 502 errors

**BLUF**

Staging deploys have been producing intermittent 502s for the past two days. Root cause is currently unknown but the evidence points to a connection pool exhaustion issue during startup. If picking up now: check if the new connection pool limits from yesterday's change have taken effect, and grab fresh logs.

**Shape**

This is a handoff for a debugging session.

**The problem**

Staging deploys show 502s for the first 30-90 seconds after the new version comes up. Errors stop on their own without intervention. Not reproducible in local environments. Started two days ago, no obvious corresponding deploy.

**What was tried**

*Hypothesis: load balancer timeout too aggressive.* Checked LB config, timeouts are at default 30s, unchanged for months. Ruled out.

*Hypothesis: slow startup in new container image.* Checked startup times, they're slightly longer (8s vs 5s) but well within the readiness probe window. Ruled out as sole cause.

*Hypothesis: database connection pool exhaustion at startup.* Checked pool metrics, saw pool hitting max connections during the 502 window. Strong signal. Raised pool size as a test; results pending.

*Hypothesis: migration from shared to dedicated Redis.* Happened three days ago, close to the start of the issue. Checked Redis connection behaviour, looks healthy, no connection-level errors. Partially ruled out but worth keeping in mind.

**Current hypothesis**

Connection pool exhaustion during startup, possibly exacerbated by the Redis migration causing slightly different concurrent-connection patterns than before. Pool size increase deployed yesterday; waiting to see if today's deploys are clean.

**Where to look next**

Check staging deploys from today. If clean, confirm the pool-size hypothesis. If still failing, look at whether the Redis migration changed connection semantics for the ORM layer.

**Action items**

- Check today's staging deploy logs.
- If still failing, get ORM maintainers involved on the Redis side.

---

## Example 4: Research (lightweight)

**Title:** State of Danish corporate tax deductions for AI consulting expenses (2026)

**BLUF**

Most AI/software consulting expenses are deductible as ordinary business expenses for Danish enkeltmandsvirksomhed. A few categories have special rules. If picking up now: confirm the specifics with a Danish accountant before the next filing.

**Shape**

This is a handoff for a research survey.

**The question**

Which AI-consulting-related expenses (software subscriptions, cloud compute, training, conferences) are deductible for a Danish sole proprietorship, and are any treated specially?

**Findings**

- Software subscriptions: fully deductible as ordinary business expenses. Confidence: high.
- Cloud compute (API usage, hosting): fully deductible. Confidence: high.
- Training and certifications: deductible if related to current business activities. Confidence: medium, the "related to current" test can be narrow; ask an accountant.
- Conferences: deductible if business-related, but per-diem meals cap applies. Confidence: high for the general case.
- Home office: deductible under specific conditions; separate rules. Confidence: medium.

**Sources consulted**

- skat.dk guidance on sole proprietorships
- Danish business tax guides (iværksætterguiden)
- Relevant sections of the 2026 tax statute

**What remains unknown**

Whether AI training courses (e.g., a paid Anthropic skills certification, hypothetically) count as "ordinary training" or fall under specific continuing-education rules. Needs accountant check.

**What would change the picture**

Change in enkeltmandsvirksomhed rules for 2026 filing (check before actually filing). Specific challenges by Skat on AI-related deductions would create precedent worth tracking.

---

## Example 5: Short note

**Title:** Preference for Postgres JSON columns over EAV

Decided to use Postgres JSON columns for the dynamic-schema parts of the app rather than an EAV table. Reason: better query ergonomics, the team knows it, and Postgres JSON performance is fine at our scale. Status: accepted, high confidence. If picking this up: just know that this was the call and why, no action needed unless we hit scale issues.

---

## Notes on how these examples work

Each example leads with a BLUF of no more than three sentences.

Each example names the shape explicitly.

Lightweight examples keep the main argumentative lines (what, why, alternatives) but skip supporting detail (per-option pros/cons, source-by-source summary).

Comprehensive examples preserve intellectual history, landscape, and reasoning in enough detail that a stranger could engage with the thinking, not just the conclusions.

Voice is direct. No consultant register. No fake closure on open items.

Titles are specific. Not "project handoff" but "Skills Workshop: Open-source project for creating and evaluating agent skills."
