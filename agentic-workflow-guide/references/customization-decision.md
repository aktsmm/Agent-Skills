# Customization Decision Guide

Choose the simplest customization primitive that can solve the problem.

## Decision Matrix

| Need                                                             | Best Fit    | Why                                     | Avoid When                                            |
| ---------------------------------------------------------------- | ----------- | --------------------------------------- | ----------------------------------------------------- |
| One focused slash task                                           | Prompt      | Fastest path, minimal ceremony          | The task needs bundled scripts or reusable references |
| Always-on or file-scoped guidance                                | Instruction | Loads automatically or on demand        | The behavior is really a workflow                     |
| Reusable workflow with bundled scripts, references, or templates | Skill       | Best for repeatable task packages       | The ask is only persona or tool restrictions          |
| Persona, tool restrictions, delegation, or handoffs              | Agent       | Gives role boundaries and orchestration | The task can be solved without role isolation         |
| Deterministic blocking, validation, or auto-execution            | Hook        | Enforces behavior at runtime            | Guidance alone is enough                              |

## Guidance vs Enforcement

This distinction is easy to blur when designing workflow customizations.

| Need                                                                | Use                                  | Why                                       |
| ------------------------------------------------------------------- | ------------------------------------ | ----------------------------------------- |
| Tell the model what it should usually do                            | Prompt / Instruction / Skill / Agent | Guidance is flexible and conversational   |
| Guarantee that something runs, blocks, or asks at a lifecycle event | Hook                                 | Runtime enforcement must be deterministic |

Examples:

- "Always prefer this review style" -> instruction or skill
- "Ask before running this tool" -> hook
- "Use a specialist with limited tools" -> agent
- "Package a repeatable workflow with resources" -> skill

## Escalation Ladder

Use complexity only when required.

1. Prompt
2. Prompt + instructions
3. Skill or single agent
4. Multi-agent workflow
5. Hooks for deterministic enforcement

## Questions to Ask First

1. Is this a one-off task or a reusable workflow?
2. Does it need bundled assets, scripts, or references?
3. Does it need a specialist persona or tool restrictions?
4. Must the behavior be enforced deterministically?
5. Should this live in the workspace or the user profile?

## Scope Guidance

| Scope        | Use When                               |
| ------------ | -------------------------------------- |
| Workspace    | Shared with the team or tied to a repo |
| User profile | Personal preference across repos       |

## Overdesign Smells

- Multi-agent proposed before confirming a single agent is insufficient
- Agent created only to hold long instructions
- Skill created even though there are no bundled assets or reusable resources
- Hook proposed for guidance that could stay as instructions
- Workspace asset proposed for a purely personal preference
- Questions asked before extracting obvious specialization from the conversation
- Hook proposed before confirming a lifecycle event or deterministic need

## Creation Loop

Built-in customization flows follow a lightweight loop that is worth reusing:

1. Extract the reusable pattern from the conversation
2. Clarify only the missing ambiguity
3. Draft the customization file directly
4. Identify the weakest or most ambiguous part
5. Iterate and then suggest the next adjacent customization

Use this loop for prompt / instruction / skill / agent / hook creation unless the task is already fully specified.

## Output Pattern

When designing a workflow, include this decision explicitly.

```markdown
## Primitive Decision

- Best fit: agent
- Why not prompt: needs delegation and tool boundaries
- Why not skill: persona and orchestration are the core requirement
- Scope: workspace
```
