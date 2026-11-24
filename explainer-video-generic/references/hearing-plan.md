# Brief and production plan (Step 1)

When asked for a video, do not start building. Do **a short brief -> a production plan -> the user's OK**, then the storyboard. This prevents rework.

## 1. Read first (before asking)

Fill in everything the request, attachments and conversation already answer. Do not ask about those.

| Item | Where to look |
|---|---|
| Source | attached/linked files, pasted text, "about X" topic |
| Pattern | recording attached -> C; "monthly", "brief" -> B; otherwise A |
| Audience / goal | "for executives", "for customers", "internal training", "for social" |
| Length | "about 3 minutes", "short", "one minute" |
| Voice / language | "male voice", "no narration", "in English", "Japanese version" |
| Reference | "like this video" (attached video/HTML) |

Skim the source for size and structure (used to propose length and episode count).

## 2. The brief (one round, multiple choice)

Use the agent's question tool (multiple choice with a recommended default first). Ask the open items by importance, **max 4 questions in one round**. If there is no question tool, send one short numbered message with defaults and accept "defaults are fine".

| Order | Question | Options (first = recommended default) |
|---|---|---|
| 1 | Who is the audience? | Executives / decision makers; practitioners; general public; internal team; learners |
| 2 | Length and count? | One video, 2-3 min; short (<= 1 min); one video, ~5 min; series of several |
| 3 | Tone? | Calm and professional; bright and upbeat; technical with many diagrams; match the reference |
| 4 | Voice and music? | Female voice + subtle BGM; male voice + subtle BGM; upbeat BGM (`pop`/`tech`, for a lively tone); voice only; no audio (captions only) |
| 5 | Where will it be used? | Public / customer-facing (no confidential data); internal only |
| 6 | Language? | Same as the request; English; Japanese; both |
| 7 | Must include / avoid? | Nothing special; free text |
| * | **Where should I pause for your approval?** (after the plan) | Storyboard only, then build to MP4 (recommended); storyboard and motion preview; no pauses; motion preview only |

- The checkpoint question (*) is **always asked**; choose the other three from 1-7 by importance.
- Items 5-7 can be defaulted from context; list them in the plan under "defaults used" (default: public-safe, language of the request, nothing special).
- Ask once. After the answers, do not ask more; go to the plan.
- If there is no source at all, also ask what the topic/material is. Without an answer, stop; do not guess.

### Skip the brief when

- The user says "just do it", "no questions", "decide for me".
- A storyboard or production brief is already supplied (only voice/BGM left to decide).
- The request is a fix to an existing video ("change scene 3").

Still show a short plan and get OK (except for fixes to an existing video). If there is no source or topic, always ask what to make.

## 3. The production plan

Write `{slug}_plan.md` from the template, summarize it in chat, and ask whether to proceed.

- Outline only (scene titles and purposes). Narration lines come with the storyboard.
- For long/large material propose "build episode 1 (or the first minute) first".
- Include time estimates.

### Template

```markdown
# {Video title (working)} production plan

## 1. Purpose
- Audience:
- What viewers should understand afterwards: (1-3 points)
- Where it will be used:

## 2. Specification
| Item | Content |
|---|---|
| Pattern | A: from material / B: with production brief / C: from demo recordings |
| Count and length | e.g. 1 video, ~2:30 (about 6 scenes) |
| Source | file names / URLs (versions, dates) |
| Tone | e.g. calm and professional; color meaning: green = company, orange = decline |
| Language and voice | e.g. English, en-US-AriaNeural (edge-tts) |
| BGM | subtle synthesized BGM (no rights issues) |
| Quality | Full HD 1920x1080, 30 fps |
| Logos / icons | user set > web (license recorded) > line icons |
| Visibility | public-safe / internal |

## 3. Outline (draft)
| # | Scene | Purpose | Approx. |
|---|---|---|---|
| 1 | Hook | start from the viewer's question | 15 s |

## 4. Process and checkpoints
- Deliverable: **MP4 with audio**
- Pause for approval at: (e.g. storyboard only; then straight to MP4)
1. Storyboard  2. HTML animation + motion preview  3. Narration + BGM, final MP4

## 5. Estimates
- Narration: N lines, one TTS call each (backend)
- Rendering time: about 1.3-2x the video length
- Note: real narration often changes total length by 10-20% versus the estimate

## 6. Defaults used / open points
- Defaults used:
- Not in the source (so not included):

## 7. Deliverables and file names
- `{Title}_YYYYMMDD.mp4`, `.srt`, editable `.html`, contact sheet `.png`, storyboard, plan
- Final screen: "Information as of {date}"
```

## 4. After approval

- Proceed to the storyboard. Pause only at the agreed checkpoints; elsewhere give a short update and continue.
- If the user asks for changes, update the plan and confirm once more.
- Audience, tone, length, voice and visibility chosen here apply to storyboard, HTML and narration. Update the plan before deviating.
