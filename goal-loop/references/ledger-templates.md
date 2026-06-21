# Ledger Templates

orchestrator が状態を保持する 2 つの ledger と、attempt 教訓 table の雛形。
このスキルは stateless なので、orchestrator が **毎ループこれを更新**して SSOT にする。
full transcript を抱えず、ledger を見れば現状が分かる状態を保つ。

## Ledger Mode

- **conversation**: 小〜中規模の既定。会話内に Task / Progress Ledger を保持する。
- **durable**: 長期・多段・再開前提のときだけ使う。作業フォルダ配下に `brief.md` / `goals.json` /
  `ledger.jsonl` 相当を置き、Phase 7 で残す理由か cleanup を報告する。

Durable mode でも hidden runtime state を操作したと主張しない。ファイルはあくまで repo/workspace 側の SSOT。

## Task Ledger

ゴールと計画の現在像。Phase 1 合意後に初期化し、replan のたびに作り直す。

```markdown
# Task Ledger — <goal 名>

## Goal

<1 文>

## Grounding

- audience: <誰にとって成功か>
- destination: <反映 / 提出 / 配置先>
- baseline: <現状態 / exact failure / starting metric>
- constraints: <範囲・承認・環境・互換性>
- evidence gaps: <未確認事項>

## Acceptance Criteria（freeze 済み）

- AC1: <条件> / verify: <コマンド> / status: PASS|FAIL|未検証
- AC2: <条件> / verify: <コマンド> / status: ...

## Verification Design

- primary verifier: <実成功面に最も近い検証>
- supporting checks: <補助検証>
- real surface: <URL / app / account / device / starting state。不要なら N/A>
- evidence to capture: <commands / outputs / paths / screenshots / logs / readbacks>
- capability gaps: <不足 tool / credential / environment と handoff>

## Constraints / must NOT

- <触ってよい範囲・禁止近道>

## Architecture / Domain Invariants

- <invariant> / source: <brief/spec/interview> / verify: <test/review/観測>

## 確定した事実（検証で裏が取れたこと）

- <fact 1>

## 未確定の推測（まだ裏が取れていない前提）

- <assumption 1>

## 現計画（サブゴール列）

1. <subtask> — 入力 / 期待出力 / 依存 / 並列可否 / status: pending|in_progress|complete|failed|blocked|review_blocked|superseded
2. <subtask> — ...
```

Status rules:

- `complete`: 外部検証または rubric evidence がある。
- `blocked`: 自力で制御できない外的障害。未解決のまま final complete しない。
- `review_blocked`: final gate / independent review が non-clean。blocker 解消サブゴールを追加して続行する。
- `superseded`: steering で置き換えられた。削除せず audit-visible に残す。
- primary verifier が必要なゴールでは、supporting checks だけで `complete` にしない。

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

## Steering Events（サブゴール変更の監査）

サブゴールを組み替えたときは accepted / rejected の両方を記録する。

```markdown
# Steering Events

| #   | kind                   | target | decision | evidence    | rationale             | idempotency key |
| --- | ---------------------- | ------ | -------- | ----------- | --------------------- | --------------- |
| 1   | split_subgoal          | G002   | accepted | test output | 粒度が大きすぎた      | <optional>      |
| 2   | revise_pending_wording | G003   | rejected | none        | criteria 緩和に当たる | <optional>      |
```

Allowed kinds: `add_subgoal`, `split_subgoal`, `reorder_pending`, `revise_pending_wording`, `annotate_ledger`,
`mark_blocked_superseded`。

## Event Log（durable mode 用）

JSONL 等の append-only log にする場合の event 名。

- `plan_created`
- `subgoal_started`
- `subgoal_resumed`
- `subgoal_completed`
- `subgoal_failed`
- `subgoal_blocked`
- `subgoal_retried`
- `steering_accepted`
- `steering_rejected`
- `final_review_failed`
- `subgoal_review_blocked`

## Final Quality Gate Evidence

大きなコード変更・設計変更だけ記録する。

```markdown
# Final Quality Gate

| gate                      | status | evidence |
| ------------------------- | ------ | -------- | ------------------------------------- | ----------------------------------- |
| targeted verification     | PASS   | FAIL     | <command + exit code>                 |
| cleanup                   | PASS   | FAIL     | NOOP                                  | <formatter/review cleanup evidence> |
| post-cleanup verification | PASS   | FAIL     | <command + exit code>                 |
| invariant audit           | PASS   | FAIL     | <implementation/test/review evidence> |
| independent review        | PASS   | FAIL     | <reviewer evidence>                   |
```

## Real Surface Evidence（必要時）

UI / browser / app / 認証 / OS 連携 / 複数アプリ workflow が成功条件に入るときだけ記録する。

```markdown
# Real Surface Evidence

| surface          | starting state | workflow | pass/fail criteria  | evidence                  | result |
| ---------------- | -------------- | -------- | ------------------- | ------------------------- | ------ | ---- | ------- |
| <URL/app/device> | <state>        | <steps>  | <observable result> | <screenshot/log/readback> | PASS   | FAIL | BLOCKED |
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
- worker は ledger の所有者ではない。worker から得た evidence を orchestrator が検証して checkpoint する。
