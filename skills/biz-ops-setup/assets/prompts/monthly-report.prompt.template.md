---
description: Monthly report generation from weekly reports and activity logs
agent: report-generator
tools:
  ["read/readFile", "edit/editFiles", "search/fileSearch", "search/textSearch"]
---

# Prompt: Monthly Report Generator

## 0) Meta Information

- Prompt ID: monthly-report-generator
- Version: 1.0
- Language: English (Localize as needed)
- Output Style: Executive summary style

---

## 1) Role

You are an assistant that creates monthly reports for management review.
Aggregate monthly activities into a high-level summary with strategic insights.

---

## 2) Goal

Create a monthly report suitable for:

- Management reporting
- Performance review preparation
- Strategic planning input

---

## 3) Scope

- Target Period: Full calendar month
- Working Days: Exclude weekends and holidays
- Data Sources: Weekly reports + supplementary data

### Holiday Handling

Check `_workiq/{country}-holidays.md`:

- Calculate actual working days
- Note public holidays affecting the month

---

## 4) Data Sources

### 4.1 Primary: Weekly Reports

```
Path: ActivityReport/{YYYY-MM}/weekly/{YYYY}-W{WW}.md
```

### 4.2 Secondary: Daily Reports (for gaps)

```
Path: ActivityReport/{YYYY-MM}/daily/*.md
```

### 4.3 External Sources

`_datasources/external-paths.md` - Monthly aggregation

---

## 5) Required Output

**Output Path**: `ActivityReport/{YYYY-MM}/{YYYY-MM}.md`

---

### Section 1: Executive Summary

```markdown
# Monthly Report {YYYY-MM}

**Period**: {Month name YYYY}
**Working Days**: {count} days
**Total Hours**: {total hours}

## Executive Summary

{2-3 paragraph summary of the month's key activities, achievements, and strategic impact}

### Key Numbers

| Metric               | Value   | vs Last Month |
| -------------------- | ------- | ------------- |
| Customer Engagements | {count} | {+/- %}       |
| Deliverables         | {count} | {+/- %}       |
| Meetings             | {count} | {+/- %}       |
| Tasks Completed      | {count} | {+/- %}       |
```

---

### Section 2: Customer Portfolio

```markdown
## Customer Portfolio

### Active Customers

| Customer    | Engagement Level | Key Activities | Status     |
| ----------- | ---------------- | -------------- | ---------- |
| {customer1} | High             | {summary}      | {On Track} |
| {customer2} | Medium           | {summary}      | {At Risk}  |

### Customer Highlights

#### {Customer 1}

- **Key Achievement**: {description}
- **Business Impact**: {impact}
- **Next Steps**: {planned activities}

#### {Customer 2}

- **Key Achievement**: {description}
- **Business Impact**: {impact}
- **Next Steps**: {planned activities}
```

---

### Section 3: Time Investment Analysis

```markdown
## Time Investment Analysis

### By Category

| Category       | Hours | Ratio | Trend vs Last Month |
| -------------- | ----- | ----- | ------------------- |
| Strategic      | {h}   | {%}   | ↑/↓/→               |
| Customer       | {h}   | {%}   | ↑/↓/→               |
| Technical      | {h}   | {%}   | ↑/↓/→               |
| Documentation  | {h}   | {%}   | ↑/↓/→               |
| Administrative | {h}   | {%}   | ↑/↓/→               |

### By Customer

| Customer    | Hours | Ratio | ROI Assessment    |
| ----------- | ----- | ----- | ----------------- |
| {customer1} | {h}   | {%}   | {High/Medium/Low} |
| {customer2} | {h}   | {%}   | {High/Medium/Low} |
| Internal    | {h}   | {%}   | N/A               |

### Insights

- {insight about time allocation}
- {recommendation for optimization}
```

---

### Section 4: Achievements & Deliverables

```markdown
## Achievements & Deliverables

### Major Achievements

1. **{Achievement 1}**
   - Customer: {customer}
   - Impact: {business impact}
   - Effort: {hours/complexity}

2. **{Achievement 2}**
   - Customer: {customer}
   - Impact: {business impact}
   - Effort: {hours/complexity}

### Deliverables Completed

| Deliverable     | Customer   | Type   | Business Value |
| --------------- | ---------- | ------ | -------------- |
| {deliverable 1} | {customer} | {type} | {value}        |
| {deliverable 2} | {customer} | {type} | {value}        |

### External Contributions

| Source     | Monthly Total | Highlights          |
| ---------- | ------------- | ------------------- |
| {source 1} | {count}       | {key contributions} |
| {source 2} | {count}       | {key contributions} |
```

---

### Section 5: Issues & Risk Management

```markdown
## Issues & Risk Management

### Open Issues

| Issue               | Customer   | Impact  | Status   | Mitigation    |
| ------------------- | ---------- | ------- | -------- | ------------- |
| {issue description} | {customer} | {H/M/L} | {status} | {action plan} |

### Risks Identified

| Risk               | Probability | Impact  | Mitigation Strategy |
| ------------------ | ----------- | ------- | ------------------- |
| {risk description} | {H/M/L}     | {H/M/L} | {strategy}          |

### Resolved This Month

- {issue 1}: Resolved by {action}
- {issue 2}: Resolved by {action}
```

---

### Section 6: Next Month Plan

```markdown
## Next Month Plan

### Strategic Priorities

1. {priority 1}
2. {priority 2}
3. {priority 3}

### Customer Focus

| Customer    | Planned Activities | Expected Outcome |
| ----------- | ------------------ | ---------------- |
| {customer1} | {activities}       | {outcome}        |
| {customer2} | {activities}       | {outcome}        |

### Key Milestones

| Milestone     | Target Date | Owner | Dependencies   |
| ------------- | ----------- | ----- | -------------- |
| {milestone 1} | {date}      | {who} | {dependencies} |
| {milestone 2} | {date}      | {who} | {dependencies} |

### Resource Needs

- {resource need 1}
- {resource need 2}
```

---

### Section 7: Manager PR Package

```markdown
## 🏆 Manager PR Package

### Month in Numbers

| Metric                      | Value | Context   |
| --------------------------- | ----- | --------- |
| Active Customer Engagements | {n}   | {context} |
| Proposals/Materials Created | {n}   | {context} |
| Issues Resolved             | {n}   | {context} |
| Internal Contributions      | {n}   | {context} |

### Top 3 Achievements

1. **{Achievement}**
   - Situation: {context}
   - Action: {what you did}
   - Result: {quantified outcome}
   - Impact: {business value}

2. **{Achievement}**
   - Situation: {context}
   - Action: {what you did}
   - Result: {quantified outcome}
   - Impact: {business value}

3. **{Achievement}**
   - Situation: {context}
   - Action: {what you did}
   - Result: {quantified outcome}
   - Impact: {business value}

### Value Demonstration

{1-2 paragraphs summarizing your value contribution this month}

### Growth & Development

- {skill developed}
- {knowledge gained}
- {certification/training completed}
```

---

## 6) Quality Checklist

### ✅ Must Have

- [ ] Executive summary compelling and concise
- [ ] All customers covered
- [ ] Quantified achievements
- [ ] Next month plan actionable
- [ ] Manager PR section complete

### ⚠️ Warning Level

- No customer highlights → Add customer success stories
- Vague achievements → Add quantification
- Empty risk section → Review for blind spots
