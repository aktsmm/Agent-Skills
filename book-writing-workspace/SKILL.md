---
name: book-writing-workspace
description: "Operate a reusable technical book manuscript workspace with writing structure, review rules, and optional Markdown to Re:VIEW/PDF support. Use when organizing a book manuscript repo, standardizing chapter/section files, setting writing/review agents, or assessing an existing writing workspace. Triggers on book writing workspace, technical book project, 執筆ワークスペース, manuscript workflow, and Re:VIEW workspace."
argument-hint: "本のテーマ、原稿リポジトリ名、使いたい執筆フロー"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Book Writing Workspace

Create and maintain a reusable manuscript workspace with folders, writing agents, instructions, review rules, and optional Markdown -> Re:VIEW -> PDF support.

## When to use

- **Book writing**, **technical writing**, **執筆プロジェクト**, **Re:VIEW**
- Assessing or standardizing an existing book manuscript repository
- Creating a new technical writing project from templates when needed
- Setting up Markdown → Re:VIEW → PDF workflow
- Upgrading an existing manuscript workspace so it can generate Re:VIEW output and printable PDFs
- Standardizing chapter/section file layout, writing rules, review workflow, and page allocation
- Adding optional Re:VIEW/PDF support without turning the writing workspace into a general Git or publishing operations toolkit

## Quick Start

Start by assessing the manuscript workspace, even when creating a new project:

1. Confirm the main manuscript lives in `02_contents/` and uses one file per section.
2. Confirm outlines or key points live separately from final manuscript files.
3. Confirm chapter intro files use `ch*-00_*.md` and section files start at `ch*-01_*.md`.
4. Confirm writing, heading, notation, page allocation, and review rules are available.
5. Decide whether Re:VIEW/PDF output is needed for this project; keep it optional unless the workflow requires it.

## Operating Workflow

When the workspace already exists, do not stop at setup-oriented advice. This skill should also support:

1. Normalizing manuscript folders and section naming.
2. Keeping outlines, drafts, final manuscript, and images aligned by chapter.
3. Running focused writing and review loops until P1/P2 issues are resolved.
4. Checking word count targets and source confidence before finalizing text.
5. Enabling Re:VIEW/PDF support only when the project needs reproducible output.

## Bootstrap Workflow

Use the setup script only when creating a new workspace or adding missing structure deliberately.

```powershell
python scripts/setup_workspace.py `
  --name "project-name" `
  --title "Book Title" `
  --path "D:\target\path" `
  --chapters 8

# Include Re:VIEW/PDF scaffolding only when needed.
python scripts/setup_workspace.py `
  --name "project-name" `
  --title "Book Title" `
  --path "D:\target\path" `
  --chapters 8 `
  --with-review
```

1. **Gather info**: Project name, title, location, chapter count
2. **Run script**: `scripts/setup_workspace.py`
3. **Review output**: Confirm README, agents, instructions, and docs were created
4. **Customize**: Edit `docs/page-allocation.md`, `docs/schedule.md`, and `.github/copilot-instructions.md`. If `--with-review` is used, also customize `config/review-metadata/project.yml`.

Git workflows are project-specific. Do not add generic commit/push prompts here; follow the repository's existing version-control conventions.

Metadata, migration, converter verification, and sync-back rules live in references. Keep the main SKILL focused on manuscript structure and writing workflow.

## Generated Workspace

- Manuscript folders under `01_contents_keyPoints/`, `02_contents/`, and `04_images/`
- AI workflow files under `.github/agents/` and `.github/instructions/`
- Project docs such as `README.md`, `docs/page-allocation.md`, and `docs/schedule.md`
- Helper scripts such as `scripts/count_chars.py`
- Optional Re:VIEW scripts and metadata when `--with-review` is used

## Recommended Writing Unit

- Use **1 file = 1 section** as the default manuscript unit.
- Keep chapter intro in `ch{N}-00_<title>.md` and section files in `ch{N}-01_...`, `ch{N}-02_...`.
- For PDF/Re:VIEW output, heading levels define hierarchy, while file split mainly improves authoring and review workflow.

## Agents Overview

| Agent               | Role                          | Default |
| ------------------- | ----------------------------- | ------- |
| `@writing`          | Write and edit manuscripts    | Yes     |
| `@writing-reviewer` | Review manuscripts (P1/P2/P3) | Yes     |
| `@converter`        | Convert Markdown to Re:VIEW   | Only with `--with-review` |

## Dependencies

| Tool        | Purpose           | Required |
| ----------- | ----------------- | -------- |
| Python 3.8+ | Scripts           | Yes      |
| Git         | Version control   | Yes      |
| Docker      | Re:VIEW PDF build | Optional, only with `--with-review` |

## Reference Map

| Topic                | Reference                                                                |
| -------------------- | ------------------------------------------------------------------------ |
| Folder structure     | [references/folder-structure.md](references/folder-structure.md)         |
| Setup workflow       | [references/setup-workflow.md](references/setup-workflow.md)             |
| Customization points | [references/customization-points.md](references/customization-points.md) |
| Re:VIEW / PDF tips   | [references/review-pdf-tips.md](references/review-pdf-tips.md)           |

## Done Criteria

- [ ] Workspace folder structure created
- [ ] Writing and review agents deployed to `.github/agents/`
- [ ] `docs/page-allocation.md` configured
- [ ] `README.md` and `docs/schedule.md` customized
- [ ] Manuscript files follow the chapter/section naming convention
- [ ] `scripts/count_chars.py` works for target manuscript files
- [ ] Re:VIEW/PDF output is either explicitly out of scope or enabled and verified
