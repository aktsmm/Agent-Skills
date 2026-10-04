---
name: agentic-workflow-guide
description: "Design, review, and debug agent workflows, and decide when a request should use a prompt, instruction, skill, agent, or hook before escalating to multi-agent design. Use for .agent.md / .instructions.md / .prompt.md / AGENTS.md work, workflow architecture, orchestration planning, scheduled automation model allocation, or when agent workflows may be overkill. Triggers on 'agent workflow', 'create agent', 'automation models', 'ワークフロー設計', 'orchestrator'."
argument-hint: "作りたい .agent.md / .instructions.md / .prompt.md / AGENTS.md、設計したい workflow、または困っている症状"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Agentic Workflow Guide

Design, review, and improve agent workflows based on proven principles.

この SKILL の基本姿勢は、**agent を増やすことではなく、必要最小の primitive で解くこと**。
context が膨らんだときも、まずは split / compact / reference 化を考え、いきなり multi-agent にしない。

## Primitive First

Do not start with multi-agent by default.

- Single focused slash task -> **Prompt** (Local harness only; prompt files are deprecated for Agent Host sessions, so prefer a **Skill** for new slash workflows)
- Always-on or file-scoped guidance -> **Instruction**
- Reusable workflow with bundled assets -> **Skill**
- Persona, tool restrictions, delegation, or handoffs -> **Agent**
- Deterministic enforcement -> **Hook** (Preview; events and config differ by harness)

If the ask does not require an **Agent**, stop and use the simpler primitive.

Selection details: [references/customization-decision.md](references/customization-decision.md)

## When to Use

| Action     | Triggers                                                                                 |
| ---------- | ---------------------------------------------------------------------------------------- |
| **Create** | New `.agent.md`, `.instructions.md`, `.prompt.md`, `AGENTS.md`, or workflow architecture |
| **Review** | Orchestrator not delegating, design principle check, context overflow                    |
| **Update** | Adding Handoffs, improving delegation, tool configuration                                |
| **Debug**  | Agent not found, subagent not working, picker visibility, access control                 |
| **Decide** | Determining whether multi-agent is justified or a simpler primitive is enough            |

## Core Principles

- **Simplicity First**: より単純な primitive で解けるなら agent 化しない
- **SSOT / SRP**: 情報源と責務の分割を守る
- **Fail Fast**: エラーは早く止める
- **Feedback Loop**: 各段で検証できるようにする
- **Context Discipline**: context が膨らんだら compact / split / retrieve を検討する

Principle details: [references/design-principles.md](references/design-principles.md)

## Pattern Selection

Name the pattern explicitly when complexity rises, using the selector in [references/workflow-patterns/overview.md](references/workflow-patterns/overview.md). Every loop needs explicit stop conditions.

## Design Workflow

1. Extract repeated behavior, tool preferences, and workflow shape from the conversation.
2. Choose primitive + scope (workspace / profile); ask only about ambiguities that change behavior.
3. Escalate only when split / compact / reference-ization cannot solve it, then pick a pattern.
4. Implement the smallest version and tighten the weakest parts.

## Rule Placement

- 汎用的な workflow 設計原則は、この SKILL と `references/` を SSOT にする。
- repo local の `.instructions.md` には workspace 固有の差分だけを残す。差分が無い generic instruction は merge back して削除候補にする。
- IR は原則 in-memory で扱う。validator、script、deterministic handoff が必要な場合だけ中間 file を materialize し、不要になったら片付ける。
- scheduler / service / config など決定論的な state mutation は、AI/UI loop ではなく direct script / API で現状確認 -> 最小変更 -> live read-back まで行う。LLM は scope と整合対象の判断に限定する。
- For model allocation reviews, use [scheduled runtime bindings](references/scheduled-runtime-bindings.md#model-allocation-reviews).

## Escalation Rules

Prefer the lowest level (L0 prompt → L1 + instructions → L2 single agent → L3 multi-agent) that solves the problem cleanly. Quick signals to split:

- Prompt > 50 lines
- Steps > 5
- "missed" / "overlooked" errorsが続く
- Multiple responsibilities in one agent
- Context > 70%

Threshold details: [references/splitting-criteria.md](references/splitting-criteria.md)

## Review Gates

- [ ] Primitive choice is simpler than agent if possible
- [ ] Placement is appropriate and always-loaded entry files stay thin (entry boundary smells: [review-checklist.md](references/review-checklist.md#always-loaded-entry-smells))
- [ ] New additions are proposed only after delete / merge / split / move options are checked
- [ ] Single responsibility per agent is preserved
- [ ] Errors can be detected and stopped early
- [ ] Verify actual producer-to-consumer dataflow, not only fixtures injected into a validator; cover empty results and meaningful state transitions. Repeating unchanged input proves idempotency, not the full lifecycle.
- [ ] Deterministic parts are offloaded to scripts / IR / hooks, and state changes are confirmed by reading authoritative live state back (not LLM/UI loops)

Full checklist: [references/review-checklist.md](references/review-checklist.md)

## Reference Map

Core references: [primitive decision](references/customization-decision.md), [design principles](references/design-principles.md), [workflow patterns](references/workflow-patterns/overview.md), [splitting criteria](references/splitting-criteria.md), [review checklist](references/review-checklist.md), and [context management](references/context-engineering.md).

For scheduled workflows, use [scheduled runtime bindings](references/scheduled-runtime-bindings.md). For delegated evidence and append-only current-state extraction, see [orchestrator-workers](references/workflow-patterns/4-orchestrator-workers.md) and [IR architecture](references/workflow-patterns/ir-architecture.md).

When an orchestrator promises delegation but works directly, make the delegation requirement explicit and verifiable ([agent-guide.md](references/agent-guide.md)). Tool mapping and agent scaffold: [agent-template.md](references/agent-template.md).

## Done Criteria

- [ ] Primitive and scope selected intentionally
- [ ] Workflow pattern selected and confirmed with user
- [ ] New or updated assets have clear Role/Workflow/Done Criteria where applicable
- [ ] Review Gates passed
- [ ] Recommendations are classified as delete / merge / split / move / add / keep where applicable
- [ ] Always-on instruction boundaries and DRY / SSOT risks are explicitly reviewed when `copilot-instructions.md` or `AGENTS.md` are in scope
- [ ] New agent / workflow assets are registered in the appropriate catalog or docs when needed
- [ ] `AGENTS.md` is updated only when shared guardrails or entry behavior need to change
- [ ] Long-running or ad-hoc terminals/tasks started during the workflow are closed, or remaining terminals are explicitly reported with a reason
- [ ] Distinguish configuration saved, code tested, live read verified, action authorized, and recurring cycle completed. Verify authoritative state before claiming completion or unattended readiness; pending safeguards and unobserved cycles retain their blockers and next check conditions.
