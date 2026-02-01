# Case Assignment Master

> Master data for linking case management system with tasks
> Last Updated: {YYYY-MM-DD}

---

## Usage

- Extract information from case assignment notifications (email, system alerts)
- Reference this master's Case ID when recording tasks

---

## Active Cases

| Customer Name | Case ID | Request ID | Solution Area | Assigned Date | Task Link                              |
| ------------- | ------- | ---------- | ------------- | ------------- | -------------------------------------- |
| Example Corp  | 12345   | REQ-001    | Area A        | 2026-01-01    | [Tasks](../Customers/example/tasks.md) |

---

## Past Cases (Last 12 Months)

| Customer Name | Case ID | Request ID | Solution Area | Assigned Date | Notes |
| ------------- | ------- | ---------- | ------------- | ------------- | ----- |

---

## Case URL Format

```
https://your-case-system.example.com/cases/view/{Case_ID}
```

Example: `https://your-case-system.example.com/cases/view/12345`

---

## Customer ID Mapping

| Case System Customer Name | Customer ID | Folder             |
| ------------------------- | ----------- | ------------------ |
| Example Corporation       | example     | Customers/example/ |

---

## Update Flow (MANDATORY)

> ⚠️ **Important**: Always update this master when new case is assigned.
> Unregistered cases will be missing from daily reports.

**Triggers**:

- Assignment notification email received
- New customer case started
- New case detected via workIQ

**Update Steps**:

1. Add to "Active Cases" table
2. Required: Customer Name, Case ID, Request ID, Solution Area, Assigned Date
3. If customer ID mapping missing, add to "Customer ID Mapping" section
4. If customer folder (`Customers/{id}/`) doesn't exist, consider creating

**Check Timing**:

- Check last update date before daily report generation
- Show warning if no updates in past 7 days

---

## Integration with Reports

When generating reports, cross-reference tasks with this master:

1. Detect customer name in task
2. Look up Case ID from this master
3. Include in report: `Case: {Case_ID} | Request: {Request_ID}`

---

## Update History

- {YYYY-MM-DD}: Initial creation
