---
name: book-writing-workspace
description: Set up a complete book writing workspace with AI agents, instructions, prompts, and scripts. Use when users want to create a new book/technical writing project with Markdown + Re:VIEW + PDF output workflow. Triggers on "book writing workspace", "technical book project", "執筆ワークスペース", or similar project setup requests.
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Book Writing Workspace

Set up a professional book writing workspace with AI-assisted workflow support.

## When to use

- **Book writing**, **technical writing**, **執筆プロジェクト**
- Creating a new book or technical writing project
- Setting up Markdown → Re:VIEW → PDF workflow
- Establishing multi-chapter document structure with AI agent support

## Setup Workflow

### Step 1: Gather Project Information

Ask the user for project configuration:

```
Book Writing Workspace Setup

Please provide the following information:

1. **Project Name** (folder name, e.g., "my-book-project")
2. **Book Title** (e.g., "Introduction to Cloud Security")
3. **Target Location** (e.g., "D:\projects\")
4. **Chapter Structure** - Choose one:
   - [ ] Standard (8 chapters: Intro → 6 main → Conclusion)
   - [ ] Custom (specify chapter titles)
5. **Include Re:VIEW output?** (for PDF generation)
   - [ ] Yes (requires Docker + Re:VIEW setup)
   - [ ] No (Markdown only)
6. **Include reference materials folder?**
   - [ ] Yes
   - [ ] No
```

### Step 2: Create Directory Structure

Run the setup script with gathered information:

```powershell
# Setup workspace with the collected project configuration
python scripts/setup_workspace.py `
    --name "project-name" `
    --title "Book Title" `
    --path "D:\target\path" `
    --chapters 8 `
    --include-review `
    --include-materials
```

### Step 3: Customize Configuration

After setup, guide the user to customize:

1. **Edit `docs/page-allocation.md`** - Set target word counts per chapter
2. **Edit `.github/copilot-instructions.md`** - Update book-specific overview
3. **Review agent configurations** in `.github/agents/`

## Generated Structure

```
{project-name}/
├── .github/
│   ├── agents/               # AI agent definitions
│   │   ├── writing.agent.md
│   │   ├── writing-reviewer.agent.md
│   │   ├── converter.agent.md
│   │   └── orchestrator.agent.md
│   ├── instructions/         # Writing guidelines
│   │   ├── writing/
│   │   │   ├── writing.instructions.md
│   │   │   ├── writing-heading.instructions.md
│   │   │   └── writing-notation.instructions.md
│   │   └── git/
│   │       └── commit-format.instructions.md
│   ├── prompts/              # Reusable prompts
│   │   ├── gc_Commit.prompt.md
│   │   ├── gcp_Commit_Push.prompt.md
│   │   └── gpull.prompt.md
│   └── copilot-instructions.md
├── 01_contents_keyPoints/    # Outlines and key points
│   └── {chapter folders}/
├── 02_contents/              # Final manuscripts
│   └── {chapter folders}/
├── 03_re-view_output/        # Re:VIEW source and PDF output (optional)
│   ├── output_re/
│   ├── output_pdf/
│   └── images/
├── 04_images/                # Image assets
│   └── {chapter folders}/
├── 99_material/              # Reference materials (optional)
│   ├── 01_contracts/
│   ├── 02_proposals/
│   └── 03_references/
├── docs/
│   ├── writing-guide.md      # Workflow guide
│   ├── naming-conventions.md # File naming rules
│   ├── page-allocation.md    # Word count targets
│   └── schedule.md           # Project schedule
├── scripts/
│   ├── count_chars.py        # Character counter
│   └── convert_md_to_review.py (optional)
├── .gitignore
├── AGENTS.md
└── README.md
```

## Agents Overview

| Agent               | Role                            | Permissions               |
| ------------------- | ------------------------------- | ------------------------- |
| `@writing`          | Write and edit manuscripts      | Edit `02_contents/`       |
| `@writing-reviewer` | Review manuscripts (P1/P2/P3)   | Read only                 |
| `@converter`        | Convert Markdown to Re:VIEW     | Edit `03_re-view_output/` |
| `@orchestrator`     | Coordinate multi-agent workflow | Delegate to other agents  |

## Prompts Overview

| Prompt             | Usage                             |
| ------------------ | --------------------------------- |
| `/gc_Commit`       | Git commit with formatted message |
| `/gcp_Commit_Push` | Git commit and push               |
| `/gpull`           | Git pull with change summary      |

## Customization Points

### Chapter Structure

Default 8-chapter structure:

```
0. Introduction
1-6. Main Chapters (customizable titles)
7. Conclusion
8. Glossary (optional)
```

### Word Count Targets

Configurable in `docs/page-allocation.md`:

| File Type      | Default Target    | Range      |
| -------------- | ----------------- | ---------- |
| Chapter intro  | 300-500 chars     | Adjustable |
| Main section   | 3,000-5,000 chars | Adjustable |
| Column/sidebar | 2,000-3,000 chars | Adjustable |

### File Naming Convention

Pattern: `{prefix}-{chapter}-{section}-{number}_{title}.md`

Example: `01-1-a-00_Introduction_to_Topic.md`

## Resources

| Directory     | Contents                                         |
| ------------- | ------------------------------------------------ |
| `scripts/`    | Setup and utility scripts                        |
| `references/` | Template files for agents, instructions, prompts |
| `assets/`     | Static files (.gitignore templates, etc.)        |

## Post-Setup Actions

After workspace creation:

1. **Initialize Git** (commented example):

   ```bash
   # Initialize repository and create the first commit
   git init && git add . && git commit -m "Initial commit"
   ```

2. **Open in VS Code** (commented example):

   ```bash
   # Open the project in VS Code
   code {project-path}
   ```

3. **Test prompts**: Try `/gc_Commit` to verify setup
4. **Start writing**: Create key points in `01_contents_keyPoints/`

## Dependencies

| Tool        | Purpose           | Required |
| ----------- | ----------------- | -------- |
| Python 3.8+ | Scripts           | Yes      |
| Git         | Version control   | Yes      |
| Docker      | Re:VIEW PDF build | Optional |
| Re:VIEW     | PDF generation    | Optional |
