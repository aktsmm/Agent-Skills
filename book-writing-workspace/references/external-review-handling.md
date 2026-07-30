# External Review Handling

How to take reviewer issues and pull requests into a manuscript without losing the reviewer, and without importing a wrong claim.

## Decide adoption per point, not per pull request

A single pull request usually mixes correct fact fixes, wording preferences, and claims that no longer match the source. Split it and rule on each point. Adopting or rejecting the whole request wastes the correct half.

Record three outcomes only: adopted, adopted with change, rejected. "Adopted with change" needs the reason for the change, or the reviewer reads it as a silent override.

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

## Applying fixes without breaking aligned tables

Manuscripts with mixed-width text keep Markdown tables padded to a common column width. Editing one cell silently breaks the alignment, and hand-counting spaces fails repeatedly on wide characters.

Compute display width instead: wide characters count as two columns, everything else as one. Then take the widest cell per column and repad every row, including the separator. Verify by comparing total row widths, which must all be equal.

Recompute after every edit pass. Shortening the longest cell shrinks the whole column, so rows that were correct before the edit become wrong.

## Close the loop

Reply, then close. An issue that was fixed but left open reads as ignored, and the reviewer has no way to tell the difference.

If the fix is not visible yet because the work is unpushed, publish first. A reply that references an invisible commit is worse than a late reply.
