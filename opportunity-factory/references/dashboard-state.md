# Canonical Dashboard State

Use this reference when a factory has multiple workers, schedules, or candidate lanes.

## Purpose

The dashboard state is the compact source of truth for status answers. It prevents future sessions from losing context or reconstructing state from scattered artifacts.

It is not only a visual dashboard. It is a durable JSON or equivalent state file that all workflows read first and update when status changes.

## Required Behavior

Agents should:

1. Read dashboard state before answering project status.
2. Verify only the supporting files needed for the question.
3. If durable artifacts conflict with the dashboard, update the dashboard from the newest durable evidence.
4. Store paths and compact summaries, not full copied evidence.
5. Separate observed, estimated, and assumed facts.

## Update Triggers

Update the dashboard when a workflow:

- creates/imports an artifact,
- changes a queue item,
- changes a gate or recommendation,
- changes portfolio Top-N/watchlist/rejected state,
- creates, disables, or changes automation,
- records a blocker or approval-needed item,
- changes schedule, cadence, limits, or workflow policy.
- changes local prompt files or dashboard update contracts,
- changes prototype/build verification state.

## Suggested Schema

```json
{
  "schemaVersion": 1,
  "lastUpdated": "YYYY-MM-DDTHH:mm:ssZ",
  "executiveSummary": {
    "status": "operational|blocked|needs_review",
    "summary": "",
    "sourceOfTruthForStatusAnswers": true
  },
  "activeCandidate": {},
  "portfolio": {},
  "workflows": [],
  "promptAssets": {},
  "prototypeLane": {},
  "automationPolicy": {},
  "queues": {},
  "decisions": [],
  "risksAndBlockers": [],
  "nextActions": [],
  "answeringPolicy": {
    "useDashboardFirst": true,
    "thenVerifyWith": [],
    "ifConflict": "Prefer newest durable artifact/log, update dashboard, then answer."
  }
}
```

## Write Safety

Before rewriting the dashboard:

1. Create or refresh a `.bak`.
2. Re-read the dashboard immediately before writing.
3. If `lastUpdated` changed since the initial read, merge into the newer dashboard instead of overwriting.
4. Write the full object and validate it.
5. On validation failure, restore `.bak`, append a blocker to the pipeline log, and stop.

## Anti-Patterns

- HTML-only dashboard with no machine-readable canonical state.
- Long evidence dumps that make the dashboard expensive to read.
- Workers updating artifacts but not dashboard status.
- Dashboard overwriting newer state from overlapping scheduled runs.
- Status answers based on chat memory instead of durable state.
- Prompt edits that are not reflected in dashboard decisions or pipeline logs.
