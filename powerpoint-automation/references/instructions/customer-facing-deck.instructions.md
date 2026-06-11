# Customer-Facing Deck Rules

Use these rules when creating or revising decks intended to be shown directly to customers, executives, or external audiences.

## Slide Surface vs Speaker Notes

- Slide surfaces must contain only audience-ready content.
- Do not show internal talk tracks, "avoid saying" guidance, dry-run findings, validation notes, file-purpose labels, or implementation/debug notes on visible slides.
- Put presenter guidance, source rationale, assumptions, and caveats in speaker notes.
- Speaker note citations must include usable URLs, not just source names. Example: `Source: Microsoft Scout overview - https://...`.
- If a useful slide is primarily for the presenter, either move the content into notes or mark the slide hidden.

## Template Fidelity

- When the user provides a PowerPoint template, reuse the actual template cover and its placeholders.
- If the user says to use the template's "page 1" or "page 2" design, treat that as a real slide design requirement, not as a slide master/layout hint. Prefer duplicating or visually preserving the actual source slide surface before falling back to a similar layout.
- Do not cover template placeholder text with opaque rectangles or overlaid text boxes; replace or delete the placeholder itself.
- Before handoff, inspect the rendered cover for leftover placeholders such as `Event name`, `presentation`, `XXXXXX`, or old dates.
- Do not add generic labels such as "customer introduction deck" to the slide surface unless the user explicitly requested that wording.

## Open Deck and Coauthoring Safety

- If the target deck is open in PowerPoint, use COM Automation for direct edits.
- Do not use `python-pptx` to overwrite the same open file; this can trigger sync/coauthoring conflict resolution and duplicate slide versions.
- For structural rebuilds, write to a new filename first. Once the user is reviewing a file, perform final touch-ups via COM only.
- Do not call `pres.Close()` for a user-visible deck you did not open solely for read-only validation.

## Source and URL Handling

- Put public source references in a references/appendix slide unless the user asks for per-slide citations.
- Each visible URL must be a real PowerPoint hyperlink, not plain text.
- Use neutral source labels for customer-facing decks. Avoid internal or overly personal labels unless the user wants them.
- Verify hyperlink count after generation.
- If a claim comes from a private customer notification, email, or tenant message, label it as such and do not imply that a public URL proves the exact notification text or date. Separate visible wording into: `Notification says ...` and `Public docs confirm ...`.
- For customer-facing technical decks, put a compact source strip on each factual slide when the slide makes a pricing, deadline, supportability, limitation, or actionability claim. The appendix can hold the full URL list, but it is not a substitute for slide-level citations.
- Presenter notes should use the deck language unless the user asks otherwise. For Japanese customer decks, do not leave English notes such as `Presenter guidance` or `Slide purpose`; localize notes before handoff.
- If screenshots come from the user's environment, mask personal data, customer/tenant names, email addresses, session identifiers, local file names, and other environment-specific details before insertion.
- Do not add a visible "masked" disclaimer unless the user asks for one; put that note in speaker notes instead.
- Visible slide text must not include presenter-only meta language such as "talk track", "how to say this", "explanation tip", "validation note", or "work memo". Convert these to audience wording or move them to speaker notes.

## Images and Screenshots

- Do not dump candidate images into appendix slides unless the user explicitly asks for a contact sheet. Integrate useful images into the narrative slide where they support the point.
- Prefer one clear image per concept slide. If two images are necessary, make them large enough to read and reduce surrounding text.
- Official images can be used as visual anchors, but captions must explain why the image matters to the slide's message.
- If an official image includes "AI-generated content may be incorrect" or similar caveats, avoid using it as factual proof. Use it only as an illustrative visual and keep factual claims in text sourced from documentation.
- After inserting images, render the slide and check that the image is large enough to read. Tiny screenshots are worse than no screenshot.
- If reusing a screenshot from an existing slide, ensure the screenshot itself is inserted, not a cropped render of the whole source slide with its old title/body.
- If the screenshot must be cropped, verify all important UI edges are visible in the rendered output.

## Content Accuracy Review

- Review content separately from visual layout.
- For Microsoft or Azure topics, verify claims against official Microsoft sources before handoff.
- Avoid turning preview features into GA claims. If the deck date is before a stated GA date, use "planned" or "announced for" wording.
- Prefer conservative governance wording when a control is not explicitly documented. For example, say "confirm Microsoft 365 data protection and management controls" rather than over-claiming specific enforcement.
- Use the product's official feature names on slide surfaces. For Microsoft Scout, prefer `Heartbeat` and `Automations`; if the user says "Pulse", explain it as shorthand rather than the official feature name.
- When discussing Skills, verify the actual environment or current docs before labeling something as built-in. If the environment shows additional built-in skills, it may be described as built-in for that environment.
- For Scout-specific positioning, distinguish Microsoft 365 Copilot, Copilot Cowork, GitHub Copilot, and Microsoft Scout instead of treating them as interchangeable.
- If a deck mentions Work IQ, clarify what Work IQ enables: contextual retrieval, semantic work context, people/org/collaboration understanding, Tools, and Workspaces for long-running agent state. Avoid implying Work IQ alone performs the whole workflow.

## Story Flow and Sections

- For customer decks longer than about 10 slides, add PowerPoint sections so the left pane communicates the story structure.
- For multi-session customer decks, include the session number on the file name and slide surface, for example `YYYYMMDD-01_04-topic.pptx` and `Session 1 of 4`.
- Near the end of recurring support decks, include must-decide items such as next meeting date, attendees, owners, and what the customer will try before the next session.
- Carry forward explicit requests from previous meeting notes, such as basic Git/GitHub explanations, but keep them scoped so they support the main story instead of becoming a separate training deck.
- On agenda slides, make main items visually stronger than explanatory sub-lines. Use brand color/bold for main items and muted gray/smaller text for sub-lines; avoid making sub-lines look like links or warnings.
- Recommended flow for product introduction decks:
  1. Why now / announcement context
  2. What it is and how it differs from nearby products
  3. Core capabilities and strengths
  4. Single-shot use cases
  5. Autonomous / scheduled workflow use cases
  6. Architecture, context, and governance
  7. Skills / extensibility / operations
  8. Prerequisites, pilot approach, and references
- Re-check title/body alignment after adding slides. If a slide title says "what is X", the body should define X, not list internal usage notes.
- Keep ambitious use cases credible by framing them as scenarios that combine documented capabilities (files, shell, browser, Microsoft 365, Heartbeat, Automations, sub-agents, skills) rather than unsupported product promises.

## Visual Review Gate

- Render slides to images before final response.
- Check for text cropping, empty cards, placeholder remnants, white-on-white text, and title overlays.
- Review all visible slides; hidden presenter slides are not a substitute for cleaning visible content.
- If card body text is enlarged, re-check `TextRange.BoundHeight` or image output for bottom clipping.
- Check for duplicate text introduced by iterative COM edits, especially footers, slide numbers, and titles.
- Re-run review after sectioning or slide insertion because slide numbers, notes, and flow can shift.
- For decks with media, verify the visible slide count and media slide positions after every restore, insertion, deletion, or reorder operation.
