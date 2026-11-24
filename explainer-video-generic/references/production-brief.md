# Production brief (pattern B)

An optional Markdown document between the storyboard and the HTML. All instructions for the build live in one file, which helps when:

- you rebuild a video regularly and replace only part of it (monthly update),
- design or wording rules are strict and anyone must get the same result,
- the brief is written in one tool/chat and the HTML build happens in another.

## Flow

1. Storyboard (what to use, what to say).
2. Production brief from the template below.
3. Build the HTML strictly from the brief (edit `SCENES` of the template).
4. Review/fix the HTML, render the silent MP4, then narration + BGM.

## Template

```markdown
# {Video name} production brief

| Item | Content |
|---|---|
| Version | v1.0 (history at the end) |
| Use | (who sees it, why) |
| Audience | |
| Method | single-HTML Canvas animation + MP4 render (explainer-video skill) |
| Structure | (e.g. first half 120 s "what does not change" + second half 60 s "latest" (replaced monthly)) |

## 1. Purpose and goals
### 1.1 Purpose
### 1.2 What viewers should understand (success criteria)
1. ...

## 2. Basic instructions to the builder (must read)
Terms: **MUST** = always (stop and report if impossible), **SHOULD** = by default, **MAY** = if time permits.
### 2.1 Deliverables (MUST)
| # | Deliverable | Format | Content |
### 2.2 Absolute rules (MUST)
1. Draw each frame as a pure function of time t (no randomness, no current time, no previous-frame state).
2. Canvas 2D only; no CSS animation for the main content.
3. Captions, narration and timings live in the data at the top; never hard-code them in drawing code.
4. No external CDN or web fonts.
5. Do not redraw or imitate logos; use supplied assets or a placeholder (rounded box with the name).
6. Say nothing the sources do not support.
### 2.3 After building (MUST)
1. Report the checklist in chapter 11.
2. Check a mid-shot still of every shot for overflow/overlap.
3. Render 0-5 s first, then the whole video.
4. Report resolution, frame rate, duration, codec.

## 3. Core message
### 3.1 One-sentence message
### 3.2 Pillars
| # | Pillar | How it is shown | Source # |
### 3.3 Wording rules (MUST): allowed / forbidden phrasing

## 4. Design system
### 4.1 16:9, 1920x1080 (or 4K), 30 fps, total length, safe area, tone
### 4.2 Colors (name, purpose, value); restrict special colors
### 4.3 Fonts   ### 4.4 Text sizes (kind, size, weight, max characters)
### 4.5 Motion principles (in/out, move, shot transitions, forbidden motions)
### 4.6 Icons/screens ("illustrative screen" notes, logo usage)

## 5. Structure and timeline
| ID | Start | End | Length | Content |
- Narration pace: stay within about 6.5 characters/s (CJK) or 2.5 words/s (Latin) and confirm that real audio fits each shot.

## 6. Shot instructions
### A1 | {headline} (0:00-0:12)
- Screen:
- Captions: "..." (verbatim)
- Narration: "..."
- Motion:

## 7. Replaceable part (if updated regularly)
### 7.1 Common frame layout   7.2 This month's content   7.3 Replacement steps

## 8. HTML implementation (when using this skill: "follow references/engine-guide.md")

## 9. MP4 export: H.264, fixed 30 fps, yuv420p, faststart, no audio (narration/BGM added later)

## 10. Audio: voice, readings, BGM mood, ducking amount, -16 LUFS

## 11. Quality checklist (acceptance)
### 11.1 Content   11.2 Design   11.3 Technical

## 12. Wording and compliance
- Things that must not appear on screen or in narration (competitor names, comparative numbers, unreleased info, private individuals).
- Note rules (illustrative screen, availability, "may change").
- Pre-release checks (availability, region, brand usage).

## 13. Sources
| # | Source | URL |

## Appendix A: the prompt handed to the builder
## Revision history
```

## Example prompt for the builder

```
Follow the attached production brief strictly and build the explainer video as a single HTML file.
1. Obey every MUST in chapter 2.
2. Use the captions and narration of chapter 6 verbatim.
3. Do not put anything forbidden by chapter 12 on screen or in narration.
When done: report the chapter 11 checklist; check a mid-shot still of every shot for overflow; render 0-5 s first and then the full video; report anything you could not do and why.
```

## Monthly replacement

Keep drawing code and the first half unchanged; update only the data of the replaceable part (captions, narration, badges). Keep each slot's length so the total stays the same. Re-synthesize only changed lines (`synth` caches the rest).
