# Built-in Customization Patterns

Patterns extracted from VS Code Copilot's built-in customization skills.

Use these as design heuristics for agent workflows and customization creation. Do not copy the built-in commands verbatim.

## 1. Extract Before You Interview

Built-in `create-agent`, `create-prompt`, `create-instructions`, `create-skill`, and `create-hook` all start by reviewing the conversation and generalizing what the user has already been doing.

Use this pattern when:

- The user has already demonstrated a repeated workflow
- Tool preferences or role boundaries are visible from context
- You want to minimize clarification churn

Apply it as:

1. Extract repeated task shape
2. Extract constraints and tool preferences
3. Extract desired output style
4. Ask only for what is still missing

Anti-pattern:

- Starting with a large requirements interview when the conversation already contains the specialization

## 2. Clarify the Weakest Ambiguity Only

The built-in create flows do not ask every possible setup question. They draft first, then focus on the most ambiguous or behavior-changing part.

Good clarification targets:

- scope: workspace or user profile
- role boundary: when to use this over the default agent
- enforcement: should it guide, warn, ask, or block
- output contract: expected structure or return format

Avoid:

- asking for details that do not change the file design
- collecting exhaustive requirements before a first draft

## 3. Guidance and Enforcement Are Different Primitives

The built-in `agent-customization` skill draws a hard line:

- prompts, instructions, skills, and agents are guidance
- hooks are deterministic enforcement at lifecycle events

Use this distinction when designing workflow systems:

| Situation                                       | Best fit                     |
| ----------------------------------------------- | ---------------------------- |
| Encourage a workflow or style                   | Prompt / Instruction / Skill |
| Restrict tools or specialize a role             | Agent                        |
| Guarantee a check runs before or after an event | Hook                         |

If a requirement includes words like "always block", "must ask", "inject at session start", or "run automatically before tool use", evaluate Hook explicitly.

## 4. Discovery Surface Matters

Built-in customization docs consistently treat descriptions as the routing surface.

Implications:

- descriptions need trigger phrases, not generic summaries
- vague labels reduce agent discovery and slash-command usability
- agent, skill, and instruction discovery all benefit from a strong "Use when..." shape

Use this when reviewing workflow assets:

- can another agent discover this from its description alone?
- would a user understand when to invoke it from the picker?

## 5. Draft, Then Iterate

The built-in creation flow is not "requirements -> perfect file". It is:

1. extract
2. clarify
3. draft file
4. identify weak spots
5. refine
6. suggest related next customizations

This is a strong pattern for agent workflow design too, especially when creating an orchestrator plus adjacent prompts, instructions, or hooks.

## 6. Bootstrap and Debug Are First-Class Workflows

Two built-in skills are especially worth borrowing conceptually:

### `init`

What to absorb:

- explore the codebase before writing customization assets
- prefer linking to existing docs instead of copying them
- create or update only customization files, not product code

When useful:

- initializing workflow assets for a repo
- upgrading AGENTS.md and related instructions without touching app code

### `troubleshoot`

What to absorb:

- base conclusions on evidence
- do not guess about why a workflow did or did not trigger
- separate root cause, evidence, and remediation

When useful:

- debugging why an agent was not invoked
- debugging why a prompt, skill, or instruction did not load
- explaining unexpected workflow choices

## 7. Minimal Reusable Loop

When designing or reviewing agent customizations, this is the compact loop worth keeping:

1. Extract from conversation
2. Choose primitive and scope
3. Clarify only the missing ambiguity
4. Draft the file or workflow
5. Review the weakest part
6. Refine and suggest adjacent assets

If the process starts turning into a large wizard, you are probably over-designing the customization.
