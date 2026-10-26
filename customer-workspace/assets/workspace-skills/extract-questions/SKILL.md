---
name: extract-questions
description: "Extract questions, confirmation requests, homework, and answered items from supplied meeting records into the workspace question ledger. Use for 質問を抽出, 確認事項整理, 宿題を抜き出す, or meeting-question follow-up."
argument-hint: "対象の会議ログと、会議別保存が必要な場合だけその指定"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Extract Questions

Read [the workflow](references/workflow.md) before updating question records.

- Default to the monthly ledger; use per-meeting output only when explicitly requested.
- Preserve the initial exchange and append follow-ups chronologically in the current month with a link to the original entry.
- Do not turn a tentative AI follow-up into an agreed owner, deadline, or deliverable.
- Verify technical answers with official sources; unavailable evidence leaves an explicit `要確認`, not an invented answer.

Done means extracted items, answers, source links, and reported counts match the saved ledger without duplicate entries.
