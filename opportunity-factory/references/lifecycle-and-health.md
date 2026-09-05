# Factory Lifecycle Completion and Health

Use this reference when the factory should continue beyond discovery or graybox and remain operable without manual state reconstruction.

## Complete Lifecycle

A durable end-to-end factory separates these lanes:

```text
discovery / Top-N
-> portfolio promotion
-> private graybox
-> GO / PIVOT / PARK
-> product maturation
-> private release-readiness
-> security-approve boundary for public/external actions
```

Do not collapse all lanes into one worker. Each lane needs its own state, queue, WIP limit, artifact contract, reviewer, and dashboard projection.

## Portfolio Promotion Lane

Purpose: move one Top-N candidate to an evidence-backed graybox decision.

Recommended stages:

```text
select -> direct evidence -> graybox brief/gate -> independent review
-> local prototype -> verify/playfeel -> decide -> complete
```

Controls:

- Activate only at the configured portfolio threshold.
- WIP=1 by default.
- Use a portfolio-level bootstrap task when selection itself determines the candidate.
- Protect `currentWip` from portfolio demotion/replacement.
- One stage/task/artifact per run.
- Independent reviewer owns review transitions.
- Reviewer reject triggers bounded revise/re-review before escalation.
- Build success cannot produce GO without the frozen exit verifier.

## Product Maturation Lane

Purpose: move an evidence-backed graybox GO to private release-readiness.

Recommended stages:

```text
GO intake -> MVP boundary -> implementation slice -> verify slice
-> independent review -> iterate -> release-readiness -> complete
```

Controls:

- Activate only from durable GO evidence, never score/rank/build success alone.
- WIP=1 by default.
- Freeze the MVP boundary before implementation.
- Limit implementation slices and review revisions.
- Each slice has explicit success metrics and verification.
- Reviewer decides complete/continue/revise/pivot/park.
- Private release-ready is not public release approval.
- Public publish, payment/account, external-sensitive writes, and legal-risk acceptance remain `security-approve`.

## Deterministic State Machines

Every staged lane should record:

- `currentWip`,
- `stage`,
- task sequence,
- required task schema,
- allowed transitions,
- retry/slice counters,
- completion/park history,
- next selection cooldown,
- scheduler and reviewer IDs.
- persisted slice/revision counters for any iterative build lane.

The reducer must move exactly one task to done and enqueue at most one next-stage task per transition.

When multiple eligible candidates exist, define a deterministic selection order such as oldest unconsumed gate decision then normalized candidate ID.

## Independent Review

The worker that produced evidence/design/code must not issue its own blocking PASS.

Use a separate scheduled reviewer or separate agent context that:

- reads frozen criteria and evidence,
- produces one review artifact,
- applies one deterministic transition,
- does not implement in the review run.

## Lock Scopes

SSOT for locking. `SKILL.md` and `runtime-modes.md` state the acquisition primitive; this section defines **what** must be locked.

Three scopes, all acquired with create-new/O_EXCL semantics, never test-then-create:

- **Task lock** (`locks/<task-id>`) — prevents two runs from processing the same task.
- **Worker singleton lock** (`locks/_worker`) — scoped to a **shared-state or exclusive-resource domain**. Prevents two worker runs from executing against the same domain at all. **A task lock alone is not enough**: two concurrent workers each claim a _different_ task and run in parallel, which corrupts shared state writes and breaks single-instance external resources (desktop automation, a browser profile, an exclusive database handle). Acquire it before selecting a task and hold it through the fallback lane, which also mutates state.
- **Exclusive-resource lock** — only when a lane touches a resource not already covered by its worker singleton.

Parallel workers stay allowed **only when their state and resources are disjoint**. Same-domain parallelism is not a tuning knob.

TTL rules:

- Reaping only happens after the recovery window in `## Health Reconciler` (2x TTL with no heartbeat), so the quantity to size against is **2x TTL, not TTL**. If a crashed run must be recoverable before the next scheduled run, set `2 x TTL < cadence`. Otherwise accept that one cycle may be skipped and say so explicitly rather than discovering it as an outage.
- Provide a heartbeat command so a legitimately long run can extend its own TTL instead of being preempted.
- Release must be explicit and verified. A release that silently fails to remove the lock is worse than no release, so report a non-zero result when the owner check fails.
- Reaping an expired lock belongs to the commander, and only after artifact reconciliation. Never reap a lock still inside its recovery window.

## Health Reconciler

Add a slower read/repair loop when multiple workflows share durable state.

Check:

- JSON/JSONL parse validity,
- dashboard vs durable queue/portfolio/product counts,
- scheduler prompt source/path/fallback-snapshot drift,
- stale locks and claims,
- automation enabled/schedule mismatches,
- WIP/retry/slice limits,
- workflows stalled despite safe eligible tasks.

Auto-repair only reversible local drift:

- dashboard reconciliation,
- count/path/status fixes,
- stale lock removal only after heartbeat expiry plus no matching live/in-progress state,
- interrupted-run reconciliation across lock, task claim, expected artifact, changed targets, done history, and pipeline log,
- scheduler prompt-binding repair only when source, resolved path, and normalized fallback snapshot (BOM, line endings, trailing newline) can be read back together; preserve cadence and enabled state, re-read and retry once on a concurrency conflict, otherwise record a blocker,
- missing compact no-op/error records.

Never delete a lock from TTL alone. Require an expired heartbeat (use at least 2x TTL), no live process/lease or fresh heartbeat, and reconciliation of the claimed task. A persisted `in_progress` status without a fresh heartbeat is evidence of an interrupted run, not a live run.

For an interrupted mutating run:

1. Read the lock's task ID and timestamps.
2. Check expected artifact, target-file timestamps/diff, done history, outcome log, and pipeline log.
3. If artifact and success evidence are complete, import/reduce idempotently.
4. If side effects exist but artifact or verification is missing, preserve the side effects, return the task to `pending` or `recovery`, and require bounded verification.
5. If nothing changed, return the task to `pending`.
6. Record the recovery in dashboard/outcome/pipeline state, then remove the stale lock.

For an interrupted `repair` child, also reconcile `parentTaskId`, `inputHash`, and `criticLog`. A repair claim without validation is `repair-start-failed` for its already-reserved parent attempt; preserve partial output and requeue only while the repair cap remains. A repair output with validation but no independent receipt resumes the same workflow round. Never silently reset either condition to a fresh pending repair.

For a suspected scheduled failure, require command exit/output and the expected artifact to agree. Scheduler history and terminal/PTY warnings are corroborating signals; a host warning alone is not a task failure.

For a launched app/service that must stay open, use the harness-supported detached mode and verify the same process identity remains responsive for a declared observation window **after the launch tool/caller returns**. A momentary PID/window, launcher exit code or headless test does not prove interactive lifetime. If it exits, retain logs and distinguish application failure from launch-host cleanup as hypotheses until reproduced; do not claim an argument or renderer fix from a brief restart alone.

Never infer task completion from a modified target file alone.

Never auto-change:

- product/portfolio criteria,
- GO/PIVOT/PARK decisions,
- approval boundaries,
- autonomy mode,
- schedule frequency,
- public/external state.

## Scheduling

Stagger mutating lane and independent reviewer runs. Avoid sharing a write window with weekly workflow review or another reducer.

Example order:

```text
health -> candidate lane -> discovery -> promotion -> promotion reviewer
-> maturation -> maturation reviewer -> workflow review
```

Exact cadence is a reference default and should be tuned from observed artifact throughput and collision history.

## Done Criteria

- A candidate can progress from discovery to private release-readiness without artificial human confirmation inside the approved autonomy envelope.
- Public/external actions still stop at `security-approve`.
- Every lane has WIP/retry/slice caps and an independent reviewer.
- Dashboard state can explain the complete lifecycle and current bottleneck.
- Health reconciliation repairs reversible drift without changing product decisions or safety policy.
- Interrupted runs recover through artifact/side-effect reconciliation and cannot remain permanently blocked by stale `in_progress` state.
