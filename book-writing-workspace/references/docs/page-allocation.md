# Page Allocation and Word Count Targets

Target word counts for each file type and chapter.

---

## File Type Targets

| File Type                     | Target (chars) | Range       | Notes          |
| ----------------------------- | -------------- | ----------- | -------------- |
| Chapter intro (`*-0-00_*.md`) | 300-500        | 200-700     | Brief overview |
| Main section                  | 3,000-5,000    | 2,000-6,000 | Core content   |
| Column/sidebar                | 2,000-3,000    | 1,500-3,500 | Supplementary  |

---

## Chapter Targets

Customize this table for your book:

| Chapter         | Target (chars) | Files | Notes         |
| --------------- | -------------- | ----- | ------------- |
| 0. Introduction | 3,000          | 1     | Book overview |
| 1. Chapter 1    | 20,000         | 5-7   | (customize)   |
| 2. Chapter 2    | 20,000         | 5-7   | (customize)   |
| 3. Chapter 3    | 20,000         | 5-7   | (customize)   |
| 4. Chapter 4    | 20,000         | 5-7   | (customize)   |
| 5. Chapter 5    | 20,000         | 5-7   | (customize)   |
| 6. Chapter 6    | 20,000         | 5-7   | (customize)   |
| 7. Conclusion   | 5,000          | 2-3   | Wrap up       |
| **Total**       | **~130,000**   |       |               |

---

## Tolerance Rules

| Level           | Tolerance | Action             |
| --------------- | --------- | ------------------ |
| ✅ Within range | ±20%      | OK                 |
| ⚠️ Slightly off | ±30%      | Review             |
| ❌ Out of range | >30%      | P1 issue, must fix |

---

## Word Count Check

Run the character counter script:

```bash
python scripts/count_chars.py
```

Or for a specific chapter:

```bash
python scripts/count_chars.py 02_contents/1.\ Chapter\ 1/
```

---

## Adjustment Guidelines

### Too Short

- Add examples or case studies
- Expand explanations
- Include more context

### Too Long

- Split into subsections
- Move details to appendix
- Create separate column
- Tighten prose

---

## Column Allocation

- **Max 2 columns per section** (reader attention)
- Columns are optional (not every section needs one)

### Check columns:

```powershell
Get-ChildItem -Recurse -Filter "*[Column]*" | Group-Object { $_.Directory.Name }
```
