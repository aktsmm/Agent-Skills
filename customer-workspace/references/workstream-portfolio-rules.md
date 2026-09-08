# Workstream Portfolio Rules

Use this pattern when one parent customer workspace contains multiple ongoing workstreams that need independent status tracking.

## Structure

```text
workstreams/
  README.md                 <- Portfolio index
  _candidates.md            <- New, ambiguous, or multi-workstream information
  {workstream-id}/
    README.md               <- Current status, owner, actions, and timeline
    updates/                <- Dated summaries only when detail is needed
```

`workstreams/README.md` is the cross-workstream view. Each workstream README is the source of truth for that workstream's current status. Keep raw input in `_inbox/` and meeting records in `meeting-notes/`; link to them rather than copying their contents.

## Create a Workstream

- Create a folder only after the user confirms the workstream name and scope.
- Use a lowercase kebab-case ID. Do not put customer names, people, external case IDs, or dates in the folder name.
- Start from `workstream-readme.md`. Record a named current owner, status, open actions, timeline, source links, and routing keywords.
- Do not create a workstream for a one-off question or an unconfirmed idea. Record it in `_candidates.md` first.

## Route Updates

1. Compare the input with confirmed workstream names, routing keywords, and current scope.
2. If one match is unambiguous, update that workstream's README. Create an `updates/` file only for a durable summary that would make the README too large.
3. If the input is a meeting, preserve the meeting note as the source and add only the link and state change to the workstream.
4. If multiple workstreams match, no workstream matches, or confidence is low, retain the original source and add a `candidate` record. Ask the user to choose or approve the relationship.

## Status and Ownership

Use only `candidate`, `not-started`, `in-progress`, `blocked`, `done`, or `dropped`.

- A `blocked` workstream must name the current owner of the next response and the condition that moves it forward.
- Update the portfolio index whenever a workstream's status, owner, or next action changes.
- Close a workstream only after its actions are `done` or `dropped`. Keep its folder for history.

## Relationship to Other Records

- `meeting-notes/`: one meeting's decisions and source material.
- `next-actions/`: time-bounded work between meetings.
- `workstreams/`: ongoing cross-workstream status and routing.
- `pj_{topic}/`: detailed long-lived evidence and history. Create it only when a workstream meets the existing project-thread split conditions.

## Validation

- Every portfolio row links to a real workstream README.
- Every workstream README declares a valid status and a current owner.
- Every new or ambiguous item is in `_candidates.md`, not an unconfirmed folder.
- Relative links resolve, and source records are linked rather than duplicated.
