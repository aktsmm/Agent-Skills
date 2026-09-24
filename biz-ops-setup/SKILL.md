---
name: biz-ops-setup
description: "Set up or operate a business operations workspace for activity reports, tasks, and customer routing; workIQ is optional. Use when initializing BizOps, processing ongoing business updates, reviewing reports or tasks, or preparing an operations handoff. Triggers: business-operations-workspace, BizOps, 業務管理ワークスペース, レポート管理, タスク管理, 業務引き継ぎ."
argument-hint: "作りたい業務ワークスペース、必要機能、管理したい対象"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Biz-Ops Workspace

Set up or operate a business operations workspace with reporting and task management.

## When to Use

- Creating a new business operations workspace with optional workIQ integration.
- Operating an existing workspace: classifying updates, maintaining tasks, and generating reports.
- Reviewing current activity, missing reports, open tasks, or a handoff.

## Choose a Mode

Inspect the target before acting. `DASHBOARD.md` together with `Tasks/` or `ActivityReport/` identifies an existing BizOps workspace. Other managed content or partial structure requires confirmation; never initialize over a different workspace or infer BizOps from a single shared folder.

| Mode | Use when | First action |
| ---- | -------- | ------------ |
| Setup | A new, explicitly chosen target has no managed structure | Interview and initialize the workspace. |
| Operate | New activity, task, or report request in an existing workspace | Read the relevant records and source evidence before updating. |
| Review / Handoff | Status, missing work, or continuity is requested | Read the dashboard, active tasks, report index, and relevant customer records. |

Never rerun the initialization or template deployment scripts during Operate or Review. Template deployment can rewrite customer mappings in an existing agent file even when other files are skipped. Add missing assets only when requested and after checking existing content.

## Prerequisites

| Item                     | Required | Description             |
| ------------------------ | -------- | ----------------------- |
| VS Code + GitHub Copilot | Yes      | Agent execution         |
| Git + PowerShell 7+      | Yes      | Version control/scripts |
| workIQ MCP Server        | Optional | M365 integration        |

## Setup Flow (New Workspace Only)

```
Interview → Folder Structure → Deploy Agents → Customer Workspaces → Config → Done
```

## Phase 1: Interview (MANDATORY)

Collect the following information:

1. **Customer list**: Name, ID, primary contact
2. **External folders**: Tech QA, Blog, OneDrive paths (optional)
3. **Holiday config**: japan / us / other
4. **workIQ availability**: Yes (M365 auto) / No (manual input)

> ⚠️ **CRITICAL**: Always run `Get-Date` before generating reports.

## Phase 2-5: Setup Execution

**Recommended: Use scripts**

```powershell
# Phase 2: Create folder structure
.\scripts\Initialize-BizOpsWorkspace.ps1 -WorkspacePath "D:\my-biz-ops" -Customers @("contoso")

# Phase 3: Deploy agents and prompts
.\scripts\Deploy-BizOpsTemplates.ps1 -WorkspacePath "D:\my-biz-ops"
```

**Manual setup** → [references/setup-phases.md](references/setup-phases.md)

## Deployed Components

| Type    | Count | Examples                                                          |
| ------- | ----- | ----------------------------------------------------------------- |
| Agents  | 9     | orchestrator, report-generator, task-manager, availability-finder |
| Prompts | 4     | daily-report, weekly-report, monthly-report                       |
| Folders | 7     | ActivityReport/, Customers/, Tasks/, \_inbox/                     |

## Operate an Existing Workspace

| Input | Canonical record and action |
| ----- | --------------------------- |
| New activity | Store the source once: confirmed customer items in `Customers/{id}/_inbox/`, confirmed internal items in `_internal/_inbox/`, and unresolved items in `_inbox/`; link from summaries instead of copying it. |
| Task update | Keep `Tasks/active.md` or `Tasks/completed.md` as the overall index; link to details in `Customers/{id}/tasks.md` for confirmed customer tasks, and sync both task records and `DASHBOARD.md` together. |
| Daily, weekly, or monthly report | Read existing reports and `_datasources/` configuration; collect available dated evidence, mark unavailable sources explicitly, then use the matching report prompt. |
| Ambiguous customer or project association | Keep the original input unclassified and ask for confirmation before creating a customer or project folder. |

Use the deployed task-manager, data-collector, and report-generator for their respective workflows. Keep original evidence authoritative; reports and indexes summarize or link instead of copying source content. workIQ is optional and missing data is not evidence of no activity. `Customers/{id}/` is a lightweight BizOps record, not a full per-customer workspace; do not run a customer-workspace initializer inside it. Link to a separately managed customer workspace when one exists. Do not treat a customer project thread as a separate project workspace unless the user explicitly requests one.

## Review / Handoff

Read `DASHBOARD.md`, `Tasks/active.md`, recent `ActivityReport/` entries, and only relevant `Customers/` records. Report the source of the current status, owner, next action, and any unavailable or unconfirmed information; do not fill gaps by rerunning setup.

## Done Criteria

- Setup: folders, agents, prompts, mappings, daily activity roots, and report preflight are verified without replacing existing records (see [agent list](references/agent-list.md)).
- Operate: the owning task or activity record and relevant index reflect the input; reports identify their evidence and any unavailable sources.
- Review / Handoff: the current status, owner, next action, and unresolved questions are traceable to existing records.

## Key References

| Topic            | Reference                                                        |
| ---------------- | ---------------------------------------------------------------- |
| Setup Phases     | [references/setup-phases.md](references/setup-phases.md)         |
| Folder Structure | [references/folder-structure.md](references/folder-structure.md) |
| Agent List       | [references/agent-list.md](references/agent-list.md)             |
| Holidays         | [references/holidays.md](references/holidays.md)                 |
| Daily Evidence   | [references/daily-activity-collection.md](references/daily-activity-collection.md) |
