# Evals for learning-from-videos

Three layers. The first two are free and run in seconds. The third makes model calls.

## Layer 1: script evals (free, about 40 s)

```bash
cd ~/.claude/skills/learning-from-videos
python3 evals/run_script_evals.py            # all fixtures, all depths, plus two failure cases
python3 evals/run_script_evals.py --quick    # transcript and cache manifest checks only
python3 evals/run_script_evals.py --slug <slug> --depth deep
python3 evals/run_script_evals.py --sweep    # calibration table (below)
python3 evals/run_script_evals.py --fetch    # fetch a fixture video that is not cached yet
python3 evals/run_script_evals.py --slow     # also the Whisper path on a local clip (about 1 min)
```

Fixtures live in `evals/fixtures/<slug>.json`. Each has hand-labelled `moments` (time,
label, kind `ui` | `ui-small` | `cut`), `ui_segments`, per-depth `expect` thresholds, and
the facts a notes file must contain. A moment counts as covered when a kept frame is
within 2 s. `ui-small` moments count at deep depth only.

Fixture videos:

| Slug | What it tests |
|---|---|
| `postgresql-in-100-seconds-n2Fluyr3lbc` | 2:36 explainer, animated slides, code typed on screen with no cuts |
| `consistent-ai-characters-voices-and-scenes-advanced-workflow-swx780Vy_OQ` | 9:25 tutorial, slides, B-roll, UI clicking, prompts typed, a webcam overlay, links in the description |
| `settings-sync-in-visual-studio-code-it-s-built-in-now-3dsq39DEgZ8` | 5:13 screen recording, menus and dialogs, whole-pane navigations, long static stretches |

To add a fixture: fetch the video, run `extract_frames.py --depth deep`, view the contact
sheets, label the moments, and take exact seconds from `frames/diff_series.json` (the
second whose `changed_frac` spikes), not from the frame names of an older run.

## Layer 2: notes fact check (free)

After a real skill run:

```bash
python3 evals/check_notes.py <notes.md> --fixture <slug>
```

Checks the must-contain facts (pass at 0.8), warns on garbled names, counts timestamps,
checks the template sections, and verifies every cited frame and resource file exists.

Scores log:

| Date | Fixture | Depth | Facts | Notes |
|---|---|---|---|---|
| 2026-09-17 | postgresql | standard | 7/7 | bundled example, frame names remapped after the sampler rewrite |
| 2026-09-17 | runway | standard | 9/9 | full skill run with the sequence-aware subagent; wardrobe and location prompts now captured |

## Layer 3: trigger evals (model calls)

Twenty cases under `evals/trigger-*` and `evals/notrigger-*`, each a `prompt.md` with
`allowed_tools: [Skill]` and `max_turns: 2`, graded by whether the Skill tool was called
with `learning-from-videos`. The notrigger cases are near misses: download a video,
transcribe a podcast, trim an mp4, make a video, summarize an article.

```bash
cd ~/.claude/skills/learning-from-videos
claude plugin eval . --ablation none --runs 1 --max-cost-usd 3 --threshold 0.9
claude plugin eval . --runs 1 --max-cost-usd 6      # with the no-skill baseline arm
```

Results land in `evals/results/`. Runs often end with "Reached maximum number of turns
(2)". That is expected: the case stops the model right after the routing decision so the
pipeline never runs, and the grader still scores the Skill call. Last run 2026-09-17:
20/20 cases passed with `--ablation none`.

If the target does not resolve as a skills-dir plugin,
use `evals/triggers.md` as a manual checklist: paste each prompt into a fresh session and
record whether the skill fired.

## Calibration table (2026-09-17, fps 1, uncapped candidates)

`thr` is the change threshold. Depths use 0.15 (light), 0.03 (standard), 0.012 (deep).
`ui-cov` counts `ui` and `ui-small` moments; `gap` is the largest gap in seconds inside a
UI segment.

Runway tutorial (busy pixels 0.045, the webcam overlay):

| thr | cands | change | settled | cut | ui-cov | cut-cov | gap |
|---|---|---|---|---|---|---|---|
| 0.008 | 225 | 75 | 58 | 56 | 1.00 | 1.00 | 6 |
| 0.012 | 224 | 75 | 56 | 58 | 1.00 | 1.00 | 6 |
| 0.02 | 225 | 75 | 53 | 62 | 1.00 | 1.00 | 8 |
| 0.03 | 231 | 80 | 57 | 64 | 1.00 | 1.00 | 8 |
| 0.05 | 233 | 78 | 52 | 80 | 0.80 | 1.00 | 10 |
| 0.08 | 204 | 60 | 38 | 86 | 0.70 | 1.00 | 10 |
| 0.15 | 187 | 45 | 28 | 95 | 0.50 | 1.00 | 10 |

Postgres explainer (busy pixels 0.000):

| thr | cands | change | settled | cut | ui-cov | cut-cov | gap |
|---|---|---|---|---|---|---|---|
| 0.008 | 65 | 28 | 22 | 8 | 1.00 | 1.00 | 4 |
| 0.012 | 66 | 31 | 21 | 8 | 1.00 | 1.00 | 4 |
| 0.02 | 70 | 34 | 20 | 9 | 1.00 | 1.00 | 3 |
| 0.03 | 69 | 34 | 18 | 9 | 1.00 | 1.00 | 3 |
| 0.05 | 64 | 34 | 15 | 9 | 1.00 | 1.00 | 5 |
| 0.08 | 53 | 30 | 10 | 9 | 0.62 | 1.00 | 17 |
| 0.15 | 44 | 23 | 7 | 10 | 0.38 | 1.00 | 23 |

VS Code screen recording (busy pixels 0.001):

| thr | cands | change | settled | cut | ui-cov | cut-cov | gap |
|---|---|---|---|---|---|---|---|
| 0.008 | 70 | 42 | 17 | 4 | 1.00 | 1.00 | 16 |
| 0.012 | 44 | 22 | 11 | 4 | 1.00 | 1.00 | 20 |
| 0.02 | 36 | 16 | 9 | 4 | 0.89 | 1.00 | 39 |
| 0.03 | 30 | 11 | 8 | 4 | 0.67 | 1.00 | 47 |
| 0.05 | 29 | 12 | 7 | 4 | 0.61 | 1.00 | 54 |
| 0.08 | 28 | 10 | 8 | 5 | 0.50 | 1.00 | 54 |
| 0.15 | 21 | 9 | 3 | 5 | 0.33 | 1.00 | 60 |

Reading: coverage sits on a plateau up to 0.03 and falls off from 0.05 on every video.
Menus and small dialogs (the VS Code `ui-small` moments) need 0.012 or lower, which is
why they count at deep depth only. The static floor with a webcam overlay masked is
about 0.005, so 0.012 keeps a 2x margin.

## When the evals fail after a change

- `coverage` fails with a missed label: open `frames/diff_series.json` for that video,
  look at the seconds around the label, and decide whether the label time is wrong (fix
  the fixture) or the sampler dropped it (check `--dry-run` output and the cap).
- `dedupe_keeps_ui` fails: the near-duplicate filter ran on a `change` or `settled` frame.
  It must only run on `DEDUPE_REASONS`.
- `extraction` fails on runtime: the thumbnail pass should take under 10 s for 10 minutes
  of video. Check that `ffbin` picked a working ffmpeg.
- `transcript_integrity` fails: caption timestamps are parsed in `fetch_video.py`
  `parse_ts`; keep the fractional part as a string so `080` stays 0.080.
