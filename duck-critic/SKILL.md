---
name: duck-critic
description: "Route a Duck Critic second-opinion review for plans, code, tests, and designs. Use when asked for rubber duck, ラバーダック, 別モデルレビュー, second opinion, critic, code review, design review, plan critique, or review by another model/agent harness."
argument-hint: "レビュー対象の計画/差分/コード/テスト、観点、使いたいハーネス"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Duck Critic

Get a constructive second opinion before committing to a plan, implementation, test strategy, or design.

This skill routes a second-opinion critic review. Prefer the native GitHub Copilot CLI Rubber Duck when available. If the native route is unavailable, use an equivalent read-only critic through the current agent harness: VS Code custom agents, Copilot CLI custom agents, Claude Code skills/subagents, or a separate top-reasoning model session.

## When to Use

- Use when the user asks for `rubber duck`, `ラバーダック`, `second opinion`, `別モデルレビュー`, critic review, plan critique, code review, design review, test review, or another-model review.
- Use before nontrivial implementation, after drafting tests, before architecture/deployment decisions, or after repeated failures.
- Do not use for ordinary implementation, exhaustive audit, or creating `.agent.md` files unless the user explicitly asks for a separate agent-file package.

## Core Rules

- Always report the route used. Route values and verdicts are defined in [output format](./references/output-format.md).
- Do not claim native Rubber Duck ran unless GitHub Copilot CLI actually used `/rubber-duck` or an explicit Rubber Duck consultation.
- Keep the critic read-only. Do not edit files, run mutating commands, change settings, install packages, or update state from the critic role.
- Prefer a reviewer from a different model family than the producer when the harness allows it.
- Do not hardcode model names in portable skill instructions. Verify exact local model names before storing them in harness-specific config or handoffs.
- Ignore style-only, formatting-only, naming-preference, and generic best-practice comments unless they affect the task outcome.
- Focus on issues that could break requested behavior, security, data integrity, runtime behavior, deployment, or verification.

## Procedure

1. Identify the review target.
   - Target types: `plan`, `diff`, `code`, `tests`, `design`, `architecture`, `deployment`, `security`.
   - Record the user goal, acceptance criteria if known, constraints, evidence already collected, and the current proposed approach.
2. Select the route.
   - If running inside GitHub Copilot CLI and native Rubber Duck is available, invoke it first with `/rubber-duck <question>` or an equivalent prompt such as `Rubber duck your plan.`
   - If native Rubber Duck is not available, choose a fallback from [harness adapters](./references/harness-adapters.md).
   - If multiple reviewer lanes are useful, choose from [model lanes](./references/model-lanes.md). Use one lane by default and multiple lanes only for broad, risky, or security-sensitive work.
3. Build a compact critic packet.
   - Include: goal, current plan or diff summary, assumptions, constraints, relevant file paths, verification evidence, known risks, and specific questions.
   - Exclude: long transcripts, unrelated logs, unbounded repository dumps, and hidden reasoning.
4. Run the critic.
   - Use [critic packets](./references/critic-packets.md) for native and fallback prompt shapes.
   - Native route: send the critic packet to the built-in Rubber Duck.
   - Fallback route: send the same packet to a read-only reviewer agent, subagent, or separate model session.
5. Reconcile the feedback.
   - Classify findings with [reviewer rubric](./references/reviewer-rubric.md).
   - De-duplicate overlapping findings.
   - Reject low-signal notes explicitly when needed.
6. Return the result using [output format](./references/output-format.md).
   - Start with route and verdict.
   - List blocking issues first.
   - End with concrete next actions.

## Critic Packets

Use [critic packets](./references/critic-packets.md) for native GitHub Copilot CLI Rubber Duck prompts and fallback reviewer prompts. Keep `SKILL.md` focused on routing and reconciliation; packet details live in the reference.

## Harness Reviewers

This skill does not require repository-specific agent files. Use whichever read-only reviewer mechanism the current harness already exposes: native Rubber Duck, a selected custom agent, a forked subagent, or a separate model session.

Keep `.agent.md` companion files out of this skill unless the user explicitly asks for a separate agent-file package. If exact model names are needed for future harness-specific config or handoff, verify them in the local model picker or CLI configuration first.

## Done Criteria

- The response says which route was used.
- The critic stayed read-only.
- Findings are severity-classified and tied to the user goal.
- Native Rubber Duck and fallback critic are not conflated.
- Next actions are specific enough for implementation or plan revision.
