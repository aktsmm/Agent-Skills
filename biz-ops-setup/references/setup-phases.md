# Biz-Ops Setup Phases

Use this reference for manual setup when the scripts are unavailable or need adjustment.

## Phase 1: Interview

Collect customer list, optional external folders, holiday region, and workIQ availability. Run `Get-Date` before creating report-related assets.

## Phase 2: Folder Structure

Create the standard workspace folders: `ActivityReport/`, `Customers/`, `Tasks/`, `_inbox/`, `_datasources/`, `_workiq/`, and `.github/` customization folders.

## Phase 3: Agents and Prompts

Deploy the bundled agents from `assets/agents/` (orchestrator, report-generator, report-reviewer, task-manager, data-collector, work-inventory, 1on1-assistant, availability-finder, general-worker) and the daily, weekly, monthly, and review-report prompts from `assets/prompts/`. Prompt files load only in the VS Code Local agent, so keep the matching agents usable on their own.

## Phase 4: Customer Workspaces

Create one customer folder per mapped customer and initialize profile, tasks, inbox, and meeting-note surfaces according to the target workspace conventions.

## Phase 5: Config and Verification

Configure customer mapping, holidays, external folders, and optional workIQ references. Configure `_datasources/daily-activity-sources.json`, then run the collector for a representative date before the dry daily-report flow. See [daily activity collection](daily-activity-collection.md).
