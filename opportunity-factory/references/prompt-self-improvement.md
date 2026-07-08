# Prompt Self-Improvement Loop

Use this reference when a factory should improve its own local workflow prompts, queue rules, and dashboard contracts over time.

## Purpose

A self-designing factory should not only advance product candidates. It should notice when its own prompts are stale, too noisy, too conservative, unsafe, or missing state-update duties, then make safe local improvements.

## Safe Scope

Automatic prompt improvement is allowed only for workspace-local workflow assets, such as:

- `.github/prompts/*.md`
- `prompts/*.md`
- dashboard update contracts
- workflow-review prompts
- local queue/task templates

Do not edit personal instructions, global skills, public sync outputs, remote automations, or external repositories unless the user explicitly asks for that target.

## Allowed Edits

Safe automatic edits may:

- narrow scope,
- add or clarify approval gates,
- add missing state/dashboard read order,
- add backup, stale-write, or JSON-parse validation requirements,
- add safe fallback behavior,
- improve artifact contracts,
- clarify platform-verification honesty,
- reduce duplicate/noisy work,
- add missing blocker reporting.

## Approval Required

Fresh human approval is required before:

- increasing schedule frequency,
- creating new unattended schedules,
- weakening approval gates,
- enabling external publishing, payment, account creation, login, personal data, network services, analytics, telemetry, entitlements, automated sending, or public release work,
- adding external dependencies,
- committing or pushing outside the workspace policy,
- changing global/personal instructions.

## Workflow-Review Contract

The workflow-review loop should ask:

1. Did recent artifacts change decisions?
2. Did any automation stall, loop, duplicate work, or create noise?
3. Is the dashboard accurate and fresh?
4. Are prompt files missing state-update duties?
5. Are safe fallback tasks available?
6. Are schedules too slow or too fast?
7. Are prototype/build gates too strict, too loose, or dishonest about verification?
8. What one prompt or queue change would improve the next cycle?

## Prompt-Change Artifact

Every automatic prompt edit should leave an artifact that records:

- prompt file changed,
- before/after intent,
- evidence that the old prompt caused drift, blocker, or risk,
- safety impact,
- rollback note,
- exact files changed.

## Dashboard Duty

Any prompt change must update the canonical dashboard and append one pipeline-log event. If the dashboard cannot be safely updated, write a blocker artifact and stop.

## Anti-Patterns

- Updating prompts without an artifact explaining why.
- Improving the worker prompt but not the dashboard contract.
- Letting workflow review increase autonomy by default.
- Treating generated code or UI as verified when the host cannot run the target platform.
- Depending on chat history instead of durable prompt and state files.
