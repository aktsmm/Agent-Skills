# Steering and Final Gates

UltraGoal から取り込む設計要素のうち、goal-loop に合うものだけをまとめる。
Codex goal tool、hidden thread state、生存・継続系の機能は扱わない。

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

Use this gate for large code changes, architecture changes, schema changes, security-sensitive work, or user-facing workflows.

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
