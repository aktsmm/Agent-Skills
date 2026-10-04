# External Data Source Configuration

## Overview

Configuration for data sources referenced during report generation.
Supports multiple retrieval methods: workIQ (M365), manual input, and API integration.

---

## Data Sources & Retrieval Methods

| Data Source             | workIQ | Manual | Graph API | Priority |
| ----------------------- | ------ | ------ | --------- | -------- |
| 📅 Meetings & Calendar  | ✅     | ✅     | ✅        | ⭐⭐⭐   |
| ✉️ Sent Emails          | ✅     | ✅     | ✅        | ⭐⭐⭐   |
| 📥 Received Emails (To) | ✅     | ✅     | ✅        | ⭐⭐     |
| 💬 Teams Mentions       | ✅     | ✅     | ✅        | ⭐⭐⭐   |
| 💬 Teams Posts          | ✅     | ✅     | ✅        | ⭐⭐     |
| 📄 Edited Files         | ✅     | ❌     | ✅        | ⭐⭐     |
| 📊 PowerPoint Updates   | ✅     | ❌     | ✅        | ⭐⭐     |
| 📝 OneNote              | ✅     | ✅     | ✅        | ⭐       |
| 💬 Teams Meeting Notes  | ✅     | ✅     | ❌        | ⭐⭐     |
| 📋 Planner/To Do        | ✅     | ✅     | ✅        | ⭐       |

### Retrieval Priority

```
1. workIQ (if available) → Automatic, natural language
2. Manual input → Copy & paste from source
3. Graph API → Script-based automation (requires setup)
```

---

## Method 1: workIQ (M365 Integration)

Requires the workIQ MCP server. Query templates per source and report type, query best practices, limits, error handling, and fallback are owned by `assets/_datasources/workiq-spec.template.md` (deployed to `_datasources/workiq-spec.md`). Missing workIQ data is not evidence of no activity.

---

## Method 2: Manual Input (No workIQ)

> Works without any special setup. Copy & paste from source applications.

### Teams Chat/Mentions

```markdown
# Paste into \_inbox/{YYYY-MM}.md or Customers/{id}/\_inbox/

## {YYYY-MM-DD} Teams

### From: {sender name}

{paste message content}

### Action Items

- [ ] {extracted action}
```

### Outlook Emails

```markdown
# Forward to yourself, then copy to \_inbox/

## {YYYY-MM-DD} Email

**From:** {sender}
**Subject:** {subject}
**Summary:** {brief summary}

### Key Points

- {point 1}
- {point 2}
```

### Teams Meeting Notes

```markdown
# Copy AI-generated notes from Teams meeting

## {YYYY-MM-DD} {Meeting Name}

### Attendees

- {list}

### Summary

{AI summary or manual notes}

### Decisions

- {decision 1}

### Action Items

- [ ] {action} @{assignee}
```

### Calendar Events

```markdown
# Export from Outlook or manually list

## {YYYY-MM-DD} Meetings

| Time        | Meeting        | Duration |
| ----------- | -------------- | -------- |
| 10:00-11:00 | {meeting name} | 1h       |
| 14:00-15:30 | {meeting name} | 1.5h     |
```

---

## Method 3: Graph API (Automation)

- Use a Microsoft Entra app registration (or the Microsoft Graph PowerShell SDK's own app) with delegated scopes such as `Calendars.Read`, `Mail.Read`, `Chat.Read`, `Files.Read`, `Notes.Read`, and `Tasks.Read`; connect interactively with `Connect-MgGraph -Scopes ...`.
- App-only (client credentials) needs application permissions and admin consent and reads every mailbox it is granted; do not use it for one person's activity report.
- Tenant policy may block these scopes; treat a consent or Conditional Access failure as unavailable data, not as zero activity.
- For non-developers, a scheduled Power Automate flow can export the day's calendar and sent mail as Markdown to a synced folder.

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

### 3. Deploy report-generator

`Deploy-BizOpsTemplates.ps1` deploys `assets/agents/report-generator.agent.template.md`. The agent reads `_datasources/external-paths.md` during report generation, runs each configured check command, and adds an "External Updates" section.

### 4. Update copilot-instructions

Add external data source references to the data source table (uncomment template section).

---

## External Folder Sync, Check Commands, and Output

Sync modes, update detection, auto task extraction, and per-user path variables are owned by `assets/_datasources/external-folders.template.md`. Git and file-system check commands are owned by `assets/external-paths.template.md`. Report external results as a table of source, this-period count, and total.
