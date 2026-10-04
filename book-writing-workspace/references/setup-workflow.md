# Setup Workflow

Use the setup script to create a new manuscript workspace from the bundled templates.

## Command

```powershell
python scripts/setup_workspace.py `
    --name "project-name" `
    --title "Book Title" `
    --path "<parent-dir>" `
    --chapters 8
# Append --with-review only when the project needs Re:VIEW/PDF output.
```

## Main Options

| Option             | Meaning                                                             |
| ------------------ | ------------------------------------------------------------------- |
| `--name`           | Folder name for the new workspace                                   |
| `--title`          | Human-readable book title                                           |
| `--path`           | Parent directory where the workspace will be created                |
| `--chapters`       | Number of generated chapter folders                                 |
| `--chapter-titles` | Explicit chapter names instead of defaults                          |
| `--with-review`    | Add optional Re:VIEW/PDF scaffolding (`--no-review` is the default) |
| `--with-materials` | Add `materials/references/`                                         |
| `--no-materials`   | Skip `materials/`                                                   |

## What Gets Generated

See Generated Workspace in [SKILL.md](../SKILL.md). Initial chapter intro files are created in both the outline and manuscript folders.

## Post-Setup Checks

1. Open the generated `README.md` and confirm project metadata
2. Replace all placeholders in `docs/reader-personas.md`
3. Edit `docs/page-allocation.md`, `docs/schedule.md`, and `.github/copilot-instructions.md` (see [customization-points.md](customization-points.md))
