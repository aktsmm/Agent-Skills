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

## Extended Fields (AI-Autonomous Operation)

以下 field は AI-Autonomous 運用時に workflow-review / worker / reporter-learner が append する。既存 workspace で未定義でも動作 (backward compatible)、新 event 発生時点で `[]` 初期化して append される。

```json
{
  "approvalLog": [{"ts","operation","requestedBy","decidedBy","verdict","artifactRef","reason","criticVerdict"}],
  "pendingApprovals": [{"ts","task_id","reason","bucket"}],
  "fallbackLog": [{"ts","lane","task_id","verdict"}],
  "blockerGateLog": [{"ts","task_id","questions","verdict"}],
  "deferredBrowserWrites": [{"ts","task_id","operation"}],
  "discoveryFloorCounter": 0,
  "criticLog": [{"ts","layer","role","task_id","questions_passed","questions_failed","verdict","note"}],
  "persistenceOverrides": [{"ts","task_id","profile","requestedBy"}],
  "diminishingReturnsLog": [{"ts","task_id","metric","trend"}],
  "tuningLog": [{
    "ts": "ISO-8601",
    "item": "e.g. fallback-lane-order | discovery-floor-cycles | persistence-persistent-max-iter | cadence-worker | rubric-major-threshold",
    "before": "prior value",
    "after": "new value",
    "reason": "short justification",
    "evidenceRef": "path or hash of supporting artifact",
    "decidedBy": "workflow-review|user",
    "autonomyMode": "Normal|AUTO|FULL|ALL",
    "appliedCycle": 42,
    "revertThreshold": 3,
    "revertVerdict": null,
    "trackedMetrics": ["metric1","metric2"]
  }],
  "hardRuleViolationLog": [{
    "ts": "ISO-8601",
    "invariant": "e.g. approval-bucket-structure | layer3-gate-count | fallback-auto-refill | persistence-profiles | skill-tunable-vs-hard-section",
    "detectedIn": "path",
    "beforeSnapshot": "hash or excerpt",
    "verdict": "escalated-to-user|reverted"
  }]
}
```

### Field 説明

- **approvalLog / pendingApprovals**: `references/approval-policy.md` の Log Contract 参照
- **fallbackLog / blockerGateLog / deferredBrowserWrites / discoveryFloorCounter**: `references/fallback-lane.md` 参照
- **criticLog**: Layer 1/2/3 全部の verdict、`references/rubber-duck-review.md` 参照
- **persistenceOverrides / diminishingReturnsLog**: `references/persistence-profile.md` 参照
- **tuningLog**: reference default の変更履歴。3 サイクル追跡 revert (`revertVerdict` を reporter-learner が populate)。`references/tunable-defaults.md` 参照
- **hardRuleViolationLog**: workflow-review が invariant check で検出した hard rule 誤変更。`references/tunable-defaults.md` の Invariant Check 参照

### Retention

- Log 系 (approvalLog / fallbackLog / blockerGateLog / criticLog): 90 日 rotation、archive に押し出す
- Layer 1 criticLog: 30 日 (直近だけ意味あり)
- tuningLog: 恒久 (workflow-review の学習資産)
- hardRuleViolationLog: 恒久 (audit 用)
- pendingApprovals / discoveryFloorCounter / deferredBrowserWrites: state 値、rotation なし
