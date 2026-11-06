# Choosing the bar

The bar is the most important part of the loop. The agent must be able to
inspect it and compare its own work with it, piece by piece.

## The four checks

| Check | Question | Fails when |
|---|---|---|
| Inspectable | Can the critic look at it directly? | "Make it amazing", "production-ready" |
| Comparable per piece | Is there a matching reference for each piece? | One overall image for a whole product |
| Blind-safe | Can the critic tell which is ours only from quality? | Famous work, different size or format, watermarks, style tells |
| Hard | Does it stop the agent at "pretty good"? | A bar the first draft already meets |

## Options by kind of work

### Visual: websites, UIs, 3D, games

- **Bar:** screenshots of the best real products in the category, per view or
  per element (hero section, pricing table, a weapon, a tree, a street).
- **Unit:** one view or one element. Not the whole product.
- **Blind-safe:** same size, same crop, same aspect ratio, same file format.
  Remove logos, brand names and text that reveal the source. Match the
  camera angle when possible.
- **Capture:** headless browser, one fresh page per shot, fixed wait or frame
  count, fixed viewport and pixel ratio.
- **Agent may find refs:** yes. It can search and download them. Check that
  they are high quality and match the unit.

### Something that does not exist yet

- Use a reference with the same quality level from another area. The critic
  then judges "which looks better overall", not "which is the better copy".
- Or generate reference images with an image model until the user likes them.
  This is often the stronger bar.

### Writing: articles, fiction, newsletters, docs

- **Bar:** paragraphs or sections from recent, strong, not-famous writing of
  the same kind. Pick for the quality the user wants (clarity, compression,
  voice), and say which quality in `brief.md`.
- **Unit:** paragraph, section, opening, transition. Also the whole argument,
  judged against a strong piece of similar length.
- **Blind-safe:** avoid famous authors. The model knows them. Match length
  within about 20 percent. Use the same plain-text format. Remove names and
  topic words that reveal the source when the topic differs.
- **Note:** the goal is quality, not copying the voice. Say so in the critic
  brief.

### Copy and growth: landing pages, emails, ads, campaigns

- **Bar:** the best real examples in the category, or past top performers
  from the user's own data.
- **Unit:** headline, lead paragraph, call to action, subject line, full email.
- **Blind-safe:** same format and length. Remove brand names.
- **Extra bar:** when real results exist (open rate, conversion, cost per
  subscriber), the final judge is the numbers, not the critic. Use the blind
  critic to choose what to test.

### Code and backend

- **Bar:** usually measured, not A/B. A test suite, a latency or throughput
  target, a failure-recovery test, a security review checklist, or a
  reference implementation.
- **Unit:** one module, one endpoint, one failure mode.
- **Critic:** still a fresh subagent. It runs the measurement and reads the
  code. It does not read the builder's explanation.
- **Measure distributions, not medians.** Report p50, p95, p99 and the worst
  case. A median can look fine while the real use is broken.
- **A/B is possible** for readability or API design: two versions of the same
  interface, labels hidden.

### Research, strategy, plans

- **Bar:** a strong real example of the same kind of document, or a checklist
  of questions an expert reviewer would ask.
- **Unit:** one section or one claim.
- **Critic:** checks sources and asks which of two versions a decision-maker
  would trust more.

## When the user has no bar

Make finding the bar part of the task. Tell the lead agent:

> Find a concrete comparison or measurement that plays the same role for this
> task that real Call of Duty screenshots played for Claude of Duty. Explain
> in one sentence why it is a useful bar. Then judge every round against it.

Prefer to agree the bar with the user before launch. A bar chosen during the
run is harder to check.
