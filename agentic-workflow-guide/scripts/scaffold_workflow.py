#!/usr/bin/env python3
"""
scaffold_workflow.py - Generate directory structure for agent workflows

Usage:
    python scaffold_workflow.py <workflow-name> [--pattern <pattern>] [--path <output-dir>]
    python scaffold_workflow.py --lint <path>

Examples:
    python scaffold_workflow.py my-workflow
    python scaffold_workflow.py code-review --pattern evaluator-optimizer
    python scaffold_workflow.py data-pipeline --pattern orchestrator-workers --path ./projects
    python scaffold_workflow.py --lint .github/prompts/
"""

import argparse
import re
from pathlib import Path

# Complexity thresholds (can be overridden in copilot-instructions.md)
THRESHOLDS = {
    "line_count": 50,
    "step_count": 7,
    "step_count_warning": 5,
}

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)


def yaml_quote(value: str) -> str:
    return '"' + value.replace('"', '\\"') + '"'


def infer_description(path: Path, content: str) -> str:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped.lstrip("#").strip()
    return path.stem.replace("-", " ").replace("_", " ")


def infer_instruction_apply_to(path: Path) -> str:
    path_text = path.as_posix()
    name = path.name
    if "/instructions/agents/" in path_text:
        return ".github/agents/**"
    if "/instructions/prompts/" in path_text:
        return ".github/prompts/**"
    if name == "python.instructions.md":
        return "**/*.py,**/pyproject.toml,**/requirements*.txt"
    if name == "nodejs.instructions.md":
        return "**/*.{js,ts,mjs,cjs,jsx,tsx},**/package.json"
    return "**"


def normalize_customization_content(path: Path, content: str) -> str:
    """Ensure generated customization files have VS Code-readable frontmatter."""
    is_agent = path.name.endswith(".agent.md")
    is_prompt = path.name.endswith(".prompt.md")
    is_instruction = path.name.endswith(".instructions.md")
    if not (is_agent or is_prompt or is_instruction):
        return content

    description = infer_description(path, content)
    match = FRONTMATTER_RE.match(content)
    if match:
        front = match.group(1)
        additions: list[str] = []
        if not re.search(r"(?m)^description\s*:", front):
            additions.append(f"description: {yaml_quote(description)}")
        if is_instruction and not re.search(r"(?m)^applyTo\s*:", front):
            additions.append(f"applyTo: {yaml_quote(infer_instruction_apply_to(path))}")
        if is_agent and not re.search(r"(?m)^name\s*:", front):
            agent_name = path.name[: -len(".agent.md")]
            additions.append(f"name: {agent_name}")
        if not additions:
            return content
        insert_at = match.start(1)
        return content[:insert_at] + "\n".join(additions) + "\n" + content[insert_at:]

    lines: list[str] = ["---"]
    if is_agent:
        agent_name = path.name[: -len(".agent.md")]
        lines.append(f"name: {agent_name}")
    lines.append(f"description: {yaml_quote(description)}")
    if is_instruction:
        lines.append(f"applyTo: {yaml_quote(infer_instruction_apply_to(path))}")
    lines.append("---")
    return "\n".join(lines) + "\n\n" + content


def rewrite_full_workspace_links(base_path: Path) -> None:
    replacements = {
        Path(".github/agents/orchestrator.agent.md"): {
            "../../../references/": "../../references/",
        },
    }
    for relative_path, path_replacements in replacements.items():
        path = base_path / relative_path
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        updated = content
        for source, target in path_replacements.items():
            updated = updated.replace(source, target)
        if updated != content:
            path.write_text(updated, encoding="utf-8")


def lint_files(path: str) -> None:
    """Lint prompt/agent files for complexity thresholds."""
    target = Path(path)
    
    if target.is_file():
        files = [target]
    elif target.is_dir():
        files = list(target.glob("**/*.prompt.md")) + list(target.glob("**/*.agent.md")) + list(target.glob("**/*.instructions.md"))
    else:
        print(f"❌ Path not found: {path}")
        return
    
    if not files:
        print(f"⚠️ No .prompt.md, .agent.md, or .instructions.md files found in: {path}")
        return
    
    print(f"🔍 Linting {len(files)} file(s)...\n")
    
    issues_found = False
    
    for file in files:
        content = file.read_text(encoding="utf-8")
        lines = content.split("\n")
        line_count = len(lines)
        
        # Count steps (numbered lists like "1.", "2.", etc.)
        step_pattern = re.compile(r"^\s*\d+\.\s+")
        steps = [line for line in lines if step_pattern.match(line)]
        step_count = len(steps)
        
        # Check for multiple responsibilities (SRP violation indicators)
        responsibility_keywords = ["## Phase", "## Step", "## Stage", "# Part"]
        phases = sum(1 for line in lines if any(kw in line for kw in responsibility_keywords))
        
        # Analyze issues
        file_issues = []
        
        if line_count > THRESHOLDS["line_count"]:
            file_issues.append(f"  🔴 Line count: {line_count} (threshold: {THRESHOLDS['line_count']})")
        
        if step_count > THRESHOLDS["step_count"]:
            file_issues.append(f"  🔴 Step count: {step_count} (threshold: {THRESHOLDS['step_count']})")
        elif step_count > THRESHOLDS["step_count_warning"]:
            file_issues.append(f"  🟡 Step count: {step_count} (warning threshold: {THRESHOLDS['step_count_warning']})")
        
        if phases > 3:
            file_issues.append(f"  🟡 Multiple phases detected: {phases} (consider splitting)")
        
        if file_issues:
            issues_found = True
            print(f"📄 {file.relative_to(Path.cwd()) if file.is_relative_to(Path.cwd()) else file}")
            for issue in file_issues:
                print(issue)
            print()
    
    if not issues_found:
        print("✅ All files within complexity thresholds.")
    else:
        print("─" * 50)
        print("💡 Recommendations:")
        print("  - 🔴 issues: Consider splitting (see splitting-criteria.md)")
        print("  - 🟡 warnings: Review for potential improvements")
        print()
        print("Escalation options:")
        print("  - L0 → L1: Add .instructions.md file")
        print("  - L1 → L2: Create .agent.md with tools")
        print("  - L2 → L3: Use agent for sub-tasks")


AGENTS_SHARED_TEMPLATE = '''# {workflow_name} - Shared Guardrails

This file is the thin, cross-agent guardrail for the workflow.
Catalogs, workflow maps, and detailed asset indexes belong in `README.md` or `docs/`.

## Scope

- Shared behavior boundaries for all agents
- Safety and communication rules that apply across tools
- Minimal entry guidance for non-Copilot agents

## Entry Boundaries

- GitHub Copilot entry file: `.github/copilot-instructions.md`
- Agent definitions: `.github/agents/*.agent.md`
- Catalogs and workflow maps: `README.md` or `docs/*.md`
- This file should not duplicate agent tables, flow charts, or prompt catalogs

## Workflow Pattern

**{pattern_name}** - {pattern_description}

## Shared Rules

### Behavior

1. **Plan First**: Present a step-by-step plan before tackling complex tasks. Get approval before execution.
2. **Context Awareness**: Read relevant files before working. Do not assume; check existing patterns.
3. **Self-Correction**: Run verification after changes. Analyze errors and propose fixes.

### Communication

- **Conclusion First**: State conclusion, then reasons and details.
- **Match User Language**: Respond in the user's language.

### Safety

- **No `git push`**: Do not push without explicit user instruction.
- **Confirm Destructive Ops**: Always confirm before deletion or irreversible changes.
- **Minimal Permissions**: Request only what's needed.

## References

- [Copilot Instructions](.github/copilot-instructions.md)
- [Design Document](docs/design.md)
- [.github/agents/](.github/agents/)
- [agentic-workflow-guide](https://github.com/aktsmm/Agent-Skills/tree/master/agentic-workflow-guide)
'''

# Pattern-specific AGENTS.md templates
AGENTS_MD_TEMPLATES = {
    "basic": AGENTS_SHARED_TEMPLATE,
    "prompt-chaining": AGENTS_SHARED_TEMPLATE,
    "parallelization": AGENTS_SHARED_TEMPLATE,
    "orchestrator-workers": AGENTS_SHARED_TEMPLATE,
    "evaluator-optimizer": AGENTS_SHARED_TEMPLATE,
    "routing": AGENTS_SHARED_TEMPLATE,
}

# Common templates (used for all patterns)
COMMON_TEMPLATES = {
    ".github/copilot-instructions.md": '''# Copilot Instructions for {workflow_name}

This workflow uses agentic pattern. See the following files for details.

## Role

This file is the GitHub Copilot entry file for the workflow.
Use it for repo-wide routing and global guardrails only.

## Shared Guardrails

- [AGENTS.md](../AGENTS.md) - Cross-agent guardrails and entry boundaries

## Agent Definitions

- [.github/agents/orchestrator.agent.md](.github/agents/orchestrator.agent.md) - Workflow orchestrator
- [.github/agents/worker.agent.md](.github/agents/worker.agent.md) - Worker agent template

## Instructions

- [.github/instructions/workflow.instructions.md](.github/instructions/workflow.instructions.md) - Workflow rules
- [.github/instructions/agents.instructions.md](.github/instructions/agents.instructions.md) - Agent editing rules
- [.github/instructions/prompts.instructions.md](.github/instructions/prompts.instructions.md) - Prompt editing rules

## Prompts

- [.github/prompts/](.github/prompts/) - Reusable prompt templates

## Catalogs

- [README.md](../README.md) or [docs/design.md](../docs/design.md) - Workflow maps and reference-only details

## References

- [docs/design.md](../docs/design.md) - Design document
''',
    
    ".github/instructions/workflow.instructions.md": '''---
applyTo: "**"
---

# Workflow Instructions

Rules applied to the entire workflow.

## Basic Principles

- Each agent has a single responsibility
- Errors are detected early with clear messages
- Intermediate state is always verifiable

## Naming Conventions

- Agents: `{{role}}_agent.md`
- Prompts: `{{purpose}}_prompt.md`
- Config: `{{scope}}_config.yaml`

## File Structure

```
{workflow_name}/
├── AGENTS.md                # Shared guardrails (thin)
├── .github/
│   ├── copilot-instructions.md # GitHub Copilot entry file
│   ├── instructions/
│   ├── agents/              # Agent definitions
│   │   ├── orchestrator.agent.md  # Entry point
│   │   └── worker.agent.md
│   └── prompts/             # Prompt templates
├── docs/                    # Design documents
└── config/                  # Configuration files
```
''',
    
    ".github/instructions/agents.instructions.md": '''---
applyTo: "agents/**"
---

# Agent Instructions

Rules applied when editing files in the `agents/` directory.

## Agent Definition Structure

```markdown
# Agent: {{name}}

## Role
Describe the agent's role in one sentence

## Responsibilities
- Responsibility 1
- Responsibility 2

## Input
- input1: Description

## Output
- output1: Description

## Constraints
- Constraint details
```

## Best Practices

1. **1 Agent = 1 Responsibility** - Split if there are multiple responsibilities
2. **Clear I/O** - Avoid ambiguous definitions
3. **Explicit Constraints** - Consider edge cases
''',
    
    ".github/instructions/prompts.instructions.md": '''---
applyTo: "prompts/**"
---

# Prompt Instructions

Rules applied when editing files in the `prompts/` directory.

## Prompt Structure

```markdown
# {{Purpose}} Prompt

## Context
Background information

## Task
Task description

## Guidelines
1. Guideline 1
2. Guideline 2

## Output Format
Expected output format
```

## Best Practices

1. **Clear Instructions** - Avoid ambiguous expressions
2. **Include Examples** - Show expected output examples
3. **Explicit Constraints** - Write what should NOT be done
4. **Use `{{placeholder}}` format for variables** - Enable dynamic substitution
''',
    
    ".github/prompts/system.prompt.md": '''# System Prompt

You are a specialized agent in the {workflow_name} workflow.

## Your Role

[Describe the agent's role in one sentence]

## Guidelines

1. **Plan First**: Present a plan before executing complex tasks
2. **Single Responsibility**: Focus on your responsibility, delegate the rest
3. **Validate First**: Validate input before processing
4. **Fail Fast**: Detect and report errors early
5. **Transparency**: Report progress explicitly

## Constraints

- Do not fill in data based on assumptions (confirm unclear points)
- Stop processing if validation fails
- Request confirmation before destructive operations
- `git push` is prohibited by default

## Output Format

- Conclusion first (conclusion → reasons → details)
- Strive for structured output
''',
    
    ".github/prompts/create-agent.prompt.md": '''# Prompt: Create New Agent

Prompt for creating a new agent definition (`.agent.md`).

## Prerequisites

- Reference: `.github/agents/templates/sample-agent.md` (template)
- Reference: `.github/instructions/agents.instructions.md`

## Instructions

1. Define **Role** and **Goals** from user requirements
2. Write **Done Criteria** in verifiable form
3. Follow the principle of least privilege for **Permissions**
4. Clearly define **I/O Contract**
5. Break down **Workflow** into specific steps

## Output Format

```markdown
# [Agent Name]

## Role
[Role in one sentence]

## Goals
- [Goal 1]
- [Goal 2]

## Done Criteria
- [Verifiable completion condition 1]
- [Verifiable completion condition 2]

## Permissions
- **Allowed**: [Permitted operations]
- **Denied**: `git push`, deletion without user permission

## I/O Contract
- **Input**: [Input format]
- **Output**: [Output format]

## Workflow
1. **Plan**: Analyze request and present steps
2. **Act**: Execute after approval
3. **Verify**: Verify results

## Error Handling
- When errors occur, analyze and attempt to fix
- Report to human after 3 consecutive failures

## Idempotency
- Check existing state before operations
- Avoid duplicate processing
```
''',
    
    ".github/prompts/design-workflow.prompt.md": '''# Prompt: Design Agent Workflow

Prompt for designing an agent workflow.

## Prerequisites

- Reference: `docs/design.md`
- Principles: SSOT, SRP, Simplicity First, Fail Fast

## Instructions

Design the following based on user requirements:

### Step 1: Determine Complexity Level

| Level | Agent Count | Use Case |
|-------|-------------|----------|
| Simple | 1 | Single task, simple processing |
| Medium | 2-3 | Orchestrator + workers |
| Complex | 4+ | Multiple specialized agents |

**Principle: Start Simple** - Try the minimum configuration first

### Step 2: Create Design Document

1. **Workflow Purpose**: What problem does it solve?
2. **Agent Composition**: Roles and responsibilities
3. **I/O Contract**: Input/output definitions
4. **Interaction Flow**: Data flow
5. **Verification Points**: Gate/Checkpoint placement
6. **Error Handling**: Response to failures

## Output Format

```markdown
# [Workflow Name] Design

## Overview
- **Purpose**: 
- **Complexity**: Simple | Medium | Complex
- **Pattern**: [Prompt Chaining | Routing | Parallelization | Orchestrator-Workers | Evaluator-Optimizer]

## Agents
| Agent | Role | Input | Output |
|-------|------|-------|--------|

## Flow
```mermaid
graph TD
    A[Input] --> B[Agent 1]
    B --> C{{Gate}}
    C -->|Pass| D[Agent 2]
    C -->|Fail| E[Error Handler]
```

## Checkpoints
1. [Verification points between steps]

## Error Handling
- [Response on error]
```
''',
    
    ".github/prompts/plan-workflow.prompt.md": '''# Prompt: Plan Agent Workflow

Prompt for planning a combination of multiple agents.

## Prerequisites

- Reference: `Agent.md` (list of available agents)

## Instructions

Follow these steps to create a plan for achieving the user's task:

1. **Task Decomposition**: Break down into independent subtasks
2. **Agent Selection**: Choose the optimal agent for each subtask
3. **Flow Definition**: Define data handoff and sequence
4. **Verification Points**: Verification method after each step
5. **Execution Plan**: Specific execution steps

## Output Example

### Step 1: Requirements Definition
- **Agent**: orchestrator
- **Goal**: Organize user's requirements
- **Output**: `docs/requirements.md`
- **Validation**: User confirmation

### Step 2: Implementation
- **Agent**: worker
- **Input**: requirements.md from Step 1
- **Goal**: Perform implementation
- **Output**: Implementation files
- **Validation**: Run tests
''',
    
    ".github/prompts/review-agent.prompt.md": '''# Prompt: Review Agent Definition

Prompt for reviewing agent definitions.

## Design Principles Checklist

### Tier 1: Core Principles (Required)
- [ ] **SRP**: Is it 1 agent = 1 responsibility?
- [ ] **SSOT**: Is information centrally managed?
- [ ] **Fail Fast**: Can errors be detected early?

### Tier 2: Quality Principles (Recommended)
- [ ] **I/O Contract**: Are inputs/outputs clearly defined?
- [ ] **Done Criteria**: Are completion conditions verifiable?
- [ ] **Idempotency**: Is the design retry-safe?
- [ ] **Error Handling**: Is error handling documented?

### Structure Check
- [ ] Is Role clear in one sentence?
- [ ] Are Goals specific?
- [ ] Are Permissions minimal?
- [ ] Is Workflow broken into steps?

## Output Format

```markdown
## Review Result

### ✅ Good Points
- [Good points]

### ⚠️ Improvements Needed
- [Improvement points]

### Recommendation
[Overall evaluation and recommended actions]
```
''',
    
    ".github/prompts/error-handling.prompt.md": '''# Error Handling Prompt

Protocol for handling errors.

## Error Classification

| Type | Description | Recovery |
|------|-------------|----------|
| ValidationError | Invalid input data | Fix input and retry |
| ProcessingError | Failure during processing | Analyze cause and retry |
| TimeoutError | Timeout | Retry or skip |
| DependencyError | External service failure | Fallback |

## Response Format

```yaml
error:
  type: {{error_type}}
  message: {{error_message}}
  context: {{relevant_context}}
  recovery:
    possible: true/false
    suggestion: {{recovery_suggestion}}
    retry_count: {{current_retry}}/3
```

## Escalation Rules

1. **Retry**: Same error up to 3 times max
2. **Fallback**: Try alternative method if possible
3. **Handoff**: Report to human after 3 failures
4. **Log**: Record all context

## Fail Fast Principle

- Detect errors early
- Report immediately when problems occur
- Do not continue in an ambiguous state
''',
    
    ".github/prompts/review-retrospective-learnings.prompt.md": '''# Prompt: Agent Design Retro

Extract reusable design insights from events (incident response, errors, fix PRs)
and reflect them in design assets for prevention and quality improvement.

## Your Role
You are an "AI Agent Design Improvement Architect".

## Premises
- Do not make changes based on assumptions. Always read target files first.
- Prioritize additions over new content. Use reference links for duplicates.
- For destructive changes, always confirm first.

## Input
- Response history (timeline, logs, error messages, fixes)
- Scope of reflection (AGENTS.md / README.md / docs / *.agent.md / instructions)

## Steps

### Step 0: Context Collection
1. Read target files (AGENTS.md, README.md / docs/*.md, agents/*.agent.md, instructions/*.md)
2. Summarize existing rules in 5 lines or less

### Step 1: Extract and Classify Learnings
- Design principle level (separation of concerns, idempotency)
- Workflow level (call order, preconditions, error handling)
- Agent-specific rules (input assumptions, prohibitions)

Format: Learning (1 line) + Evidence + Impact

### Step 2: Generalization Judgment
For each learning, determine:
- Individual response / Generalize / Strengthen existing rules
- Check for duplicates/conflicts

### Step 3: Determine Reflection Target
- Shared guardrail / entry boundary → AGENTS.md or .github/copilot-instructions.md
- Agent-specific → .github/agents/*.agent.md
- Overall constraints → .github/instructions/*.md
- Catalog / workflow map → README.md or docs/*.md

### Step 4: Present Update Content
Show "exactly how to rewrite" in code blocks:
- add / replace / restructure
- Change granularity (add heading, bullet points, etc.)

### Step 5: Final Check
- Design philosophy is consistent
- Reusability and maintainability improve
- Same trouble is less likely to recur
''',
    
    ".github/prompts/create-agentWF.prompt.md": '''# Create Agent Workflow Prompt

Hearing prompt for designing agent workflows through user dialogue.

## Mode: Start Hearing

You are an agent workflow design facilitator.

## Step 1: Confirm Purpose

```
What kind of agent workflow do you want to create?

Please tell me:
1. **What do you want to achieve?** (report generation, automation, analysis...)
2. **For whom?** (personal, team, customer demo...)
3. **Trigger?** (manual, schedule, event...)
```

## Step 2: Define Input/Output

```
**Input:**
- What will you receive? (file, API, user input...)
- Format? (JSON, text, CLI arguments...)

**Output:**
- What to generate? (report, diagram, file...)
- Format? (Markdown, CSV, PDF...)
- Destination? (file, Issue, Slack...)
```

## Step 3: Confirm Tools/APIs

```
- **External API**: Azure CLI, GitHub CLI, REST API...
- **Authentication**: Via environment variables?
- **Existing tools**: Scripts in the project?
```

## Step 4: Consider Workflow Structure

```
1. **Complexity**: Single agent or multiple?
2. **Steps**: How many stages?
3. **Review**: Human confirmation points?
4. **On error**: Retry? Report to human?

Examples:
- Simple → 1 agent
- Medium → Orchestrator + 1-2 workers
- Large → Orchestrator + multiple workers
```

## Step 5: Design Principles Confirmation

```
This workflow follows:
- Two-stage architecture: Input → IR → Output
- Idempotency: Same input → same result
- Separation of concerns
- Fail-safe with error handling
- Observability with logs
```

## Step 6: Generate Deliverables

```
Deliverables:
1. Agent definition (.github/agents/{{name}}.agent.md)
2. IR schema (if needed)
3. Report template (if needed)
```

## Hearing Result IR Template

```yaml
workflow:
  name: "{{{{workflow_name}}}}"
  purpose: "{{{{purpose}}}}"
  trigger: "{{{{trigger}}}}"
io:
  input: {{ source: "", format: "" }}
  output: {{ type: "", format: "", destination: "" }}
architecture:
  complexity: "simple|medium|complex"
  agents: []
  human_checkpoints: []
  error_handling: ""
```
'''
}

# Extended instruction templates (optional, generated with --include-instructions flag)
EXTENDED_INSTRUCTIONS = {
    ".github/instructions/communication.instructions.md": '''---
applyTo: "**"
---

# Communication Instructions

## 1. Response Style
- **Conclusion First**: State conclusion, then reasons and details.
- **Conciseness**: Avoid verbose explanations.
- **Logical Structure**: Use bullet points, tables, headings.

## 2. Language Settings
- Match user's language for dialogue
- Follow existing comment style in code

## 3. Citation of References
- Include relative paths for file references
- Include URLs for external resources

## 4. Confirmation and Approval
Always seek user confirmation before:
- File deletion or large-scale changes
- External service connections
- Design policy decisions

## 5. Error Reporting Format
1. What happened (overview)
2. Why (cause analysis)
3. What to do (recommended remediation)
''',
    
    ".github/instructions/git.instructions.md": '''---
applyTo: "**"
---

# Git Commit Instructions

Use **Conventional Commits** format.

## Format
```
<type>(<scope>): <subject>
```

## Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation only
- **style**: Formatting (no code change)
- **refactor**: Code change (no feature/bug)
- **test**: Adding/correcting tests
- **chore**: Build/tool changes

## Rules
- Use imperative form ("add" not "added")
- No period at end
- Lowercase first letter

## Important
- **Push Prohibited**: No `git push` without explicit instruction
- Split commits for multiple logical changes
''',
    
    ".github/instructions/terminal.instructions.md": '''---
applyTo: "**"
---

# Terminal Instructions

## 1. Confirm Current Directory
Always verify location before commands:
```powershell
Get-Location
Set-Location "path/to/project"
```

## 2. Command Syntax (PowerShell)
- Use `;` to chain commands (not `&&`)
- Use pipeline `|` for data operations

## 3. Destructive Operations
- Verify paths before delete/move
- Avoid wildcards; use specific names

## 4. Long-running Processes
- Use background execution for servers
- Inform user about non-terminating commands
''',
    
    ".github/instructions/security.instructions.md": '''---
applyTo: "**"
---

# Security Instructions

## 1. Confidential Information
**Prohibited:**
- Hardcoding API keys, passwords, tokens
- Committing `.env` or secret files

**Recommended:**
- Use environment variables
- Use secret management (Key Vault, GitHub Secrets)
- Configure `.gitignore`

## 2. External Libraries
- Check license compatibility
- Check for vulnerabilities (npm audit, pip-audit)

## 3. API Calls
- Principle of least privilege
- Implement rate limiting and backoff

## 4. Git Operations
- No `git push` without instruction
- No `--force` push
- Use PR-based workflow

## 5. Input Validation
- Sanitize for injection attacks
- Prevent directory traversal
''',
    
    ".github/instructions/microsoft-docs.instructions.md": '''---
applyTo: "**"
---

# Microsoft Documentation Instructions

## Basic Policy
Reference latest official documentation for Microsoft/Azure answers.

## Required Procedure
1. Use MCP tools to get latest info
2. Always include reference URLs
3. Note API versions

## MCP Tool Workflow
```
1. microsoft_docs_search → Find docs
2. microsoft_code_sample_search → Get code samples
3. microsoft_docs_fetch → Get full content
```

## Answer Format
```markdown
## Answer
[Content]

### References
- [Doc Title](URL) - Microsoft Learn
- API Version: 2024-01-01
```

## Priority
1. Official docs via MCP tools (highest)
2. Official GitHub repos
3. Official blogs/announcements
'''
}

# Templates for each workflow pattern
PATTERNS = {
    "basic": {
        "description": "Basic workflow structure",
        "structure": {
            ".github/agents": {
                "__description__": "Agent definitions",
                "orchestrator.agent.md": '''# Orchestrator Agent

## Role

You are the orchestrator (commander). You analyze user requests, delegate work to appropriate sub-agents, and manage overall progress.

**This is the entry point for this workflow.**

## Goals

- Understand user requests and decompose tasks
- Assign appropriate work to each sub-agent
- Monitor progress and report results to users

## Done Criteria

- All subtasks have `completed` or `skipped` status
- Final report has been presented to the user

## Permissions

- **Allowed**: Task decomposition, delegation to sub-agents, progress reporting
- **Denied**: Direct code editing, file deletion, `git push`

## Non-Goals (What not to do)

- Do not write code directly (delegate implementation to specialized agents)
- Do not review yourself (delegate reviews to specialized agents)
- Do not assume user intent (confirm unclear points)

## I/O Contract

- **Input**: Natural language request from user
- **Output**:
  - Task decomposition results
  - Final report (deliverables list + status)

## Workflow

1. **Analyze**: Analyze user request and identify required tasks
2. **Plan**: Decompose tasks and present plan for which sub-agent to delegate to
3. **Delegate**: After user approval, invoke sub-agents
4. **Monitor**: Check results from each sub-agent and handle any issues
5. **Report**: Report overall results to user

## Error Handling

- If a sub-agent fails 3 times consecutively, report to human and handoff
- Log failed tasks and maintain retry-capable state

## Idempotency

- Always read task state from files (do not depend on conversation history)
- Do not re-execute already completed tasks
''',
                "worker.agent.md": '''# Worker Agent

## Role

You are a worker agent. You execute specific subtasks assigned by the orchestrator.

## Goals

- Execute assigned subtask accurately
- Report results back to orchestrator

## Done Criteria

- [Completion condition 1: Describe in verifiable form]
- [Completion condition 2]

## Permissions

- **Allowed**: File reading, file editing, proposal creation
- **Denied**: `git push`, file deletion without user permission

## I/O Contract

- **Input**: Subtask description from orchestrator
- **Output**: Task result and status

## References

- [Workflow Instructions](../instructions/workflow.instructions.md)

## Workflow

1. **Receive**: Receive subtask from orchestrator
2. **Plan**: Analyze subtask and present steps
3. **Act**: Execute after approval
4. **Verify**: Confirm results
5. **Report**: Report results to orchestrator

## Error Handling

- When errors occur, analyze error messages and attempt to fix
- Report to orchestrator after 3 consecutive failures
- Always request confirmation before destructive operations

## Idempotency

- Check for existing files before operations
- Always check state to avoid duplicate processing
'''
            },
            ".github/prompts": {
                "__description__": "Prompt templates"
            },
            "docs": {
                "__description__": "Design documents",
                "design.md": '''# Workflow Design Document

## Overview
- **Name**: 
- **Purpose**: 
- **Pattern**: 

## Agents
| Agent | Role | Input | Output |
|-------|------|-------|--------|
| | | | |

## Flow
```mermaid
graph TD
    A[Start] --> B[Agent 1]
    B --> C[Agent 2]
    C --> D[End]
```

## Design Principles Check
- [ ] SSOT: Is information centrally managed?
- [ ] SRP: Is each agent single responsibility?
- [ ] Fail Fast: Stop immediately on error?
- [ ] Iterative: Is it divided into small steps?
- [ ] Feedback Loop: Can results be verified?
''',
                "review_notes.md": '''# Review Notes

## Review Date
- 

## Reviewer
- 

## Checklist Results
See: agentic-workflow-guide/references/review-checklist.md

## Issues Found
1. 

## Action Items
1. 
'''
            },
            "config": {
                "__description__": "Configuration files",
                "workflow_config.yaml": '''# Workflow Configuration

name: "{workflow_name}"
version: "1.0.0"

# Agents
agents:
  - name: agent_1
    prompt: prompts/system_prompt.md
    
# Flow
flow:
  - step: 1
    agent: agent_1
    next: 2
    
# Error handling
error_handling:
  max_retries: 3
  on_failure: stop
'''
            }
        }
    },
    "prompt-chaining": {
        "description": "Sequential processing pattern",
        "structure": {
            ".github/agents": {
                "__description__": "Sequentially executed agents",
                "orchestrator.agent.md": "# Orchestrator Agent\n\n## Role\nCoordinate sequential step execution\n\n**Entry point for this workflow.**\n",
                "step1.agent.md": "# Step 1 Agent\n\n## Role\nHandle the first step\n",
                "step2.agent.md": "# Step 2 Agent\n\n## Role\nHandle the second step\n",
                "step3.agent.md": "# Step 3 Agent\n\n## Role\nHandle the final step\n"
            },
            ".github/prompts": {
                "__description__": "Prompts for each step"
            },
            "gates": {
                "__description__": "Validation gates between steps",
                "gate_template.md": '''# Gate: Step N → Step N+1

## Validation Criteria
- [ ] Condition 1
- [ ] Condition 2

## On Pass
Proceed to next step

## On Fail
Error handling or retry
'''
            },
            "docs": {
                "__description__": "Design documents",
                "design.md": "# Prompt Chaining Workflow\n\n## Pattern: Prompt Chaining\nSequential processing with validation at each step\n"
            },
            "config": {
                "__description__": "Configuration files"
            }
        }
    },
    "parallelization": {
        "description": "Parallel processing pattern",
        "structure": {
            ".github/agents": {
                "__description__": "Parallel executed agents",
                "orchestrator.agent.md": "# Orchestrator Agent\n\n## Role\nCoordinate parallel task execution and aggregate results\n\n**Entry point for this workflow.**\n",
                "worker1.agent.md": "# Worker 1 Agent\n\n## Role\nHandle parallel task 1\n",
                "worker2.agent.md": "# Worker 2 Agent\n\n## Role\nHandle parallel task 2\n",
                "worker3.agent.md": "# Worker 3 Agent\n\n## Role\nHandle parallel task 3\n"
            },
            ".github/prompts": {
                "__description__": "Prompts for workers"
            },
            "docs": {
                "__description__": "Design documents",
                "design.md": "# Parallelization Workflow\n\n## Pattern: Parallelization\nExecute independent tasks simultaneously\n"
            },
            "config": {
                "__description__": "Configuration files"
            }
        }
    },
    "orchestrator-workers": {
        "description": "Orchestrator + workers pattern",
        "structure": {
            ".github/agents": {
                "__description__": "Orchestrator and workers",
                "orchestrator.agent.md": '''# Orchestrator Agent

## Role
Dynamically decompose tasks and assign to workers

**Entry point for this workflow.**

## Responsibilities
1. Analyze input
2. Generate subtasks
3. Launch workers
4. Integrate results
''',
                "worker.agent.md": '''# Worker Agent Template

## Role
Execute assigned subtask

## Input
- task: Subtask content
- context: Required context

## Output
- result: Task result
- status: Success/Failure
'''
            },
            ".github/prompts": {
                "__description__": "Prompts for each agent"
            },
            "docs": {
                "__description__": "Design documents",
                "design.md": "# Orchestrator-Workers Workflow\n\n## Pattern: Orchestrator-Workers\nDynamically decompose tasks and dispatch to workers\n"
            },
            "config": {
                "__description__": "Configuration files"
            }
        }
    },
    "evaluator-optimizer": {
        "description": "Evaluation-improvement loop pattern",
        "structure": {
            ".github/agents": {
                "__description__": "Orchestrator, generator and evaluator",
                "orchestrator.agent.md": '''# Orchestrator Agent

## Role
Coordinate the generate-evaluate-improve loop

**Entry point for this workflow.**

## Responsibilities
1. Send generation requests to generator
2. Send outputs to evaluator
3. Route feedback back to generator
4. Decide when to stop iteration
''',
                "generator.agent.md": '''# Generator Agent

## Role
Generate content

## Input
- request: Generation request
- feedback: Previous feedback (if any)

## Output
- content: Generated content
''',
                "evaluator.agent.md": '''# Evaluator Agent

## Role
Evaluate generated content

## Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Output
- passed: true/false
- feedback: Improvement points (on failure)
'''
            },
            ".github/prompts": {
                "__description__": "Generation and evaluation prompts"
            },
            "docs": {
                "__description__": "Design documents",
                "design.md": '''# Evaluator-Optimizer Workflow

## Pattern: Evaluator-Optimizer
Generate → Evaluate → Improve loop

## Flow
```mermaid
graph TD
    A[Input] --> B[Generator]
    B --> C[Output]
    C --> D[Evaluator]
    D -->|Not Good| E[Feedback]
    E --> B
    D -->|Good| F[Final Output]
```

## Loop Control
- max_iterations: 5
- on_max_reached: return_best
'''
            },
            "config": {
                "__description__": "Configuration files",
                "loop_config.yaml": '''# Evaluator-Optimizer Loop Configuration

max_iterations: 5
evaluation_criteria:
  - name: criteria_1
    weight: 0.4
  - name: criteria_2
    weight: 0.3
  - name: criteria_3
    weight: 0.3

threshold: 0.8
on_max_reached: return_best  # or: fail
'''
            }
        }
    },
    "routing": {
        "description": "Routing pattern",
        "structure": {
            ".github/agents": {
                "__description__": "Router and specialized handlers",
                "orchestrator.agent.md": '''# Orchestrator (Router) Agent

## Role
Classify input and route to appropriate handler

**Entry point for this workflow.**

## Categories
- type_a: Route to Handler A
- type_b: Route to Handler B
- type_c: Route to Handler C
''',
                "handler-a.agent.md": "# Handler A Agent\n\n## Role\nHandle Type A processing\n",
                "handler-b.agent.md": "# Handler B Agent\n\n## Role\nHandle Type B processing\n",
                "handler-c.agent.md": "# Handler C Agent\n\n## Role\nHandle Type C processing\n"
            },
            ".github/prompts": {
                "__description__": "Routing and handler prompts"
            },
            "docs": {
                "__description__": "Design documents",
                "design.md": "# Routing Workflow\n\n## Pattern: Routing\nClassify input and route to specialized processing\n"
            },
            "config": {
                "__description__": "Configuration files"
            }
        }
    }
}


def create_structure(base_path: Path, structure: dict, workflow_name: str):
    """Recursively create directory structure"""
    for name, content in structure.items():
        if name == "__description__":
            continue
            
        path = base_path / name
        
        if isinstance(content, dict):
            # Create directory
            path.mkdir(parents=True, exist_ok=True)
            # Create .gitkeep for empty directory
            if not any(k for k in content.keys() if k != "__description__"):
                (path / ".gitkeep").touch()
            else:
                create_structure(path, content, workflow_name)
        else:
            # Create file
            file_content = content.format(
                workflow_name=workflow_name,
                name=workflow_name,
                role_description="",
                context="",
                task_description="",
                output_format=""
            )
            file_content = normalize_customization_content(path, file_content)
            path.write_text(file_content, encoding="utf-8")


def scaffold_workflow(name: str, pattern: str = "basic", output_path: str = ".", include_instructions: bool = False, full_workspace: bool = False):
    """Generate workflow directory structure
    
    Args:
        name: Workflow name
        pattern: Workflow pattern (basic, prompt-chaining, etc.)
        output_path: Output directory
        include_instructions: If True, generate extended instruction templates
        full_workspace: If True, copy full workspace templates from assets/workspace-templates
    """
    
    if pattern not in PATTERNS:
        print(f"❌ Unknown pattern: {pattern}")
        print(f"   Available patterns: {', '.join(PATTERNS.keys())}")
        return False
    
    pattern_info = PATTERNS[pattern]
    base_path = Path(output_path) / name
    
    if base_path.exists():
        print(f"❌ Directory already exists: {base_path}")
        return False
    
    print(f"🚀 Creating workflow: {name}")
    print(f"   Pattern: {pattern} - {pattern_info['description']}")
    print(f"   Location: {base_path.absolute()}")
    print()
    
    # Create directory structure
    base_path.mkdir(parents=True, exist_ok=True)
    create_structure(base_path, pattern_info["structure"], name)
    
    # Create .github directory and instructions
    github_dir = base_path / ".github"
    github_dir.mkdir(parents=True, exist_ok=True)
    instructions_dir = github_dir / "instructions"
    instructions_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate AGENTS.md with pattern-specific template
    agents_md_template = AGENTS_MD_TEMPLATES.get(pattern, AGENTS_MD_TEMPLATES["basic"])
    agents_md_content = agents_md_template.format(
        workflow_name=name,
        pattern_name=pattern,
        pattern_description=pattern_info["description"],
    )
    (base_path / "AGENTS.md").write_text(agents_md_content, encoding="utf-8")
    
    # Generate common templates (excluding AGENTS.md which is pattern-specific)
    for filename, template in COMMON_TEMPLATES.items():
        file_path = base_path / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        content = template.format(
            workflow_name=name,
            pattern=pattern,
            pattern_description=pattern_info['description'],
            purpose="your use case",
            agent_role="Describe your agent's role here",
            context="",
            task_description="",
            input_data="",
            output_format="",
            good_example="",
            bad_example=""
        )
        content = normalize_customization_content(file_path, content)
        file_path.write_text(content, encoding="utf-8")
    
    # Generate extended instructions if requested
    if include_instructions:
        print("📋 Generating extended instructions...")
        for filename, template in EXTENDED_INSTRUCTIONS.items():
            file_path = base_path / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            content = normalize_customization_content(file_path, template)
            file_path.write_text(content, encoding="utf-8")
    
    # Copy full workspace templates if requested
    if full_workspace:
        print("📦 Copying full workspace templates...")
        import shutil
        # Find the assets/workspace-templates directory relative to this script
        script_dir = Path(__file__).parent
        templates_dir = script_dir.parent / "assets" / "workspace-templates"
        
        if not templates_dir.exists():
            print(f"⚠️ Workspace templates not found: {templates_dir}")
            print("   Run with --include-instructions instead for basic templates.")
        else:
            github_dir = base_path / ".github"
            github_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy copilot-instructions.md
            src_copilot = templates_dir / "copilot-instructions.md"
            if src_copilot.exists():
                shutil.copy2(src_copilot, github_dir / "copilot-instructions.md")
                print("   📄 copilot-instructions.md")
            
            # Copy agents/, instructions/, prompts/ directories
            for folder in ["agents", "instructions", "prompts"]:
                src_folder = templates_dir / folder
                dst_folder = github_dir / folder
                if src_folder.exists():
                    shutil.copytree(src_folder, dst_folder, dirs_exist_ok=True)
                    file_count = len(list(dst_folder.rglob("*")))
                    print(f"   📁 {folder}/ ({file_count} files)")

            src_references = script_dir.parent / "references"
            dst_references = base_path / "references"
            if src_references.exists():
                if dst_references.exists():
                    shutil.rmtree(dst_references)
                shutil.copytree(src_references, dst_references)
                file_count = len(list(dst_references.rglob("*")))
                print(f"   📁 references/ ({file_count} files)")

            rewrite_full_workspace_links(base_path)
    
    # Generate README.md
    readme_content = f'''# {name}

## Overview
Generated with `agentic-workflow-guide` skill.

## Pattern
**{pattern}** - {pattern_info['description']}

## Entry Point

**Start with [.github/copilot-instructions.md](.github/copilot-instructions.md)** for GitHub Copilot behavior.
Use [AGENTS.md](AGENTS.md) only for shared cross-agent guardrails.

## Directory Structure
```
{name}/
├── AGENTS.md                   # Shared guardrails (thin)
├── .github/
│   ├── copilot-instructions.md # GitHub Copilot entry file
│   ├── instructions/           # Individual instructions
│   ├── agents/                 # Agent definitions
│   │   ├── orchestrator.agent.md  # Entry point
│   │   └── worker.agent.md
│   └── prompts/                # Prompt templates
├── docs/                       # Design documents
└── config/                     # Configuration files
```

## Quick Start

1. Read **.github/copilot-instructions.md** for GitHub Copilot entry behavior
2. Read **AGENTS.md** for shared cross-agent guardrails
3. Customize orchestrator in **.github/agents/orchestrator.agent.md**
4. Add workers in **.github/agents/**
5. Document workflow maps in **README.md** or **docs/design.md**

## Files

| File | Purpose |
|------|---------|
| `AGENTS.md` | Shared guardrails and entry boundaries |
| `.github/copilot-instructions.md` | GitHub Copilot entry file |
| `.github/agents/*.agent.md` | Agent definitions |
| `.github/prompts/*.prompt.md` | Prompt templates |
| `README.md` / `docs/*.md` | Catalogs and workflow maps |
| `.github/instructions/*.instructions.md` | File pattern-specific rules |

## Design Principles

This workflow should follow:

- **SSOT** - Single Source of Truth
- **SRP** - Single Responsibility Principle
- **Fail Fast** - Early error detection
- **Iterative Refinement** - Small iterations
- **Feedback Loop** - Verify results

See: `agentic-workflow-guide` for full checklist.

## References

- [agentic-workflow-guide](https://github.com/aktsmm/Agent-Skills/tree/master/agentic-workflow-guide)
- [Anthropic: Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
'''
    
    (base_path / "README.md").write_text(readme_content, encoding="utf-8")
    
    print("✅ Created structure:")
    print(f"   📄 AGENTS.md")
    print(f"   📄 README.md")
    print(f"   📁 .github/")
    print(f"      📄 copilot-instructions.md")
    print(f"      📁 instructions/")
    print(f"      📁 agents/")
    print(f"         📄 orchestrator.agent.md")
    print(f"      📁 prompts/")
    for dir_name in pattern_info["structure"].keys():
        if dir_name != "__description__" and not dir_name.startswith(".github"):
            print(f"   📁 {dir_name}/")
    
    print(f"\n✅ Workflow '{name}' scaffolded successfully!")
    print("\nGenerated files:")
    print("  📄 AGENTS.md - Entry point with orchestrator")
    print("  📄 .github/copilot-instructions.md - Links to agents")
    print("  📄 .github/agents/*.agent.md - Agent definitions")
    print("  📄 .github/prompts/*.prompt.md - Prompt templates")
    print("  📄 .github/instructions/*.instructions.md - Individual rules")
    print("\nNext steps:")
    print("1. Read AGENTS.md for entry point")
    print("2. Customize .github/agents/orchestrator.agent.md")
    print("3. Add workers in .github/agents/")
    print("4. Update .github/prompts/ with your prompts")
    print("5. Review with agentic-workflow-guide checklist")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Generate agent workflow directory structure"
    )
    parser.add_argument("name", nargs="?", help="Workflow name")
    parser.add_argument(
        "--pattern", "-p",
        choices=list(PATTERNS.keys()),
        default="basic",
        help="Workflow pattern (default: basic)"
    )
    parser.add_argument(
        "--path",
        default=".",
        help="Output directory (default: current directory)"
    )
    parser.add_argument(
        "--list-patterns",
        action="store_true",
        help="List available patterns"
    )
    parser.add_argument(
        "--include-instructions", "-i",
        action="store_true",
        help="Include extended instruction templates (agent-design, git, security, etc.)"
    )
    parser.add_argument(
        "--full-workspace", "-f",
        action="store_true",
        help="Copy full workspace templates (agents, instructions, prompts, references) from bundled assets"
    )
    parser.add_argument(
        "--lint",
        type=str,
        metavar="PATH",
        help="Lint prompt/agent files for complexity thresholds (line count, step count)"
    )
    
    args = parser.parse_args()
    
    # Handle --lint option
    if args.lint:
        lint_files(args.lint)
        return
    
    if args.list_patterns:
        print("Available patterns:\n")
        for name, info in PATTERNS.items():
            print(f"  {name}")
            print(f"    {info['description']}")
            print()
        print("Extended instructions (use --include-instructions):")
        print("  - communication.instructions.md")
        print("  - git.instructions.md")
        print("  - terminal.instructions.md")
        print("  - security.instructions.md")
        print("  - microsoft-docs.instructions.md")
        return
    
    if not args.name:
        parser.print_help()
        return
    
    scaffold_workflow(args.name, args.pattern, args.path, args.include_instructions, args.full_workspace)


if __name__ == "__main__":
    main()
