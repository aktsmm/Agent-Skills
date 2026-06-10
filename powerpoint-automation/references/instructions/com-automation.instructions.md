# PowerPoint COM Automation Rules

Use this reference when editing existing PPTX files, especially files that may already be open in PowerPoint.

## Core Rules

- If the target PPTX is open, use COM Automation with `win32com`; `python-pptx` commonly fails on locked files.
- COM slide indexes are 1-based. `python-pptx` slide indexes are 0-based.
- Prefer direct edits to the existing file. Do not create extra similarly named files unless lock handling requires it.
- Save with `pres.Save()` after edits. If OneDrive sync causes a save error, wait briefly and retry.
- Never call `app.Quit()` unless you own the entire PowerPoint process. Use `ReleaseComObject` (PowerShell) or `del app` (Python) to release the COM reference without killing the application.
- For write operations on a user-visible file, call `pres.Save()` only. Do not call `pres.Close()`; the user needs the file open for review.
- Run Japanese text scripts with `python -X utf8` to avoid PowerShell smart quote and encoding issues.
- Colors are BGR in COM: `#0078D4` becomes `0xD47800`.
- `Font.Bold = -1` means true. Do not use PowerShell `$true` in COM assignments.

## Open Presentation Handling

- Do not assume `app.Presentations(1)` is the target. Search by presentation name or path.
- Guard `Presentation.Name` and `Presentation.FullName` access with `try/except`; automation permission errors can occur.
- If enumeration is unstable, use `DispatchEx` and open explicit paths. Use `ReadOnly=True` for reference decks and `ReadOnly=False` for the edit target.
- For a deck the user is actively viewing, prefer `GetActiveObject("PowerPoint.Application")` and locate the open file by name.
- After ad-hoc edits (slide moves, text changes), release the COM reference but leave the file open. Only `pres.Close()` for read-only verification scripts that opened the file themselves.
- If the user asks for a direct touch-up on an already-open deck, do not rebuild-and-reopen by default. Locate the active presentation, apply the minimal edits with COM, call `pres.Save()`, and leave it open.
- For direct touch-ups, keep edit and verification in the same COM session and audit the active `Presentation` object. Do not verify a stale copied file or a separate read-only presentation unless the task is explicitly read-only.

## Text and Paragraph Editing

- Paragraph separators should be `\r` / `chr(13)`. `\n` may not create real PowerPoint paragraphs.
- Avoid `TextRange.Text = "..."` for append operations because it resets formatting.
- Use `Paragraphs(n).InsertAfter(chr(13) + text)` for append operations, then immediately set the new paragraph font.
- Add a trailing `chr(13)` when needed to prevent newly inserted text from merging with the next paragraph.
- `IndentLevel` is valid from 1 to 5. Setting 0 raises an out-of-range COM error.
- If run boundaries split text, `Runs(r).Text` replacement may miss. Use `Characters(start, length).Text = "new"` for reliable replacement.
- For major paragraph restructuring, clear and rebuild the whole `TextRange.Text` in a single assignment, then reapply per-paragraph formatting. Do not loop over `Paragraphs(n).Text = newValue`: a trailing `\r` in `newValue` silently appends a new paragraph and shifts later indexes, leaving later paragraphs unmodified.
- To insert before the first paragraph, use `InsertBefore(chr(13))`, then set `Paragraphs(1)` text and font.

## Font and Layout Stability

- Japanese font replacement must set `Name`, `NameAscii`, `NameFarEast`, and `NameComplexScript` together.
- Update slide master and custom layouts as well as visible shapes; otherwise placeholder edits can revert to old fonts.
- If a text box has shape-level default bold, `Run.Font.Bold = 0` may not override it. Recreate the text box at the same location and size.
- When replacing most of a slide, do not hide old placeholders with a white rectangle or overlay text boxes. Inspect the shape list first, delete or reuse the real placeholder shapes, or create a new blank slide and move it into position.
- Table cell word wrap should not be set explicitly. `cell.Shape.TextFrame.WordWrap = -1` can raise a bounds error.
- `Slides.Range()` footer/header batch updates can fail. Set `Slides(i).HeadersFooters` per slide.
- Notes can often be accessed through `slide.NotesPage.Shapes.Placeholders(2)` even when `HasNotesPage` is false.

## Bullet Normalization

- If manual symbols such as `■`, `●`, `→`, or `・` are used, set `Bullet.Type = 0` to prevent double bullets.
- If automatic bullets are enabled and `Bullet.Character` is not the standard bullet `8226`, reset `Bullet.Type = 0`.
- Audit both automatic bullets and manual leading symbols; checking only one misses double-bullet cases.
- After slide creation or content insertion, run a final pass that resets bullets for decks using manual symbols.

## Hyperlinks and Reference URLs

- For one URL attached to a whole RefURL text box, prefer shape-level links: `Shape.ActionSettings(1/2).Hyperlink.Address`.
- Use one text box per URL when multiple URLs must be clickable. Avoid packing several URLs into one text box.
- `TextRange.Hyperlinks` is not available. Use `Characters(pos, len).ActionSettings(1).Hyperlink.Address` for character-level links.
- If URL text has leading spaces, detect the offset with `raw.find('http')` before calling `Characters()`.
- Split `#` fragments into `Address` and `SubAddress`; COM may store them separately.
- Hyperlink auditing must inspect `ActionSettings(1/2).Hyperlink`, not only `slide.Hyperlinks`.
- To remove visible hyperlink underlines, remove the hyperlink first, then control `Font.Underline`.

## RefURL Placement

- Shape name: `RefURL`.
- Position: bottom-right or bottom-left. Pick one and keep it consistent across the deck. Recommended margin: 12-16 pt from the side, 2-6 pt from bottom.
- Font: Calibri + BIZ UDPGothic, 13 pt or larger. Typical width: 540 pt at 13 pt, 600 pt at 14 pt to fit Microsoft Learn URLs on one line.
- Show both title and URL. Use either `Page title | URL` or two lines.
- Title color: gray `0x808080`. URL color: blue `0xD47800` / `#0078D4`.
- Use left paragraph alignment for multi-line reference boxes. Set horizontal alignment via `ParagraphFormat.Alignment`; do not assign `TextFrame.HorizontalAnchor` because COM `TextFrame` does not expose it and raises a bounds error. `TextFrame.VerticalAnchor` is supported.
- One URL per text box when multiple URLs must be clickable. Stack them vertically with a small gap (3-4 pt) and recompute top positions after font-size changes.
- Recalculate height after font-size changes using `TextRange.BoundHeight`.
- Recalculate width using `TextRange.BoundWidth + padding`, while keeping the chosen bottom-side anchor.
- Verify `Shape.Left + Shape.Width <= SlideWidth` and `Shape.Top + Shape.Height <= SlideHeight`.
- For Microsoft Learn / Docs URLs, prefer the localized variant (`ja-jp`, `ja`) and verify the page returns 200 before completion.
- Before completion, verify URLs return a valid page and that the displayed title matches the destination.

## Review Gates

- Check hidden slides and do not mistake them for missing content.
- Review notes on all visible slides. Section title slides also need purpose or transition notes.
- Image-heavy slides should not be judged by text volume alone.
- Confirm the story order moves from concept to basics to application to practice.
- After slide moves or insertions, re-check slide numbers and section boundaries.
- Normalize slide number placeholders if they contain non-numeric copied text.
- Flag unsupported numbers in KPIs, success criteria, or examples; add source or mark as example-specific.
- If one slide has inconsistent font size, bold, or color, scan the whole deck for the same issue.
- After font replacement, audit overflow with `TextRange.BoundHeight > Shape.Height`.
- For COM touch-ups, audit text density, hyperlink count, and overflow before releasing the reference; this avoids repeated open/close cycles while the user is reviewing the deck.
- If a COM edit script fails before save, inspect the active deck state before retrying. Do not run multiple partially failing scripts against the same deck; repair or rebuild the affected slide first.
- Move audience-visible navigation paths and URLs from notes to slide body when appropriate.
- Remove empty placeholders left by `Slides.AddSlide()`.
- Prefer integrating useful points from reference decks into existing summary slides instead of copying whole slides.

## Design Defaults

- Body text: 16 pt or larger.
- Reference URLs and annotations: 13 pt or larger.
- Header lines beginning with `■`: blue `#0078D4` / BGR `0xD47800`.
- Body text: `#333333`; navigation lines: gray `#808080`; URLs: blue with hyperlink.
- For code or file paths, use `NameAscii = "Consolas"` with `NameFarEast = "BIZ UDPGothic"`.
- Detect PowerPoint auto-shrink by scanning runs below 13 pt. Fix by reducing text, enlarging placeholders, or splitting slides.

## Section Management

- Add sections with `SectionProperties.AddBeforeSlide(slideIndex, name)`.
- Use prefixes such as `Day1:` and `Day2:` for multi-day workshops.
- After adding or deleting sections, re-check slide numbers and section structure.
- When inserting section cover slides, delete the old section boundary with `SectionProperties.Delete(index, 0)` and re-add it before the correct slide.
- Track moved slides by `SlideID`, not by changing index.
- For large restructures, rebuild all sections by scanning section title layouts and calling `AddBeforeSlide()` again.
- On some template-derived or cloud-synced decks, `SectionProperties.Delete()` or `Rename()` can fail with an error equivalent to "presentation cannot be modified" even when `ReadOnly=0`. If section mutation fails, stop trying to patch the existing deck in place. Instead, build a fresh presentation copy, bring the slides into that clean deck, and add the desired sections there.

## Template Surface Fallbacks

- Some cloud-synced or protected templates can reject `Slides.InsertFromFile`, `Slide.Copy`, `Shapes.AddPicture`, `Shapes.AddShape`, or `Slide.FollowMasterBackground` with an access-denied error. If preserving the exact template surface is still required, render the source template slide to an image, use that image as a full-slide visual surface in a fresh/editable deck, and place editable text on top only after clearing or masking original placeholder text. Treat this as a fallback when real slide duplication is blocked, and disclose it if the user explicitly required fully editable template shapes.
