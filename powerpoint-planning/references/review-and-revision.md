# Review and Revision

Use this reference after a deck, prompt draft, or slide plan exists.

## Review Gates

Section flow:

- Are sections clear and distinct?
- Does the reader understand where they are in the story?
- Are Agenda and divider slides visually distinct from content slides?
- Does the closing section land an implication, action, or decision instead of becoming a crowded recap?

Executive hook:

- Does the opening make clear why the deck matters?
- Is the decision, implication, recommendation, or reader action clear?

Logic and evidence:

- Does the deck move from conclusion to rationale to evidence to implication?
- Are recommendations supported by analysis?
- Are numbers, claims, timelines, and customer facts traceable?
- Are assumptions marked as assumptions?

Customer proposal fit:

- Does the deck name the customer's actual environment, risk, problem, constraint, or decision timing before proposing an answer?
- Does it explain why this solution or vendor is better, safer, faster, more credible, or more unique than plausible alternatives?
- Are differentiation claims supported by evidence, examples, or conservative reasoning instead of slogans?
- If the deck would still make sense with any customer name swapped in, add stronger customer-specific framing or move generic content to an appendix.

Standalone readability:

- Can the reader understand the slide by reading only the title and lead sentence?
- Is the lead sentence a narrative explanation rather than a vague tagline?
- Does the lead sentence take a clear position instead of merely labeling the topic?
- Is the main message short enough to scan quickly, ideally within two lines?
- If the message is long, is the problem unclear thinking, too much information on one slide, or both?
- Does the body explain diagrams, cards, matrices, or flows instead of relying on visuals alone?

Visual hierarchy:

- Is the main message visible within five seconds?
- Is there one clear visual entry point?
- Can the reader tell where to look first, second, and third?
- Are caveats and assumptions quiet?
- Are all boxes, icons, colors, and text blocks shouting at the same volume?

Typography and shapes:

- Is all text 12pt or larger?
- Are titles, leads, body, labels, and notes visually distinct?
- Does card text have comfortable internal padding?
- Do lines, connectors, arrows, and rounded cards align consistently?

AI artifact check:

- Remove vague filler and fake precision.
- Replace decorative icons or visuals that do not explain anything.
- Redesign repeated card grids when the comparison itself is not the point.
- Remove content generic enough to apply to any company or situation.

## Revision Prompt Pattern

Do not say only "make it better". Specify:

- Target slide number or section
- Current issue
- Desired correction
- Design constraint
- Information that must remain unchanged
- Whether section flow should change
- What to make prominent
- What to make quiet
- Desired reading path
- Typography or font-size issue
- Shape, connector, or card alignment issue
- Prohibited changes

Example:

```text
Revise slide 4 so that the reader's eyes land first on the key conclusion, then move to the three supporting reasons, then finally to the caveat note at the bottom. Make the conclusion area visually dominant using a stronger title and a blue highlight band. Keep the three reason cards secondary with smaller headings. Move caveats and assumptions into a quiet footer note. Use Biz UDP Gothic when available and do not use text smaller than 12pt anywhere. Do not give all elements the same size, color, or emphasis. Keep the current facts and slide topic unchanged.
```

## Human Review Triggers

Require human review before final use when the deck is customer-facing, executive-facing, legally sensitive, brand-sensitive, externally distributed, or contains unapproved hypotheses, customer facts, contract terms, prices, dates, staffing, commitments, or generated images that could imply a real person, customer, brand, protected character, or copyrighted asset.
