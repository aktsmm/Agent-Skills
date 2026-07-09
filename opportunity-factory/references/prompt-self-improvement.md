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

## Commit Gate (Layer 3 Blocking Critic)

Prompt 変更の commit は **Layer 3 blocking critic gate を必ず経由**。SSOT: `references/rubber-duck-review.md` の "Layer 3 Blocking Critic (重要 gate) — SSOT"。

### Commit 手順 (Small-Bet-First)

Worker が prompt を自動編集した場合:

1. **Diff 生成**: 対象 prompt file の変更内容を diff artifact に出力
2. **Apply**: worker が変更を working tree に適用 (未 commit)
3. **Layer 3 Critic dispatch**: 別 context で critic role を起動、diff artifact を input に verdict 取得
4. **Smoke test**: `python scripts/smoke_test_initializers.py` 相当を必ず走らせる (プラス `python scripts/validate_factory_skill.py <skill-root>`)
5. **判定分岐**:
   - Critic verdict = `pass` AND smoke test PASS → commit 実施
   - Critic verdict = `conditional` → critic 提示条件で worker が修正、再 (3)
   - Critic verdict = `reject` OR smoke test FAIL → **自動 revert** (`git checkout -- <prompt-path>`、既に stash してある場合は clean up)、`dashboard-state.tuningLog` に "reverted-by-commit-gate" 記録
   - `stash` は使わない (未 commit 状態で smoke test 走らせるため、stash すると変更が消える)

Rule: **critic pass + smoke test pass の両方**が commit 条件。片方でも fail なら revert。

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
