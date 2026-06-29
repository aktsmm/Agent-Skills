# Handoff Template

Use this structure to produce one paste-ready message for a fresh session. Omit sections that do not apply. In the final response, show this entire message in a single fenced `markdown` block.

```markdown
これは前セッションから貼り付けた状況共有メモです。現在のセッションの agent は、まず内容を読み取り、理解した作業状態・未完了事項・次に確認すべきことを短く返してください。ユーザーが明示的に「進めて」「実行して」と言うまでは、ファイル編集・コマンド実行・外部サービス操作を開始しないでください。

## Initial Response Expected

- まず「了解しました」と返す。
- 認識した現在地、未完了、次に確認することを短く要約する。
- 明示指示があるまで作業を開始しない。

## Goal

- 目的:
- 完了条件:
- 明示された制約:
- 禁止事項 / stop condition:

## Current State

- 完了済み:
- 作業中:
- 未完了:
- ブロッカー:
- 未確認 / 仮説:

## Files And Artifacts

- 主要ファイル:
- 生成・変更したファイル:
- 触ってはいけない / 巻き戻してはいけない変更:

## Commands And Validation

- 実行済みコマンド:
- 成功した確認:
- 失敗した確認:
- まだ実行していない確認:

## Next Action

1. 再開する場合の最初の候補:
2. 作業開始前に確認すること:
3. 迷ったらユーザーに確認すること:

## Done Criteria

- ここまで達したら完了:
```

## Compression Rules

- Keep only continuation-critical facts.
- Prefer workspace-relative file paths.
- Include exact error text only when it changes the next action.
- Do not include tokens, passwords, cookies, private account identifiers, or sensitive URLs.
- Write the opening line as an instruction to acknowledge and summarize the state first, not as a request to draft another handoff.
- Do not tell the next agent to resume immediately; gate action behind an explicit user request.
- Keep prohibited actions and external-system safety constraints near the top.
- If the previous terminal may be unreliable, say which artifacts or files should be trusted instead of stdout.
- If a decision needs the user, write the exact question to ask next.
