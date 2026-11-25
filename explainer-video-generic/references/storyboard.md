# Writing the storyboard

The storyboard is the blueprint: when, what is on screen, what is said. The quality of the video is decided here. Show it to the user before building the HTML (if it is a checkpoint).

## Principles

- **Open the way agreed in the brief**, including any title card / agenda scene (see `hearing-plan.md`). Never default to a question opening; do not open with an unframed feature list.
- **Show structure in the middle**: diagrams, flows, comparisons, timelines, charts, built up by motion. One idea per screen.
- **Each video stands alone.** Close it on the takeaway and what it actually showed (what a person still verifies), plus the "as of" line for time-sensitive topics; do not end on a planned next demo or an untested capability. Teasers for unperformed work read as promises and blur what is verified. Build the follow-up as its own video once it has been shown; in a series, each episode must still make sense by itself.
- **Analogies help** for technical topics (a library index, a parcel route).
- **10-30 seconds per scene, 2-5 narration lines**, each line 1-2 sentences.
- **Timing comes from the narration**: about 6.5 characters/s for Japanese/Chinese, about 2.5 words/s for English/Latin scripts, plus pauses. The real TTS audio later replaces these estimates.
- **Keep it short**: 1.5-4 minutes; split longer material into episodes.
- **Match the reference** if the user supplied one.
- **No facts beyond the source.** Mark invented illustrations "(example)". Put dates on figures. Product/feature claims need an official-documentation URL under Sources; preview/beta features get a "preview" caption.
- **Icons from the start.** In each scene's Screen note, name the real icon each product/service uses (and its source); mark "no icon found" only after trying every source in `icons.md`.
- **Name the product in full.** Use its official full name at first mention and keep the distinguishing part afterwards ("SRE agent", not "the agent"); never shorten to a generic noun other products share. Apply it to narration, captions, section labels and subtitles. Ask the user for the localized official name if unsure.
- **Attribute to the owner, not the document site.** Narrate "Microsoft recommends ..." rather than "the docs site says ..."; the document title and URL go under Sources. Show an on-screen source line only when the user asks for one.
- **Numbers on screen** are rendered from data in the HTML (e.g. chart points), so they match the narration exactly.
- **Real screenshots move where it helps and rest where it matters.** Push in (`zoomFrame`, `engine-guide.md`) on the part each narration line is about, with a highlight chip or card beside it; hold still while the viewer has to read a prompt, a result or a table (give it at least the time the line takes to read), and move again only when the narration moves on. Viewers called the zoomed version "dynamic and much better" than static frames with a highlight box. Do not zoom constantly: motion without a reason is noise.
- **Define a term where it first appears.** A viewer who sees "the command" cold asks what it is. Give a one-line premise (a label or a short scene) for every product feature or term the story depends on, and use one name for it everywhere. If a demo's "match" relies on a trace the test setup itself left (an injected fault that appears in an audit log), say so on screen.
- **Tell it as a story** when the audience is not experts: a situation (who is on call and what happens), then the steps, then the answer check, then the next step.
- **Demos of an AI or automation result**: show input -> what it did -> result, then close with an answer check (what was really injected or true vs what the tool reported; which parts matched, which a person still verifies). When the tool itself says "unconfirmed", write "narrowed down", not "identified"; state the observation count ("one trial"); say what the tool was or was not given only if the owner confirmed it.

## Fix the meaning of colors

Decide once and keep it: e.g. brand color = the main subject, green = gains/good, orange = declines, gold = the one thing to remember, navy = text. Avoid red (reads as an error) unless the meaning is danger.

## Template

```markdown
# {Title} storyboard v0.1

## 0. Premise
- Goal: (who, what to convey, what they should think afterwards)
- Audience:
- Target length: (e.g. 2:30) / 16:9 (1920x1080)
- Source: (files, URLs, dates)
- Reference: (if any)

## 1. Look and rules
- Color meaning:
- On-screen text short (<= 20 characters per line); captions at the bottom
- Section label top-left (e.g. "Timeline", "The stock", "Takeaway")
- Avoid: feature lists, unsupported numbers, exaggeration, speculation about people

## 2. Scenes

### Scene 1: {title} (about {s} s)
- Screen: (what is where and how it moves; which narration line triggers what)
- Captions: "..." (sub: "...")
- Narration:
  1. "..."
  2. "..."
- Motion: (fade-in, line draws, highlight frame, ...)

### Scene 2: ...

## 3. Readings (for TTS)
| Written | Spoken |
|---|---|

## 4. Sources
| # | Source | URL / date |
```

## Several episodes

Write one overview first (how many episodes, what each conveys), then one storyboard file per episode. Build episode 1, get approval, then reuse its HTML as the template for the rest.
