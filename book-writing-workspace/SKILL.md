---
name: book-writing-workspace
description: Set up a reusable book-writing workspace with AI agents, instructions, prompts, and scripts. Use when creating a new book or technical writing project, bootstrapping a manuscript repository, or preparing a Markdown + Re:VIEW + PDF workflow. Triggers on "book writing workspace", "technical book project", "執筆ワークスペース", "book manuscript repo", and "Re:VIEW workspace".
argument-hint: "本のテーマ、原稿リポジトリ名、使いたい執筆フロー"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Book Writing Workspace

Create and maintain a reusable manuscript workspace with folders, agents, prompts, instructions, setup scripts, and a repeatable Markdown -> Re:VIEW -> PDF workflow.

## When to use

- **Book writing**, **technical writing**, **執筆プロジェクト**, **Re:VIEW**
- Creating a new book or technical writing project
- Bootstrapping a manuscript repository from templates
- Setting up Markdown → Re:VIEW → PDF workflow
- Upgrading an existing manuscript workspace so it can generate Re:VIEW output and printable PDFs
- Standardizing PDF house style, title pages, running headers, side markers, metadata, and review output folders across multiple books in the same repo
- Standardizing metadata layers, cover assets, series title patterns, and cover typography across multiple books in the same repo

## Quick Start

```powershell
python scripts/setup_workspace.py `
    --name "project-name" `
    --title "Book Title" `
    --path "D:\target\path" `
    --chapters 8
```

## Existing Workspace Upgrade

When the workspace already exists, do not stop at setup-oriented advice. This skill should also support:

1. Creating or normalizing `03_re-view_output/`
2. Converting existing manuscript Markdown into `.re`
3. Building PDF with Docker + `vvakame/review`
4. Applying shared house style defaults and a metadata layer for title page, cover image, colophon, and project-specific book metadata
5. Verifying both the intermediate `.re` output and the final PDF

## Setup Workflow

1. **Gather info**: Project name, title, location, chapter count
2. **Run script**: `scripts/setup_workspace.py`
3. **Review output**: Confirm README, agents, prompts, and docs were created
4. **Customize**: Edit `docs/page-allocation.md`, `docs/schedule.md`, `.github/copilot-instructions.md`, and `config/review-metadata/project.yml`

Metadata, migration, converter verification, and sync-back rules live in references. Keep the main SKILL focused on setup and operating flow.

## Generated Workspace

- Manuscript folders under `01_contents_keyPoints/`, `02_contents/`, and `04_images/`
- AI workflow files under `.github/agents/`, `.github/instructions/`, and `.github/prompts/`
- Project docs such as `README.md`, `docs/page-allocation.md`, and `docs/schedule.md`
- Helper scripts such as `scripts/count_chars.py`, `scripts/convert_md_to_review.py`, `scripts/build_review_pdf.py`, `scripts/inspect_pdf.py`, and `scripts/review_metadata.py`
- Re:VIEW metadata templates such as `config/review-metadata/common.yml` and `config/review-metadata/project.yml`

## Recommended Writing Unit

- Use **1 file = 1 section** as the default manuscript unit.
- Keep chapter intro in `ch{N}-00_<title>.md` and section files in `ch{N}-01_...`, `ch{N}-02_...`.
- For PDF/Re:VIEW output, heading levels define hierarchy, while file split mainly improves authoring and review workflow.

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

## Reference Map

| Topic                | Reference                                                                |
| -------------------- | ------------------------------------------------------------------------ |
| Folder structure     | [references/folder-structure.md](references/folder-structure.md)         |
| Setup workflow       | [references/setup-workflow.md](references/setup-workflow.md)             |
| Customization points | [references/customization-points.md](references/customization-points.md) |
| Re:VIEW / PDF tips   | [references/review-pdf-tips.md](references/review-pdf-tips.md)           |

## Done Criteria

- [ ] Workspace folder structure created
- [ ] 4 agents deployed to `.github/agents/`
- [ ] `docs/page-allocation.md` configured
- [ ] `README.md` and `docs/schedule.md` customized
- [ ] `/gc_Commit` prompt working
- [ ] `config/review-metadata/common.yml` and `project.yml` customized appropriately
- [ ] `03_re-view_output/` can regenerate `.re` files
- [ ] PDF build works on a clean run
