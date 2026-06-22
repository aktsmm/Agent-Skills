# Steering and Final Gates

goal-loop の subgoal steering、durable ledger、final gate の実行ルール。
Codex goal tool、hidden thread state、生存・継続系の機能は扱わない。設計背景と外部出典は [design-rationale.md](./design-rationale.md) に置く。

## Effort Scaling

ゴールの大きさに応じて重さを変える。小さいゴールに full loop を被せない。

| ゴールの規模               | orchestrator                | worker                         | evaluator          | final reviewer         | ledger             | Small-Bet      |
| -------------------------- | --------------------------- | ------------------------------ | ------------------ | ---------------------- | ------------------ | -------------- |
| 些末（1 ファイル・自明）   | この skill を使わず直接実行 | -                              | -                  | -                      | -                  | -              |
| 小（数ステップ・低リスク） | 軽量                        | 1-2 直列                       | 外部検証 1 回      | 外部 evidence 突合で可 | 暗黙でよい         | 任意           |
| 中（複数成果物・依存あり） | 通常                        | 並列 read-only + 直列 mutation | rubric 評価        | 別 subagent 推奨       | 明示               | 大変更時は必須 |
| 大（不可逆・広範囲・多段） | 厳格                        | 多段 + replan                  | rubric + reference | 別 subagent 必須       | 明示・毎ループ更新 | 必須           |

Roles: orchestrator は state を所有するが、自分の成果に最終合格判定を出さない。mutation する worker と判定する evaluator / reviewer は別人格にし、役割を「読み取り/実装」と「評価/レビュー」の 2 系統に寄せる。

長期・多段・context compaction で再開が必要なゴールだけ Durable Ledger Mode を使う。会話内 ledger で足りる小さいゴールではファイルを作らない。

## Anti-Patterns

- criteria 未合意のまま実行を始める。
- 自己評価だけで PASS を出す。
- max iteration だけで stop を組む。
- 大きな変更を pilot 無しで全体適用する。
- 「委譲する」と言って orchestrator が広い調査・実装・primary verifier 実行を抱え込む。
- worker に checkpoint / complete / blocked 判定を任せる。
- ループ中に criteria をこっそり緩める。
- 改定後 criteria の PASS を original criteria の PASS として報告する。
- 実サーフェスが必要な成果を mock / static check / unit test だけで完了扱いする。
- deploy / 配布 goal を `Succeeded` 応答や build-pass だけで完了扱いする。
- worker に full transcript を渡して context を膨らませる。
- サブゴールを hard-delete する。不要になったものは `superseded` として audit-visible に残す。

## Dynamic Steering

Steering は、original brief と criteria を守ったままサブゴール分解だけを変える操作。
発見・検証失敗・blocker によって現在の分解が最善でなくなったときに使う。

Allowed mutation kinds:

- `add_subgoal`: 新しい必要作業を pending として追加する。
- `split_subgoal`: 大きすぎる subgoal を小さく分ける。
- `reorder_pending`: pending の順序だけ変える。
- `revise_pending_wording`: 目的を弱めずに wording を明確化する。
- `annotate_ledger`: 事実・判断・証跡だけ追加する。
- `mark_blocked_superseded`: replacement がある blocked goal を superseded として scheduling から外す。

Must not:

- original brief、Acceptance Criteria、must NOT、quality gate を弱める。
- subgoal を hard-delete する。
- evidence なしで auto-complete する。
- 検証や review を甘くして PASS にする。
- 通常文の曖昧な指示だけで silent mutation する。

Record accepted and rejected steering attempts in the ledger. Rejected attempts are useful evidence because they show which shortcuts were refused.

## Status Taxonomy

- `pending`: 未着手。
- `in_progress`: orchestrator が現在扱っている。
- `complete`: 外部 evidence で完了確認済み。
- `failed`: 試行が失敗した。retry 可能。
- `blocked`: 自力で制御できない外的障害がある。
- `review_blocked`: final gate / independent review が non-clean。
- `superseded`: steering で置き換え済み。削除せず監査可能に残す。

`blocked` と `review_blocked` は final completion をブロックする。解消済み evidence か replacement steering が必要。

## Durable Ledger Mode

Use durable mode only for long-running, multi-stage, or resumable goals.

Suggested artifacts:

- `brief.md`: original user brief and frozen criteria.
- `goals.json`: ordered subgoals with status, attempts, evidence, and active id.
- `ledger.jsonl`: append-only events for checkpoints and steering.

Keep the aggregate objective as a pointer to the durable plan, not a duplicated list of every subgoal. This lets steering add or split pending work without weakening the frozen top-level goal.

## Final Quality Gate

Use this gate only for high-risk changes: security-sensitive work, schema changes, deployment/distribution, wide refactors, architecture changes, or user-facing workflows.

Gate order:

1. Run targeted verification for changed behavior.
2. Run cleanup on changed files only, or record a no-op cleanup if nothing relevant exists.
3. Rerun targeted verification after cleanup.
4. Run invariant audit from Phase 1 sources.
5. Run independent review when available.

Invariant audit format:

```json
{
  "invariant": "Preserve the parser boundary.",
  "source": "brief/spec/interview/criteria",
  "status": "proved",
  "implementationEvidence": "Changed files keep parsing in the existing module.",
  "testEvidence": "Parser boundary regression passed.",
  "reviewEvidence": "Independent review confirmed the boundary."
}
```

If the gate is non-clean, do not complete the goal. Mark the current subgoal `review_blocked`, add a blocker-resolution subgoal, and continue the loop unless the blocker is genuinely external.

## Real Surface Verification

When the outcome depends on UI, browser state, authentication, native dialogs, files, clipboard, keyboard or pointer input,
window focus, notifications, media, accessibility, installation, restart behavior, OS integration, or a multi-app workflow,
the primary verifier should exercise that real surface.

Record:

- exact surface, build, URL, account type, device, and starting state;
- reproducible workflow with observable pass and fail criteria;
- evidence such as screenshots, video, console or network output, logs, resulting files, or final state readback;
- clean-state, reload, restart, failure-recovery, or negative-path checks when risk justifies them;
- required capability and fallback owner if the agent cannot access the surface.

Do not silently replace a needed real-surface verifier with a weaker check. If worker / verifier cannot access the real surface,
record the capability gap and hand off the exact manual test and required evidence to the user. Do not attempt broad real-surface
verification yourself as orchestrator.

## Worker Boundary

Workers may investigate, edit, test, and return evidence. Verifier workers may run the primary verifier and return exit code,
logs, screenshots, or readbacks. They must not own the durable ledger, mark the goal complete, or decide that a blocker is final.
The orchestrator reconciles worker evidence with frozen criteria and updates the ledger; it should not absorb broad research,
implementation, pilot, or primary-verifier execution into the main context.
