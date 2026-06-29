---
name: session-handoff
description: "Create a compact handoff note so a new chat/session can first acknowledge the current state before work resumes. Use when the user asks to close the current session, make a message for the next session, create/export a handoff, resume later, セッションを閉じる, 引き継ぎを作る, or 伝言を作る. Do not use for pasted handoff notes that instruct the current agent to resume work; consume those as instructions instead."
argument-hint: "引き継ぎたい作業、完了条件、再開先セッションへ渡したい制約"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Session Handoff

現在の作業を一度閉じ、新しいセッションでまず状態を認識できるように、貼り付け可能な伝言を作る。
成果物は「次の agent が最初に読むべき最小コンテキスト」であり、作業ログの全文でも即時実行指示でもない。

## When to Use

- ユーザーが `セッションを閉じる` / `引き継ぎを作る` / `伝言を作る` / `handoff を作成` / `resume later` と、次セッション用メッセージの作成を依頼した。
- 長い作業の途中で context が重くなり、次セッションに必要な状態だけを渡したい。
- 未完了タスク、作業中ファイル、検証状況、次に実行するコマンドを残す必要がある。

## Do Not Use For

- ユーザーが handoff 風の本文を貼っただけ、または `次のセッションでは...` で始まる作業指示を現在の agent に実行してほしい場合。これは handoff 作成ではなく、指示の消費・再開として扱う。
- 通常の進捗報告や完了報告だけで足りる小さな依頼。
- 永続的な運用ルールの保存。ルール化が必要なら instruction / skill / repo docs を検討する。
- 秘密情報、トークン、個人情報、認証済み URL を次セッションへそのまま渡す用途。

## Workflow

1. Confirm the user is asking to create a handoff note, not asking this agent to consume an existing handoff-like instruction and continue work now. If ambiguous, ask one short clarification before drafting.
2. Identify the resume target: current goal, requested outcome, and the nearest concrete artifact.
3. Capture only state needed to continue: touched files, commands already run, validation results, blockers, assumptions, and pending decisions.
4. Separate facts from guesses. Mark uncertain items as `未確認` or `仮説`.
5. Preserve user constraints that still matter, including wording, scope limits, and prohibited actions.
6. Write a paste-ready handoff using [references/handoff-template.md](references/handoff-template.md).
7. Review the handoff before finalizing: remove secrets, private account identifiers, sensitive URLs, absolute personal paths unless necessary for local continuation, duplicate logs, and stale TODOs.
8. If the user asked for rubber-duck review, or the handoff is non-trivial, run a second-pass review against the checklist below.

## Rubber-Duck Review Checklist

- Does the first line say this is a handoff note pasted from another session, and the current agent should acknowledge the state before taking action?
- Would a fresh agent know the goal without reading the old session?
- Is the next concrete action unambiguous?
- Are completed, pending, blocked, and unknown items separated?
- Are file paths workspace-relative when possible?
- Are verification results stated with command names and outcomes?
- Are secrets, credentials, and irrelevant transcript details omitted?
- Is the message concise enough to paste as a new-session prompt?

## Output Rules

- Put the paste-ready handoff itself in one fenced `markdown` block so the user can copy it without surrounding commentary.
- Start the block with a self-identifying line: it is a handoff note from another session, and the current agent should first acknowledge and summarize the state.
- Do not instruct the next agent to start work immediately. Tell it to wait for explicit user approval before editing files, running commands, or operating external services.
- Avoid wording that sounds like a request to create another handoff, such as starting only with `次のセッションでは...`.
- Prefer bullets over narrative history.
- Include exact commands only when they are safe and likely to be rerun.
- Include no more than one `Next action` section.
- Include prohibited actions and stop conditions near the top when user safety or external systems are involved.
- End with the expected stop condition or done criteria.

## References

- [handoff-template.md](references/handoff-template.md): Paste-ready structure for the next-session message.
