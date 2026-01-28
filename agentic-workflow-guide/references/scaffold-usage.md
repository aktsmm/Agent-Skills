# Scaffold Workflow Usage

Automatically generate workflow directory structures using `scaffold_workflow.py`.

## Usage

```bash
# Basic workflow
python scripts/scaffold_workflow.py my-workflow

# Specify pattern
python scripts/scaffold_workflow.py code-review --pattern evaluator-optimizer

# Specify output path
python scripts/scaffold_workflow.py data-pipeline --pattern orchestrator-workers --path ./projects

# List available patterns
python scripts/scaffold_workflow.py --list-patterns
```

## Available Patterns

| Pattern                | Description                    |
| ---------------------- | ------------------------------ |
| `basic`                | Basic workflow structure       |
| `prompt-chaining`      | Sequential processing pattern  |
| `parallelization`      | Parallel processing pattern    |
| `orchestrator-workers` | Orchestrator + workers pattern |
| `evaluator-optimizer`  | Evaluation-improvement loop    |
| `routing`              | Routing pattern                |

## Generated Structure

```
my-workflow/
├── README.md                       # Usage guide
├── .github/
│   ├── copilot-instructions.md    # GitHub Copilot instructions
│   ├── agents/                     # Custom agent definitions
│   │   ├── orchestrator.agent.md  # Main orchestrator agent
│   │   ├── planner.agent.md       # Planning specialist
│   │   ├── implementer.agent.md   # Implementation agent
│   │   └── reviewer.agent.md      # Code review agent
│   └── instructions/               # File-pattern-specific rules
│       └── workflow.instructions.md
├── prompts/                        # Prompt templates (optional)
│   └── system_prompt.md
└── docs/                           # Design documentation
    └── design.md
```

**Note**: Custom agents use `.agent.md` extension in `.github/agents/` directory (VS Code 1.106+).

## Pattern Selection

Use `--pattern` flag based on your workflow needs:

- **Sequential tasks with validation** → `prompt-chaining`
- **Independent parallel tasks** → `parallelization`
- **Dynamic task decomposition** → `orchestrator-workers`
- **Quality improvement loop** → `evaluator-optimizer`
- **Input-dependent routing** → `routing`
