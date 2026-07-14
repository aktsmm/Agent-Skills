# Setup Workflow

Use the setup script to create a new manuscript workspace from the bundled templates.

## Command

```powershell
python scripts/setup_workspace.py `
    --name "project-name" `
    --title "Book Title" `
    --path "D:\target\path" `
    --chapters 8

# Add Re:VIEW/PDF support only when the project needs it.
python scripts/setup_workspace.py `
    --name "project-name" `
    --title "Book Title" `
    --path "D:\target\path" `
    --chapters 8 `
    --with-review
```

## Main Options

| Option             | Meaning                                              |
| ------------------ | ---------------------------------------------------- |
| `--name`           | Folder name for the new workspace                    |
| `--title`          | Human-readable book title                            |
| `--path`           | Parent directory where the workspace will be created |
| `--chapters`       | Number of generated chapter folders                  |
| `--chapter-titles` | Explicit chapter names instead of defaults           |
| `--with-review`    | Add optional Re:VIEW/PDF scaffolding                 |
| `--with-materials` | Add `materials/references/`                          |
| `--no-materials`   | Skip `materials/`                                    |

## What Gets Generated

1. Folder structure for outlines, drafts, images, docs, and optional output
2. Writing/review agents and writing instructions under `.github/`
3. Project docs such as `README.md`, `docs/reader-personas.md`, `docs/page-allocation.md`, and `docs/schedule.md`
4. Helper scripts such as `scripts/count_chars.py`
5. Initial chapter intro files in both outline and manuscript folders
6. Optional Re:VIEW/PDF scripts and metadata when `--with-review` is used

## Post-Setup Checks

1. Open the generated `README.md` and confirm project metadata
2. Replace all placeholders in `docs/reader-personas.md`
3. Edit `docs/page-allocation.md` to fit the book length
4. Edit `docs/schedule.md` to replace placeholder dates
5. Adjust `.github/copilot-instructions.md` for project goals and constraints
