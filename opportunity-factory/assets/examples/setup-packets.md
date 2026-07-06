# Setup Packet Examples

Use these examples as shapes, not product guarantees. Verify current product capabilities before marking any setup unattended.

## VS Code GitHub Copilot Chat Supervised Setup

```markdown
## Opportunity Factory Workspace Setup

- Primary surface: VS Code GitHub Copilot Chat
- Secondary surfaces: none
- Skill location: workspace skill folder or attached skill context
- Prompt runner: manual Agent mode prompt invocation
- Schedule mechanism: manual supervised loop
- State store: workspace-local `factory-state/` folder or user-provided equivalent
- Approval policy: user approval for terminal, write, publish, account, secret, payment, and personal-data actions
- Verification source: VS Code product UI or current docs checked by user/agent
- Verification timestamp: <timestamp>
- Checked by: <name or agent>
- Runtime profile: supervised
- Preflight result: PASS / FAIL / BLOCKED
- First three jobs: commander -> worker -> commander/reporter-learner
```

## GitHub Copilot CLI Scheduled Setup

```markdown
## Opportunity Factory Workspace Setup

- Primary surface: GitHub Copilot CLI
- Secondary surfaces: cron / Windows Task Scheduler / CI scheduler
- Skill location: workspace path passed to the CLI or personal skill location if supported
- Prompt runner: CLI wrapper that invokes `assets/prompts/*.md`
- Schedule mechanism: external scheduler
- State store: workspace-local state folder committed or ignored according to repo policy
- Approval policy: no publish/payment/account/secret/personal-data action without explicit approval
- Verification source: CLI help output, current docs, or smoke-tested wrapper command
- Verification timestamp: <timestamp>
- Checked by: <name or agent>
- Runtime profile: conservative or standard
- Preflight result: PASS / FAIL / BLOCKED
- First three jobs: commander hourly, worker every 2h, reporter daily
```

## GitHub Copilot App Hosted Setup

```markdown
## Opportunity Factory Workspace Setup

- Primary surface: GitHub Copilot App
- Secondary surfaces: GitHub issues, pull requests, or repo artifacts for state/reporting if supported
- Skill location: repository skill folder or product-supported context attachment
- Prompt runner: product-supported hosted agent prompt/job mechanism, if available in the current version
- Schedule mechanism: verified product scheduler; otherwise use manual or external scheduler
- State store: repository files, issues/discussions, artifacts, or product memory confirmed by current UI/docs
- Approval policy: product-native approval for PRs, file writes, publish, secrets, payment, account, and personal-data actions
- Verification source: current product UI/docs confirming scheduling, persistence, and approval behavior
- Verification timestamp: <timestamp>
- Checked by: <name or agent>
- Runtime profile: conservative until persistence and approvals pass preflight
- Preflight result: PASS / FAIL / BLOCKED
- First three jobs: commander -> worker -> reporter-learner, with no unattended publish/payment/secret actions
```

## Microsoft Scout Background Setup

```markdown
## Opportunity Factory Workspace Setup

- Primary surface: Microsoft Scout
- Secondary surfaces: VS Code or repo files for review
- Skill location: Scout-supported workspace or custom skill location, if available in the current version
- Prompt runner: Scout automation / heartbeat / manual chat, depending on verified capabilities
- Schedule mechanism: verified Scout background mode or manual supervised loop
- State store: workspace-local files inside Scout's permitted workspace
- Approval policy: Scout permission gates; stricter policy for background modes than interactive runs
- Verification source: current Scout UI/docs confirming enabled capabilities and permissions
- Verification timestamp: <timestamp>
- Checked by: <name or agent>
- Runtime profile: conservative first, standard only after one successful preflight
- Preflight result: PASS / FAIL / BLOCKED
- First three jobs: commander -> worker -> reporter-learner, all within permitted workspace scope
```

## Copilot Scheduler VS Code Extension Setup

```markdown
## Opportunity Factory Workspace Setup

- Primary surface: Copilot Scheduler (VS Code extension)
- Secondary surfaces: VS Code GitHub Copilot Chat for supervised review
- Skill location: workspace skill folder or prompt context used by scheduled tasks
- Prompt runner: Copilot Scheduler scheduled prompt task
- Schedule mechanism: cron expressions in Copilot Scheduler, workspace task scope
- State store: workspace-local `factory-state/` folder or selected SQLite state store
- Approval policy: no unattended publish/payment/account/secret/personal-data/destructive actions; rely on Copilot Chat and VS Code approval prompts where applicable
- Verification source: Copilot Scheduler Marketplace/GitHub README plus current extension UI/settings
- Verification timestamp: <timestamp>
- Checked by: <name or agent>
- Runtime profile: conservative first, standard only after preflight and one Run Now check pass
- Preflight result: PASS / FAIL / BLOCKED
- First three jobs: commander hourly, worker every 2h with max-runs/day, reporter daily or twice daily
```

## OpenClaw Cron Setup

```markdown
## Opportunity Factory Workspace Setup

- Primary surface: OpenClaw
- Secondary surfaces: VS Code Chat for manual review
- Skill location: workspace skill folder or runtime-distributed instruction assets
- Prompt runner: OpenClaw agent prompts mapped to commander, worker, reporter-learner
- Schedule mechanism: OpenClaw cron isolated sessions
- State store: shared state folder selected for the factory
- Approval policy: no external publish/payment/account/secret/personal-data action from workers
- Verification source: OpenClaw config/cron status and one successful dry-run pulse
- Verification timestamp: <timestamp>
- Checked by: <name or agent>
- Runtime profile: conservative first, standard only after preflight passes
- Preflight result: PASS / FAIL / BLOCKED
- First three jobs: commander every 15-30m, workers every 30-60m, reporter every 6-8h
```

## GitHub Actions Low-Frequency Setup

```markdown
## Opportunity Factory Workspace Setup

- Primary surface: GitHub Actions
- Secondary surfaces: GitHub issues/artifacts for reports
- Skill location: repository files or workflow-provided context
- Prompt runner: workflow command or action that can invoke the chosen agent runner
- Schedule mechanism: low-frequency `schedule` plus `workflow_dispatch`
- State store: repository files, workflow artifacts, issue comments, or external storage approved for the repo
- Approval policy: no external publish/payment/account/secret-dependent action by default
- Verification source: workflow dry run, runner permissions, and repo policy check
- Verification timestamp: <timestamp>
- Checked by: <name or agent>
- Runtime profile: low-cost
- Preflight result: PASS / FAIL / BLOCKED
- First three jobs: commander 1-3h, worker daily/manual, reporter daily
```
