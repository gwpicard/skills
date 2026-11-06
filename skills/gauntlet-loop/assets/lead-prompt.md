# Lead prompt template

Fill the brackets and save as `.gauntlet/prompt.md`. Keep it short. Do not add
the architecture, the list of pieces, or a number of rounds. The details live
in `brief.md` and `critic.md`.

```
[GOAL, one or two sentences]. It must reach the level of [BAR]. [ONE SENTENCE
ON WHAT "GOOD" MEANS, only if the user is prescriptive.]

Read .gauntlet/brief.md first. Break the goal into the smallest pieces that
can be judged on their own. Give coupled parts a single owner. Fan out
sub-agents: one builder per piece.

For every piece, loop. After each change, capture the real output with the
capture step in the brief. Pair it blind with the matching reference using
.gauntlet/blind_pair.py. Then start a new, harsh critic sub-agent with fresh
context. Give it only .gauntlet/critic.md and the pair folder. If the
reference wins, send the builder the biggest gap and go again. Builders may
push back on a critic with evidence.

After each wave, have one fresh agent smooth the whole result so the pieces
fit. Keep .gauntlet/workbench.md up to date with captures, win counts and
open gaps. Don't stop until our pieces win blind, or a stop rule in the
brief is met. [Use ultracode. — only if the user accepts the cost]
```

## The original (for reference)

The original Claude of Duty prompt:

```
I want you to build a first-person shooter at the level of the most recent Call of Duty games. It should be utterly perfect, visually beautiful, with every single thing done at AAA quality—from textures to physics to anything you could think of.

Fan out sub-agents and have sub-agents tackle each one individually so that the game is utterly perfect. You should /loop on each item and have a separate sub-agent check it visually to ensure it looks triple A. That separate sub-agent should be a really harsh critic, and if it doesn't look triple A, it should keep going.

Don't stop until each sub-agent is utterly wowed with the quality when compared with the actual Call of Duty game. It should literally compare them side by side blind and say which one looks better. Do this in ThreeJS. /loop until it's utterly perfect. Fan out sub-agents and ultracode.
```

Note what it does not say: no architecture, no piece list, no round count.
