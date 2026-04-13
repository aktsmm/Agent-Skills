---
name: book-writing-workspace
description: Set up a reusable book-writing workspace with AI agents, instructions, prompts, and scripts. Use when creating a new book or technical writing project, bootstrapping a manuscript repository, or preparing a Markdown + Re:VIEW + PDF workflow. Triggers on "book writing workspace", "technical book project", "執筆ワークスペース", "book manuscript repo", and "Re:VIEW workspace".
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Book Writing Workspace

Create a reusable manuscript workspace with folders, agents, prompts, instructions, and setup scripts.

## When to use

- **Book writing**, **technical writing**, **執筆プロジェクト**, **Re:VIEW**
- Creating a new book or technical writing project
- Bootstrapping a manuscript repository from templates
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
3. **Review output**: Confirm README, agents, prompts, and docs were created
4. **Customize**: Edit `docs/page-allocation.md`, `docs/schedule.md`, and `.github/copilot-instructions.md`

## Generated Workspace

- Manuscript folders under `01_contents_keyPoints/`, `02_contents/`, and `04_images/`
- AI workflow files under `.github/agents/`, `.github/instructions/`, and `.github/prompts/`
- Project docs such as `README.md`, `docs/page-allocation.md`, and `docs/schedule.md`
- Helper scripts such as `scripts/count_chars.py` and `scripts/convert_md_to_review.py`

## Recommended Writing Unit

- Use **1 file = 1 section** as the default manuscript unit.
- Keep chapter intro in `ch{N}-00_<title>.md` and section files in `ch{N}-01_...`, `ch{N}-02_...`.
- For PDF/Re:VIEW output, heading levels define hierarchy, while file split mainly improves authoring and review workflow.

## Migration Checklist (Path / Naming Changes)

When reorganizing workspace paths or file naming rules, update these together:

1. Docs: `docs/naming-conventions.md`, `docs/page-allocation.md`, `docs/writing-guide.md`
2. Instructions: `templates/instructions/writing-*.instructions.md` (`applyTo` and examples)
3. Scripts: `templates/scripts/count_chars.py`, `templates/scripts/convert_md_to_review.py`
4. Agent docs: `templates/agents/*.agent.md` if paths are explicitly written

Then verify with:

- `python scripts/count_chars.py`
- `python scripts/convert_md_to_review.py`

## Converter Change Verification

When changing the Markdown-to-Re:VIEW converter or related templates:

1. Regenerate `.re` files first with `python scripts/convert_md_to_review.py`
2. Rebuild the final PDF, not just the intermediate `.re` output
3. Inspect both a representative `.re` snippet and the final PDF when the change affects footnotes, tables, images, captions, or line breaking
4. If the change affects running headers, side markers, or odd/even page layout, verify that `texdocumentclass` uses `twoside`; `oneside` disables odd/even-specific `fancyhdr` placement
5. If a note semantically belongs to a table, attach the footnote marker in prose immediately before or after the table rather than inside table cells or table headers
6. When checking visual PDF changes, compare against the newly archived/timestamped PDF or the updated file timestamp; some viewers keep showing a cached file when the output name stays the same
7. If footnotes cluster at the chapter end in the PDF, check that `//footnote` definitions in the `.re` file are placed near their references, not all appended at chapter end. Also confirm no `//footnote` sits inside a `//table{...//}` or `===[column]...===[/column]` block (causes `Counter too large` build failure)

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
- [ ] `README.md` and `docs/schedule.md` customized
- [ ] `/gc_Commit` prompt working

## Key References

| Topic            | Reference                                                                |
| ---------------- | ------------------------------------------------------------------------ |
| Folder Structure | [references/folder-structure.md](references/folder-structure.md)         |
| Setup Workflow   | [references/setup-workflow.md](references/setup-workflow.md)             |
| Customization    | [references/customization-points.md](references/customization-points.md) |
| Re:VIEW PDF Tips | [references/review-pdf-tips.md](references/review-pdf-tips.md)           |
