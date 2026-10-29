# Late-Stage Revision Review

Use this workflow when a manuscript has already been handed to a publisher or printer and further changes (product-fact updates, trims, wording fixes) must be reviewed by the author in small, reversible steps. Project-local commands and exam- or topic-specific rules stay in the target repository.

## Scope Decisions

- Pin the handed-over commit and report every change as a diff against it. When the working tree and the repository normalize newlines differently, compare with `git diff --stat --ignore-space-at-eol <base> -- <manuscript>`.
- For an exam-prep book, keep or cut by the current official skills-measured document and the book's overview doc. Re-check that the document is still the latest version before deciding. A legacy question bank shows past emphasis only; it predates the current objectives, so zero hits for a topic is not proof that it is out of scope. Page ratios are not a criterion.
- Keep passages that are short but important, passages carrying the author's own experience or opinion, and features the owner chose to promote. Trim over-detailed procedure outside the objectives. Defer cuts that are coupled to figures or tables when a print deadline makes layout shifts costly.
- Treat roundup articles, summaries, and other AI output as unverified. Locate each quoted official sentence in the primary page; if it is absent, drop the claim and do not state a GA or preview status.
- When a behavior depends on surface or version (for example a UI element that one runtime shows and another does not), record the condition per source and ask the owner to confirm on the real screen. Write the condition into the text rather than an absolute.

## Review Loop

1. Present one chapter at a time as a numbered table: `#`, line, before -> after, why, what is lost, risk. Mark items that change meaning separately.
2. Apply each edit with the editor's edit tool, one location per edit, not with a script that rewrites files, so the IDE change view tracks them. If that view does not show earlier edits, open `code --diff <baseline copy> <file>` for the chapter.
3. The owner approves or rejects by number. Restore a rejected item with the exact baseline sentence, then compare the paragraph with the baseline after normalizing newlines; a partial-string replacement can silently drop the rest of the sentence.
4. After each batch, run the manuscript gates and the question-grounding check, and report per-chapter character deltas against the pre-work baseline.
5. After a bulk apply, have a critic from a different model family check every deleted or rewritten sentence for dangling references, dropped conditions or cautions, and new unsupported claims. Verify its findings in the file before acting (one run found two real blockers in 86 edits: a lost preview caution and an invented trend claim).
6. Keep chapter-end and final questions byte-identical to the baseline unless the owner asks otherwise; verify by comparing the question blocks.
