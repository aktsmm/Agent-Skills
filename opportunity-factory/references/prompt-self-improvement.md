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

## Approval Required (Autonomy Mode 参照)

承認要否は **workspace の Autonomy Mode に従う**。SSOT: `references/runtime-modes.md` の `ai-autonomous` preset "Tune Apply by Autonomy Mode" table。Prompt self-improvement は tune の一種として同 table 適用。

**Hard rule 変更**:

- 全 Autonomy Mode で `security-approve` バケット必須 (user 明示承認まで proceed 不可)
- 対象: approval gate 弱化、hard rule list (SKILL.md §Tunable vs Hard Rules) の直接変更、external publish / payment / account 作成 / login / personal data / network service / broadcast 等

**Reference default (tunable) 変更**:

- Normal / AUTO: workflow-review propose → user 承認 → apply
- FULL / ALL: workflow-review propose → 自動 apply (reporter-learner が 3 サイクル追跡、悪化で自動 revert)
- 対象: schedule frequency 増加、新規 unattended schedule 作成、外部依存追加、workspace policy 外の commit / push、global/personal instructions 変更

## Enforcement Outside the Editable Surface

A self-improving factory can edit the very prompts and state that describe its own safety rules. A rule written only in those files survives exactly one apply: delete the line that says "run the critic", and no later run notices it is gone. Put the invariants in a guard the loop is not allowed to edit.

- Keep an **explicit allowlist of editable targets**. Exclude the guard itself, its verification record, apply/audit logs, task queues, event logs, and scheduler definitions. A broad prefix such as "the whole state directory" reopens the hole.
- **Verify the guard's own hash** against its recorded baseline before every apply and fail closed on mismatch. Re-baselining is a human action, not a factory action.
- Validate candidate **content**, not only its path: required markers in workflow prompts, and immutable constraints still present in state (critic required, one change per run, approval boundaries). Reject a candidate that drops them.
- Bind the change to hashes: base file, candidate file, and the input artifacts it was derived from. **Re-validate under the target lock at apply time**, because validation done earlier is a time-of-check/time-of-use gap.
- Apply **one target file per change**, then validate the result and restore the rollback copy automatically when the post-apply check fails. Without an atomic multi-file transaction, "no partial apply" only holds for a single file.
- Require the critic receipt to carry the resolved model, its family, the producer family, and the reviewed candidate hash. A receipt missing a field, matching the producer family, or pointing at a different hash is fail-closed.

## Change-Rate Limits and Circuit Breaker

"One change per run" bounds nothing once the loop can also change its own cadence.

- Cap applies **per day** and **cumulatively until a human reviews them**, both enforced by the guard rather than by prompt text.
- Halt after N consecutive validate/apply failures and require an explicit manual reset. Fail-closed without a halt is an endless silent failure.
- Append every apply to an audit log (target, base hash, candidate hash, rollback path) that the loop cannot edit.
- The reporter must surface the halted state and the pending applies. A gate nobody reads is the same as no gate.

## Commit Gate (Layer 3 Blocking Critic)

Prompt 変更の commit は **Layer 3 blocking critic gate を必ず経由**。SSOT: `references/rubber-duck-review.md` の "Layer 3 Blocking Critic (重要 gate) — SSOT"。

### Commit 手順 (Small-Bet-First)

Worker が prompt を自動編集した場合:

1. **Diff 生成**: 対象 prompt file の変更内容を diff artifact に出力
2. **Apply**: worker が変更を working tree に適用 (未 commit)
3. **Layer 3 Critic dispatch**: 別 context で critic role を起動、diff artifact を input に verdict 取得。**producer とは別 model family で起動し、`independenceVerdict` を記録する**
4. **Smoke test**: `python scripts/smoke_test_initializers.py` 相当を必ず走らせる (プラス `python scripts/validate_factory_skill.py <skill-root>`)
5. **判定分岐**:
   - Critic verdict = `pass` AND `independenceVerdict` = `different-family` AND smoke test PASS → commit 実施
   - Critic verdict = `conditional` → critic 提示条件で worker が修正、再 (3)
   - Critic verdict = `reject` OR smoke test FAIL → **自動 revert** (`git checkout -- <prompt-path>`、既に stash してある場合は clean up)、`dashboard-state.tuningLog` に "reverted-by-commit-gate" 記録
   - `stash` は使わない (未 commit 状態で smoke test 走らせるため、stash すると変更が消える)

Rule: **critic pass + smoke test pass の両方**が commit 条件。片方でも fail なら revert。

### Commit Selection

Factory commits usually happen in a worktree that also holds unrelated human edits and tool-synced files.

- Stage only allowlisted paths **whose current hash still matches the reviewed candidate** recorded in the audit log. Never `add -A` or `add -u`.
- Skip silently when nothing qualifies. Do not create an empty commit to prove the job ran.
- Keep push manual unless workspace policy says otherwise, and never force-push from an unattended run.

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
