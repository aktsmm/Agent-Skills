# Factory Plan

## Frame

- Domain:
- Artifact type:
- Audience:
- Success metric:
- Constraints:

## Roles

| Role         | Owner | Notes |
| ------------ | ----- | ----- |
| Orchestrator |       |       |
| Scout        |       |       |
| Researcher   |       |       |
| Critic       |       |       |
| Designer     |       |       |
| Builder      |       |       |
| Reviewer     |       |       |
| Tracker      |       |       |
| Workflow Reviewer | | Reviews cadence, queue quality, dashboard freshness, and missing gates |

## Durable State

- Dashboard/status state:
- Factory state:
- Pending queue:
- Done history:
- Outcome log:
- Pipeline log:
- Artifact directory:
- Portfolio/Top-N state:

## Queue Slice

| Kind         | Task | Artifact |
| ------------ | ---- | -------- |
| discover     |      |          |
| research     |      |          |
| evaluate     |      |          |
| design/build |      |          |
| review       |      |          |
| track/learn  |      |          |

## Runtime Preset

- Environment: hosted agent scheduler / OpenClaw / cron / Windows Task Scheduler / GitHub Actions / manual / other
- Profile: low-cost / supervised / standard / burst
- Commander cadence:
- Worker cadence:
- Reporter-learner cadence:
- Workflow-review cadence:

## Workspace Setup Matrix

| Surface | Skill location | Prompt runner | Schedule mechanism | State store | Approval mode | Verification status |
| ------- | -------------- | ------------- | ------------------ | ----------- | ------------- | ------------------- |
|         |                |               |                    |             |               |                     |

## Human Approval Boundaries

- Cost:
- Login/account:
- External publish:
- Personal data:
- Legal/platform risk:

## Operating Limits

- Max pending tasks:
- Max daily worker runs:
- Max active portfolio candidates:
- Max daily cost estimate:
- Lock TTL:
- Stale task TTL:
- Blocker threshold:
- Notification policy:

## Next Decision

- Continue if:
- Stop if:
- Ask human if:

## Portfolio Replacement Gate

- Top-N capacity:
- Promote if:
- Demote incumbent if:
- Watchlist if:
- Reject if:
- Required reviewer evidence:
