---
name: triage-workstream-update
description: "Match supplied Teams, email, meeting, or status updates to confirmed workspace workstreams and update their current owner, state, and history. Use for 案件更新, 更新情報の振り分け, or 案件候補の確認; not for retrieving new external updates."
argument-hint: "更新情報、または確認したい案件候補"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Triage Workstream Update

Read [the workflow](references/workflow.md) before changing a workstream record.

- Keep the workstream README authoritative; link meeting/inbox sources without duplicating their full content.
- Confirm a new workstream name and scope before creating its folder.
- Check linked external work locations before marking work `not-started` or `done`; absence inside this workspace is not proof.
- A `blocked` entry names its current owner and the condition that allows progress.

Done means the owning README, portfolio, and affected action records reflect the same verified state, or an ambiguous match is saved as a candidate.
