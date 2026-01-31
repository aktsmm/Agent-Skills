# Holiday Configuration

## Overview

Configuration to skip holidays during report generation.
Daily reports are not generated on holidays.

## Supported Countries

| Country | File                 | Notes            |
| ------- | -------------------- | ---------------- |
| Japan   | `japan-holidays.md`  | Default          |
| USA     | `us-holidays.md`     | Federal holidays |
| Custom  | `custom-holidays.md` | Manual setup     |

## Japan Holidays (2026)

```markdown
# 日本の祝日 2026

| 日付       | 祝日名       |
| ---------- | ------------ |
| 2026-01-01 | 元日         |
| 2026-01-13 | 成人の日     |
| 2026-02-11 | 建国記念の日 |
| 2026-02-23 | 天皇誕生日   |
| 2026-03-20 | 春分の日     |
| 2026-04-29 | 昭和の日     |
| 2026-05-03 | 憲法記念日   |
| 2026-05-04 | みどりの日   |
| 2026-05-05 | こどもの日   |
| 2026-05-06 | 振替休日     |
| 2026-07-20 | 海の日       |
| 2026-08-11 | 山の日       |
| 2026-09-21 | 敬老の日     |
| 2026-09-22 | 国民の休日   |
| 2026-09-23 | 秋分の日     |
| 2026-10-12 | スポーツの日 |
| 2026-11-03 | 文化の日     |
| 2026-11-23 | 勤労感謝の日 |
```

## US Holidays (2026)

```markdown
# US Federal Holidays 2026

| Date       | Holiday                     |
| ---------- | --------------------------- |
| 2026-01-01 | New Year's Day              |
| 2026-01-19 | Martin Luther King Jr. Day  |
| 2026-02-16 | Presidents' Day             |
| 2026-05-25 | Memorial Day                |
| 2026-06-19 | Juneteenth                  |
| 2026-07-03 | Independence Day (observed) |
| 2026-09-07 | Labor Day                   |
| 2026-10-12 | Columbus Day                |
| 2026-11-11 | Veterans Day                |
| 2026-11-26 | Thanksgiving Day            |
| 2026-12-25 | Christmas Day               |
```

## Setup Process

1. Select country during initial interview
2. Copy corresponding file to `_workiq/`
3. Save as `_workiq/{country}-holidays.md`

## Reference During Report Generation

```
1. Check if target date is included in holiday table
2. If included → Skip
3. For weekly/monthly reports, exclude holidays from working days
```

## Data Collection vs Report Generation

| Operation             | Target Period       | Weekend/Holiday Handling |
| --------------------- | ------------------- | ------------------------ |
| **Data Collection**   | All days, all hours | All included             |
| **Report Generation** | Business days only  | Holidays skipped         |

### Data Collection Policy

All activities, including those outside business hours, are recorded for the following reasons:

- **Flexible remote work** - Activities may occur at non-traditional hours
- **Time zone coordination** - International collaboration across time zones
- **Emergency response** - On-call duties and urgent issues
- **Self-development** - Technical blogging, OSS contributions, learning activities

By recording all activities, work inventory and analysis can accurately reflect the true scope of work, including weekend deployments, after-hours support, and personal development efforts.

### Important Distinction

- **Holidays in the table** affect report _generation_ (skip creating reports on holidays)
- **Data retrieval** from workIQ always includes all days and times
- **Weekly/monthly reports** summarize data from all days, but only count business days for metrics
