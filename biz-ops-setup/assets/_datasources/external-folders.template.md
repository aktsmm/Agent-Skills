# External Folder Reference Configuration

> Reference external folders and auto-check for updates during report generation

---

## Overview

Monitor folders outside the workspace and sync updated files automatically.

---

## Root Folder

```
<!-- Configure your root folder path -->
<!-- Example: C:\Users\{user}\OneDrive - Microsoft\{path} -->
```

---

## Folder Structure and Customer Mapping

### Transaction (One-time projects)

| Folder | Customer ID | Customer Name |
| ------ | ----------- | ------------- |
| `{folder_name}` | `{customer_id}` | {Customer Name} |

### Ongoing Projects

| Folder | Customer ID | Customer Name | Notes |
| ------ | ----------- | ------------- | ----- |
| `{folder_name}` | `{customer_id}` | {Customer Name} | {notes} |

---

## Reference Folders (Detail)

| Customer ID | Folder Path | Target Files |
| ----------- | ----------- | ------------ |
| `{id}` | `{path}` | `_inbox/*.md`, `_meetings/*.md` |

---

## Check Target Files

| File Pattern | Content | Sync To |
| ------------ | ------- | ------- |
| `_inbox/{YYYY-MM}.md` | Customer info accumulation | `Customers/{id}/_inbox/` |
| `_meetings/*.md` | Meeting notes | `Customers/{id}/_meetings/` |
| `*_議事録.md` | Meeting notes (alt format) | `Customers/{id}/_meetings/` |
| `AGENTS.md` | Workspace overview | Reference only |

---

## Sync Workflow

### Auto-check Timing

1. **On report generation**: Before daily/weekly/monthly report creation
2. **Manual trigger**: "Check external folders" command

### Process Flow

```mermaid
graph TD
    A[Start Report Gen] --> B[Check External Folders]
    B --> C{Updates?}
    C -->|Yes| D[Read Files]
    D --> E[Extract Diff]
    E --> F[Append to Customers/{id}/_inbox/]
    F --> G[Extract Tasks]
    G --> H[Update Tasks/active.md]
    C -->|No| I[Skip]
    H --> J[Continue Report Gen]
    I --> J
```

---

## Customer Configuration Example

```yaml
customer_id: {id}
customer_name: {Customer Name}
external_folder: {absolute_path}
sync_targets:
  - source: _inbox/{YYYY-MM}.md
    destination: Customers/{id}/_inbox/{YYYY-MM}.md
    mode: merge  # Diff merge
  - source: _meetings/*.md
    destination: Customers/{id}/_meetings/
    mode: copy   # Copy
check_frequency: on_report_generation
last_checked: {YYYY-MM-DD}
```

---

## Update Detection Rules

### Diff Detection

1. Check external file `LastWriteTime`
2. If newer than last check, read content
3. Extract diff by section (`## {date}` header delimiter)
4. Append only new sections to workspace

### Auto Task Extraction

Detect and create tasks from these patterns:

| Pattern | Action |
| ------- | ------ |
| `📌 **TODO**:` | Add to Tasks/active.md |
| `⚠️ **Warning**:` | Add with priority "Medium" |
| `🔲` (unchecked) | Notify as task candidate |

---

## Commands

```
# Manual check external folders
"Check external folders"

# Check specific customer only
"Check {customer} folder"

# Check all customers
"Sync all customer folders"
```

---

## Adding New Customer

To add a new customer folder:

1. Add configuration to this file
2. Create `Customers/{id}/` folder (if not exists)
3. Run initial sync

---

## Notes

- **OneDrive sync**: Files must be synced locally
- **Path changes**: Use environment variables if paths differ by user
- **Large files**: Binary files (PowerPoint, etc.) are reference only (no content extraction)

---

## Environment Variables (Optional)

```powershell
# Absorb path differences per user
$env:BIZ_OPS_ONEDRIVE = "C:\Users\{username}\OneDrive - Microsoft"
$env:BIZ_OPS_EXTERNAL = "$env:BIZ_OPS_ONEDRIVE\{folder}"
```
