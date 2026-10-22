# Handoff Template

Omit irrelevant fields. Fill this structure as one fenced `markdown` block, not as a second handoff request.

```markdown
これは前セッションからの状況共有メモです。まず現在地を短く要約してください。最新の明示的な再開依頼がある場合はその範囲だけ再開し、なければ編集・コマンド・外部操作を始めず実行承認を待ってください。状態要約への訂正や了承だけでは実行承認とみなしません。

## Constraints

- 承認された範囲:
- Must NOT / 追加承認が必要な操作:
- 停止条件 / 再開条件:

## Session Reference

- 系譜（root と直近2件の non-root ID）:
- 作成日:
- workspace / repo / branch / HEAD:

## Goal

- 大目的（当初）:
- 大目的（現在。転換時のみ）:
- このセッションの目的 / 依頼成果 / 直近の具体的成果物:
- 完了条件:

## State And Evidence

- 完了 / 作業中 / 未完了:
- ブロッカー / 未確認 / 仮説:
- 主要ファイル / 保存済みの未送信ドラフト:
- 自分の変更 / stage・巻き戻し禁止の他者変更:
- 実行済みコマンドと結果:
- 失敗した確認 / 未実行の検証:
- 共有対象の所有者・完了観測点・許可された read-only probe:
- 信頼する artifact / 不安定な terminal:

## Next Action

- 次に行うこと（適用する direct-entry workflow があればその呼び出し）:
- 承認待ちの範囲 / 本当に複数の選択肢がある場合のみ A/B:
- 未解決の質問:

## Done / Stop

- 完了または停止とする具体的条件:
```

## Field Rules

- Keep at most two overarching objectives: original and current. Direction changes update current, not original; only a user correction rewrites an incorrect original. If indistinguishable, preserve both as a direction change. Collapse equal objectives; omit intermediate versions.
- At most one marker per objective: `未確認` for uncertain wording, dated direction change or dated user correction. New markers replace old ones; confirmation clears `未確認`. Do not require reconfirmation of a clear purpose. If unreconstructable, mark `未確認` and identify the root source to recover.
- Include exact errors or safe rerunnable commands only when continuation needs them. A saved draft is not approved text.
- Do not fabricate A/B alternatives or add session-name/model advice by default; include such suggestions only on request.
- Candidate selection authorizes only that candidate. Even an immediate-resume request does not override prohibitions, shared-resource ownership or additional approval requirements.
- Keep required but unverified work, missing evidence and concrete failure/recovery conditions explicit. Do not duplicate a workflow's execution contract.
