# Writing the storyboard

The storyboard is the blueprint: when, what is on screen, what is said. The quality of the video is decided here. Show it to the user before building the HTML (if it is a checkpoint).

## Principles

- **Open with a question**, the viewer's situation or the news itself; do not open with a feature list.
- **Show structure in the middle**: diagrams, flows, comparisons, timelines, charts, built up by motion. One idea per screen.
- **Close with the takeaway and the next step** (and the "as of" line for time-sensitive topics).
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
