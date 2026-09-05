# Project Thread Rules

A project thread is a topic that runs across many meeting cycles inside one customer workspace: a support case, an incident investigation, a migration, a PoC. `meeting-notes/` records a single meeting and `next-actions/` covers the gap to the next one, so neither can hold a topic that stays open for months.

## Split Checklist

Required:

- The topic spans multiple meeting cycles.

Plus at least one:

- It already has three or more files. Count what exists now; do not split on a forecast.
- It accumulates its own evidence: logs, packet captures, vendor or support replies, an external case ID.
- Its owners differ from the people who normally attend the recurring meeting, for example a vendor support team or a different customer department.

If the required condition fails, keep it in the meeting note. If only the required condition holds, use `next-actions/ongoing/`.

## Do Not Split

- A one-off question answered inside a single meeting.
- Work that already fits the next meeting's homework folder.
- A topic created only because the name sounds like a project. Empty threads are worse than a long meeting note, because a reader assumes a folder holds current state.

## Naming

- `pj_{topic}/`, where `{topic}` is kebab-case: `pj_dns-resolution-case`, `pj_tenant-consolidation`.
- No date prefix. A thread is identified by topic, and the start date stops being useful as soon as the thread moves.
- Do not put an external case ID in the folder name. Case IDs change owners and formats; record them inside `README.md` instead.

## Layout

```text
pj_{topic}/
  README.md                      <- current state, timeline, open actions
  YYYYMMDD_{subject}.md          <- meeting record, analysis, or deliverable, in date order
  _evidence/                     <- optional: raw logs, captures, vendor replies as received
```

- Keep raw evidence unedited under `_evidence/` and put interpretation in the dated files.
- Do not nest another meeting-notes structure inside the thread. Dated files at the thread root stay readable.

## README Required Sections

| Section       | Content                                                                         |
| ------------- | ------------------------------------------------------------------------------- |
| Overview      | What the topic is, in two or three lines                                        |
| External IDs  | Support case, ticket, or change request numbers, with the owning vendor or team |
| Current state | One line: the status and **who holds the ball right now**                       |
| Timeline      | Date, event, outcome. Newest entry last so the file appends cleanly             |
| Open actions  | Item, owner, due date, status                                                   |
| Related files | Links to the dated files and to the meeting notes that reference this thread    |

The current-state line is the point of the folder. If a reader has to reconstruct the status from the timeline, the README has failed. Include the verification date; if the formal status is not explicitly confirmed, record the last confirmed action and mark the formal status unconfirmed instead of carrying forward a stale `Open`, owner, or waiting party.

## Single Source of Truth

- The thread folder owns status and history. Meeting notes link to the thread and do not restate its status.
- When the topic comes up in a meeting, record the meeting-specific decision in the meeting note and append the outcome to the thread timeline. Do not copy the thread's analysis into the meeting note.
- The reverse also holds: do not copy meeting logistics, attendees, or unrelated agenda items into the thread.

## Migration

Move an existing topic into a thread when either trigger fires: the topic has been appended to the same meeting note across three or more meetings, or its section in that note is longer than all the other sections combined.

1. Create `pj_{topic}/` and write `README.md` first, so the current state is captured before anything moves.
2. Search the workspace for inbound references to the files being moved. Relative links, prompts, and scripts all break silently.
3. Move the files, then repair the links found in step 2 and re-check them.
4. Leave a one-line pointer in the original meeting note instead of deleting the mention.

## Closing a Thread

A thread stays open until someone closes it, so the end has to be defined or the workspace fills with folders that still look active.

- Close when the underlying case is resolved, the work is cut over, or the topic is dropped. No open actions and no timeline entry for two meeting cycles makes it a closure candidate: raise it instead of letting it sit.
- On closure, put the outcome and the closing date in the `README.md` current-state line, and set every open action to `done` or `dropped`.
- Keep the folder where it is and do not delete it. Move closed threads under `_archive/` only once active threads become hard to scan, and repair inbound links afterward.
- If the topic reopens, reuse the original folder. A second thread for the same topic splits the history and neither side is complete.

## Done Criteria

- `README.md` exists and its current-state line names the current owner.
- Every dated file in the thread is reachable from `README.md`.
- No meeting note written after the split restates the thread's status.
- Inbound links still resolve after a migration.
- A closed thread states its outcome and closing date, and has no action left in an open state.
