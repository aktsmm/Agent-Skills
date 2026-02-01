# External Data Sources

Configuration for external folders referenced during report generation.

---

## Configuration

| Data Source                                    | Path                                                | Purpose                                             | Check Method                              |
| ---------------------------------------------- | --------------------------------------------------- | --------------------------------------------------- | ----------------------------------------- |
| <!-- Example: Tech QA Repository -->           | <!-- C:\Users\{user}\repos\{repo-name} -->          | <!-- PR count, QA responses by project -->          | <!-- Git log / File modification date --> |
| <!-- Example: Blog Folder -->                  | <!-- D:\{blog-folder} -->                           | <!-- Published blog article count -->               | <!-- New files / Modification date -->    |
| <!-- Example: Customer Projects (OneDrive) --> | <!-- C:\Users\{user}\OneDrive\{customer-folder} --> | <!-- Customer materials and deliverable updates --> | <!-- Folder modification date -->         |

---

## Check Commands

### Git Repository

```powershell
# Get commits for target period
git -C "{path}" log --since="{start date}" --until="{end date}" --oneline --pretty=format:"%h - %s"

# Count PRs or commits
git -C "{path}" log --since="{start date}" --until="{end date}" --oneline | Measure-Object | Select-Object -ExpandProperty Count
```

### File System

```powershell
# List updated files in target period
Get-ChildItem -Path "{path}" -Recurse -File |
  Where-Object { $_.LastWriteTime -ge (Get-Date "{start date}") -and $_.LastWriteTime -le (Get-Date "{end date}") } |
  Select-Object FullName, LastWriteTime

# Count updated files
Get-ChildItem -Path "{path}" -Recurse -File |
  Where-Object { $_.LastWriteTime -ge (Get-Date "{start date}") } |
  Measure-Object | Select-Object -ExpandProperty Count
```

---

## Usage in report-generator

This file is automatically referenced by `report-generator.agent.md` during report generation.

### Integration Flow

1. Report generation triggered (daily/weekly/monthly)
2. report-generator reads this file
3. Executes check commands for each data source
4. Includes results in activity summary section

---

## Notes

- Update paths after OneDrive sync or folder relocation
- Use absolute paths to avoid path resolution issues
- Git repositories must be valid (initialized with `.git/`)
