# Purpose: Incident Report Instructions

Slide creation guide for incident reports and postmortems.

---

## Required Sections

| Section         | Slides | Content                            |
| --------------- | ------ | ---------------------------------- |
| Title           | 1      | Incident name, date, severity      |
| Summary         | 1      | Impact scope, duration, resolution |
| Timeline        | 1-2    | Key events with timestamps         |
| Root Cause      | 1-2    | Technical root cause analysis      |
| Impact          | 1      | Users/systems affected, metrics    |
| Resolution      | 1-2    | Steps taken to resolve             |
| Lessons Learned | 1      | What we learned                    |
| Action Items    | 1      | Preventive measures, owners        |
| Closing         | 1      | Q&A, contact info                  |

---

## Tone Guidelines

- **Factual**: Stick to facts, avoid blame
- **Chronological**: Clear timeline
- **Action-oriented**: Focus on solutions
- **Transparent**: Acknowledge issues honestly

---

## Timeline Format

```
| Time (JST)    | Event                           |
| ------------- | ------------------------------- |
| 09:15         | Monitoring alert triggered      |
| 09:20         | Incident confirmed              |
| 09:45         | Root cause identified           |
| 10:30         | Fix deployed                    |
| 11:00         | Service restored                |
```

---

## Impact Metrics

Include quantitative data:

- **Duration**: X hours Y minutes
- **Users affected**: N users / X% of traffic
- **Error rate**: Increased from X% to Y%
- **SLA impact**: X% → Y%

---

## Action Items Format

| #   | Action                    | Owner    | Due Date   | Status      |
| --- | ------------------------- | -------- | ---------- | ----------- |
| 1   | Add monitoring alerts     | @alice   | 2025-01-20 | In Progress |
| 2   | Update runbook            | @bob     | 2025-01-25 | Not Started |
| 3   | Implement circuit breaker | @charlie | 2025-02-01 | Planned     |

---

## Speaker Notes

For incident reports, notes should include:

- Additional technical context
- Related incidents if any
- Discussion points for Q&A
- Links to detailed documentation

---

## Sensitive Information

⚠️ Consider before including:

- Customer names → Anonymize
- Internal system names → Check disclosure policy
- Security vulnerabilities → Limit detail
- Employee names → Use roles instead
