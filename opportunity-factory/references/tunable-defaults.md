# Tunable Defaults

Skill が示す数値・順序・cadence・rubric 判定基準・質問セット等は **reference default**。AI が実運用で改善して良い。**Hard rule** (下記) だけは変えない。

## 変更主体と Autonomy Mode

- **変更主体は workflow-review role のみ**。worker / commander / reporter-learner は変更不可 (change propose も禁止、observation の report のみ可)
- **Autonomy Mode に応じて propose or apply が決まる**。SSOT は `references/runtime-modes.md` の `ai-autonomous` preset 内 "Tune Apply by Autonomy Mode" table

概略:

- Normal / AUTO: workflow-review が propose、user 承認で apply
- FULL / ALL: workflow-review が propose、自動 apply (hard rule 誤変更疑いは security-approve escalate)
- 3 サイクル追跡 revert は reporter-learner が担当 (全 mode 共通)

## Workflow-review Dispatch

Weekly cadence + 以下 ad-hoc trigger で hourly cycle 内でも dispatch (fallback lane #3 の advisory critic とは別レイヤー):

- Blocker Test 4/4 escalation が 24h で 3 件以上
- Anti-pattern registry の同一 fingerprint count が K=3 到達
- Discovery Floor trigger が 3 サイクル連続でも新規 candidate 流入ゼロ
- Critic-log の Layer 3 reject が 24h で 2 件以上

Ad-hoc trigger 条件も tunable、実運用で調整可。

## 変更可能項目一覧

| 項目                                                                                                                                               | 既定値                                                                                                                                 | 変更判断シグナル                 | 変更手順                                           |
| -------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------- | -------------------------------------------------- |
| Fallback lane 順序                                                                                                                                 | 品質重視 A (1..10)                                                                                                                     | Discovery 偏り、lane 特定枯渇    | workflow-review propose → smoke test → apply       |
| Discovery Floor cycles                                                                                                                             | 5                                                                                                                                      | Portfolio 停滞率、Discovery 偏り | workflow-review 調整                               |
| Persistence Standard                                                                                                                               | max 12 / stall 4 / replan 4 / approach 4 / dim 2                                                                                       | Diminishing returns 増加         | task class 別に調整可                              |
| Persistence Persistent                                                                                                                             | max 20 / stall 5 / replan 5 / approach 6 / dim 3                                                                                       | 同上                             | 同上                                               |
| Persistence Exhaustive                                                                                                                             | max 30 / stall 6 / replan 6 / approach 8 / dim 4                                                                                       | 同上                             | 同上                                               |
| Task class → Profile mapping                                                                                                                       | portfolio/cleanup/digest=Standard, worker本流/discovery/small-bet=Persistent, prompt-workflow-self-improvement/anti-pattern=Exhaustive | Diminishing returns データ       | workflow-review 調整                               |
| Cadence worker                                                                                                                                     | hourly                                                                                                                                 | Workspace 目的の頻度             | setup or workflow-review                           |
| Cadence workflow-review                                                                                                                            | weekly + ad-hoc trigger                                                                                                                | Adhoc trigger 発火頻度           | workflow-review 調整                               |
| Cadence digest                                                                                                                                     | daily                                                                                                                                  | User UX                          | workflow-review 調整                               |
| Focus theme 期間                                                                                                                                   | 3 ヶ月 (workspace override 可)                                                                                                         | Theme apply 頻度が過剰/不足      | workspace override or workflow-review              |
| Focus theme apply gate                                                                                                                             | (**hard rule**: Layer 3 blocking critic 必須)                                                                                          | —                                | 変更禁止                                           |
| Layer 1 Critic 質問セット                                                                                                                          | 5 問/role (rubber-duck-review.md 参照)                                                                                                 | Critic verdict skew              | role 単位で追加/削除、workflow-review 調整         |
| Layer 3 Rubric 段階名 (info/minor/major/critical/blocking)                                                                                         | (**hard rule**)                                                                                                                        | —                                | 変更禁止 (verdict 比較保護)                        |
| Layer 3 Rubric 各段階判定基準                                                                                                                      | 現行定義 (rubber-duck-review.md 参照)                                                                                                  | Severity 分布 skew               | workflow-review 調整                               |
| Anti-pattern K 閾値                                                                                                                                | 3 反復                                                                                                                                 | 誤 skip 発生                     | workflow-review 調整                               |
| Anti-pattern retention                                                                                                                             | 90 日                                                                                                                                  | Registry 肥大化                  | workflow-review 調整                               |
| Adapter 選択                                                                                                                                       | 環境依存 (Copilot Scheduler / Scout / OpenClaw / Copilot App / GH Actions / Task Scheduler / cron)                                     | Adapter 障害 / 機能変化          | 環境変化時に user notify + workflow-review propose |
| Push cadence                                                                                                                                       | manual (setup で 1 度質問、既定 manual)                                                                                                | Remote 運用実態                  | setup or workflow-review                           |
| Blocker Test 4 問の中身                                                                                                                            | (**hard rule**)                                                                                                                        | —                                | 変更禁止 (中身は固定)                              |
| Approval bucket 構造 (auto / security-approve)                                                                                                     | (**hard rule**)                                                                                                                        | —                                | 変更禁止 (下記 invariant check)                    |
| Backup-First 原則                                                                                                                                  | (**hard rule**)                                                                                                                        | —                                | 変更禁止                                           |
| Critic 3 Layer の存在 + Independence 契約                                                                                                          | (**hard rule**)                                                                                                                        | —                                | 変更禁止                                           |
| Layer 3 blocking gate 対象 5 種 (portfolio promote / focus theme apply / prompt-self-improvement commit / external publish / small-bet→本実装昇格) | (**hard rule**)                                                                                                                        | —                                | 変更禁止 (rubber-duck-review.md SSOT)              |
| Fallback lane Auto-Refill 契約                                                                                                                     | (**hard rule**)                                                                                                                        | —                                | 変更禁止 (中身の lane 順序は tunable)              |
| North-star + focus theme の合意事実                                                                                                                | (**hard rule**)                                                                                                                        | —                                | 変更禁止 (期間だけ tunable)                        |

## Tune Apply の詳細動作

**変更 log は `dashboard-state.tuningLog` に append**。schema は `references/dashboard-state.md`。

Autonomy Mode 別動作:

| Mode          | Propose                    | Apply                        | Revert 追跡                                           |
| ------------- | -------------------------- | ---------------------------- | ----------------------------------------------------- |
| Normal        | workflow-review が propose | user 承認 (security-approve) | user 判断                                             |
| **AUTO 既定** | workflow-review が propose | user 承認 (security-approve) | reporter-learner が 3 サイクル追跡、悪化で自動 revert |
| FULL          | workflow-review が propose | 自動 apply                   | reporter-learner 3 サイクル追跡、悪化で自動 revert    |
| ALL           | workflow-review が propose | 自動 apply + criteria 拡張可 | 同上                                                  |

Rule: どの mode でも **hard rule 変更疑いは security-approve に escalate**、user 明示承認まで proceed 不可。

## Revert Contract

reporter-learner が 3 サイクル追跡:

- `tuningLog` の `trackedMetrics` を各サイクルで測定
- Baseline (change 前 3 サイクル平均) と比較
- 悪化閾値 (既定: -10% 以上、これも tunable) 超過で `revertVerdict = { verdict: "reverted", reason }` を append
- Revert は元の値を再 apply、`tuningLog` に新 entry (reason: "auto-revert")
- 悪化なしなら `revertVerdict = { verdict: "kept" }`

## Hard Rule 誤変更抑止 (Invariant Check)

workflow-review が weekly + ad-hoc で以下 invariant を check:

1. `references/approval-policy.md` に "auto" と "security-approve" バケット両方の見出しが存在するか (grep)
2. `references/rubber-duck-review.md` の "Layer 3 Blocking Gate List" に 5 gate が全部あるか
3. `references/fallback-lane.md` の Auto-Refill 契約節が存在するか
4. `references/persistence-profile.md` の 3 profile (Standard / Persistent / Exhaustive) が全部定義されているか
5. `SKILL.md` の "Tunable vs Hard Rules" 節が存在するか

**Invariant 違反検出時**:

- `dashboard-state.hardRuleViolationLog` に append
- workflow-review が blocker として user notify + revert 提案
- Auto-apply mode (FULL/ALL) でも hard rule 違反は必ず user 承認要 (security-approve escalate)

## 既存 workspace への影響 (Backward Compatibility)

- `tuningLog` / `hardRuleViolationLog` は新 field。既存 workspace の `dashboard-state.json` に field が無くても動作
- 新 tuning event 発生時点で workflow-review が自動 append (field が無ければ `[]` で初期化)
- 既存 tune 履歴は補完しない (前向き記録のみ)

## Split Rule

このファイルが 300 行超えたら `references/tunable-defaults-{category}.md` に split:

- `-fallback` (fallback lane / discovery floor / anti-pattern)
- `-persistence` (3 profile / class mapping / attempt-log)
- `-cadence` (worker / workflow-review / digest / burst)
- `-critic` (layer / rubric / questions)

Split 時も本ファイルは index として残す (categories 一覧 + hard rules 再掲)。

## See Also

- `references/runtime-modes.md`: `ai-autonomous` preset SSOT (Autonomy Mode 別 tune 動作 table)
- `references/dashboard-state.md`: tuningLog / hardRuleViolationLog schema
- `references/rubber-duck-review.md`: Critic Layer / Layer 3 Blocking Gate List SSOT
- `references/approval-policy.md`: Approval bucket 構造 (hard rule)
- `references/fallback-lane.md`: Fallback lane 順序 (tunable) / Auto-Refill 契約 (hard rule)
- `references/persistence-profile.md`: 3 profile 数値 (tunable) / Replan 契約 (hard rule)
