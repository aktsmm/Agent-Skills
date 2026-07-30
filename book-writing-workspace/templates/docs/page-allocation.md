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

## Estimated vs Actual Pages

Character-count estimates run high. Do not decide chapter splits or large cuts from an estimate alone.

- A rough conversion such as 1,000 chars = 1 page overstated a real B5 build by roughly 11 percent in one project: 223 estimated pages against 198 actual.
- That gap moved one chapter from "P1, over budget by 61 percent" to "within tolerance at 25 percent", and dropped the whole-book overrun from 25 percent to 8 percent. The structural rework it implied was never needed.
- Build the PDF and measure before escalating a page-budget overrun. Treat the estimate as an early-draft signal only, and note in the review record which number is which.

## Word Count Check

```bash
python scripts/count_chars.py
```
