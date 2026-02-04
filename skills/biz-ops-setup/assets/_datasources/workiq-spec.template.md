# workIQ Data Retrieval Specification

Specification for data retrieval from workIQ (Microsoft 365 Copilot) for report generation.

> **Note**: workIQ integration is OPTIONAL. If unavailable, the system falls back to workspace data.

## Overview

Use `mcp_workiq_ask_work_iq` tool to automatically retrieve data from Microsoft 365.

---

## 1. Available Data Sources

### 1.1 📅 Meetings/Calendar (Priority: ⭐⭐⭐)

**Retrievable Information**:

- Meeting name
- Date/time (start/end)
- Attendance duration
- Participants
- Teams link

**Query Examples**:

```
# Daily
"List of meetings on {YYYY-MM-DD}. Include meeting name, time, duration"

# Weekly
"List of meetings from {YYYY-MM-DD} to {YYYY-MM-DD}"

# Monthly
"List of meetings in {YYYY}-{MM}. Include meeting name, time, duration"
```

---

### 1.2 ✉️ Sent Emails (Priority: ⭐⭐⭐)

**Retrievable Information**:

- Subject
- Send date/time
- Recipients
- (Body summary)

**Query Examples**:

```
# Daily
"List of emails I sent on {YYYY-MM-DD}. Include subject, time, recipient"

# Weekly
"Emails I sent this week. Include subject and recipient"

# Monthly
"Count and main recipients of emails sent in {YYYY}-{MM}"
```

**Filter Options**:

- "External only" - External recipients only
- "With attachments" - Material deliveries
- "To {customer}" - Specific customer

---

### 1.3 📥 Received Emails (To me) (Priority: ⭐⭐)

**Query Examples**:

```
"List of emails addressed to me on {YYYY-MM-DD}. Include subject, sender, time"
"Unread emails addressed to me" - Check for missed items
```

---

### 1.4 💬 Teams Mentions (Priority: ⭐⭐⭐)

**Retrievable Information**:

- Source chat/channel
- Who mentioned
- Message content
- Date/time
- Reply status

**Query Examples**:

```
"Chats with mentions to me on {YYYY-MM-DD}. Include sender, content, reply status"
"Unreplied mentions to me this week"
```

---

### 1.5 💬 Teams Posts (My messages) (Priority: ⭐⭐)

**Query Examples**:

```
"Messages I posted in Teams on {YYYY-MM-DD}. Include chat name, content, time"
"My Teams posts this week with reaction counts"
```

---

### 1.6 📄 Edited Files (Priority: ⭐⭐)

**Retrievable Information**:

- File name
- Type (Word/Excel/PowerPoint/PDF)
- Last edit time
- Location (OneDrive/SharePoint)

**Query Examples**:

```
# General
"Word, PowerPoint, Excel files I edited on {YYYY-MM-DD}"

# PowerPoint specific
"PowerPoint files I edited on {YYYY-MM-DD}. Include filename, location"

# OneNote specific
"OneNote pages I updated on {YYYY-MM-DD}. Include note name, section"
```

**Supported File Types**:

- Word (.docx)
- PowerPoint (.pptx)
- Excel (.xlsx)
- PDF (.pdf)
- Loop (.loop)
- Copilot Pages

---

### 1.7 💬 Teams Meeting Notes (Priority: ⭐⭐)

**Query Examples**:

```
"Meeting notes from {meeting name}"
"Decisions and action items from today's meetings"
"AI transcript from {meeting name}"
```

---

### 1.8 📋 Tasks (Planner/To Do) (Priority: ⭐)

**Query Examples**:

```
"Tasks I completed today"
"Tasks due this week"
"My Planner tasks status"
```

---

## 2. Query Procedures by Report Type

### 2.1 Daily Report Generation

```
Step 1: Get meeting data
  Query: "Meetings on {date}. Include name, time, duration"

Step 2: Get sent emails
  Query: "Emails I sent on {date}. Include subject, time, recipient"

Step 3: Get edited files
  Query: "Word/PowerPoint/Excel files I edited on {date}"

Step 4: Get Teams meeting notes (key meetings only)
  Query: "Decisions and action items from {meeting name}"

Step 5: Get mentions
  Query: "Mentions to me on {date}. Include content, reply status"

Step 6: Get OneNote (optional)
  Query: "OneNote I updated on {date}"
```

### 2.2 Weekly Report Generation

```
Step 1: Aggregate from daily reports (if exist)
  Path: ActivityReport/{YYYY-MM}/daily/{dates}.md

Step 2: Get meeting data (for days without daily reports)
  Query: "Meetings from {start} to {end}"

Step 3: Get sent email summary
  Query: "Count and main recipients of emails I sent this week"

Step 4: Get edited files summary
  Query: "Files I edited this week"

Step 5: Get key meeting notes
  Query: "Key decisions from this week's meetings"
```

### 2.3 Monthly Report Generation

```
Step 1: Aggregate from weekly reports (if exist)
  Path: ActivityReport/{YYYY-MM}/weekly/*.md

Step 2: Get monthly meeting summary
  Query: "Meeting count and total hours for {month}"

Step 3: Get monthly email summary
  Query: "Email count and main recipients for {month}"

Step 4: Get monthly file summary
  Query: "Files I edited in {month}"
```

---

## 3. Query Best Practices

### 3.1 Date Specification

```markdown
# ✅ Good (specific dates)

"Meetings on 2026-01-27"
"Meetings from 2026-01-20 to 2026-01-24"

# ❌ Bad (ambiguous)

"Recent meetings"
"Meetings from a while ago"
```

### 3.2 Output Format Specification

```markdown
# ✅ Good (format specified)

"List with meeting name, time, duration"
"Include subject, time, recipient"

# ❌ Bad (no format)

"Show meetings"
```

### 3.3 Filtering

```markdown
# ✅ Good (with conditions)

"External emails only"
"Emails with attachments only"
"Meetings about {customer}"

# ❌ Bad (fetch all)

"Show all emails"
```

---

## 4. Error Handling

### 4.1 Query Failure

```
If workIQ query fails:
  1. Supplement with workspace data
  2. Supplement with estimates (mark as [Estimated])
  3. Note retrieval failure in report
```

### 4.2 Insufficient Data

```
If data is insufficient:
  1. Use "hidden tasks" to reach 8 hours
  2. Mark all estimates as [Estimated]
  3. Note data shortage
```

---

## 5. Limitations

| Limitation      | Description             | Workaround                         |
| --------------- | ----------------------- | ---------------------------------- |
| Item count      | ~100 items per query    | Split period into multiple queries |
| Body retrieval  | Summary only for emails | Judge by subject and recipient     |
| Historical data | ~90 days recommended    | Use workspace data for older       |
| Real-time       | Slight delay            | Get today's data in evening        |

---

## 6. Security & Privacy

- workIQ retrieves data only **within existing access permissions**
- Cannot retrieve others' emails or files
- Retrieved data used only for report generation
- Mask confidential information appropriately in reports

---

## 7. Fallback Behavior

When workIQ is unavailable:

1. **Primary**: Use workspace data (`_inbox/`, `Tasks/`, `Customers/`)
2. **Secondary**: Use external data sources (`_datasources/external-paths.md`)
3. **Tertiary**: Mark sections as "Data unavailable - manual input needed"

The system should function without workIQ, with reduced automation.
