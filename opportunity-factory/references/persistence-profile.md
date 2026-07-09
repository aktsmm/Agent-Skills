# Persistence Profile

Task 単位で「どこまで粘るか」を制御する profile。goal-loop の Persistence Profile を opportunity-factory に取り込み、worker 増殖と cost 暴走を抑えつつ、大事な task はしっかり粘る。

## Profile 定義

| Profile               | max iteration | stall→replan 閾値 | replan→次 approach 閾値 | blocker 認定前 approach 数 | diminishing returns 判定 |
| --------------------- | ------------- | ----------------- | ----------------------- | -------------------------- | ------------------------ |
| **Standard**          | 12            | 4 連続 stall      | 4 サイクル              | 4 approach                 | 2 連続改善なし           |
| **Persistent (既定)** | 20            | 5 連続 stall      | 5 サイクル              | 6 approach                 | 3 連続改善なし           |
| **Exhaustive**        | 30            | 6 連続 stall      | 6 サイクル              | 8 approach                 | 4 連続改善なし           |

- **max iteration**: 単一 task の総試行上限。到達で `deferred-exhausted` へ落とす
- **stall→replan**: 同じ approach で連続 stall (前進なし) が N 回で replan (計画自体を疑う) に強制遷移
- **replan→次 approach**: replan 後の再走が N 回不発なら次 approach へ切替
- **blocker 認定前 approach 数**: Blocker Test の Q2 で「異なる approach を N 個試したか」の N
- **diminishing returns**: 直近 N iteration で成果指標が停滞なら task を defer し fallback へ

## Task Class 別のマッピング

Commander が task 起票時に class を判定し、対応する profile を紐付ける。

| Task class                                    | Profile           | 理由                                      |
| --------------------------------------------- | ----------------- | ----------------------------------------- |
| Portfolio review / cleanup / digest           | Standard          | 軽い定型 task、粘りすぎ不要               |
| Worker 本流 (candidate 育成, small-bet pilot) | Persistent (既定) | 通常 dev cycle                            |
| Prompt / workflow self-improvement            | Exhaustive        | 工場自体の改修は慎重に                    |
| Anti-pattern 分析                             | Exhaustive        | パターン抽出は深掘り必要                  |
| Critic Role (harsh critic run)                | Persistent        | verdict は 1 発で確定させる、粘りすぎ抑制 |
| Discovery                                     | Persistent        | 新規候補探索、深追いは 6 approach まで    |
| Real-surface verification                     | Standard          | read-only なので短時間                    |

class 未指定の task は Persistent 扱い (既定)。

## Cost / Quota との関係

- AI 使用料 (LLM 呼び出し量)、rate limit、premium request quota は **skill 側で扱わない**
- Adapter (scheduler / task runner) 側で管理、超過時は adapter が worker を throttle
- Skill は profile による iteration 上限のみを持つ (cost 概念は持ち込まない)

## Attempt 教訓 Table

同一 task 内での approach 履歴を持ち、次 approach 選択と anti-pattern registry 連携に使う。

### File

`data/attempt-log.jsonl` (task 完了で `data/attempts/<task_id>.jsonl` に archive)

### Schema

```jsonl
{
  "ts": "ISO-8601",
  "task_id": "...",
  "approach_id": "AP-01",
  "iteration": 3,
  "verdict": "stall|progress|complete|failed",
  "note": "short",
  "learning": "optional short",
  "evidenceRef": "path or hash"
}
```

### Rule

- 各 iteration 末尾で 1 行 append
- Verdict = `stall` が profile.stall→replan 閾値に達したら replan 強制
- Verdict = `failed` が profile.approach 数に達したら Blocker Test 起動
- Verdict = `complete` で task 終了、attempts を archive、learning を reporter-learner に渡す

## Replan Contract

Stall→replan trigger で:

1. Worker は現 approach を停止、attempt-log に `verdict: stall + replan-triggered` 記録
2. Commander に replan request を返す (worker 増殖ではなく task ledger 再構築)
3. Commander が新 approach id (AP-02, AP-03, ...) を発行、task を再 dispatch
4. Replan 回数が profile 閾値を超えたら次 approach へ、それも尽きたら Blocker Test へ

Rule: **worker は自分で approach を増やさない**、commander に replan させる (worker は 1 approach に集中)。

## Diminishing Returns 判定

「回してるが改善していない」の検出。

- 各 task に **成果指標** を定義 (Portfolio candidate なら score、pilot なら test pass rate 等)
- 直近 N iteration の指標変化が閾値未満なら `diminishing-returns` 認定
- 認定で task を `deferred-diminishing` に落とし、fallback lane #3 (Critic Role) にエスカレート
- Critic が「approach 妥当、諦めるべき」なら reject、`rejected-diminishing` に落として portfolio から demote
- Critic が「approach 変更で行ける」なら replan 強制

## Override / User 明示指示

- User が task に `persistence: exhaustive` 等を明示指定できる (dashboard 経由 or prompt)
- Commander は user 指定を優先、class 別 default は上書きされる
- Log 化 (`dashboard-state.persistenceOverrides`)

## Dashboard-State Fields (追加)

```json
{
  "persistenceOverrides": [ { "ts", "task_id", "profile", "requestedBy" } ],
  "diminishingReturnsLog": [ { "ts", "task_id", "metric", "trend" } ]
}
```

## See Also

- `references/fallback-lane.md`: Blocker Test / anti-pattern registry / defer 状態
- `references/rubber-duck-review.md`: Critic Role (Exhaustive task の critic 強制)
- `references/battle-tested-patterns.md`: 既存の blocker threshold との整合
- `assets/templates/dashboard-state.json`: persistenceOverrides / diminishingReturnsLog スキーマ
