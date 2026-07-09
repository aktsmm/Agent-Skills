# Runtime Modes

The factory should keep working even when OpenClaw-specific features are unavailable. Treat the periodic prompts as the portable core, then choose an execution adapter.

## Portable Core

Use three recurring prompt roles:

| Prompt             | Typical cadence     | Purpose                                                           |
| ------------------ | ------------------- | ----------------------------------------------------------------- |
| `commander`        | frequent            | inspect state, import artifacts, refill queue, aggregate blockers |
| `worker`           | frequent / parallel | run exactly one task and write one artifact                       |
| `reporter-learner` | slower              | summarize outcomes, update learning, choose next-cycle focus      |

The same prompt text can run in OpenClaw, VS Code Chat, Copilot CLI, another agent runner, or a human-operated checklist.

## Mode Selection

| Environment            | How to run                                                                    | Notes                                                        |
| ---------------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------------ |
| Hosted agent scheduler | register the three prompts as recurring jobs                                  | best when the platform persists state and has approval gates |
| OpenClaw available     | schedule the three prompts with cron / isolated sessions                      | best for unattended local loops                              |
| VS Code only           | run prompts manually or through task/script wrappers                          | good for design and supervised runs                          |
| Generic CLI agent      | call the prompt files from a scheduler                                        | keep state paths configurable                                |
| No file tools          | return proposed state updates and artifact text for human/application to save | do not pretend persistence happened                          |

## State Files

Use a workspace-local state folder such as `factory-state/` or any user-provided equivalent. Avoid hardcoded absolute paths.

Suggested files:

- `factory-state.json`: frame, counters, learning, thresholds
- `tasks-pending.json`: executable queue
- `tasks-done.json`: completed/skipped/failed history
- `artifacts/*.md`: one artifact per task
- `outcome-log.json`: observed/estimated/assumed metrics
- `pipeline-log.jsonl`: append-only audit log

If the user already has a state layout, adapt to it instead of renaming everything.

## Single-Cycle Automation

When the queue is small and tasks are safe/local, prefer one scheduled automation that performs `commander -> one worker task -> reducer` in a single run instead of separate commander and worker automations. This reduces state drift and halves scheduled runs, but only works when the cycle can safely update state.

Rules:

- Pick at most one auto-eligible task per run.
- Auto-skip tasks that require manual play, GUI-only judgment, legal/risk acceptance, publishing, payment, account creation, secrets, personal data, or long-running work.
- Before rewriting JSON array state files, create backups, parse the original, rewrite the full array, parse the result, and restore backup on failure.
- Use an append-only JSONL pipeline log for audit records.
- Use a short-lived lock file or equivalent lease; if the lock is still valid, skip and log a no-op.
- Mark a task done only when its artifact contains evidence that the success metric was met; otherwise leave it pending or blocked.

## Cadence Defaults

Start conservative and tune after the first few cycles:

- commander: every 15-60 minutes
- worker: every 15-120 minutes, depending on task cost
- reporter-learner: every 6-24 hours
- workflow-review: weekly, or after 10-20 artifacts if the factory is moving quickly

For manual operation, run one commander, one worker, then one reporter-learner after a few artifacts exist.

## Scheduler Presets

Use these as starting points when the environment can run scheduled prompts or jobs. Replace command placeholders with the local agent runner.

For surface-specific setup across GitHub Copilot App, GitHub Copilot CLI, Microsoft Scout, VS Code GitHub Copilot Chat, OpenClaw, and GitHub Actions, first use `references/workspace-setup.md` to verify capabilities and state persistence.

### Conservative Default

Use this first for a new factory or expensive model/tool stack.

| Job              | Cadence    | Action                                                            |
| ---------------- | ---------- | ----------------------------------------------------------------- |
| commander        | every 60m  | import artifacts, refill queue to low targets, aggregate blockers |
| worker           | every 120m | run one pending task and write one artifact                       |
| reporter-learner | every 24h  | summarize, update learning, choose next focus                     |
| workflow-review  | weekly     | review cadence, queue quality, state drift, and missing gates     |

### OpenClaw / Cron

Best for unattended operation with isolated sessions and shared state.

| Job              | Cadence                      | Notes                                                             |
| ---------------- | ---------------------------- | ----------------------------------------------------------------- |
| commander        | every 15-30m                 | single writer for queue/state/logs                                |
| worker           | every 30-60m per worker      | each worker runs one task only; parallel workers are allowed      |
| reporter-learner | every 6-8h                   | compress notifications and update learning                        |
| workflow-review  | weekly or every 20 artifacts | rubber-duck the factory itself and propose prompt/cadence changes |

Rules:

- Run worker prompts in isolated sessions when possible.
- Give each specialist worker a narrow capability or task kind.
- Keep external publish, paid actions, account creation, and secret access behind human approval.

### Hosted Agent Scheduler

Use this for scheduler-capable hosted agent environments. Examples might include Copilot Scheduler, GitHub Copilot App, Microsoft Scout, or similar products when the current product version actually supports recurring prompts/jobs.

| Job              | Cadence       | Notes                                                            |
| ---------------- | ------------- | ---------------------------------------------------------------- |
| commander        | every 30-60m  | inspect platform-persisted state, import artifacts, refill queue |
| worker           | every 60-180m | run one task; use platform tools only within the approved scope  |
| reporter-learner | every 8-24h   | publish a compact report and update learning                     |
| workflow-review  | weekly        | check scheduler drift, dashboard freshness, and unsafe autonomy  |

Rules:

- Treat the hosted platform as an execution adapter, not as the factory design itself.
- Verify where state persists: repo files, platform memory, issue/discussion, database, artifact storage, or external workspace.
- Prefer platform-native approvals for publish, payment, account, secret, personal-data, and policy-risk actions.
- If the platform cannot write durable artifacts, have workers return artifact text and let commander persist or propose persistence.
- Do not assume product-specific feature names; map whatever the platform offers to `commander`, `worker`, and `reporter-learner`.
- For small queues, a single-cycle hosted automation can replace separate commander/worker jobs if JSON state updates are backed up, validated, and locked.

### Copilot Scheduler (VS Code Extension)

Use this when the VS Code Copilot Scheduler extension is installed and the factory should run as scheduled Copilot Chat prompts in a workspace.

| Job              | Suggested schedule           | Notes                                                         |
| ---------------- | ---------------------------- | ------------------------------------------------------------- |
| commander        | `0 * * * *` or every 60m     | workspace-scoped task; imports artifacts and refills queue    |
| worker           | `15 */2 * * *` or every 120m | workspace-scoped task; one task only; task-level max runs/day |
| reporter-learner | `0 9,17 * * *` or daily      | compact status report; use quiet notifications if available   |

Settings and task options to verify:

- Task scope is workspace, not global, unless intentionally shared.
- Prompt templates point to local `.github/prompts/*.md`, the configured global prompts folder, or inline prompt text.
- Agent/model selection works for the selected Copilot Chat mode.
- `Max Runs/Day`, allowed time window, jitter, and minimum interval warnings are configured.
- Notification mode and execution history are configured for low noise.
- `auto-mode` or autonomous-execution hints are enabled only after preflight passes.
- Copilot usage and acceptable-use limits are respected; avoid excessive automated bulk activity.

Treat Copilot Scheduler as a VS Code adapter. It schedules prompt execution; the factory still needs durable state, artifacts, approval boundaries, and validation.

### Generic Cron / CLI Scheduler

Use when any command-line agent can be invoked from cron, systemd timer, launchd, or another scheduler.

```text
# placeholders only; replace <run-prompt> with the local runner
0 * * * * <run-prompt> assets/prompts/commander.md
15 */2 * * * <run-prompt> assets/prompts/worker.md
0 9,17 * * * <run-prompt> assets/prompts/reporter-learner.md
```

Keep state paths configurable. Do not embed machine-specific absolute paths in prompt files.

### Windows Task Scheduler

Use for a Windows workstation or always-on desktop.

| Job              | Cadence              | Recommended conditions                        |
| ---------------- | -------------------- | --------------------------------------------- |
| commander        | every 30-60m         | run only when network is available            |
| worker           | every 60-120m        | run only on AC power for laptops              |
| reporter-learner | daily or every 8-24h | run at logon plus scheduled summary if useful |

Prefer a small PowerShell wrapper that calls the local agent runner with a prompt file. If Task Scheduler cannot be registered, use a user-level startup/keepalive mechanism only after confirming it will not spawn duplicate loops.

### GitHub Actions

Use only for low-frequency, repo-safe automation.

| Job              | Cadence                    | Notes                                                         |
| ---------------- | -------------------------- | ------------------------------------------------------------- |
| commander        | every 1-3h                 | propose or commit state updates only if repo policy allows it |
| worker           | daily or workflow_dispatch | avoid expensive or secret-dependent work by default           |
| reporter-learner | daily                      | publish to workflow summary, issue comment, or artifact       |

Rules:

- Treat runners as ephemeral; persist state as repository files, artifacts, issues, or external storage.
- Avoid external publishing, payments, account creation, and secret-dependent actions unless explicitly approved.
- Keep GitHub-hosted runner minutes and API rate limits in the runtime limits.

### Manual Supervised Loop

Use when no scheduler is available or when testing a new factory.

```text
commander -> worker -> worker -> reporter-learner
```

Run the reporter after two or more artifacts exist, or when a blocker appears.

## Operating Profiles

| Profile    | Commander | Worker  | Reporter | Workflow review  | Use when                                       |
| ---------- | --------- | ------- | -------- | ---------------- | ---------------------------------------------- |
| low-cost   | daily     | daily   | weekly   | monthly/weekly   | exploration is cheap but not urgent            |
| supervised | manual    | manual  | manual   | manual           | new factory or high-risk domain                |
| standard   | 30-60m    | 60-120m | 8-24h    | weekly           | normal unattended improvement                  |
| burst      | 15m       | 15-30m  | 6h       | after sprint/day | short sprint with explicit budget and approval |

Do not use burst mode without daily run limits and a clear stop condition.

## AI-Autonomous Preset (`ai-autonomous`)

`ai-autonomous` preset は Autonomy Mode 別に skill 全体を自律運用するための SSOT preset。既定は AUTO、setup で mode 未指定なら Phase 1 で必ず user に確認する。

### 既定値 (all reference default, tunable)

| Item                         | Default                                                                                                | Tunable?                            |
| ---------------------------- | ------------------------------------------------------------------------------------------------------ | ----------------------------------- |
| Autonomy Mode                | **AUTO**                                                                                               | setup 質問で mode 選択              |
| Approval buckets             | `auto` / `security-approve` (詳細: `references/approval-policy.md`)                                    | **hard rule** (bucket 構造)         |
| Fallback lane                | enabled、順序 A、Discovery Floor=5 cycles、Browser-Defer=enabled (詳細: `references/fallback-lane.md`) | tunable (順序/Floor/lane 内容)      |
| Persistence default          | Persistent、class 別 mapping (詳細: `references/persistence-profile.md`)                               | tunable (数値/mapping)              |
| Cadence                      | worker=hourly、workflow-review=weekly + ad-hoc trigger、digest=daily                                   | tunable (workspace 目的で override) |
| Per-hour override            | 可 (workspace ごとに quiet hours / burst 定義可)                                                       | tunable                             |
| Burst mode                   | AI 自律判定 (新規テーマ 3 日は 15min 昇格可)                                                           | tunable                             |
| Critic Layer 3 blocking gate | 5 gate (SSOT: `references/rubber-duck-review.md`)                                                      | **hard rule** (5 gate 対象)         |
| Adapter                      | 環境依存 (下記例示)                                                                                    | 環境変化時 workflow-review propose  |
| Push cadence                 | manual (setup で 1 度質問)                                                                             | tunable                             |
| Cost / quota                 | skill 対象外 (adapter throttle 任せ)                                                                   | —                                   |

### Adapter 例示 (実選択は環境依存)

- Copilot Scheduler (VS Code Extension)
- Microsoft Scout Automation
- OpenClaw
- GitHub Copilot App
- GitHub Actions
- Windows Task Scheduler
- cron / Generic CLI Scheduler
- Manual Supervised Loop

各 adapter の設定例は本ファイル `## Scheduler Presets` セクション参照。

### Tune Apply by Autonomy Mode (SSOT)

**この table が Autonomy Mode 別の tune apply 動作の SSOT**。`references/tunable-defaults.md` はこの table を参照する。

| Mode          | Tune propose               | Tune apply                           | Hard rule 変更疑い          | Revert 追跡                                        |
| ------------- | -------------------------- | ------------------------------------ | --------------------------- | -------------------------------------------------- |
| Normal        | workflow-review が propose | user 承認必須 (security-approve)     | 全 rule change が user 承認 | user 判断                                          |
| **AUTO 既定** | workflow-review が propose | **user 承認必須 (security-approve)** | user 承認必須               | reporter-learner 3 サイクル追跡、悪化で自動 revert |
| FULL          | workflow-review が propose | 自動 apply                           | security-approve escalate   | 同上                                               |
| ALL           | workflow-review が propose | 自動 apply + criteria 拡張可         | security-approve escalate   | 同上                                               |

Rule:

- どの mode でも hard rule 変更疑いは security-approve に escalate、user 明示承認まで proceed 不可
- Reference default 変更は tunable-defaults.md の一覧項目のみ、hard rule 侵食禁止
- 3 サイクル追跡の baseline / 悪化閾値は tunable-defaults.md 参照

### Workflow-review Dispatch

- 通常: weekly cadence
- Ad-hoc: 以下 trigger で hourly cycle 内でも dispatch (詳細: `references/tunable-defaults.md` "Workflow-review Dispatch" 節)
  - Blocker Test 4/4 escalation が 24h で 3 件以上
  - Anti-pattern registry の同一 fingerprint count が K=3 到達
  - Discovery Floor trigger が 3 サイクル連続でも新規 candidate 流入ゼロ
  - Critic-log の Layer 3 reject が 24h で 2 件以上

### Invariant Check (Hard Rule 誤変更抑止)

Workflow-review が weekly + ad-hoc で以下 invariant を check、違反検出時は `dashboard-state.hardRuleViolationLog` に append + user notify + revert 提案:

1. `references/approval-policy.md` に `auto` / `security-approve` 見出し両方 present か
2. `references/rubber-duck-review.md` の "Layer 3 Blocking Gate List" に 5 gate 全部 present か
3. `references/fallback-lane.md` の Auto-Refill 契約節 present か
4. `references/persistence-profile.md` の 3 profile 全部定義 present か
5. `SKILL.md` の "Tunable vs Hard Rules" 節 present か

詳細と対処: `references/tunable-defaults.md` "Hard Rule 誤変更抑止 (Invariant Check)" 節。

### See Also

- `references/tunable-defaults.md`: reference default 一覧 + hard rules + Autonomy Mode 別動作
- `references/approval-policy.md`: 2 バケット詳細
- `references/rubber-duck-review.md`: Layer 3 gate SSOT
- `references/fallback-lane.md`: fallback lane / Discovery Floor / Auto-Refill
- `references/persistence-profile.md`: 3 profile / class mapping
- `references/dashboard-state.md`: tuningLog / hardRuleViolationLog schema

## Runaway Controls

Every scheduled setup should define these controls in state or scheduler configuration:

| Control                | Purpose                                     | Suggested default                               |
| ---------------------- | ------------------------------------------- | ----------------------------------------------- |
| `maxPendingTasks`      | prevents queue inflation                    | 10-30                                           |
| `maxDailyWorkerRuns`   | bounds cost and tool usage                  | 6-24                                            |
| `maxDailyCostEstimate` | makes model/API spend visible               | user-defined                                    |
| `lockTtlMinutes`       | prevents stuck claims                       | 120-240                                         |
| `staleTaskTtlHours`    | forces old tasks to be reviewed or replaced | 24-72                                           |
| `blockerThreshold`     | avoids interrupting humans too early        | 3 similar blockers                              |
| `quietHours`           | reduces noise                               | local non-working hours                         |
| `notifyOnlyOn`         | compresses notifications                    | reporter, repeated-blocker, high-value-decision |

Commander must not add work when limits are exceeded. Reporter-learner should surface limit hits and recommend lowering cadence, increasing budget, or pruning stale work.

## OpenClaw-Specific Behavior

OpenClaw can run this as unattended cron pulses, but the skill must not require OpenClaw.

When OpenClaw is present:

- map `commander` to the orchestrator agent
- map `worker` to one or more specialist agents
- map `reporter-learner` to the reporting/orchestrator agent
- keep worker outputs artifact-only
- keep shared state updates single-writer

When OpenClaw is absent, preserve the same contracts and run the prompts through whatever execution mechanism is available.

## Stop and Ask

Stop unattended execution and ask the user when:

- external publishing, payment, account creation, or secret access is required
- repeated blockers pass the configured threshold
- the factory cannot persist state or artifacts
- the next step could create legal, safety, privacy, or platform policy risk
- the success metric cannot be observed or estimated honestly
