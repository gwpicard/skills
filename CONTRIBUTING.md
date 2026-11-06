# Contributing

## What makes a learning worth adding

A learning enters a skill only if it passes all four tests:

1. **General.** It applies beyond the project it came from. Remove client names, brand names, people, paths, prices and private decisions. Use neutral examples, not the project's real lines or assets.
2. **Evidenced.** It names what happened: the rounds it cost, the measurement, the correction in the user's words (anonymised). An opinion without an incident is not a learning.
3. **Actionable.** It changes what an agent does: a new instruction, a sharper one, a removed one, a script or a template.
4. **Placed.** It lives in one place. If the instruction already exists, sharpen it rather than adding a second one.

## How to add one

1. Add an entry to `LEARNINGS.md` using the format there.
2. Edit the skill file it changes. Keep `SKILL.md` short; detail goes in `references/`.
3. If a script changes, run it on a real page and note the result in the pull request.
4. Bump the plugin version in both `plugins/<name>/.claude-plugin/plugin.json` and `plugins/<name>/agent-plugin/plugin.json`.

## Writing standard

Write clear, precise, natural prose. Use the established term when it is right and define it once. Choose verbs that name the actual operation. Keep the scope and certainty of every claim. Do not invent jargon.

## Privacy

Session logs contain private material. Never commit logs, extracts or screenshots from a client project. The `.gitignore` excludes `harvest/`; keep extracts there or in a temporary folder outside the repository.
