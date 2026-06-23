---
name: receipt-ocr
description: "個人事業・副業・確定申告専用。日本の勘定科目（印刷費 / 事業主借 等）で領収書画像を OCR してリネームし、月次メモを整える。D365 / 出張経費は d365-expense-sorter を使う。Use when: 領収書, レシート, receipt, OCR, リネーム, 確定申告, 勘定科目, 経費, rename."
argument-hint: "OCRしたい画像やリネーム指示"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Receipt OCR & Rename Skill

## When To Use

- **領収書**, **レシート**, **receipt**, **OCR**, **リネーム**
- 日本の個人事業・副業の経費整理をしているとき
- 領収書フォルダで作業しているとき
- 画像ファイルをOCRしてリネームしたいとき
- 確定申告準備で経費整理をしているとき

## Core Rules

- **Account unclear** → Ask the user, do not guess
- **Scope** → The default examples assume Japanese bookkeeping and Japanese tax-filing terminology
- **Filename format** → Use `YYYY-MM-DD-content-vendor-note-amount-勘定科目[-メモ].ext`
- **Date** → Use the service date, not screenshot date or settlement date
- **Private card payment** → The receipt itself uses the real expense account (e.g. 印刷費); the reimbursement transfer uses 事業主借
- **Amount** → Use the displayed amount as-is (tax-inclusive)
- **Multiple categories** → Use the primary one, hint at others in note
- **Only surviving evidence is non-expense** → Cart screens, canceled bookings, and other non-expense screenshots should not be treated as 補助画像 when they are the only remaining evidence. Record them in the monthly memo table as `対象外` with amount and reason.
- **Multiple items in one image** → When one screenshot contains multiple products, tickets, books, or shipping supplies, keep one file but add item-by-item breakdown notes in the monthly memo.

## Procedure

1. Check the current directory for image files
2. OCR each image and extract date, vendor, amount, and transaction type
3. Determine the accounting category, asking the user if unclear
4. Rename files using the standard format
5. Create or update the monthly memo file
6. Show a summary table of old → new filenames

## References

- Filename parts, vocabulary, category examples, and sample outputs: [references/filename-rules.md](references/filename-rules.md)
- Monthly memo rules and `対象外` / 補助画像 handling: [references/monthly-memo.md](references/monthly-memo.md)
