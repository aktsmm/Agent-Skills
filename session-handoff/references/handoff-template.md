# Handoff Template

Use this structure to produce one paste-ready message for a fresh session. Omit sections that do not apply. In the final response, show this entire message in a single fenced `markdown` block.

```markdown
これは前セッションから貼り付けた状況共有メモです。現在のセッションの agent は、まず内容を読み取り、理解した作業状態・未完了事項・次に確認すべきことを短く要約し、A/B の次の候補を提示してください。ユーザーが明示的に「進めて」「実行して」または候補名を選ぶまで、ファイル編集・コマンド実行・外部サービス操作を開始しないでください。

## Session Reference

- 推奨セッション名:
- 推奨モデル（助言。理由1行 / 検証不能なら unspecified）:
- セッション系譜（`root: <id> → … → this session: <id>`）:
- 作成日:
- ワークスペース / repo:
- branch / HEAD:

## Initial Response Expected

- まず「了解しました」と返す。
- 認識した現在地、未完了、次に確認することを短く要約する。
- `理解しました。次は A（...）/ B（...）のどちらにしますか？` を優先する。
- 状態要約への訂正・補足・了承だけでは実行承認とみなさない。
- 選択は選んだ候補の範囲だけを承認する。既存の禁止事項、stop condition、外部操作・破壊的操作の追加承認を上書きしない。
- 明示指示があるまで作業を開始しない。

## Goal

- 大目的（当初。ユーザー訂正でのみ更新）:
- 大目的（現在。転換したときだけ書く）:
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

## Next Candidates

1. A:
2. B:
3. 選択前に確認する未解決事項（creator側の大目的確認は再掲しない）:

## Done Criteria

- ここまで達したら完了:
```

## Compression Rules

- Keep at most two 大目的 lines, 当初 and 現在. A change of direction updates 現在 and leaves 当初 intact; only the user saying the recorded wording itself was wrong rewrites 当初. When you cannot tell the two apart, treat it as a change of direction so nothing is lost. Collapse to one line when they are the same, and never list intermediate versions however many times the direction changed.
- Give each 大目的 line at most one parenthesized marker: `未確認` until the user confirms that wording, `（<date> 転換）` for a change of direction, or `（<date> ユーザー訂正）` for a corrected record. A confirmation clears `未確認`, a newer marker replaces the older one, and when no wording can be reconstructed at all, write `未確認` alone and name the root session as where to recover it.
- Keep only continuation-critical facts.
- Prefer workspace-relative file paths.
- Include exact error text only when it changes the next action.
- Do not include tokens, passwords, cookies, private account identifiers, or sensitive URLs.
- Write the opening line as an instruction to acknowledge and summarize the state first, not as a request to draft another handoff.
- Do not tell the next agent to resume immediately; gate action behind an explicit user request.
- Keep prohibited actions and external-system safety constraints near the top.
- If the previous terminal may be unreliable, say which artifacts or files should be trusted instead of stdout.
- If a decision needs the user, write the exact question to ask next.
