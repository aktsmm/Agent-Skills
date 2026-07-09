# Self-Designing Factory Loop

Use this reference when the user gives a theme or purpose and expects the agent to create a workspace that keeps improving over time.

## Core Pattern

Given a theme, the factory should design both the product workflow and the meta-workflow:

```text
theme intake
-> factory frame
-> workspace/state layout
-> portfolio or candidate lane
-> scheduled workflows
-> canonical dashboard
-> workflow-review loop
-> approval and runaway controls
```

The goal is not to make infinite apps. The goal is to keep producing evidence, candidate improvements, and next-phase decisions inside explicit safety boundaries.

## Required Loops

### 1. Candidate advancement loop

Moves the current best candidate toward its next gate.

- Reads dashboard, queue, artifacts, candidate gate, and state.
- Picks at most one safe task.
- Produces at most one artifact.
- Updates queue, outcome log, pipeline log, and dashboard.
- Does not expand scope when the latest gate is PIVOT/PARK.

### 2. Discovery / portfolio loop

Finds new ideas and keeps a bounded portfolio.

- Starts from market/user pain, not random themes.
- Runs researcher + adversarial reviewer + state recorder in one bounded cycle.
- Keeps Top-N capacity fixed.
- Uses watchlist/rejected states instead of forcing promotion.
- Compares before replacing an incumbent.

### 3. Workflow-review loop

Reviews the factory itself.

- Runs slower than workers, usually weekly or after a fixed artifact count.
- Rubber-duck reviews cadence, queue quality, missing gates, state drift, dashboard freshness, duplicate work, and unsafe autonomy.
- Recommends prompt, queue, dashboard, or schedule changes.
- Does not directly weaken gates or increase autonomy unless the approval policy allows it.

### 4. Prompt self-improvement loop

Turns workflow-review findings into safe local prompt and contract updates.

- Edits only workspace-local prompt or contract files by default.
- Leaves a prompt-change artifact with before/after intent and rollback note.
- Updates the canonical dashboard after prompt changes.
- Requires approval before increasing autonomy, schedule frequency, external actions, or weakening gates.

## Minimal Workspace Layout

```text
AGENTS.md
.github/prompts/
  factory-*-cycle.md
  factory-dashboard-update-contract.md
factory-state/
  factory-state.json
  dashboard-state.json
  tasks-pending.json
  tasks-done.json
  outcome-log.json
  pipeline-log.jsonl
  artifacts/
  portfolio-topN.json        # when portfolio discovery is needed
  dashboard-state.json.bak   # refreshed before dashboard rewrites
```

Adapt names to the workspace, but keep the concepts distinct.

## Setup Algorithm

1. Ask at most one clarifying question if the theme is ambiguous.
2. Freeze domain, artifact type, audience, success metric, approval boundaries, and forbidden actions.
3. Decide whether the factory needs:
   - candidate advancement only,
   - discovery + portfolio,
   - build/prototype lane,
   - workflow-review loop.
4. Create the durable state files and dashboard before scheduling workers.
5. Create prompt files that read the dashboard first and update it after state changes.
6. Add schedules only after explicit user approval and with WIP/run limits.
7. Run a small manual cycle or dry-run before trusting unattended runs.
8. Add a workflow-review loop that can reduce noise, fix prompt drift, and propose cadence changes.
9. Add a prompt self-improvement contract if workflows are allowed to edit local prompt files.

## Replacement Gate for Top-N Portfolios

When Top-N is full, a new idea can replace an incumbent only if the artifact includes:

- evidence links or observed signals,
- score/rubric comparison against the weakest incumbent,
- reviewer critique for both the challenger and incumbent,
- demotion reason for the incumbent,
- next evidence required for the promoted idea,
- explicit note that no implementation is started by promotion alone.

If the evidence is not strong enough, put the idea in watchlist or rejected.

## Runaway Controls

Every self-designing factory needs:

- max active candidates,
- max pending tasks,
- max artifacts per run,
- max daily runs,
- lock/lease or stale-write check for shared state,
- human approval boundaries,
- quiet/notification rules,
- dashboard backup and conflict handling,
- prompt-change artifact and rollback note for self-improvement edits,
- stop conditions for repeated blockers and low-value churn.

## Gate Taxonomy

Do not use "approval" as one ambiguous gate. Record three separate gates:

1. **Reviewer gate**: an independent evaluator checks evidence, scope, risks, and success criteria. PASS can advance work inside the approved autonomy envelope.
2. **Queue-eligibility gate**: the next task must explicitly name candidate/scope, success metric, verification, WIP limit, and forbidden actions before a worker can pick it.
3. **Human-approval gate**: required only for the `security-approve` bucket, such as public release, payment/account creation, secret write/issue/delete/external send, personal-data external send, backup-impossible destructive actions, legal-risk acceptance, or expanding the approved automation envelope.

When the user has already authorized local/private prototype or code work:

- do not block every implementation task on another user confirmation,
- use reviewer PASS to create the next explicit queued task,
- keep public/external/paid/legal actions blocked,
- on reviewer reject/ambiguity, revise, narrow, re-queue, or use a fallback lane before escalating,
- surface the user only when bounded retries cannot resolve the review or a `security-approve` boundary is reached.

Store the autonomy envelope and human-only boundaries in durable dashboard/state so future sessions do not reintroduce artificial blockers.

## Done Criteria

- The workspace can answer "what is going on?" from dashboard state without chat history.
- Every scheduled workflow has a role, cadence, WIP limit, artifact contract, and dashboard update duty.
- The factory can keep improving its own workflow without silently increasing risk.
- Candidate promotion, phase advancement, and portfolio replacement all require review evidence.
- Work inside the approved autonomy envelope does not repeatedly ask for human approval; reviewer and queue gates provide bounded progression.
- Prompt self-improvements are local, evidenced, reversible, and dashboard-recorded.
