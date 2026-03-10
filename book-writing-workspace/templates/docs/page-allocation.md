# Page Allocation and Word Count Targets

Target word counts for each file type and chapter.

## File Type Targets

**1 file = 1 section**

| File Type                | Target (chars) | Range       | Notes                  |
| ------------------------ | -------------- | ----------- | ---------------------- |
| Chapter intro (`ch*-00`) | 300-500        | 200-700     | Chapter overview       |
| Section (`ch*-01~`)      | 3,000-5,000    | 2,000-6,000 | Core section content   |
| Column/sidebar           | 2,000-3,000    | 1,500-3,500 | Supplementary material |

## Chapter Targets

Customize this table for your book:

| Chapter         | Target (chars) | Files | Notes         |
| --------------- | -------------- | ----- | ------------- |
| 0. Introduction | 3,000          | 1     | Book overview |
| 1. Chapter 1    | 20,000         | 5-7   | Customize     |
| 2. Chapter 2    | 20,000         | 5-7   | Customize     |
| 3. Chapter 3    | 20,000         | 5-7   | Customize     |
| 4. Chapter 4    | 20,000         | 5-7   | Customize     |
| 5. Chapter 5    | 20,000         | 5-7   | Customize     |
| 6. Chapter 6    | 20,000         | 5-7   | Customize     |
| 7. Conclusion   | 5,000          | 2-3   | Wrap up       |
| **Total**       | **~130,000**   |       |               |

## Tolerance Rules

| Level        | Tolerance | Action             |
| ------------ | --------- | ------------------ |
| Within range | ±20%      | OK                 |
| Slightly off | ±30%      | Review             |
| Out of range | >30%      | P1 issue, must fix |

## Word Count Check

```bash
python scripts/count_chars.py
```
