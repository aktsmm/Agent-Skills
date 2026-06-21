# Ledger Templates

orchestrator が状態を保持する 2 つの ledger と、attempt 教訓 table の雛形。
このスキルは stateless なので、orchestrator が **毎ループこれを更新**して SSOT にする。
full transcript を抱えず、ledger を見れば現状が分かる状態を保つ。

## Task Ledger

ゴールと計画の現在像。Phase 1 合意後に初期化し、replan のたびに作り直す。

```markdown
# Task Ledger — <goal 名>

## Goal

<1 文>

## Acceptance Criteria（freeze 済み）

- AC1: <条件> / verify: <コマンド> / status: PASS|FAIL|未検証
- AC2: <条件> / verify: <コマンド> / status: ...

## Constraints / must NOT

- <触ってよい範囲・禁止近道>

## 確定した事実（検証で裏が取れたこと）

- <fact 1>

## 未確定の推測（まだ裏が取れていない前提）

- <assumption 1>

## 現計画（サブゴール列）

1. <subtask> — 入力 / 期待出力 / 依存 / 並列可否 / status
2. <subtask> — ...
```

## Progress Ledger

ループごとの進捗と停止判定。毎 iteration の末尾で更新する。

```markdown
# Progress Ledger

| iter | goal_satisfied? | making_progress? | looping(oscillation)? | stall_counter | 次アクション               |
| ---- | --------------- | ---------------- | --------------------- | ------------- | -------------------------- |
| 1    | No              | Yes              | No                    | 0             | AC2 を再実行               |
| 2    | No              | Yes              | No                    | 0             | AC3 を再実行               |
| 3    | No              | No               | Yes                   | 1             | replan（oscillation 検知） |
```

判定メモ:

- `making_progress?` = このループで PASS 基準が増えた or gap が縮んだか。
- `stall_counter` = 進展なしで +1、進展で 0。`≥4` で replan。
- `looping?` = 同一 `(action, target)` の反復を検知したか。

## Deferred / Next Actions（保留して最後にハンドオフ）

自律で進めず保留した項目を記録し、Phase 7 で Next Action としてユーザーへ渡す。

```markdown
# Deferred

| #   | 保留した操作     | なぜ保留したか                           | 実行に要るもの | 推奨アクション      |
| --- | ---------------- | ---------------------------------------- | -------------- | ------------------- |
| 1   | 本番へ deploy    | backup 不能の不可逆操作（Normal モード） | ユーザー承認   | 確認後に手動 deploy |
| 2   | 外部サイトへ公開 | 安全弁: 未許可の外部公開                 | 明示許可       | 公開可否を判断      |
```

## Attempt 教訓 Table

同じ失敗を繰り返さないための記録。worker prompt には関連分だけ delta で渡す。

```markdown
# Attempts

| #   | subtask | approach（何を試したか） | 外部 signal（検証結果） | 教訓 / 次に避けること            |
| --- | ------- | ------------------------ | ----------------------- | -------------------------------- |
| 1   | AC2     | X を一括置換             | build FAIL: 型不一致    | 一括前に 1 ファイルで pilot する |
| 2   | AC2     | 1 ファイルで pilot       | build PASS              | 同パターンを残りへ展開可         |
```

## 運用ヒント

- ledger は会話内に書いて更新すれば十分。長い・多段ゴールでファイル化するなら
  作業フォルダ配下（例 `tmp/` や日付フォルダ）に置き、Phase 7 で不要なら cleanup する。
- worker へは ledger 全体でなく、そのサブタスクに要る行だけを抜き出して渡す（context 節約）。
