# Recurring Decks (periodic meeting or status decks rebuilt from the previous cycle)

Use when a deck is rebuilt every cycle from the previous one. The failure mode is stale carry-over: last cycle's questions, statuses and source dates survive into a deck that will be shown to the customer.

## Refresh before reuse

1. **Re-verify every carried-over item** (status, open question, source date) against its primary source: ticket or support mails, calendar, survey tool, operations logs. A slide whose source line still shows last cycle's date is stale by definition.
2. **Replace answered questions with the answer.** Never ask the customer something that was answered since last cycle.
3. **Drop what was closed.** Read the previous minutes: a topic with a recorded "no further follow-up" decision, or a carry-over item that is no longer wanted, gets no slide, agenda row, hearing row or SR-check row. Likewise, when a ticket has closed and no action remains for the presenter, delete that topic's "today's confirmation" row on the slide and in the closing summary; keep the background and next-steps facts, and leave the agenda wording if it still matches the content.
4. **Fill status columns** from operations records (for example a periodic watch log: run dates and counts) instead of leaving them blank for the meeting. State what is known; omit what is not.
5. **State the product's official name** (for example the product family name, not a shorthand).

## Make each topic readable on its own

- Put a one-line recap of the previous cycle ("last time: ...") in the lead or first table row of each topic slide. A topic slide whose link to a carry-over item is not visible forces the presenter to explain it.
- Write a case or ticket ID together with a short summary wherever the ID appears (title, agenda, source line, table). An ID alone is meaningless to readers.
- Open a multi-event workstream (training, surveys, follow-up sessions) with one summary slide: a dated timeline of actions and results, then the detail slides. Verify every row's event, date and owner against primary records (meeting transcripts, chat posts, invitations) before writing; do not merge two events that share a date window, and do not turn a term merely heard in chat into an activity ("introduced X"). Add an owner column for the vendor side only with names confirmed in those records, written as the family name without an honorific under a "vendor-side owner" heading (the user's preference), mark planned owners as planned, and leave unverified cells empty. For a meeting with a customer executive, describe it by role ("management-level 1:1") without the name unless the user confirms the name and the sharing.
- Gloss jargon and acronyms where they first appear (product names, abbreviations, version names such as sensor v2/v3, internal terms). When one clause is not enough, add a short term-list slide or a "what is X" row at the start of the section, including the practical consequence (for example how a migration is actually performed). Check product behavior against official documentation before writing it, and do not invent a gloss for an internal term; ask instead. If the audience reader cannot say what a term means, the slide is not done.
- For survey results show when it ran (distribution date, deadline), the respondent count and the headline numbers. When a feedback form is shared across audiences, filter to the audience by organisation and date, exclude test submissions, list the distinct organisation spellings before filtering, and report only aggregates and paraphrased themes (no per-person quotes or names).

## Emphasis

Use one accent treatment (bold plus a single colour) for two things only: what changed since last cycle (decisions, replies, closures, new items) and the one or two key facts per slide (dates, cautions, headline results). Do not colour everything. Also mark the small token that tells look-alike items apart (for example a `-stg` suffix in a host or app name), wherever it appears: table cells, diagram boxes and questions. Do not add a legend ("red = key point") or boilerplate disclaimers to source lines; the emphasis is self-evident and the repeated notes add noise. Keep only a source line that names the actual source and confirmation date; omit the line when it would be empty.

## Consultation slides

A slide titled as a consultation must ask for a decision. A list of fact-check questions with explanatory notes reads as a checklist. Title mixed slides "confirmation and consultation", and give each row the presenter's recommendation (for example "start in the same environment; is that acceptable?") rather than only background.

## Incorporating verification results or a hand-off request

- Replace "not yet verified" wording with the verified content. Reproduce the customer's own names and addresses in diagrams; never reuse the verification environment's diagram as is.
- Customer-facing body, source line and notes must not contain the verification environment's identifiers, cost, retention or deletion plans, internal history, personal names, or checking notes and confidence labels ("unconfirmed", "to be checked", "confirmed"). For things not verified write "this varies by environment; please confirm beforehand". Confidence labels belong in the completion report.
- Put supporting detail, likely questions with answers, and the source URLs in the speaker notes as `参照: <URL>` lines. Scan the generated manuscript for the forbidden wording before handing over.

## Notes the presenter can speak from, and visuals

- When the presenter is not the subject expert, 30-200 character notes are not enough. Write each slide's notes as: what to say (order), what to ask the audience, terms in plain words, likely questions with answers, and source URLs. Give each section divider a note on how to run that section. Answers that rest on the author's judgement rather than a source are flagged to the presenter in the report, not in the customer-facing deck.
- A term in the body that the audience may not know (a setting name, a protocol detail) gets its own short supplementary slide with a diagram, placed right after the slide that uses it, rather than a longer table cell. Skip the diagram if no accurate one can be drawn.
- Add visual weight with the vendor's official icon set on diagram boxes, section dividers and a small top-right slide icon. Use only icons whose meaning matches; where the set has none (another vendor's product), omit the icon instead of substituting.
