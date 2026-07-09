# Fallback Lane

Worker task が blocked / stall / idle になったときに **自動で dequeue する代替 task の順序** と **auto-refill / blocker gate / browser-defer / anti-pattern registry** の契約。工場が空回りせず、承認待ちで止まらず、同じ罠を反復しないようにする。

## Lane Order (品質重視 A)

Fallback lane 起動時、以下の順に auto-dequeue する。各 lane は必要な入力が揃っていれば実行、揃っていなければ次 lane へ skip。

| #   | Lane                                       | 中身                                                                  | Persistence | 承認                                    |
| --- | ------------------------------------------ | --------------------------------------------------------------------- | ----------- | --------------------------------------- |
| 1   | Portfolio review / scoring                 | Top-N 候補比較、demote / promote / watchlist 整理                     | Standard    | auto                                    |
| 2   | Prompt / workflow self-review              | 実行済 task の教訓を prompt / cadence 改善提案 (Small-Bet-First)      | Exhaustive  | auto (commit は smoke test 経由)        |
| 3   | Critic Role invocation (advisory)          | 既存 top artifact に対して harsh critic run、`critic-report.md` 出力  | Persistent  | auto                                    |
| 4   | Anti-pattern registry 更新                 | 直近 failure fingerprint を registry に append                        | Standard    | auto                                    |
| 5   | Discovery                                  | 新規 candidate 探索、Web 検索 / API GET / 関連トピック抽出            | Persistent  | auto (write 系 API は security-approve) |
| 6   | Small-Bet Pilot                            | Validated 候補で dummy data + MVP を回す                              | Persistent  | auto (real-surface write は defer)      |
| 7   | Learning 反映                              | reporter-learner が learning を更新、次サイクル queue seed に落とす   | Standard    | auto                                    |
| 8   | Cleanup                                    | tmp 掃除、log rotate、backup rotate                                   | Standard    | auto                                    |
| 9   | Real-surface verification (read-only 限定) | 保留中の real-world 検証、API GET / DOM snapshot / screenshot のみ    | Standard    | auto (write は defer)                   |
| 10  | HITL digest 作成                           | pending approval batch、Auto-Handled Blockers、Next 3 runs をまとめる | Standard    | auto                                    |

## Discovery Floor Rule

Fallback lane を回すたびに Discovery (#5) を skip すると portfolio が古くなる。

- Counter: 最後に Discovery を実行してからの経過 fallback cycle 数
- Trigger: **5 サイクル毎に最低 1 回、必ず Discovery を実行**
- 実装: Fallback dispatcher は counter >= 5 のとき lane #5 を top に一時 promote
- 追加コスト (Web 検索料等) は skill 側で考慮しない (adapter 任せ)

## Browser-Defer Rule

Small-Bet Pilot (#6) や Real-surface verification (#9) が **browser 経由の書込み系操作** を要求した場合:

- Lane 全体を止めず、対象 task を `deferred-browser-write` 状態に落とす
- 次 lane に進む
- 該当 task は human digest (#10) に「browser 承認待ち」として集約
- User が承認したら別サイクルで resume

Rule: 承認待ち task 1 個が lane 10 個全部を止めない。

## Auto-Refill Contract

Lane が全消化 (10 個全部 skip か完了) されたら:

- Reporter-learner が次の 3 種類を自動 seed:
  - **Discovery task**: 新規テーマ / 関連分野の探索
  - **Rubber-duck 対象**: 既存 top-N 候補で最古の critic-log を持つもの
  - **Top-N replacement 候補**: 直近 learning から promote 候補生成
- 3 種類全部 seed 失敗なら `workspace-idle` を dashboard-state に記録、workflow-review の cadence 対象に含める
- Idle 状態でも hourly cadence は継続 (workflow が完全停止しない)

## Blocker Test (Genuine Blocker Gate)

Task が failed / stall した瞬間に blocker 認定せず、以下 4 問 gate を通す (goal-loop 由来):

1. 外部 signal (verify 出力、test 結果、real-world response) で失敗を確認したか
2. Persistence profile 相当の **異なる approach** を N 個試したか (Standard=4 / Persistent=6 / Exhaustive=8)
3. **Replan** した (計画自体を疑って再構成した) か
4. 残った障害は自分で制御不能 (外部依存 / 承認必要 / 情報欠落) か

- 4/4 Yes: `security-approve` バケット経由で HITL escalate、dashboard に blocker 記録
- それ以外: fallback lane 遷移 (状態は `deferred` or `retry-planned`)

Test 結果は `dashboard-state.blockerGateLog` に append (schema は `dashboard-state.md` 参照)。

## Anti-Pattern Registry

同一 fingerprint の失敗を反復しない仕組み。Lane #4 が保守する。

### File

`data/factory-state.antipatterns.json` (workspace 内)

### Schema

```json
{
  "version": 1,
  "entries": [
    {
      "fingerprint": "sha256 of task_type + inputs_hash + failure_kind",
      "task_type": "e.g. small-bet-pilot | discovery | prompt-self-improvement",
      "inputs_hash": "sha256 of normalized inputs",
      "failure_kind": "e.g. schema-mismatch | rate-limit | dep-missing",
      "first_seen": "ISO-8601",
      "last_seen": "ISO-8601",
      "count": 3,
      "sample_evidence": ["path or short excerpt", "..."]
    }
  ]
}
```

### Trigger

Worker が新規 task を起票する前に registry を照合:

- Fingerprint 一致 count < 3: proceed
- Count == 3: warning、代替 approach を rubber-duck に投げるよう commander に signal
- Count >= 3: 該当 approach を **skip**、代替候補が無ければ Critic Role (#3) にエスカレート

### Retention

- 90 日で workflow-review が rotation (last_seen が 90 日以内のものだけ保持)
- 保持期間中に count が新たに +1 されたら first_seen は維持、last_seen 更新
- Rotation で消えた entry は `data/antipatterns-archive.jsonl` に append (audit 用)

## Fallback Dispatcher Contract

Worker loop の各 iteration 末尾で:

1. Primary queue に ready task があれば通常 dispatch (fallback は起動しない)
2. Primary queue が空 or 全 task が deferred/blocked:
   - Discovery Floor counter を確認、trigger 条件を満たせば lane #5 を top へ移動
   - Lane #1〜#10 を順に走査、実行可能な最初の lane を dispatch
   - どの lane も条件不足なら Auto-Refill を起動
3. Fallback 完了で counter update、log 化 (`dashboard-state.fallbackLog`)

## Dashboard-State Fields (追加)

```json
{
  "fallbackLog": [ { "ts", "lane", "task_id", "verdict" } ],
  "blockerGateLog": [ { "ts", "task_id", "questions", "verdict" } ],
  "pendingApprovals": [ { "ts", "task_id", "reason", "bucket" } ],
  "deferredBrowserWrites": [ { "ts", "task_id", "operation" } ],
  "discoveryFloorCounter": 3
}
```

## See Also

- `references/approval-policy.md`: security-approve 判定
- `references/persistence-profile.md`: approach 数の Standard/Persistent/Exhaustive 定義
- `references/rubber-duck-review.md`: Layer 1 self-critic + Layer 2/3 Critic Role
- `references/prompt-self-improvement.md`: Lane #2 の Small-Bet-First 契約
- `references/dashboard-state.md`: fallbackLog / blockerGateLog スキーマ
