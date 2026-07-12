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

## Health Reconciler

Add a slower read/repair loop when multiple workflows share durable state.

Check:

- JSON/JSONL parse validity,
- dashboard vs durable queue/portfolio/product counts,
- prompt-file vs embedded scheduler drift,
- stale locks and claims,
- automation enabled/schedule mismatches,
- WIP/retry/slice limits,
- workflows stalled despite safe eligible tasks.

Auto-repair only reversible local drift:

- dashboard reconciliation,
- count/path/status fixes,
- stale lock removal only after heartbeat expiry plus no matching live/in-progress state,
- prompt reference drift,
- missing compact no-op/error records.

Never delete a lock from TTL alone. Require an expired heartbeat plus no matching live/in-progress state update; use at least 2x TTL before automatic removal.

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
