# External Data Source Configuration

## Overview

Configuration for data sources referenced during report generation.
Automatic retrieval from workIQ (M365) and reference to folders outside the workspace.

---

## workIQ Data Sources (M365 Integration)

List of data sources available via workIQ MCP server.

| Data Source             | Priority | Purpose                                  |
| ----------------------- | -------- | ---------------------------------------- |
| 📅 Meetings & Calendar  | ⭐⭐⭐   | Attended meetings, time, duration        |
| ✉️ Sent Emails          | ⭐⭐⭐   | Emails sent by you                       |
| 📥 Received Emails (To) | ⭐⭐     | Emails received addressed to you         |
| 💬 Teams Mentions       | ⭐⭐⭐   | Mentions directed to you, reply status   |
| � Teams Posts           | ⭐⭐     | Messages posted by you                   |
| �📄 Edited Files        | ⭐⭐     | Word/Excel/PDF edit history              |
| 📊 PowerPoint Updates   | ⭐⭐     | PPTX edit history (explicitly retrieved) |
| 📝 OneNote              | ⭐       | Note updates, sections                   |
| 💬 Teams Meeting Notes  | ⭐⭐     | AI meeting minutes, decisions            |
| 📋 Planner/To Do        | ⭐       | Task completion                          |

### workIQ Query Examples

```
# Daily
"List of meetings on {target date}. Meeting name, time, duration"
"List of emails received addressed to me on {target date}. Subject, sender"
"Chats with mentions to me on {target date}. Content, reply status"
"List of PowerPoint files edited on {target date}"
"OneNote updated on {target date}. Note name, section"

# Weekly
"Teams mentions to me in {target week}. Prioritize unresponded ones"
"Frequently edited OneNote sections in {target week}"
```

---

## External Folder Configuration

### 1. Collect via Interview

During setup, ask the following:

```
Please specify external folders to reference during report generation.

- Technical QA repository
- Blog folder
- Customer project folders (OneDrive, etc.)
```

### 2. Record in Configuration File

**Use template:** `assets/external-paths.template.md`

```powershell
# Copy template to workspace
Copy-Item assets/external-paths.template.md _datasources/external-paths.md
```

**Fill in paths from interview:**

```markdown
# External Data Sources

| Data Source        | Path                                       | Purpose                | Check Method      |
| ------------------ | ------------------------------------------ | ---------------------- | ----------------- |
| Tech QA Repository | C:\Users\{user}\repos\{repo-name}          | PR count, QA responses | Git log           |
| Blog Folder        | D:\{blog-folder}                           | Published articles     | File modification |
| Customer Projects  | C:\Users\{user}\OneDrive\{customer-folder} | Deliverables           | Folder update     |
```

### 3. Deploy report-generator with Integration

**Use template:** `assets/report-generator.agent.template.md`

```powershell
# Copy template to workspace
Copy-Item assets/report-generator.agent.template.md .github/agents/report-generator.agent.md
```

**Integration features:**

- Automatic read of `_datasources/external-paths.md` during report generation
- Execute check commands for each configured source
- Include results in "External Updates" section

### 4. Update copilot-instructions

Add external data source references to the data source table (uncomment template section).

## Check Query Examples

### MS Learn QA

```powershell
# Get commits/changes for target period
git -C "{path}" log --since="{start date}" --until="{end date}" --oneline

# Count PRs (estimated from file count)
Get-ChildItem -Path "{path}" -Recurse -File |
  Where-Object { $_.LastWriteTime -ge "{start date}" } |
  Measure-Object
```

### Qiita Blog

```powershell
# New/updated articles for target period
Get-ChildItem -Path "{path}" -Recurse -Include "*.md" |
  Where-Object { $_.LastWriteTime -ge "{start date}" }
```

### Customer Project Folders

```powershell
# Updated files by customer
Get-ChildItem -Path "{path}" -Recurse |
  Where-Object { $_.LastWriteTime -ge "{start date}" } |
  Group-Object { Split-Path (Split-Path $_.FullName -Parent) -Leaf }
```

## Output Example

Include in report with following format:

```markdown
### External Activity Results

| Source         | This Period | Total |
| -------------- | ----------- | ----- |
| MS Learn QA PR | 3           | 15    |
| Qiita Blog     | 1           | 8     |
| Customer Docs  | 5           | -     |
```
