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

> Requires workIQ MCP server to be running.

### workIQ Query Examples

**Meetings & Calendar:**

```
# Daily
"List of meetings on {YYYY-MM-DD}. Meeting name, time, duration"

# Weekly
"Meetings from {YYYY}-{MM}-{DD} to {DD}. Include name, time, duration"

# Monthly
"Meetings in {YYYY}-{MM}. Meeting count and total time"
```

**Sent Emails:**

```
# Daily
"Emails I sent on {YYYY-MM-DD}. Subject, time, recipients"

# Weekly
"Email count and main recipients this week"

# Filters
- "External recipients only" - limit to outside organization
- "With attachments only" - identify deliverables
- "Specific recipient: {name}" - customer-focused
```

**Received Emails (To):**

```
# Daily
"Emails addressed to me on {YYYY-MM-DD}. Subject, sender, time"

# Weekly
"Emails addressed to me this week. Prioritize important ones"

# Filters
- "From external only" - limit to outside organization
- "With attachments only" - identify received materials
- "Unread only" - check for missed items
```

**Teams Mentions:**

```
# Daily
"Chats with mentions to me on {YYYY-MM-DD}. Sender, content, reply status"

# Weekly
"Teams mentions to me this week. Prioritize unresponded ones"

# Filters
- "Unresponded only" - check for missed items
- "From specific channel: {name}" - project-focused
- "From specific person: {name}" - manager/customer focus
```

**Teams Posts (My Messages):**

```
# Daily
"Messages I posted in Teams on {YYYY-MM-DD}. Chat name, content, time"

# Weekly
"Messages I posted in Teams this week. Main chats and count"

# Filters
- "Specific chat/channel: {name}" - project-focused
- "With attachments only" - identify shared materials
- "External chats only" - customer communication
```

**Edited Files:**

```
# Daily
"Word, PowerPoint, Excel files edited on {YYYY-MM-DD}"

# Weekly
"Files edited this week. Name, type, last edit time"

# PowerPoint Specific
"PowerPoint files edited on {YYYY-MM-DD}. Name, location"
"PPTX files updated this week and changes"

# OneNote Specific
"OneNote pages updated on {YYYY-MM-DD}. Note name, section, content"
"Frequently edited OneNote sections this week"
```

**Supported File Types:**

- Word (.docx)
- PowerPoint (.pptx)
- Excel (.xlsx)
- PDF (.pdf)
- Loop (.loop)
- Copilot Pages (.page)

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

> Requires Azure AD app registration and API permissions.

### Prerequisites

1. Azure AD App with delegated permissions:
   - `Calendars.Read`
   - `Mail.Read`
   - `Chat.Read`
   - `Files.Read`
   - `Notes.Read`
   - `Tasks.Read`

2. Authentication method:
   - Device code flow (interactive)
   - Client credentials (daemon app)

### PowerShell with Microsoft.Graph

```powershell
# Install module
Install-Module Microsoft.Graph -Scope CurrentUser

# Connect (interactive)
Connect-MgGraph -Scopes "Calendars.Read","Mail.Read","Chat.Read"

# Get calendar events
Get-MgUserCalendarEvent -UserId "me" -Filter "start/dateTime ge '{start}' and end/dateTime le '{end}'"

# Get sent emails
Get-MgUserMessage -UserId "me" -Filter "sentDateTime ge {start}" | Where-Object { $_.From.EmailAddress.Address -eq $env:USERNAME }

# Get Teams chats (mentions require parsing)
Get-MgUserChat -UserId "me" | ForEach-Object {
    Get-MgUserChatMessage -UserId "me" -ChatId $_.Id -Filter "createdDateTime ge {start}"
}
```

### Example: Export Today's Meetings

```powershell
$today = (Get-Date).ToString("yyyy-MM-dd")
$tomorrow = (Get-Date).AddDays(1).ToString("yyyy-MM-dd")

$events = Get-MgUserCalendarEvent -UserId "me" `
    -Filter "start/dateTime ge '${today}T00:00:00' and start/dateTime lt '${tomorrow}T00:00:00'"

$events | Select-Object Subject, @{N='Start';E={$_.Start.DateTime}}, @{N='Duration';E={
    $start = [DateTime]$_.Start.DateTime
    $end = [DateTime]$_.End.DateTime
    ($end - $start).TotalMinutes
}} | Format-Table
```

### Power Automate Alternative

For non-developers, use Power Automate flows to:

1. Trigger daily at 6 PM
2. Get today's calendar events, sent emails
3. Format as Markdown
4. Save to OneDrive folder (synced to workspace)

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

---

## External Folder Sync Settings

### Environment Variables (Recommended)

Use environment variables to handle path differences between users:

```powershell
# Absorb user-specific path differences
$env:BIZ_OPS_ONEDRIVE = "C:\Users\{username}\OneDrive - {org}"
$env:BIZ_OPS_CUSTOMER_FOLDER = "$env:BIZ_OPS_ONEDRIVE\Customers"
```

### Target File Patterns

| Pattern               | Content            | Destination                 |
| --------------------- | ------------------ | --------------------------- |
| `_inbox/{YYYY-MM}.md` | Customer info      | `Customers/{id}/_inbox/`    |
| `_meetings/*.md`      | Meeting notes      | `Customers/{id}/_meetings/` |
| `*_議事録.md`         | Meeting notes (JP) | `Customers/{id}/_meetings/` |
| `AGENTS.md`           | Workspace overview | Reference only              |

### Sync Mode Options

| Mode    | Behavior                         |
| ------- | -------------------------------- |
| `merge` | Append new sections (diff merge) |
| `copy`  | Full copy (overwrite)            |

### Update Detection Rules

1. Check file `LastWriteTime`
2. Compare with last check timestamp
3. Extract diff by section (`## {date}` headers)
4. Append only new sections

### Auto Task Extraction Patterns

| Pattern          | Action                     |
| ---------------- | -------------------------- |
| `📌 **TODO**:`   | Add to Tasks/active.md     |
| `⚠️ **注意**:`   | Add with priority "medium" |
| `🔲` (unchecked) | Notify as task candidate   |

---

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

---

## Query Best Practices

### Date Specification

```markdown
# ✅ Good (specific dates)

"Meetings on 2026-01-27"
"Meetings from 2026-01-19 to 2026-01-23"

# ❌ Bad (ambiguous)

"Recent meetings"
"Last time's meeting"
```

### Output Format

```markdown
# ✅ Good (format specified)

"Display meeting name, time, duration as a list"
"Include subject, send time, recipients"

# ❌ Bad (no format)

"Tell me about meetings"
```

### Filtering

```markdown
# ✅ Good (conditions specified)

"External recipients only"
"Emails with attachments only"
"Meetings related to {customer name}"

# ❌ Bad (all items)

"Show me all emails"
```

---

## Limitations

| Limit           | Description                | Workaround                         |
| --------------- | -------------------------- | ---------------------------------- |
| Item count      | ~100 items per query       | Split period into multiple queries |
| Email body      | Summary only               | Identify by subject and recipient  |
| Historical data | Recommended within 90 days | Use workspace data for older items |
| Real-time       | Slight delay               | Retrieve today's data in evening   |

---

## Security & Privacy

- workIQ retrieves data **within existing access permissions only**
- Cannot retrieve others' emails or files
- Retrieved data used for report generation only
- Mask sensitive information in reports appropriately
