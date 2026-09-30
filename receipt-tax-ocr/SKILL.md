---
name: receipt-tax-ocr
description: "Organize receipt images and subscription invoice/receipt PDFs for Japanese sole-proprietor or side-business bookkeeping: extract evidence, rename files, and update monthly memos. Use for 領収書, レシート, receipt, OCR, リネーム, 確定申告, 勘定科目, 経費, subscription receipts, or payment-method change history. For company/D365 travel expenses, use receipt-expense-workflow."
argument-hint: "Receipt files or service, period, payment-method change, and save scope"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Receipt Tax OCR

## When To Use

- **領収書**, **レシート**, **receipt**, **OCR**, **リネーム**
- 日本の個人事業・副業の経費整理をしているとき
- 領収書フォルダで作業しているとき
- 画像ファイルをOCRしてリネームしたいとき
- Retrieve subscription invoices/receipts or identify when payments switched to a business card
- 確定申告準備で経費整理をしているとき

## Core Rules

- **Account unclear** → Ask the user, do not guess
- **Context affecting the account is missing** → Ask before renaming or updating the memo when the recipient name, the relationship to that person, or the business purpose is unclear. These change the account (e.g. 接待交際費 / 会議費 / 事業主貸). Never infer them from vendor or amount alone.
- **Scope** → The default examples assume Japanese bookkeeping and Japanese tax-filing terminology
- **Filename format** → Use `YYYY-MM-DD-content-vendor-note-amount-勘定科目[-メモ].ext`
- **Date** → Use the documented service date (subscription period start), not screenshot date or settlement date; record conflicting history/PDF dates in the memo.
- **Evidence priority when values conflict** → Trust EXIF first, then the existing filename, then the OCR result, and use the file timestamp only as a last resort. The file timestamp shifts on copy, sync, and re-save, so never let it override a date visible in the receipt.
- **Private card payment** → Keep the actual business expense account on the receipt; record personal funding as 事業主借 separately from the expense and any later reimbursement. Payment method alone does not establish business purpose.
- **Payment-method change** → Confirm the business card's last four digits and inspect each transaction's paid receipt; the current default card does not prove past payments. Confirm which periods to save before a batch.
- **Personal withdrawal from booked business account** → Use `借方: 事業主貸 / 貸方: 普通預金`, never `対象外`; include the source account and journal entry in the monthly memo.
- **Cash withdrawal source or use unclear** → Ask whether the source is a booked business `普通預金` and whether the cash was for private or business use before renaming or updating the memo.
- **Amount** → Preserve the displayed tax-inclusive amount and currency; do not invent a JPY total or mistake a tax-only JPY display for the total.
- **Multiple categories** → Use the primary one, hint at others in note
- **Only surviving evidence is non-expense** → Cart screens, canceled bookings, and other non-expense screenshots should not be treated as 補助画像 when they are the only remaining evidence. Record them in the monthly memo table as `対象外` with amount and reason.
- **Multiple items in one image** → When one screenshot contains multiple products, tickets, books, or shipping supplies, keep one file but add item-by-item breakdown notes in the monthly memo.

## Procedure

1. Identify local receipt files or the requested service, period, and save scope
2. Extract native PDF text before OCR; extract date, vendor, amount, currency, and transaction type
3. Determine the accounting category, asking the user if unclear
4. Present a rename/move dry-run, obtain confirmation, then execute using the standard format
5. Create or update the monthly memo file
6. Show a summary table of old → new filenames

## References

- Filename parts, vocabulary, category examples, and sample outputs: [references/filename-rules.md](references/filename-rules.md)
- Monthly memo rules and `対象外` / 補助画像 handling: [references/monthly-memo.md](references/monthly-memo.md)
- Payment-method history, foreign-currency subscriptions, and PDF matching: [references/subscription-receipts.md](references/subscription-receipts.md)
