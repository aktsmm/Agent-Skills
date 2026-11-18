---
name: convert-meeting-minutes
description: "Convert supplied Teams AI notes, transcripts, or meeting memos into one workspace record with linked questions and actions, plus source-linked WorkIQ context when requested. Use for 議事録変換, 会議メモ整理, Teams AI議事録, or フォローアップ タスク."
argument-hint: "会議メモ・文字起こし、会議日・URL（分かる場合）、補足したい関係者や論点（任意）"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Convert Meeting Minutes

Read [the workflow](references/workflow.md) before processing the source.
Template paths in that workflow are relative to this skill directory.

- Keep one working meeting note; protect existing edits and source links.
- Record transcript coverage and label uncertain names, dates, prices, support boundaries, and commitments `要確認`; keep cited WorkIQ context separate from meeting decisions.
- Extract open questions into `_questions/` and actionable follow-ups into `next-actions/` in the same operation; do not invent commitments.
- Follow the sharing boundary before creating customer-shareable highlights; exclude internal paths, speculation, and commercial terms.
- When a workspace-specific template exists in `_templates/`, preserve that format; otherwise use the bundled [meeting](assets/meeting-minutes.md) or [internal memo](assets/internal-memo.md) template.

Done means the note, question/action records, and relevant workstream links agree; a captured meeting URL is not proof of full-content verification.
