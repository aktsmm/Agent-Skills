---
name: session-handoff
description: "Create a compact handoff note so work can be resumed in a new chat/session. Use when the user says to close the current session, make a message for the next session, create a handoff, resume later, セッションを閉じる, 次セッションで再開, 引き継ぎ, or 伝言を作る."
argument-hint: "引き継ぎたい作業、完了条件、再開先セッションへ渡したい制約"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Session Handoff

現在の作業を一度閉じ、新しいセッションで安全に再開できるように、貼り付け可能な伝言を作る。
成果物は「次の agent が最初に読むべき最小コンテキスト」であり、作業ログの全文ではない。

## When to Use

- ユーザーが `セッションを閉じる` / `新しいセッションで再開` / `引き継ぎ` / `伝言を作る` / `handoff` / `resume later` と依頼した。
- 長い作業の途中で context が重くなり、次セッションに必要な状態だけを渡したい。
- 未完了タスク、作業中ファイル、検証状況、次に実行するコマンドを残す必要がある。

## Do Not Use For

- 通常の進捗報告や完了報告だけで足りる小さな依頼。
- 永続的な運用ルールの保存。ルール化が必要なら instruction / skill / repo docs を検討する。
- 秘密情報、トークン、個人情報、認証済み URL を次セッションへそのまま渡す用途。

## Workflow

1. Identify the resume target: current goal, requested outcome, and the nearest concrete artifact.
2. Capture only state needed to continue: touched files, commands already run, validation results, blockers, assumptions, and pending decisions.
3. Separate facts from guesses. Mark uncertain items as `未確認` or `仮説`.
4. Preserve user constraints that still matter, including wording, scope limits, and prohibited actions.
5. Write a paste-ready handoff using [references/handoff-template.md](references/handoff-template.md).
6. Review the handoff before finalizing: remove secrets, private account identifiers, sensitive URLs, absolute personal paths unless necessary for local continuation, duplicate logs, and stale TODOs.
7. If the user asked for rubber-duck review, or the handoff is non-trivial, run a second-pass review against the checklist below.

## Rubber-Duck Review Checklist

- Would a fresh agent know the goal without reading the old session?
- Is the next concrete action unambiguous?
- Are completed, pending, blocked, and unknown items separated?
- Are file paths workspace-relative when possible?
- Are verification results stated with command names and outcomes?
- Are secrets, credentials, and irrelevant transcript details omitted?
- Is the message concise enough to paste as a new-session prompt?

## Output Rules

- Start with a one-sentence instruction to the next session.
- Prefer bullets over narrative history.
- Include exact commands only when they are safe and likely to be rerun.
- Include no more than one `Next action` section.
- End with the expected stop condition or done criteria.

## References

- [handoff-template.md](references/handoff-template.md): Paste-ready structure for the next-session message.
