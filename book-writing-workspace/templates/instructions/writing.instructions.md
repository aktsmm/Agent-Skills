---
applyTo: "02_contents/**/*.md"
---

# Writing Instructions

Guidelines for manuscript writing style and quality.

## Style Rules

### Tone

- Use polite/desu-masu style (です・ます調)
- Write natural Japanese (avoid translation-style)
- Keep sentences under 500 characters
- Vary sentence length and endings for natural flow

### Terminology

- Explain technical terms on first use
- Format: Japanese (English) - e.g., 機密性（Confidentiality）
- Use consistent terminology throughout

### Structure

- Abstract -> Concrete -> Re-abstract
- Why -> What to protect -> How to design
- End with practical application, not just theory

## Source Confidence

- Do not write feature behavior, limits, UI paths, metrics, or procedures from guesswork.
- If a point is not verified, do not smooth it into final prose with plausible wording.
- Keep unresolved items in outline or key-points notes as explicit verification tasks, not as normal explanatory sentences.
- Final manuscript files should contain only verified statements or clearly attributed interpretation.
- Avoid fallback phrasing such as "probably", "should be", or similar hedges when they are only hiding missing verification.

## Introduction Pattern

1. Hook
2. Concrete scene
3. Core learning
4. Tomorrow's action
5. Lingering thought

## Summary Pattern

- Key point recap
- Practical next step
- Lingering thought or question
- Bridge to next chapter

## Figures and Lists

| Element      | Rule                                                            |
| ------------ | --------------------------------------------------------------- |
| Bullet lists | Max 3 consecutive in a section, end with prose                  |
| Tables       | Prefer for 3+ item comparisons; keep headers short and scannable |
| Figures      | Plan from outline stage; use for concept, flow, hierarchy, or direction |
| Images       | Format: `![Image: Title](images/fig-X-X-XX.png)`                |

## Diagram and Table Rules

- If a section compares terms, roles, plans, tools, or options, check whether a table is clearer than bullets or prose.
- If a section explains flow, direction, lifecycle, source/target movement, or hierarchy, plan a figure before expanding the prose.
- Keep diagram intent explicit in the outline: note both the visual type and the reader takeaway.
- Use tables for comparison and figures for flow; do not overload a table with process steps that belong in a diagram.
- When using a figure, add 1 to 2 sentences before or after it to tell the reader what to look at.

## Word Count Targets

See `docs/page-allocation.md` for detailed targets per file type.

## Forbidden Patterns

- Overuse of em-dashes for dramatic effect
- Consecutive bullet lists without prose breaks
- Translation-style Japanese
- Sentences over 500 characters
- Speculative statements presented as facts
