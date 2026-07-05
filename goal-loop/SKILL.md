---
name: goal-loop
description: "Run an explicit end-to-end goal loop with frozen Scope/criteria, worker delegation, external verification, evaluator review, and bounded retries. Use when the user asks for 'goal-loop', 'ゴールまで回す', '必ずやり遂げる', 'loop until done', 'until it actually works', or an orchestrator + evaluator loop. Do not use for ordinary planning, casual advice, reviews, or small single-file fixes."
argument-hint: "達成したいゴール（成果物・終了条件・制約があれば一緒に）"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Goal Loop

合意した Scope と success criteria を満たすまで、worker / verifier / evaluator を使ってゴールをやり遂げる手順書。
このスキルを起動した現在の agent が orchestrator になり、criteria、ledger、evidence reconciliation、次の一手の決定を担う。

## When to Use

- ユーザーが `goal-loop` / `ゴールまで回す` / `必ずやり遂げる` / `loop until done` / `until it actually works` と依頼した。
- 成果物を end-to-end に完成させる必要があり、単発修正ではなく検証・再試行・評価のループが必要。
- worker 生成と evaluator 判定を分ける価値がある、中規模以上または不可逆・多段の作業。

## Do Not Use For

- 1 ファイル・自明・低リスクの修正。通常 agent が直接実行する。
- 普通の相談、計画だけ、コードレビューだけ、事実確認だけ。
- skill / prompt / instruction / agent 自体の設計レビュー。まず `skill-creator-plus` や `agentic-workflow-guide` を使う。

## Execution Contract

- Freeze scope, AC, verifier, out-of-scope, must NOT, autonomy, and persistence before execution.
- Keep a compact ledger: AC status, evidence, attempts, gaps, and next action.
- Delegate broad research, mutation, and primary verification when workers are available; workers return evidence only.
- Judge by external signals first. Never PASS from self-evaluation, supporting checks alone, skipped tests, TODOs, or weakened criteria.
- On failure, update the ledger from the failed signal, change approach, and avoid repeating attempts.
- Use Small-Bet-First for broad, irreversible, dependency, schema, deployment, or user-facing changes.
- Stop or replan on stall, oscillation, diminishing returns, budget exhaustion, or genuine external blockers.

## Phase 1: Scope + Criteria Freeze

Use [criteria-agreement.md](./references/criteria-agreement.md).

- Freeze goal, scope terminus, AC with `verify:`, primary verifier, out-of-scope, must NOT, autonomy, and persistence.
- If the finish line is ambiguous, ask one structured question before execution.
- Do not use build/control-plane success as the primary verifier when the real outcome is deploy / runtime / UI / app behavior.

## Phase 2: Plan Minimal Subgoals

Use [steering-and-final-gates.md](./references/steering-and-final-gates.md) and [ledger-templates.md](./references/ledger-templates.md).

- Pick the lightest effort level that still protects the goal; downgrade trivial work.
- Split into verifiable subgoals, record status, parallelize only independent read-only work.

## Phase 3: Delegate Workers

Use [loop-control.md](./references/loop-control.md).

- Start broad or risky changes with a pilot; never expand a failed pilot.
- Give workers only the subgoal, AC, boundaries, must NOT, relevant attempt lessons, and expected evidence.
- If no subagent tool exists, record degraded mode; only downgraded small work may run in main context.

## Phase 4: External Verification

- Run the frozen `verify:` steps and capture exit codes, logs, screenshots, readbacks, or capability gaps.
- If the primary verifier is unavailable, record exact manual verification steps and required evidence; do not complete from weaker checks.

## Phase 5: Evaluate

Use [evaluation-rubric.md](./references/evaluation-rubric.md).

- Reconcile evidence against each AC. Use a separate evaluator for non-small or non-read-only work.
- PASS only when every must AC passes and confidence is above threshold.

## Phase 6: Loop Control

Use [loop-control.md](./references/loop-control.md).

- If unmet, update the ledger from the external signal and replan before adding workers.
- Escalate only after the Blocker Test proves the blocker is external or structural.

## Phase 7: Report or Handoff

- Report AC-by-AC status, primary evidence, supporting checks, capability gaps, criteria changes, and residual risks.
- For high-risk changes, include final quality gate and independent review evidence.
- Cleanup scratch state unless it is needed for resumability.

## References

- [criteria-agreement.md](./references/criteria-agreement.md): Scope / criteria freeze テンプレ。
- [ledger-templates.md](./references/ledger-templates.md): Task / Progress ledger と attempt table。
- [loop-control.md](./references/loop-control.md): stop、replan、Small-Bet、reflection、HITL。
- [evaluation-rubric.md](./references/evaluation-rubric.md): rubric と judge bias 対策。
- [steering-and-final-gates.md](./references/steering-and-final-gates.md): Effort Scaling、dynamic steering、final gate、worker boundary。
- [design-rationale.md](./references/design-rationale.md): 設計根拠と出典。
