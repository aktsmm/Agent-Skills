# Prompting and Execution

Use this reference when producing a production brief or prompt for local PowerPoint work, manual slide creation, Copilot Chat, PowerPoint for the web / Edit with Copilot, a human designer, or a separate slide production workflow.

## Prompt Must Include

- Audience
- Purpose
- Usage context
- Slide count or density target
- Section architecture
- Storyline
- Slide-by-slide instructions
- Style mode
- Design direction
- Typography requirements
- Page-level emphasis instructions
- Anti-AI-slide requirements
- Source handling rules
- Image generation instructions when needed
- Human review conditions

## General Instruction Block

```text
Create a high-quality business PowerPoint deck. Prioritize information clarity, storyline, section flow, and reader action over decoration. Each slide should be readable as a standalone page, but the deck should also have clear section-level progression. The slide title and lead sentence should be enough for the reader to understand the point of the slide. Lead sentences must be careful narrative explanations, not short teaser copy. Use visual structure for the body, but do not make the body overly schematic; include narrative explanatory text that helps the reader interpret diagrams, tables, flows, or cards. Use plain descriptive section titles and slide titles. Avoid decorative writing and excessive emotional messaging. Do not invent unsupported numbers, customer facts, prices, dates, commitments, or source claims.
```

## Typography Block

```text
Use Biz UDP Gothic as the primary font when available. Do not use text smaller than 12pt anywhere. Use at least 30pt for slide titles, 18pt for lead sentences, 14pt for main body text, and 12pt for labels, card text, footnotes, caveats, source notes, and quiet notes. If content does not fit, reduce text volume or split the slide instead of shrinking the font.
```

## Section Block

```text
Organize the deck into clear sections. Add section divider slides when helpful, even if slide count increases. Section divider slides should be simple navigation pages with plain descriptive section titles and a one-sentence purpose. Agenda and section divider slides must use a clearly different visual template from normal content slides and should be recognizable as navigation or transition slides at a glance.
```

## Page-Emphasis Block

```text
Do not make every element equally prominent. Each slide must have one dominant primary message, one clear visual entry point, a deliberate reading path, supporting evidence that stays secondary, and quiet areas for notes, caveats, or assumptions.
```

## Message-Discipline Block

```text
Each slide must have one clear, position-taking message, not a neutral topic label. Keep the message short enough to scan quickly, ideally within two lines. If the message cannot be shortened, either clarify the claim or split the slide instead of shrinking the font or burying the point in body text.
```

## Card-Padding Block

```text
Use comfortable internal padding inside all cards, rounded rectangles, callout boxes, timeline boxes, and process boxes. Text must not touch or visually hug the shape border, especially the top-left corner. If content does not fit with adequate padding and 12pt minimum font size, reduce wording, split the card, or simplify the layout rather than pushing text to the edge.
```

## Internal-Friendly Image Guidance

```text
Use friendly, bright, scenario-based visuals where they improve understanding. Prefer simple metaphorical images over photorealistic business stock imagery. Avoid logos, real people, copyrighted characters, and brand imitation.
```

## PowerPoint for the Web Notes

When using PowerPoint for the web or Edit with Copilot, treat it as one execution path, not the skill's identity.

- Open the target deck or new deck.
- Confirm model, image, brand, and template options when available before submitting a long prompt.
- Paste the production prompt only after the execution settings are clear.
- Save the result and move to review.

If actual PPTX export, rendering, hyperlink audit, or COM editing is needed, switch to an appropriate PPTX file-operation workflow.
