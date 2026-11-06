# Skills

The skills I use with Claude every day. Each one is a folder in [`skills/`](skills/) with a `SKILL.md`, following the [Agent Skills](https://agentskills.io) format, so it works in Claude Code, on claude.ai and in other agents that read skills.

## Stable

| Skill | What it does |
|---|---|
| [analyze-repo](skills/analyze-repo) | Analyses a repository across architecture, features, security, code quality, data model, API and performance, with parallel agents and 9 presets. |
| [im-lost](skills/im-lost) | Re-explains confusing or overly complex content in simpler, clearer language. |
| [language-audit](skills/language-audit) | Reviews text for AI writing patterns, hollow language and structural problems. |
| [learning-from-videos](skills/learning-from-videos) | Pulls the transcript, on-screen content and useful links out of a video into a reusable notes file. |
| [prd](skills/prd) | Guides the writing of an in-depth Product Requirements Document. |
| [skill-authoring](skills/skill-authoring) | Best practices for creating, improving and organising skills. |
| [website-review](skills/website-review) | Reviews a website for marketing, SEO, GEO, messaging, conversion and UX. |

## Experimental

These work for me but still change often.

| Skill | What it does |
|---|---|
| [eval-skill](skills/eval-skill) | Reviews a `SKILL.md` against best practices for descriptions, structure and triggering. |
| [evals](skills/evals) | Designs evaluation strategies for LLM products. |
| [gauntlet-loop](skills/gauntlet-loop) | Runs a loop where builder agents improve an output and blind critics compare it against a real reference until it wins. |
| [handoff-session](skills/handoff-session) | Writes a continuation prompt and reference document so a new session resumes work without re-deriving decisions. |
| [organize-directory](skills/organize-directory) | Organises a folder in three steps (scan, propose, apply), reversibly and with an undo script. |
| [pageload-loop](skills/pageload-loop) | Speeds up web pages one measured change at a time, keeps only real gains and reports before, during and after. |
| [project-init](skills/project-init) | Sets up CLAUDE.md, `.claude/` and a development plan for a new or existing project. |

## Install

**Claude Code (plugin)**

```
/plugin marketplace add gwpicard/skills
/plugin install gwp-skills@gwpicard-skills
/plugin install gwp-experimental@gwpicard-skills
```

Plugin skills are namespaced, for example `/gwp-skills:prd`. Turn on auto-update under `/plugin` → Marketplaces to receive new versions.

**Any agent (skills CLI)**

```
npx skills add gwpicard/skills            # pick skills interactively
npx skills add gwpicard/skills -g         # install for your user, not one project
```

**Manually**

Copy or symlink a folder from `skills/` into `~/.claude/skills/`.

**claude.ai or Claude Desktop**

Zip a skill folder (the folder itself at the zip root) and upload it under Customize → Skills.

## License

[MIT](LICENSE)
