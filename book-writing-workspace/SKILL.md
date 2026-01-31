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

## Quick Start

```powershell
python scripts/setup_workspace.py `
    --name "project-name" `
    --title "Book Title" `
    --path "D:\target\path" `
    --chapters 8
```

## Setup Workflow

1. **Gather info**: Project name, title, location, chapter count
2. **Run script**: `scripts/setup_workspace.py`
3. **Customize**: Edit `docs/page-allocation.md` and `.github/copilot-instructions.md`

## Agents Overview

| Agent               | Role                          | Permissions               |
| ------------------- | ----------------------------- | ------------------------- |
| `@writing`          | Write and edit manuscripts    | Edit `02_contents/`       |
| `@writing-reviewer` | Review manuscripts (P1/P2/P3) | Read only                 |
| `@converter`        | Convert Markdown to Re:VIEW   | Edit `03_re-view_output/` |
| `@orchestrator`     | Coordinate workflow           | Delegate to agents        |

## Dependencies

| Tool        | Purpose           | Required |
| ----------- | ----------------- | -------- |
| Python 3.8+ | Scripts           | Yes      |
| Git         | Version control   | Yes      |
| Docker      | Re:VIEW PDF build | Optional |

## Done Criteria

- [ ] Workspace folder structure created
- [ ] 4 agents deployed to `.github/agents/`
- [ ] `docs/page-allocation.md` configured
- [ ] `/gc_Commit` prompt working

## Key References

| Topic            | Reference                                                                |
| ---------------- | ------------------------------------------------------------------------ |
| Folder Structure | [references/folder-structure.md](references/folder-structure.md)         |
| Agents           | [references/AGENTS.md](references/AGENTS.md)                             |
| Instructions     | [references/copilot-instructions.md](references/copilot-instructions.md) |
