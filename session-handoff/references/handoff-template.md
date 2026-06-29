# Handoff Template

Use this structure to produce one paste-ready message for a fresh session. Omit sections that do not apply.

```markdown
次のセッションでは、以下の状態から作業を再開してください。

## Goal

- 目的:
- 完了条件:
- 明示された制約:

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

1. 最初にやること:
2. その次に確認すること:

## Done Criteria

- ここまで達したら完了:
```

## Compression Rules

- Keep only continuation-critical facts.
- Prefer workspace-relative file paths.
- Include exact error text only when it changes the next action.
- Do not include tokens, passwords, cookies, private account identifiers, or sensitive URLs.
- If the previous terminal may be unreliable, say which artifacts or files should be trusted instead of stdout.
- If a decision needs the user, write the exact question to ask next.
