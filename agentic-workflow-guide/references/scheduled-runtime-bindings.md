# Scheduled Runtime Bindings

Use this when an extension or service stores a scheduled task that points to a prompt, agent, model, or other runtime asset.

## Runtime And Fallback State

- Identify the authoritative runtime source: inline text, local file, global file, or remote asset.
- A scheduler may load the current local file at execution time while retaining a stored snapshot as fallback.
- Verify both the live binding and fallback copy. A valid local binding does not make a stale fallback harmless.
- When migrating a task from inline text to a local file, refresh the stored fallback from the same normalized prompt text. A redirect stub is not an equivalent fallback.

## Read-Only Verification

A deterministic verifier checks:

- task exists exactly once in the intended scope
- task is enabled and owned by the expected workspace
- schedule and selected agent/model are expected
- prompt source and relative path resolve
- the current prompt contains its required runtime contract
- the normalized fallback snapshot matches during strict release or retro validation

Normalize BOM, CRLF/LF, and trailing newlines before comparing prompt text.

## Mutation Rule

The verifier does not auto-repair scheduler state. Read current state, report exact drift, update only the intended fields through the scheduler API or UI, then read the task back.

On an optimistic-concurrency rejection, re-read the task before exactly one retry. A second rejection is a stop condition.

## Model Allocation Reviews

- Inventory live enabled tasks, actual schedules, explicit model overrides, and inherited defaults. Keep disabled/deletion candidates separate; ambiguous deletion scope needs confirmation. Preserve both the original snapshot and a refreshed current baseline after any applied change.
- Trace the execution graph, not role names: which task creates the design, changes the product, evaluates it, and repairs state? An advisory commander whose output no worker consumes is not the execution planner. Improving a workflow reviewer alone does not improve a weak producer.
- Establish the user's quality floor and cost preference before allocating tiers. Treat role fit as a hypothesis until representative outcomes support it; do not assign the newest/most expensive model automatically or downgrade every producer just to lower unit prices.
- Discover the available models from the current harness. Verify applicable official input/output/cache rates, context tiers, promotions, and billing basis before asserting relative cost. A name or family is not a price or capability measurement. For Copilot, consult [models and pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing); do not persist a dated price table as policy.
- A different-family critic can provide another perspective without requiring its flagship tier; it does not guarantee independence or better findings. Preserve separate context, source evidence, receipt requirements, and any stronger existing gate.
- Present `task | role | current explicit/inherited model | proposed model | reason | risk/rollback`. Freeze the rationale to the agreed objective rather than changing all assignments on every follow-up; explain which new evidence or requirement changes a recommendation.
- Weight estimates by actual scheduled frequency, including multiple daily runs. Label equal-token scenarios as hypothetical; include token/cache assumptions and applicable prices. Distinguish public list-price consumption, included allowance, and actual incremental billing. Compare against the named current baseline, and also the original baseline when prior upgrades would otherwise hide a net increase.
- Prefer cost per accepted outcome over unit price: include retries, idle runs, producer failures, reviewer misses, and artifact quality. Stronger models need task-specific acceptance criteria, not only a successful configuration save.
- After approval, save rollback values including absent overrides, update only authorized model fields, and read back assignments. Preserve schedules, prompts, notifications, and approval gates unless separately approved. Report configuration applied separately from real-run quality/cost evaluation; do not imply automatic monitoring or fallback exists unless implemented.

### Role Routing And Bounded Pilots

- A scheduler's controller model is not necessarily its design, implementation or image-review worker. Verify that the consumed prompt resolves a role policy and dispatches each worker with an explicit model in a separate context; keep requested and host-reported effective identity separate, with unavailable metadata marked unknown.
- Pilot a new allocation on a bounded scope before broad rollout. When both rubric and model are suspect, freeze inputs and compare both factors, including defective cases and scoped controls; store measured results separately from configuration readback. Preserve unrelated workflows and concurrent setting changes.
- Reserve comparison calls durably before dispatch and count failed/timed-out attempts against the total and per-run caps. After interruption, reconcile receipts and resume only undispatched cases; an unknown outcome is not permission to repeat a call or invent a result.
- Cache completed reviews by source hash, image/input hashes, rubric version, role and model. Skip expensive worker dispatch for unchanged or ineligible work, but include the scheduled controller's remaining overhead in cost estimates.
- Keep a blocked production task linked to the pilot's explicit adoption state. Only evidence-backed adoption unblocks that same task; failed calibration records replan or capability-blocked, not a silent model fallback, duplicate queue item or owner-test request.

## Scheduled Run Outcome Triage

- For a scheduled run, use the command exit/output and expected artifact as primary result signals. Scheduler history and terminal/PTY warnings are corroborating signals.
- A terminal/PTY exit warning, including a host-specific `-1`, is not a task failure by itself. If primary checks pass and a subsequent terminal command succeeds, record host evidence without changing interpreter or extension configuration. Escalate when a normal terminal cannot be recreated or a required command/artifact fails.

Never persist task IDs, local absolute paths, account names, or environment-specific schedules in a portable skill.
