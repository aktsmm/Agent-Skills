---
name: agentic-workflow-guide
description: "Design, review, and debug agent workflows, and decide when a request should use a prompt, instruction, skill, agent, or hook before escalating to multi-agent design. Use for .agent.md / .instructions.md / .prompt.md / AGENTS.md work, workflow architecture, orchestration planning, or when agent workflows may be overkill. Triggers on 'agent workflow', 'create agent', 'ワークフロー設計', 'orchestrator'."
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

- Single focused slash task -> **Prompt**
- Always-on or file-scoped guidance -> **Instruction**
- Reusable workflow with bundled assets -> **Skill**
- Persona, tool restrictions, delegation, or handoffs -> **Agent**
- Deterministic enforcement -> **Hook**

If the ask does not require an **Agent**, stop and use the simpler primitive.

> この primitive 選択表が SSOT。skill-creator-plus / skill-finder などの判定表は「そのスキルを使うべきか」の即時ゲートとして扱い、基準がずれたらここに合わせる。

Selection details: [references/customization-decision.md](references/customization-decision.md)

## When to Use

| Action     | Triggers                                                                      |
| ---------- | ----------------------------------------------------------------------------- |
| **Create** | New `.agent.md`, `.instructions.md`, `.prompt.md`, `AGENTS.md`, or workflow architecture |
| **Review** | Orchestrator not delegating, design principle check, context overflow         |
| **Update** | Adding Handoffs, improving delegation, tool configuration                     |
| **Debug**  | Agent not found, subagent not working, picker visibility, access control      |
| **Decide** | Determining whether multi-agent is justified or a simpler primitive is enough |

## Core Principles

- **Simplicity First**: より単純な primitive で解けるなら agent 化しない
- **SSOT / SRP**: 情報源と責務の分割を守る
- **Fail Fast**: エラーは早く止める
- **Feedback Loop**: 各段で検証できるようにする
- **Context Discipline**: context が膨らんだら compact / split / retrieve を検討する

Principle details: [references/design-principles.md](references/design-principles.md)

## Pattern Selection

- **Prompt Chaining**: 順序のある段階処理
- **Routing**: 入力タイプで分岐する処理
- **Parallelization**: 独立タスクを並列で進める処理
- **Orchestrator-Workers**: 動的に subtasks を分解する処理
- **Evaluator-Optimizer**: 品質基準を満たすまで反復する処理

Every loop needs explicit stop conditions.

Pattern details: [references/workflow-patterns/overview.md](references/workflow-patterns/overview.md)

## Design Workflow

1. **Extract from conversation**
   Repeated behavior, tool preferences, workflow shape, and obvious specialization を先に拾う。
2. **Choose primitive + scope**
   Prompt / instruction / skill / agent / hook と workspace / profile を決める。
3. **Clarify only the gaps**
   挙動を変える曖昧さだけ聞く。
4. **Check escalation**
   agent や multi-agent が本当に必要か確認する。
5. **Choose pattern**
   complexity が上がるなら pattern を明示して設計する。
6. **Review before expanding**
   split / compact / reference 化で済まないかを見る。
7. **Implement and iterate**
   最初から完成形を狙わず、弱い箇所を見つけて詰める。

## Rule Placement

- 汎用的な workflow 設計原則は、この SKILL と `references/` を SSOT にする。
- repo local の `.instructions.md` には workspace 固有の差分だけを残す。差分が無い generic instruction は merge back して削除候補にする。
- IR は原則 in-memory で扱う。validator、script、deterministic handoff が必要な場合だけ中間 file を materialize し、不要になったら片付ける。
- scheduler / service / config など決定論的な state mutation は、AI/UI loop ではなく direct script / API で現状確認 -> 最小変更 -> live read-back まで行う。LLM は scope と整合対象の判断に限定する。

## Escalation Rules

- **L0**: Single Prompt
- **L1**: Prompt + Instructions
- **L2**: Single Agent
- **L3**: Multi-Agent

Prefer the lowest level that solves the problem cleanly.

Quick signals:

- Prompt > 50 lines
- Steps > 5
- "missed" / "overlooked" errorsが続く
- Multiple responsibilities in one agent
- Context > 70%

Threshold details: [references/splitting-criteria.md](references/splitting-criteria.md)

## Entry Boundary Smells

### Instruction Elevation Smell

always-loaded entry において、強い命令語が直下の catalog、reference list、workflow map、rule inventory を会話の優先レイヤーへ昇格させる状態。

### Always-Loaded Entry Budget

always-loaded entry は会話境界と最小 guardrail のみを持つ。catalog、詳細手順、広い参照一覧は docs、README、task-specific assets へ退避する。

### Runtime Boundary Rule

Review assets improve design quality and detect structural problems. Default conversational behavior is controlled by always-loaded entries.

### Casual Input Safety Check

Lightweight inputs such as greetings, short Q&A, and numeric-only replies should not be force-routed into task intake unless the task context is explicit.

## Review Gates

- [ ] Primitive choice is simpler than agent if possible
- [ ] Placement is appropriate and always-loaded entry files stay thin
- [ ] New additions are proposed only after delete / merge / split / move options are checked
- [ ] Single responsibility per agent is preserved
- [ ] Errors can be detected and stopped early
- [ ] Results are verifiable at each step
- [ ] Deterministic parts are offloaded to scripts / IR / hooks, and state changes are confirmed by reading authoritative live state back (not LLM/UI loops)

Full checklist: [references/review-checklist.md](references/review-checklist.md)

## Reference Map

Core references: [primitive decision](references/customization-decision.md), [design principles](references/design-principles.md), [workflow patterns](references/workflow-patterns/overview.md), [splitting criteria](references/splitting-criteria.md), [review checklist](references/review-checklist.md), and [context management](references/context-engineering.md).

## agent Quick Fix

When an orchestrator promises delegation but works directly, make the delegation requirement explicit and verifiable. See [agent-guide.md](references/agent-guide.md).

## Tools Reference

Use [references/agent-template.md](references/agent-template.md) for tool mapping and stable agent scaffold details.

## Done Criteria

- [ ] Primitive and scope selected intentionally
- [ ] Workflow pattern selected and confirmed with user
- [ ] New or updated assets have clear Role/Workflow/Done Criteria where applicable
- [ ] Design principles checklist passed
- [ ] Recommendations are classified as delete / merge / split / move / add / keep where applicable
- [ ] Always-on instruction boundaries and DRY / SSOT risks are explicitly reviewed when `copilot-instructions.md` or `AGENTS.md` are in scope
- [ ] New agent / workflow assets are registered in the appropriate catalog or docs when needed
- [ ] `AGENTS.md` is updated only when shared guardrails or entry behavior need to change
- [ ] Long-running or ad-hoc terminals/tasks started during the workflow are closed, or remaining terminals are explicitly reported with a reason
- [ ] Async operations are verified by live state before being called complete; if blocked by retention/locks/background platform work, the blocker and next check condition are explicit
