# Workspace Setup

Use this reference when turning Opportunity Factory into a working workspace across GitHub Copilot App, GitHub Copilot CLI, Microsoft Scout, VS Code GitHub Copilot Chat, OpenClaw, or another agent runtime.

## Setup Principle

Do not assume a product supports every capability. Select the adapter by checking capabilities, then map them to the same portable core:

```text
commander -> worker -> reporter-learner
```

## Capability Checklist

Before registering schedules or running unattended work, verify:

| Capability           | Required question                                                                           |
| -------------------- | ------------------------------------------------------------------------------------------- |
| Skill discovery      | Where does this surface load workspace or personal skills from?                             |
| Prompt invocation    | Can it run prompt files directly, or must prompts be pasted/wrapped?                        |
| Scheduling           | Does it support recurring/background jobs, or do we need an external scheduler?             |
| Persistence          | Where are state, queues, artifacts, and logs saved durably?                                 |
| Tool permissions     | Which file, shell, browser, network, and repo actions are allowed?                          |
| Approval gates       | How are publish, payment, secret, account, personal data, and policy-risk actions approved? |
| Duplicate prevention | How does the runtime avoid overlapping runs or stale claims?                                |
| Reporting            | Where do summaries and blocker questions go?                                                |

If any answer is unknown, start in supervised mode and do not schedule workers yet.

## Surface Matrix

| Surface                               | Best use                                                                                                                             | Setup notes                                                                                                                                                                    |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| GitHub Copilot App                    | repo-centered cloud or hosted agent work when recurring jobs are available                                                           | Verify scheduling, state persistence, approvals, and PR/issue behavior in the current product before unattended runs.                                                          |
| GitHub Copilot CLI                    | portable command-line runner behind cron, Task Scheduler, or another scheduler                                                       | Use prompt files or wrapper commands; keep state paths configurable and avoid secrets in prompts.                                                                              |
| Microsoft Scout                       | desktop/background agent surface when workspace, shell, browser, Microsoft 365, heartbeat, or automations are available              | Verify enabled capabilities, permission gates, workspace boundaries, and background-mode restrictions before unattended runs.                                                  |
| VS Code GitHub Copilot Chat           | supervised workspace setup, manual runs, prompt/skill authoring, and review                                                          | Use Agent mode and prompt files manually; external scheduling needs tasks/scripts or another runner.                                                                           |
| Copilot Scheduler (VS Code extension) | VS Code-local scheduled prompt execution with cron expressions, task scope, prompt templates, agent/model selection, and run history | Verify extension settings, task-level limits, prompt template paths, workspace scope, jitter, max daily executions, and Copilot Chat approval behavior before unattended runs. |
| OpenClaw                              | unattended local multi-agent cron pulses                                                                                             | Map roles to agents and keep shared state single-writer.                                                                                                                       |
| GitHub Actions                        | low-frequency repo-safe automation                                                                                                   | Persist state through repo files, artifacts, issues, or external storage; avoid secret-dependent work by default.                                                              |

## Setup Steps

1. **Pick target surfaces**
   Choose one primary runtime and optional secondary surfaces for manual review or reporting.
2. **Install or expose the skill**
   Put the skill in the surface's workspace or personal skill location, or pass the skill folder as context if the surface has no skill discovery.
3. **Create state storage**
   Initialize `factory-state.json`, `tasks-pending.json`, `tasks-done.json`, `artifacts/`, `outcome-log.json`, and `pipeline-log.jsonl` or equivalent.
   Use `assets/templates/first-run-queue.json` as the starter pending queue when the workspace has no existing queue.
   Before enqueueing it, replace domain, audience, success metric, dates, and any capability-specific assignees; leave `assignee: null` when the runtime routes tasks by capability instead of named workers.
   If file and shell access are available, use `python scripts/init_factory_workspace.py --state-dir <state-dir> --domain <domain> --artifact-type <artifact-type> --audience <audience> --success-metric <metric> --apply` to create the starter state from templates. Omit `--apply` for dry-run.
4. **Bind prompt runners**
   Map `assets/prompts/commander.md`, `worker.md`, and `reporter-learner.md` to the surface's prompt, job, or wrapper mechanism.
5. **Select schedule profile**
   Start with conservative or supervised mode. Move to standard or burst only after persistence and approvals are verified.
6. **Configure approval policy**
   Require human approval for external publishing, payment, account creation, secrets, personal data, destructive commands, and legal/platform risk.
7. **Run preflight**
   Confirm state is writable, no duplicate schedule exists, limits are present, and a test artifact can be created and imported.
   If file and shell access are available, run `python scripts/validate_factory_skill.py <skill-root>` before registering recurring jobs.
8. **Start the loop**
   Run commander once, worker once, commander again, then reporter-learner after at least two artifacts or one blocker.
   The starter queue should cover one demand-discovery task, one setup/preflight task, and one review/learning task so the first cycle tests both product fit and runtime health.

## Product-Specific Caution

Product names and capabilities change. Treat GitHub Copilot App, GitHub Copilot CLI, Microsoft Scout, and VS Code GitHub Copilot Chat as surfaces with capabilities to verify, not as fixed contracts.

Use official docs or the product UI to confirm scheduling, permissions, state persistence, and approval features before recording a setup as unattended.

## Setup Output

When asked to set up a workspace, return or write this summary:

```markdown
## Opportunity Factory Workspace Setup

- Primary surface:
- Secondary surfaces:
- Skill location:
- Prompt runner:
- Schedule mechanism:
- State store:
- Approval policy:
- Verification source:
- Verification timestamp:
- Checked by:
- Runtime profile:
- Preflight result:
- First three jobs:
```

Use `assets/templates/setup-preflight.md` when a human-readable setup gate is needed.
Use `assets/examples/setup-packets.md` for concrete surface-specific packet shapes before filling real values.
