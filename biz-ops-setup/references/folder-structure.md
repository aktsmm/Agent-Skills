# Biz-Ops Folder Structure

## Structure Diagram

```
{workspace-name}/
├── DASHBOARD.md              # Daily hub
├── AGENTS.md                 # Workspace description
│
├── ActivityReport/           # Activity reports (for manager PR and performance reviews)
│   └── {YYYY-MM}/
│       ├── daily/            # Daily reports
│       ├── weekly/           # Weekly reports
│       └── {YYYY-MM}.md      # Monthly reports
│
├── Customers/                # Customer-specific workspaces
│   ├── {customer-id}/
│   │   ├── profile.md        # Customer profile
│   │   ├── tasks.md          # Customer-specific tasks
│   │   ├── _inbox/           # Customer-dedicated inbox
│   │   └── _meetings/        # Meeting minutes
│   └── README.md
│
├── Tasks/                    # Task management (overall)
│   ├── active.md             # Active tasks
│   ├── completed.md          # Completed tasks
│   ├── backlog.md            # Backlog
│   └── unclassified.md       # Unclassified
│
├── _internal/                # Internal events and activities
│   ├── _inbox/               # Internal-related information
│   ├── _meetings/            # Internal meeting minutes
│   ├── tech-connect/         # Tech Connect related
│   └── team/                 # Team and 1-on-1
│
├── _inbox/                   # Information accumulation (unclassified logs)
│   └── {YYYY-MM}.md
│
├── _datasources/             # Data source configuration
│   ├── README.md
│   └── workiq-spec.md
│
├── _workiq/                  # workIQ core configuration
│   ├── README.md
│   └── japan-holidays.md     # Holiday configuration
│
└── .github/
    ├── agents/               # Agent definitions
    ├── prompts/              # Prompt templates
    ├── skills/               # Skills
    └── copilot-instructions.md
```

## Naming Conventions

| Prefix       | Purpose                      | View Frequency |
| ------------ | ---------------------------- | -------------- |
| `PascalCase` | Human-use, daily operations  | High           |
| `_xxx`       | System-use, log accumulation | Low            |

## Creation Command

`scripts/Initialize-BizOpsWorkspace.ps1` owns the folder list and also creates customer folders and README files. For manual setup, create the folders shown in the diagram above.
