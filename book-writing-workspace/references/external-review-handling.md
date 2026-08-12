# External Review Handling

How to take reviewer issues, pull requests, and publisher proof comments into a manuscript without losing the reviewer, and without importing a wrong claim.

## Decide adoption per point, not per pull request

A single pull request usually mixes correct fact fixes, wording preferences, and claims that no longer match the source. Split it and rule on each point. Adopting or rejecting the whole request wastes the correct half.

Record three outcomes only: adopted, adopted with change, rejected. "Adopted with change" needs the reason for the change, or the reviewer reads it as a silent override.

## Merge a contributor's pull request rather than retyping it

Merging is the default, because it preserves the contribution in the history for free: the attribution and the request's own merged state. Retyping the change locally and closing the request leaves the discussion visible but severs that linkage, and it silently drops whatever you failed to copy across.

Overlapping edits are not a reason to skip the merge. When the manuscript has already changed the same lines, the conflict has to be settled by hand either way, so settle it on your side and merge. A fork-based request that does not allow maintainer edits still merges: take it locally, resolve the conflict there, and land it on the base branch with a merge that keeps the request's own commits reachable. A local squash or cherry-pick drops them, and a forge that reads merged state from reachability then stops recognising the request — the forge's own squash merge button is unaffected. When the base branch refuses a direct push, route the resolved work through the workspace's normal request path rather than closing the original.

Merging by request and ruling by point still coexist. When a request mixes adopted and rejected points, merge it and correct the rejected part in the commit that resolves the merge or in the one right after it, then name the points you changed back in the reply.

Keep generated artifacts out of contributor requests. Built output — typeset files, converted sources, rendered pages — widens conflicts and is often binary, so ask for source-only changes and regenerate the output yourself after the merge, unless the workspace's own release rules require the artifacts inside the request.

Close a request without merging when the contributor withdrew it, when none of its points is adopted, or when it carries material that must not enter the history at all for rights or confidentiality reasons. That last case outranks the rule about mixed requests: do not merge such a request for the sake of a useful point elsewhere in it, carry that point by hand instead. Name the reason in the reply. On the rare path where you land a contributor's work by hand, every commit carrying it needs a co-authorship trailer with the name and address the contributor wants used for that purpose. Their existing commits identify them, but a visible address is not consent — ask which one to use.

Fork-based requests that allow maintainer edits offer a third path: review the request, propose the exact change, and apply it yourself, which records both people. Send anything a primary source settles uniquely down that path, and hand anything that needs the contributor's intent back to them.

A truncated or half-finished edit is usually an attempt to replace an empty phrase with something concrete. Recover the intent from the surrounding voice before rewriting it, and count how many times the same empty phrase appears elsewhere.

Where repository-level instructions set a conflicting rule for external review intake, follow them and use this section for what they leave undecided.

## A notation complaint may be a defect in the notation rule

Before applying a complaint about terminology or notation, test whether the written rule actually decides the case. When two readings of the rule both pass, the complaint found a gap in the rule rather than a slip in the manuscript.

Rebuild the rule from counted usage across the manuscript instead of from taste, and put that count in the reply. A rule that ranks its own criteria settles the next case without another round.

## Proof comments arrive as PDF annotations, not as text

Once a book reaches typesetting, review stops arriving as issues and starts arriving as an annotated PDF. Do not read every page. Extract the annotations mechanically into one row per comment, then rule on the rows.

Editors mix two kinds of annotation in the same file: instructions the typesetter already acted on, and questions that need an author decision. Filter on the marker the editor uses for the latter, and state the count of the remainder explicitly so nobody assumes it was skipped. When a publisher uses no marker at all, classify by intent instead: anything phrased as a question, a confirmation request, or an approval request needs an author decision.

The extractor must fail loudly. Exit non-zero when an input file is missing or an annotation cannot be read. Counts become the basis for the adoption record, so a silently partial result is worse than no result.

## Resolve what an annotation points at, not just what it says

Annotation text alone is often unanchored. "Should the T and R be capitals?" names no word, and "may we add a screenshot here?" names no place. Ruling on those from the comment text is guesswork.

Extract the anchor mechanically. A highlight carries a rectangle, so clipping the page text to that rectangle returns the exact string the editor marked. A sticky note carries only a small icon rectangle and clipping returns nothing useful, so pull the whole page text and locate the comment by what surrounds the note.

Text pulled out through a shell pipe can arrive mis-decoded when the console encoding differs from the file. Write the extracted text to a file from inside the extractor with an explicit encoding instead of redirecting stdout.

## Treat unfamiliar typeset elements as placeholders until proven otherwise

A proof carries page furniture the manuscript never had: chapter frontispieces, straplines, running heads. Some of it is finished copy the editor wrote and some is filler that only looks finished, and the two are indistinguishable from a summary of the proof. Guessing wrong produces a reply that thanks the editor for text nobody wrote.

Extract those pages as text and compare them against each other. Repetition is the tell: the same paragraph on every chapter opener is a strong signal of filler, and an editor's "to be updated" note on two of them says nothing about the rest. Treat the reading as provisional until the editor confirms it, since a house style that reuses one lead across chapters would look identical.

Once it is filler, settle who writes the replacement before drafting any reply. When it falls to the author, the text also needs a home in the manuscript, marked so the converter can emit it. Otherwise the only copy lives in the typeset page and the two drift apart on the next revision.

Do not size the replacement from the filler. Measuring a placeholder tells you what the designer typed, not what the frame holds. Write to the intent, measure the range you produced, and hand that range back with an explicit offer to cut. Trimming approved prose to hit an inferred number is the worse trade.

## Map PDF pages to printed folios before quoting any page

PDF page numbers and printed folios do not line up. Front matter uses roman numerals, and a proof is often delivered split into volumes that each restart at PDF page 1.

Derive the offset, do not assume it. Verify it against at least two known landmarks whose printed page is visible, such as chapter opener pages and end-of-chapter summaries. The same landmark-detection technique measures chapter lengths in [Re:VIEW PDF tips](review-pdf-tips.md); keep the two consistent when either changes. Quote printed folios in every reply; the editor has no view of your PDF page numbers.

One printed page frequently carries several comments, so the folio alone is not a unique key. Identify a comment by folio plus a short quote of its text.

## Find which revision the proof was typeset from

A proof is built from whatever the publisher held, not from your current source. When comments stop matching the manuscript, suspect a version gap before assuming the editor erred. The tells are specific: a disputed answer key that reads as correct on the page, a question about a sentence you already rewrote, an exam item that is not the one you wrote.

Bracket the typeset revision with sentinels rather than guessing at dates. Pick text whose history you can query: a wording you corrected, a paragraph you added, an item you replaced. Whether each one appears in the proof sets a lower or an upper bound, and two bounds that meet identify the revision.

The size of the gap decides the order of work, so diff that revision against current and read what the untouched commits contain. Wording drift can wait for the normal reply. Corrected facts cannot: the proof is carrying errors you already fixed, and the editor is proofreading them as if they were the manuscript. Say so before answering individual comments.

From that point the current manuscript is the single source of truth, and every comment earns one of three verdicts: still valid, already resolved, or void because its premise changed. Guard the middle one. "Already resolved" is the verdict that costs trust when it is wrong, so require a quote of the current text and the commit that resolved it before recording it. Without both, record it as pending.

## Rank proof comments by what cannot be recalled after printing

The top priority is anything that becomes unfixable once printed: a disputed answer key, a rights or licensing question, and any note saying the typesetter already changed the text.

A note phrased as "changed this because ..." is not a question. It is a completed edit awaiting confirmation, and it ships as-is if you skim past it. List those separately from questions and put them first.

Keep notation inconsistencies out of that top tier. They must be fixed, but they do not justify holding the print run, and mixing them in buries the comments that do.

The top tier usually cannot be answered without the proof file in hand, since those comments are identified by folio. Do not let that stall the pass: the notation tier is decided entirely from the manuscript source, so run it while you wait.

## Answer-key labels break when options are reordered

Reordering the choices in an exam item and forgetting to move the answer label produces an item that passes every structural check. The label exists, it names a listed option, the counts add up. Only the explanation exposes it, by arguing for a different option than the label names.

Structural validators cannot reach this, so judge the explanation against the label item by item. Scope the sweep from the commits that reordered or replaced options instead of trusting the single instance the editor happened to catch, and extend it to anything that restates the answer elsewhere, since digests and generated output drift independently of the source.

## Answer a rights question from the permitted-use list

Brand and trademark guidelines enumerate the uses they allow. Treat that list as exhaustive whenever the same page also states the mark may not be used without prior written permission: a medium missing from the list is not permitted by omission. Permission covering blog posts and news articles does not extend to a commercial book.

Separate the constraints from the permission. Guidelines that forbid altering a mark usually still publish a monochrome variant, so single-colour printing is rarely the blocker. The blocker is the permission, and its lead time may not fit the print schedule. Offer a substitute that carries no mark alongside the finding, so the editor can proceed without waiting.

## Answer proposal-type comments with one policy, not one by one

Requests to add diagrams or screenshots arrive dozens at a time, phrased as "may we add one here?". Answering each one individually multiplies the round trips.

Decide the axes once and reply in bulk. Two axes that hold up in practice: whether a reader is likely to stall at that spot, and whether the visual will go stale on the next UI change.

## Verify a factual claim before adopting it

Reviewers quote whatever page they landed on. Official documentation contradicts itself more often than expected, so find the source of truth before deciding.

1. Prefer the page that exists to define the thing over the page that mentions it in passing. A per-role permission matrix outranks a one-line "who can use this feature" note in a how-to page.
2. Go under the rendered page. Docs sites are generated; the same table often lives in a data file that several pages include. Reading that file removes ambiguity about which page is stale.
3. Extract structured content mechanically instead of reading it. Check marks and matrix cells are rendered as icons with accessibility labels, so pull the labels rather than eyeballing the table.
4. Date the conflicting statements. Line-level history tells you which wording has been maintained and which has sat untouched since a beta launch.

## A wrong claim is often a stale-but-once-true claim

When the current source contradicts the reviewer, check the history of the source before answering. A claim that fails today may have been correct when the reviewer learned it.

Walking the commit history of the underlying data file separates three cases:

- Never true: correct the reviewer directly
- True in the past, changed since: say so, and say when it changed
- True in the past, quietly removed: say so, and note that the source never announced it

The second and third cases change the tone of the reply completely. "That is wrong" and "that was right until February" cost the same effort to write and land very differently.

## Write the reply so the reviewer can check it

For every rejected point, give the primary source, quote the sentence, and explain where the reviewer's version probably came from. Pointing at the stale page they likely read is what keeps the exchange collaborative.

For every adopted point, name what changed and, where the wording differs from the proposal, why. Common reasons: the proposal broke an established form used elsewhere in the book, or its politeness level did not match the surrounding prose.

Group related requests into one commit when they share a topic, and reference that commit from each reply so the reviewer can see the result.

## Widen the scope before applying

A reported occurrence is a sample. Search the whole manuscript for the same pattern before editing, or the next review reports the siblings.

Two follow-ups pay off repeatedly:

- Related files that mirror the manuscript, such as outlines, key-point notes, and chapter maps
- Third variants of the same idea that neither the reviewer nor the original author noticed

Widening the corpus is not enough if the query stays narrow. A reviewer quotes whichever inflection they landed on, so search the invariant core of the word rather than that inflected form. Run the narrow pattern and the broad one and compare counts: a gap means the narrow pattern was hiding siblings that would ship unchanged.

## Confirm a reported inconsistency is really one term

A notation report assumes the flagged spellings are the same word. Check that before unifying. One of them may be a proper noun with a fixed form, such as a product role or a feature name, while the other is the ordinary word it was named after. Unifying them makes the ordinary sentence read as a reference to the product, which is a worse error than the inconsistency. Replace the ordinary use with plain language instead, and record it as adopted with change naming the collision as the reason.

Pick the surviving form from an external orthography standard first and manuscript majority second; author preference invites the same comment on the next proof. When the flagged spelling has zero occurrences in the manuscript, rule on nothing. It may exist only in the typeset text, so ask for the folio instead of recording a rejection.

## Applying fixes without breaking aligned tables

Manuscripts with mixed-width text keep Markdown tables padded to a common column width. Editing one cell silently breaks the alignment, and hand-counting spaces fails repeatedly on wide characters.

Compute display width instead: wide characters count as two columns, everything else as one. Then take the widest cell per column and repad every row, including the separator. Verify by comparing total row widths, which must all be equal.

Recompute after every edit pass. Shortening the longest cell shrinks the whole column, so rows that were correct before the edit become wrong.

## Close the loop

Reply, then close. An issue that was fixed but left open reads as ignored, and the reviewer has no way to tell the difference.

Before closing, recompute whatever is derived from the manuscript text. A global replacement shifts counts, and counts feed page budgets and schedule decisions, so closing on a stale number pushes the error into planning.

If the fix is not visible yet because the work is unpushed, publish first. A reply that references an invisible commit is worse than a late reply.
