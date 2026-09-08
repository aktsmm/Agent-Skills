# {{CUSTOMER_NAME}} Workstream Portfolio

Last reviewed: {{TODAY}}

This folder tracks confirmed workstreams within the parent workspace. Each workstream README is the source of truth for its current status, current owner, actions, and timeline. This index is for cross-workstream review only.

## Workstreams

No confirmed workstreams yet.

| Workstream ID | Workstream | Status | Current owner | Last updated | Next action | Folder |
| ------------- | ---------- | ------ | ------------- | ------------ | ----------- | ------ |

## Routing Updates

1. Match incoming Teams messages, email, meeting notes, or pasted updates against confirmed workstream names, keywords, and current scope.
2. When one match is unambiguous, update that workstream's README and create a dated summary in its `updates/` folder when needed.
3. Preserve the source in `_inbox/` or `meeting-notes/`; link to it instead of copying the full source.
4. Put new, ambiguous, or multi-workstream information in `_candidates.md` and ask for confirmation before creating a folder.

## Status Values

| Status      | Meaning                                        |
| ----------- | ---------------------------------------------- |
| candidate   | New workstream candidate awaiting confirmation |
| not-started | Confirmed but not started                      |
| in-progress | Work is active                                 |
| blocked     | Waiting on a named owner or condition          |
| done        | Completed                                      |
| dropped     | Deliberately not pursued                       |
