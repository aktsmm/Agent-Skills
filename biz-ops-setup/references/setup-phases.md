# Biz-Ops Setup Phases

Use this reference for manual setup when the scripts are unavailable or need adjustment.

## Phase 1: Interview

Collect customer list, optional external folders, holiday region, and workIQ availability. Run `Get-Date` before creating report-related assets.

## Phase 2: Folder Structure

Create the standard workspace folders: `ActivityReport/`, `Customers/`, `Tasks/`, `_inbox/`, `_datasources/`, `_workiq/`, and `.github/` customization folders.

## Phase 3: Agents and Prompts

Deploy the orchestrator, report, task, data, 1on1, availability, C360, and proposal agents. Deploy daily, weekly, monthly, and operations prompts when the workspace uses them.

## Phase 4: Customer Workspaces

Create one customer folder per mapped customer and initialize profile, tasks, inbox, and meeting-note surfaces according to the target workspace conventions.

## Phase 5: Config and Verification

Configure customer mapping, holidays, external folders, and optional workIQ references. Run a dry daily-report or task-management flow to verify routing and preflight behavior.
