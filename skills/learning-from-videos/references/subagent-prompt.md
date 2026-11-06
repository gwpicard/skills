# Prompt for the frame-viewing subagent

Use this when there are more than 30 frames. Fill the placeholders, then launch one
general-purpose Agent with the text below. The subagent writes its findings to files so the
main session never holds the images in context. When the main session views frames itself
(30 frames or fewer), follow the same steps 2 to 5 directly.

---

You are inspecting frames from a video so the on-screen content is captured in words,
including what changes from one frame to the next.

Video: {{title}}
Work directory: {{workdir}}
Manifest: {{workdir}}/frames/manifest.md. One row per frame: time, chapter, why it was
picked, how much of the screen changed since the previous frame and where, what was said
in the 4 seconds before and the 4 seconds after.
Contact sheets: {{workdir}}/sheets/ (6 frames each, in order; a yellow box marks the
changed region on UI-change frames).
Pair images: {{workdir}}/pairs/ (for UI changes only: previous frame on the left, this frame
on the right with the yellow box).
{{#focus}}The person wants to use this video to: {{focus}}. Give priority to frames that help with that.{{/focus}}

The "why" column: cut = new shot or slide; change = something changed on a mostly still
screen (a click, a menu, typed text); settled = the end state after typing or dragging;
sample = a periodic frame inside a long run; motion = camera or B-roll movement;
interval = safety net; start = first frame.

Do this in order:

1. Read the manifest fully with the Read tool. Note the chapter boundaries.
2. View every contact sheet in order. For each frame decide whether it carries information
   the transcript does not: code, terminal output, diagrams, tables, slide lists, UI
   layouts, settings values, charts, URLs, file names. Skip talking heads and near-repeats.
3. For rows whose why is "change" or "settled", open the pair image first. State what
   changed inside the box and what action caused it (a menu opened, a value went from X
   to Y, text was typed, a tab was selected). Open the full-size frame only when you must
   transcribe text.
4. For other useful rows, open the full-size frame.
5. Write the observations, split by chapter. One file per chapter that has at least one
   useful frame, at {{workdir}}/frames/observations/NN-<chapter-slug>.md where NN is the
   chapter order starting at 01. When the video has no chapters, split by 10-minute
   blocks (01-00m, 02-10m). Keep each file under 12 KB. If a chapter needs more, split it
   into NN-<slug>-a.md and NN-<slug>-b.md at a frame boundary.

   One entry per useful frame, at most 120 words plus verbatim text:

   ### [mm:ss] f_NNN — short label
   - Type: code | terminal | slide | diagram | table | ui | chart | other
   - Changed since f_PPP: one sentence. Write "new shot" for cuts. Omit for the first frame.
   - What is shown: one to three sentences.
   - Verbatim text: code, commands, labels, field values, exactly as shown. Fenced block
     for code. Mark unreadable characters with `?`. Never invent text that is not visible.
   - Said here: the phrase from "said before" or "said after" that this frame illustrates,
     in a few words, or "not referenced" when the speech does not point at the screen.

   Group frames with no screen content in one line each, for example
   "f_010 to f_014: presenter, no screen content".

   Then write {{workdir}}/frames/observations/00-index.md with one line per file (path,
   chapter, time range, number of entries) and a section "Patterns across frames" for
   anything that repeats: the same repo, the same tool, an evolving diagram, the model
   or setting used at each step, mismatches between what is said and what is shown.

6. Reply with the path of 00-index.md, the list of part files, and three lines on the
   most important on-screen content. Do not paste the files into your reply.
