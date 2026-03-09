# Setup Workflow

Use the setup script to create a new manuscript workspace from the bundled templates.

## Command

```powershell
python scripts/setup_workspace.py `
    --name "project-name" `
    --title "Book Title" `
    --path "D:\target\path" `
    --chapters 8
```

## Main Options

| Option             | Meaning                                              |
| ------------------ | ---------------------------------------------------- |
| `--name`           | Folder name for the new workspace                    |
| `--title`          | Human-readable book title                            |
| `--path`           | Parent directory where the workspace will be created |
| `--chapters`       | Number of generated chapter folders                  |
| `--chapter-titles` | Explicit chapter names instead of defaults           |
| `--no-review`      | Skip `03_re-view_output/`                            |
| `--no-materials`   | Skip `99_material/`                                  |

## What Gets Generated

1. Folder structure for outlines, drafts, images, docs, and output
2. Agent, instruction, and prompt files under `.github/`
3. Project docs such as `README.md`, `docs/page-allocation.md`, and `docs/schedule.md`
4. Helper scripts such as `scripts/count_chars.py` and `scripts/convert_md_to_review.py`
5. Initial chapter intro files in both outline and manuscript folders

## Post-Setup Checks

1. Open the generated `README.md` and confirm project metadata
2. Edit `docs/page-allocation.md` to fit the book length
3. Edit `docs/schedule.md` to replace placeholder dates
4. Adjust `.github/copilot-instructions.md` for the target audience and goals
