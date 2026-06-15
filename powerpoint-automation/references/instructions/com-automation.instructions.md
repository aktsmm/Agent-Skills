# PowerPoint COM Automation Rules

Use this reference when editing existing PPTX files, especially files that may already be open in PowerPoint.

## Core Rules

- If the target PPTX is open, use COM Automation with `win32com`; `python-pptx` commonly fails on locked files.
- COM slide indexes are 1-based. `python-pptx` slide indexes are 0-based.
- Prefer direct edits to the existing file. Do not create extra similarly named files unless lock handling requires it.
- Save with `pres.Save()` after edits. If OneDrive sync causes a save error, wait briefly and retry.
- For OneDrive/SharePoint templates or slide-master work, do not assume a successful COM save preserved OpenXML `.pptx` packaging. Verify the saved file is a ZIP package (`PK` header / `zipfile.is_zipfile`) before doing python-pptx or package-level edits.
- Never call `app.Quit()` unless you own the entire PowerPoint process. Use `ReleaseComObject` (PowerShell) or `del app` (Python) to release the COM reference without killing the application.
- For write operations on a user-visible file, call `pres.Save()` only. Do not call `pres.Close()`; the user needs the file open for review.
- Run Japanese text scripts with `python -X utf8` to avoid PowerShell smart quote and encoding issues.
- Colors are BGR in COM: `#0078D4` becomes `0xD47800`.
- `Font.Bold = -1` means true. Do not use PowerShell `$true` in COM assignments.
- `Shape.Adjustments.Item(n) = value` raises SyntaxError in Python (assignment to function call). Use `Shape.Adjustments.SetItem(n, value)` for rounded-rect corner radius etc.
- Iterating `for pres in app.Presentations` can raise `自動化の権限がありません` on some open decks (e.g., cloud-protected or hidden window). Iterate by index with `try/except`: `for i in range(1, app.Presentations.Count+1): try: p = app.Presentations(i) ...`.

## Open Presentation Handling

- Do not assume `app.Presentations(1)` is the target. Search by presentation name or path.
- Guard `Presentation.Name` and `Presentation.FullName` access with `try/except`; automation permission errors can occur.
- For OneDrive-synced files, `Presentation.FullName` may resolve to a SharePoint URL even when opened from a local path. Match by basename as well as full path.
- Read-only presentations can still hold a OneDrive/PowerPoint lock and block rename/move/delete. Close every matching open presentation by basename before filesystem operations.
- If PowerPoint shows a coauthoring/競合の解決 dialog, stop automation and resolve/close the dialog before continuing. Do not keep running file operations while the dialog is open.
- Opening a OneDrive deck for review can still change timestamps, locks, or packaging. Keep a validated temp artifact for automation, and treat the user-opened file as a review surface until it is closed and revalidated.
- For read-only extraction from OneDrive-synced legacy `.ppt` files, direct `Presentations.Open()` can fail when the file is a reparse point. Copy the file to a local workspace temp folder first, then open the copy with `ReadOnly=True` / `WithWindow=False` or equivalent COM flags.
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

- `CustomLayouts.Add(idx)` auto-inserts Title / Footer / SlideNumber placeholders. Slides switched to the new layout inherit empty "タイトルを入力" ghosts. Delete unwanted placeholders from the layout AND from each affected slide (`sh.Type == 14` placeholder, delete those with empty `TextFrame.TextRange.Text`).
- For layout-driven backgrounds: `lay.FollowMasterBackground = 0`; `lay.Background.Fill.Solid()`; `lay.Background.Fill.ForeColor.RGB = COLOR`. Then delete per-slide full-slide background rectangles (detect with `Left<5, Top<5, Width>950, Height>530, Type==1`). Bake repeating shapes (vertical bars, accent rules) into the layout itself.
- `Slides.InsertFromFile(src_path, after_index, start, end)` copies slides from another pptx and inherits theme/fonts of the target deck. Useful for community-title / self-intro templates. After insert, fill placeholders by name (`"Title"`, `"Subtitle"`) and set `SlideShowTransition.Hidden = -1` for variant slides.
- Japanese font replacement must set `Name`, `NameAscii`, `NameFarEast`, and `NameComplexScript` together.
- Update slide master and custom layouts as well as visible shapes; otherwise placeholder edits can revert to old fonts.
- For reusable templates, sample slide text is not enough. Put prompt text, default fonts, slide numbers, reusable background art, and reusable image placeholders on `SlideMaster.CustomLayouts`; remove literal placeholder strings from sample slides.
- When a sample slide's background or image frame is unique, create/assign a distinct custom layout for that surface before moving art to the layout. Shared layouts should only contain genuinely shared design elements.
- To verify reusable layouts, add temporary preview slides to the same presentation/copy that owns the layouts. Do not pass a `CustomLayout` object from one presentation into `Slides.AddSlide()` on another presentation.
- If a text box has shape-level default bold, `Run.Font.Bold = 0` may not override it. Recreate the text box at the same location and size.
- When replacing most of a slide, do not hide old placeholders with a white rectangle or overlay text boxes. Inspect the shape list first, delete or reuse the real placeholder shapes, or create a new blank slide and move it into position.
- For visual touch-ups on an existing slide, never assume a new card/shape covers old content. Hide/delete the original title, bullet, table, or callout shapes explicitly, then export the active deck and inspect the affected slide image before continuing.
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
- Before adding or updating RefURL boxes, delete existing `RefURL*` shapes and bottom-area URL text boxes. Repeated post-processing can otherwise leave duplicate visible citations.
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
- Footer page-number renumber heuristic: scan all shapes per slide, find textboxes where text `isdigit()` and `Top > 490` and `Left > 800` (typical bottom-right corner), and rewrite to `str(SlideIndex)`. Run after any insert/move/delete.
- Normalize slide number placeholders if they contain non-numeric copied text.
- Flag unsupported numbers in KPIs, success criteria, or examples; add source or mark as example-specific.
- If one slide has inconsistent font size, bold, or color, scan the whole deck for the same issue.
- After font replacement, audit overflow with `TextRange.BoundHeight > Shape.Height`.
- Safe text-size bump algorithm for small-text cleanup: compute current fill = `TextRange.BoundHeight / Shape.Height`; predict new_fill = fill * (new_size / current_size); accept only if predicted ≤ 0.95; after applying, re-measure actual fill and step down 1pt at a time until ≤ 1.0. Skip URLs (`startswith('http')`), code paths (`startswith('~','/')`), and footer textboxes (`Top > 490`).
- After broad font normalization, re-render representative body slides as well as table slides. A geometry-only check can miss accidental style changes such as body text being promoted to title size/color.
- For tables intended for presentation, keep body cells at 16 pt or larger when space allows; center header text horizontally and vertically, and shorten wording or rebalance row/column sizes instead of shrinking below the readability target.
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
