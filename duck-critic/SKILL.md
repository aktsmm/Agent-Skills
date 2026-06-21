---
name: duck-critic
description: "Run a Duck Critic producer-critic loop: you (main) keep producing the plan/code/tests and gate your own work at checkpoints with a different-model critic, revising until it passes. Use when asked for rubber duck, ラバーダック, 別モデルレビュー, second opinion, critic, code review, design review, plan critique, or review by another model/agent harness."
argument-hint: "レビュー対象の計画/差分/コード/テスト、観点、使いたいハーネス"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Duck Critic

Run a producer-critic loop, the way the native Rubber Duck works: you keep producing the work and gate it at checkpoints with a second-opinion critic, then revise until the critic passes.

This is **not** "hand the whole task to a reviewer subagent". You stay the **producer** and own the plan, the implementation, and the tests. At high-leverage checkpoints you pause and send your current artifact to a read-only **critic** from a different model family, take in its findings, and continue. Prefer the native GitHub Copilot CLI Rubber Duck when available. Otherwise drive the same loop through the current harness: a VS Code subagent on a different model, a Copilot CLI custom agent, a Claude Code subagent, or a separate top-reasoning model session.

## When to Use

- Use when the user asks for `rubber duck`, `ラバーダック`, `second opinion`, `別モデルレビュー`, critic review, plan critique, code review, design review, test review, or another-model review.
- Use when the user says "rubber duck で実装して" / "ラバーダックで作って": you implement it yourself and gate your own checkpoints with the critic. Do not delegate the whole implementation to a subagent.
- Use before nontrivial implementation, after drafting tests, before architecture/deployment decisions, or after repeated failures.
- Skip the critic for small, obvious changes — like the native Rubber Duck, consulting is optional and zero rounds is a valid outcome.
- Do not use for an exhaustive audit, or for creating `.agent.md` files unless the user explicitly asks for a separate agent-file package.

## Producer vs Critic Roles

- **Producer (you, the main agent)**: own and keep producing the artifact — plan, code, tests, design. You never hand the whole job to the critic. You decide checkpoints, send packets, reconcile findings, and apply revisions yourself.
- **Critic (a different model)**: a read-only reviewer that only inspects the producer's current artifact and returns severity-classified findings. It never writes files or runs mutating commands.
- This is a **gated checkpoint loop**, not two agents running at the same wall-clock moment. The producer reaches a checkpoint, hands off to the critic, gets findings, revises, and re-consults — that is where the second model's value comes from. Running multiple critic _lanes_ in parallel at a single checkpoint is fine; the producer and critic taking turns is the loop.

## Core Rules

- The producer keeps producing. Never delegate the entire implementation to the critic or a single reviewer subagent — gate your own work, do not outsource it.
- Always report the route used and how many rounds it took. Route values and verdicts are defined in [output format](./references/output-format.md).
- Do not claim native Rubber Duck ran unless GitHub Copilot CLI actually used `/rubber-duck` or an explicit Rubber Duck consultation.
- Keep the critic read-only. Do not edit files, run mutating commands, change settings, install packages, or update state from the critic role.
- Use a critic from a **different model family** than the producer whenever the harness allows it. If a different family is unavailable or no model was specified, fall back per [model lanes](./references/model-lanes.md) instead of blocking the loop, and report when the critic ended up same-family or self-review.
- Do not hardcode model names in portable skill instructions. Verify exact local model names before storing them in harness-specific config or handoffs.
- Ignore style-only, formatting-only, naming-preference, and generic best-practice comments unless they affect the task outcome.
- Focus on issues that could break requested behavior, security, data integrity, runtime behavior, deployment, or verification.

## Procedure

This is a loop. The producer advances to a checkpoint, the critic reviews, the producer revises, and the loop repeats until the critic passes. See [loop protocol](./references/loop-protocol.md) for checkpoints and stop conditions.

1. Identify the target and set up the loop.
   - Target types: `plan`, `diff`, `code`, `tests`, `design`, `architecture`, `deployment`, `security`.
   - Record the user goal, acceptance criteria if known, constraints, evidence already collected, and the current proposed approach.
   - Pick the route: native Rubber Duck inside GitHub Copilot CLI (`/rubber-duck <question>` or `Rubber duck your plan.`), or a fallback critic from [harness adapters](./references/harness-adapters.md). Use one critic lane by default; choose extra lanes from [model lanes](./references/model-lanes.md) only for broad, risky, or security-sensitive work.
2. Produce up to a checkpoint (producer).
   - Advance the actual work — draft the plan, write the code, or write the tests — until you reach a high-leverage checkpoint from [loop protocol](./references/loop-protocol.md).
3. Build a compact critic packet.
   - Include: goal, current plan or diff summary, assumptions, constraints, relevant file paths, verification evidence, known risks, and specific questions.
   - On round 2+, use the revision-round packet shape in [critic packets](./references/critic-packets.md): restate the prior findings and show what you changed.
   - Exclude: long transcripts, unrelated logs, unbounded repository dumps, and hidden reasoning.
4. Run the critic (read-only).
   - Native route: send the packet to the built-in Rubber Duck.
   - Fallback route: send the same packet to a read-only reviewer agent, subagent, or separate model session on a different model family.
5. Reconcile the feedback.
   - Classify findings with [reviewer rubric](./references/reviewer-rubric.md).
   - De-duplicate overlapping findings and reject low-signal notes explicitly.
6. Apply revisions and check the stop condition (producer).
   - If there are blocking findings: revise the artifact yourself and go back to step 2 for a re-critique.
   - Stop on PASS only when there are no blocking findings and no notes worth acting on. If non-blocking notes remain, stop as PASS_WITH_NOTES only after you explicitly accept and record them. As a fail-safe against an endless loop, also stop after the max rounds in [loop protocol](./references/loop-protocol.md) and report any unresolved blocking findings.
7. Return the result using [output format](./references/output-format.md).
   - Start with route, final verdict, and the number of rounds.
   - List any remaining blocking issues first.
   - End with concrete next actions.

## Critic Packets

Use [critic packets](./references/critic-packets.md) for native GitHub Copilot CLI Rubber Duck prompts and fallback reviewer prompts. Keep `SKILL.md` focused on routing and reconciliation; packet details live in the reference.

## Harness Reviewers

This skill does not require repository-specific agent files. Use whichever read-only reviewer mechanism the current harness already exposes: native Rubber Duck, a selected custom agent, a forked subagent, or a separate model session.

Keep `.agent.md` companion files out of this skill unless the user explicitly asks for a separate agent-file package. If exact model names are needed for future harness-specific config or handoff, verify them in the local model picker or CLI configuration first.

## Done Criteria

- The producer kept ownership of the work; the implementation was not delegated wholesale to the critic.
- The response says which route was used and how many rounds the loop ran.
- The critic stayed read-only and, where the harness allowed, was a different model family than the producer.
- The loop stopped on a real condition: critic PASS, an explicitly accepted PASS_WITH_NOTES, or the max-rounds fail-safe with unresolved blocking findings reported.
- Findings are severity-classified and tied to the user goal.
- Native Rubber Duck and fallback critic are not conflated.
- Next actions are specific enough for implementation or plan revision.
