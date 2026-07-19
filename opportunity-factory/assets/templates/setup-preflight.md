# Opportunity Factory Setup Preflight

## Target

- Primary surface:
- Secondary surfaces:
- Runtime profile:
- State store:
- Prompt runner:
- Schedule mechanism:
- Verification source:
- Verification timestamp:
- Checked by:

## Capability Gate

- [ ] Skill or prompt assets are available to the target surface
- [ ] `commander`, `worker`, and `reporter-learner` prompts are callable
- [ ] State, queue, artifact, outcome, and audit-log storage are durable
- [ ] The runtime can prevent duplicate or overlapping runs
- [ ] Lock acquisition is atomic and long runs refresh a heartbeat
- [ ] A stale-lock recovery path reconciles partial target changes against required artifacts and verification
- [ ] Runtime limits are configured
- [ ] Human approval boundaries are configured
- [ ] A test artifact can be created and imported
- [ ] Reporting destination is configured
- [ ] Capability verification source is recorded

## Approval Boundaries

- [ ] External publishing requires approval
- [ ] Payment or paid API usage requires approval
- [ ] Account creation or login requires approval
- [ ] Secrets require approval and are never written into prompts
- [ ] Personal data processing requires approval
- [ ] Destructive commands require approval or are denied
- [ ] Legal/platform policy risks stop unattended runs

## Schedule Gate

- [ ] Commander cadence:
- [ ] Worker cadence:
- [ ] Reporter-learner cadence:
- [ ] Max pending tasks:
- [ ] Max daily worker runs:
- [ ] Max daily cost estimate:
- [ ] Lock TTL:
- [ ] Stale-lock recovery threshold (recommended >= 2x TTL):
- [ ] Stale task TTL:
- [ ] Quiet hours / notification policy:

## Result

- Preflight: PASS / FAIL / BLOCKED
- Blocking issue:
- Safe first run:
- First three jobs:
- Evidence:
