---
name: convert-meeting-minutes
description: "Convert supplied Teams AI notes, transcripts, or meeting memos into one workspace meeting record with linked questions and follow-up actions. Use for 議事録変換, 会議メモ整理, Teams AI議事録, or フォローアップ タスク."
argument-hint: "会議メモ・文字起こし、会議日、分かる場合は会議URL"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Convert Meeting Minutes

Read [the workflow](references/workflow.md) before processing the source.
Template paths in that workflow are relative to this skill directory.

- Keep one working meeting note; protect existing edits and source links.
- Mark uncertain names, dates, prices, support boundaries, owners, deadlines, and agreements as `要確認`; record available transcript coverage.
- Extract open questions into `_questions/` and actionable follow-ups into `next-actions/` in the same operation; do not invent commitments.
- Keep internal paths, speculation, and commercial terms out of customer-shareable highlights.
- When a workspace-specific template exists in `_templates/`, preserve that format; otherwise use the bundled [meeting](assets/meeting-minutes.md) or [internal memo](assets/internal-memo.md) template.

Done means the note, question/action records, and relevant workstream links agree; a captured meeting URL is not proof of full-content verification.
