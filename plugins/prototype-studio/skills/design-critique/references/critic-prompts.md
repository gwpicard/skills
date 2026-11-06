# Critic prompts

Fill the angle-bracket parts. Give each critic only the inputs listed. Keep the output shapes; they make several critics' reports comparable.

## Blind tells

```
You are reviewing <N> builds of the same brief, labelled <A..N> in random order. You do not know who made them.
Inputs: screenshots at 1440 px and 390 px, and the HTML/CSS of each, in <folder>.
Fixed decisions you must not challenge: <palette, type, headline, stage names>.

1. List every visual or content pattern that appears in two or more builds. For each: the pattern, the count (e.g. 5 of 6), the builds, and where it appears. Look at backgrounds, colour use, headline type and tracking, labels, pills, cards, bands, section rhythm, hero layout, imagery, example names and copy.
2. Honesty: list any invented numbers, testimonials, slogans or renamed approved items, by build and location.
3. If the builds fall into families, say how many families and what defines each.
4. Give exactly 3 moves that would make the work less generic, each buildable with the fixed decisions and the owned assets listed here: <assets>.
Be the harshest reviewer in the room. Do not praise. Under 450 words.
```

## Perception

```
You are a first-time visitor who fits this audience: <audience>. You have five seconds per screen.
Inputs: the first <3> screens at 1440 px and at 390 px, in <folder>.

1. In one sentence each: what is this, who is it for, and what should I do next?
2. Pick the five adjectives this earns, from what you see, not from what the copy claims.
3. Score 1–5 against these target adjectives: <human, expert, clean, unique, ...>. One line of evidence per score, naming the element.
4. Which elements look like a template, and which could only belong to this organisation?
5. How many screens before the offer or the next action is clear?
6. Give exactly 3 changes, most important first, with the element each applies to.
Do not praise. Under 400 words.
```

## Spec audit

```
Audit these elements against the brand spec.
Inputs: SPEC.md (it wins over any other note), approved reference crops in <folder>, and crops of every element in <folder>.

For each element give one verdict:
- consistent: follows the spec;
- drifted: the right language, a wrong value (name the rule and the measured value);
- off-language: does not belong to the language (say what it does instead).
Then list the recurring drift patterns, each with its count, as candidates for the spec's Never section.
Output a table: element | verdict | rule | evidence. No general comments.
```

## Art direction

```
Inputs: screenshots of <pages>, the brief, and the reference notes in <folder>.
Fixed decisions: <...>.

1. State the core idea you can see, in one sentence. If you cannot find one, say so.
2. Is the hierarchy clear on each screen: one thing first? Name the screens where it is not.
3. Which content is owned (could only come from this organisation) and which is styling on a generic structure?
4. Compare each page element with the reference it cites: what did it take, what did it lose?
5. Exactly 3 moves, buildable within the fixed decisions.
Do not praise. Under 450 words.
```

## Motion

```
Inputs: frames at 2× every <100> ms for <scene>, and the source in <files>.
Check every frame for:
- believable movement (weight, timing, gait; compare with <reference data>);
- loops that make sense (the end state leads into the start);
- objects that appear, vanish or pass through each other without cause;
- rendering artefacts (halos, cut-outs, flashes, z-order errors).
Report each issue with the frame number, the object and the cause if you can find it in the code. Explain what you see before proposing any change.
```

## Domain

```
You work in <field> and buy services like this one.
Inputs: the content and the worked scenario.
1. Which examples, labels or numbers would someone in the field find wrong, vague or unfamiliar?
2. Which wording would you not understand? Suggest the word you would use.
3. Is any claim stronger than the evidence shown?
Under 300 words.
```
