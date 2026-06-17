# Deck Iteration Review

Use this when generating or revising a PowerPoint deck from a reference deck, brand catalog, or user feedback.

## Failure pattern to avoid

Do not stop at "PPTX was generated". A deck can be technically valid but still fail user review when:

- the reference deck design was not actually followed
- old source-deck terms remain after shallow text replacement
- cards are large but mostly empty
- body text is too small to read in presentation mode
- icons are pasted with ugly background boxes or wrong product context
- the final file is opened/closed by automation while the user is reviewing
- a broad font-size increase creates overlaps because card heights and text boxes were not rebalanced
- screenshots from a source deck are cropped or scaled so the important UI is cut off
- slide deletion is discovered late and video slides/media are missing from the final deck

## Required review loop

Before handoff:

1. Export every slide to images from the actual final PPTX.
2. Inspect the images, not only extracted text.
3. Run a text scan for old product names, old acronyms, placeholder text, and literal escape sequences.
4. Verify slide count, section/story order, and embedded media/video count against the expected deck.
5. Fix visible issues, regenerate/export, and inspect the affected slides again.
6. Only then open the final PPTX for the user.

## Visual checks

For each slide, explicitly check:

- **Density**: no slide should look like a few small words floating in large empty boxes.
- **Readability**: body text should normally be 14-18 pt; avoid shrinking text to fit.
- **Reflow after font changes**: if body text is enlarged, resize cards or simplify content; do not merely force 14pt into the old boxes.
- **Box utilization**: if a card is large, fill it with useful examples, inputs/outputs, outcomes, or decision criteria.
- **Icon fit**: icons must match the product context. Do not use unrelated Copilot family icons.
- **Icon quality**: remove white/off-white backgrounds from cropped PNGs or use real transparent assets. Dark marks on dark cards need a light backplate or an approved inverse asset.
- **Screenshots**: use source screenshots only when they are readable and not cut off. Do not insert a whole rendered slide into a slide unless a slide-within-slide is explicitly intended.
- **Template fidelity**: if the user asked to follow a reference deck, preserve the visual structure, not just the color palette.
- **Old-content removal**: after adapting a reference deck, search for old acronyms, customer scenario terms, prices, offer names, and placeholder strings.
- **Final slide**: do not leave a "coming soon" or empty CTA slide unless the user explicitly wants a placeholder.

## Content adaptation rules

- Replace source-deck business logic, not just names. If a source deck says "AH / SS / TRF", map the slide's purpose to the new offering and rewrite the slide.
- When the user corrects offer semantics, update the deck model first, then slides. Example:
  - VBD standalone is a standalone VBD offer.
  - Designated Engineering Tier 1 / Tier 2 are DE tiers, not generic "T1/T2" labels.
  - If source material says DE Tier 1 includes VBD x3 + engineering hours and DE Tier 2 includes VBD x4 + engineering hours, show that explicitly.
- If a statement is based on internal material, phrase it as an internal basis or assumption; do not make unsupported customer-facing claims.

## Brand asset handling

- Prefer curated brand assets when the user points to an icon catalog.
- If extracting from a rendered catalog slide, crop tightly and make white/off-white pixels transparent before inserting.
- Use product lockups sparingly. A title slide may not need icons if the template already carries brand weight.
- For GitHub Copilot / VS Code decks, do not substitute Microsoft 365 Copilot, Copilot Studio, or unrelated "cowork" icons.
- If a required concept icon is absent, prefer official/local app icons before drawing a simple pictogram. For terminal/CLI concepts, a clean `>_` pictogram is preferable to a random executable/DLL icon.

## Media and recovery checks

- Before any structural edit, save a backup of the user-visible deck.
- For decks with embedded videos, record expected video slide numbers and total media shapes before editing.
- If slides disappear during manual review or automation, do not keep editing the damaged deck. First save the damaged state, then inspect candidate backups and restore the missing slide range from the closest valid deck.
- After restoring, verify:
  - expected slide count
  - expected video count and slide positions
  - agenda/section story flow
  - no duplicated or shifted slide numbers

## File/opening rules

- For viewing, use normal PowerPoint window opening (for example `powerpnt.exe /n <file>`), not long-lived COM sessions.
- For COM edits to an open deck, save only the target presentation and do not call `Application.Quit()`.
- If PowerPoint locks the file, save to a clearly named next artifact; after user acceptance, remove intermediate PPTX files.
- Keep only one final PPTX in the output folder unless the user asks to preserve variants.
- If PowerPoint shows a modal dialog or rejects COM calls, stop batching operations, dismiss the dialog, and re-run validation from the actual open deck before continuing.
