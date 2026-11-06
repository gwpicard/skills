# Positioning, vocabulary and lines

## Ground the position in evidence

Abstract framing produces generic positioning. Start from what the organisation has actually done and said.

Sources, in order of value:

1. **The record of work.** Past projects, what was delivered, for whom, and what changed for the client. Re-read them for the recurring value, which is often not the one the organisation advertises. One consultancy's projects, re-read, showed that its value was cutting experts' preparation time, which was more specific than the "we help teams adopt AI" on its site.
2. **The founder's own frameworks and artefacts.** Scales, canvases, sketches, decision rules. These carry a point of view that competitors do not share.
3. **Conversations with buyers.** What they asked, what convinced them, what they objected to.
4. **A competitor teardown.** How ten or so direct competitors phrase their offer. The aim is to find the phrases everyone uses, so you can avoid them.

Write `positioning.md` with: audience (who, size, what they are like, who is excluded), the problem in the buyer's words, the position, the point of view, and the constraints the user sets (markets to avoid, what the organisation will not do).

## Fix vocabulary and point of view early

A point of view the organisation owns, such as a scale, a belief or a decision rule, becomes the content that styling cannot fake. Settle its terms one at a time with the user, and check each term for ambiguity ("task" and "job" read as the same thing; "outcome" is unclear).

Name stages and offers by the work, kept short: "Review and plan" beats "Review the whole business and plan the opportunities". Keep method detail for client meetings; the public surface shows the top-line labels.

Pressure-test ambition words before adopting them. "Lean" can imply headcount cuts; define an aspiration through observable traits instead.

## Attributes that do work

Pick three to five attributes, and make each one operational so it can steer copy and design:

```
Precise
  In copy: name the operation and the number; no hedging adjectives.
  In design: fine consistent line, a visible grid, exact alignment.
  Must not become: cold or technical for its own sake.
```

An attribute without a design line and a "must not become" line is a slogan. Where it helps, give voice and design the same pillars, so a copywriter and a designer apply the same idea.

## Voice

Write `voice.md` with a small set of rules, each with a before/after pair from the organisation's own copy. Rules that recur:

- Active voice, from the perspective of what the organisation does.
- Plain, precise words. Plain does not mean elementary: use the established term where it is right.
- Verbs that name the actual operation ("detects", "reports", "approves") rather than "helps", "enables", "drives".
- A banned-word list: consultant jargon and AI-sounding words ("real work", "holistic", "groundwork", "seamless", "unlock", "empower", "leverage"), plus terms the user rejects during the work.
- Remove copy that adds nothing: legends, eyebrows, meta lines, instructions the interface makes obvious.

Keep the terms as data in `terminology.yaml`, so banned and preferred words can be checked mechanically:

```yaml
- prefer: "review"
  avoid: ["audit", "health check"]
  context: "name of the first stage, everywhere"
  source: "decisions.md D4"
- avoid: ["seamless", "unlock", "leverage"]
  context: "all copy"
  source: "voice review, round 2"
```

## Lines that take a stance

Succinct lines tend to sound generic. Two tests separate a stance from a platitude:

- **Opposite test.** Could a sensible competitor claim the opposite? "We automate where it helps most" fails: nobody claims the opposite. "We automate only where it pays back" passes, because many firms automate everything they can.
- **Swap test.** Put a competitor's name in front of the line. If it still works, the line belongs to nobody.

Also check: three to seven words for a headline, active voice, no banned words, and whether one word ("only", "never", "first") would turn a platitude into a stance.

## The rejected-lines log

Keep every rejected line in `lines.md` with the reason in the user's words:

```
## Rejected
- "Expertise for the challenges that matter": "expertise" sounds cheesy; not active voice
- "Make technology work for real teams": "real teams" sounds like AI-written copy
```

Give this file to every model and fresh agent that generates copy. It stops repeat suggestions and lets a new generator contribute on the first try. When two different models arrive at the same line independently, treat that as a signal worth showing the user.
