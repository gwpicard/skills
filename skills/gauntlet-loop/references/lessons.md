# Lessons from real runs

Sources: the original Gauntlet Loop guide, a video walkthrough, and the
Claude of Duty repo README.
Add the lessons that apply to `.gauntlet/brief.md`.

## Setup

- **Use an agent harness, not a chat.** The loop needs files, tools,
  rendering and subagents. (guide)
- **Give the goal, not the plan.** When you prescribe the architecture and
  the pieces, you replace the model's judgment with yours. For real work,
  you can still say what is good about the reference. (guide, video 11:15)
- **Build the harness first.** In Claude of Duty the capture and measure
  tools were "arguably the interesting part". (README)
- **Captures must be reproducible.** Reusing one browser page across shots
  leaked state. Two identical runs differed on 10 of 11 shots. One fresh page
  per shot made captures bit-identical. (README)
- **Measure distributions.** A static benchmark said 94 fps. Real play was
  12 to 17 fps with stalls over 700 ms. Report p50, p95, p99 and worst case.
  (README)

## Splitting the work

- **Split to the smallest piece that can be judged alone.** "Make the game
  better" is too vague. "Make this tree beat this reference tree" is a
  problem the agent can attack. (guide)
- **Coupled parts need one owner.** Six agents each owning one folder moved
  the score +0.46 and made defects worse (60 to 66), because tonemapping, sky
  and indirect light are one system. One sequential pass with one owner per
  coupled concern moved it +1.00 and cut defects to 26. Tell the lead to
  group coupled parts before it fans out. (README)
- **Write a contract.** Claude of Duty had an ARCHITECTURE.md with interfaces,
  folder ownership and shared types. Parallel builders need it. (README)
- **Smoothing pass.** After each wave, one fresh agent checks that the pieces
  fit together. It does not redesign. (guide)

## Critics

- **Blind means fresh context.** In Claude Code, a forked subagent inherits
  the lead's context and acts like the builder. Use a new subagent with only
  the brief and the items. (video 06:01)
- **Say "harsh".** Models are agreeable by default. (video 05:31)
- **Critics can be wrong.** For three rounds every critic called the weapon
  "untextured". It was not. It was too shiny, because earlier rounds had made
  the colors darker to answer other complaints. The fix was the opposite of
  what critics asked. Let the builder measure and push back with evidence.
  (README)
- **The critic looks at the real thing.** Pixels, the running page, test
  output, the finished text. Never a summary from the builder. (guide)

## Running

- **No fixed number of rounds.** With a hard bar there is almost always
  another gap. (guide)
- **The bar can stay out of reach and still work.** Claude of Duty never
  beat Call of Duty. Every blind A/B picked the real game. Scores still went
  from 3.59 to 5.05 of 10. The bar gave direction. (README)
- **Watch without stopping it.** A live workbench page lets you check from a
  phone. (guide)
- **Steer when needed.** "I like this direction, but pull back here" is fine
  mid-run. (video 11:15)
- **Stop on value.** A demo does not need the full budget. Important work may
  be worth a few hundred dollars. (video 11:46)
- **Report honestly at the end.** The README lists where the game still falls
  short. Do the same.
