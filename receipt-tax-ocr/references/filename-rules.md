# Filename Rules

These filename parts and accounting examples assume Japanese bookkeeping terminology for sole proprietors or side businesses.

## Standard Format

```text
YYYY-MM-DD-content-vendor-note-amount-勘定科目[-メモ].ext
```

## Parts

| Part    | Language | Rule                                | Examples                                                                           |
| ------- | -------- | ----------------------------------- | ---------------------------------------------------------------------------------- |
| Date    | -        | YYYY-MM-DD（サービス利用日）        | 2026-04-04                                                                         |
| Content | English  | Short transaction type              | print, transfer, purchase, transport, subscription, shipping, service, fee, rental |
| Vendor  | English  | Abbreviated company name            | nikko, amazon, adobe, rakutravel                                                   |
| Note    | English  | Event name etc. (optional)          | tbf20, c105                                                                        |
| Amount  | Digits   | No yen sign, no commas              | 155380                                                                             |
| Account | Japanese | Accounting category                 | 印刷費, 事業主借                                                                   |
| Memo    | Japanese | Event name + description (optional) | 技術書典20大阪東京バス                                                             |

## Date Rule

Use the service date（乗車日・購入日・利用日）, not screenshot date or settlement date.

## Content Vocabulary

| English      | Meaning                    |
| ------------ | -------------------------- |
| print        | 印刷・製本                 |
| transfer     | 銀行振込                   |
| purchase     | 物品購入                   |
| transport    | 交通（バス・電車・飛行機） |
| subscription | サブスク・月額サービス     |
| shipping     | 送料・配送                 |
| service      | サービス利用料             |
| fee          | 手数料                     |
| rental       | レンタル・リース           |

## Common Accounting Categories

| Category   | When to use                       |
| ---------- | --------------------------------- |
| 印刷費     | Printing, bookbinding             |
| 外注費     | Outsourced work                   |
| 消耗品費   | Supplies under 100,000 yen        |
| 通信費     | Internet, phone, server           |
| 旅費交通費 | Transportation, accommodation     |
| 新聞図書費 | Books, reference materials        |
| 広告宣伝費 | Advertising, promotion            |
| 支払手数料 | Bank transfer fees etc.           |
| 事業主借   | Reimbursement: private → business |
| 事業主貸   | Personal withdrawal/payment: business → private |
| 雑費       | Anything else                     |

## Cash Withdrawal Classification

| Situation | Accounting and record |
| --------- | --------------------- |
| Cash from an account recorded as business `普通預金`, used privately | `借方: 事業主貸 / 貸方: 普通預金`. Use `事業主貸` in the filename and monthly memo; do not label it `対象外`. |
| Cash retained for business use | `借方: 現金 / 貸方: 普通預金`. |
| Cash used immediately for a documented business cost | Use the actual expense account and retain the supporting receipt. |
| Withdrawal from an unbooked personal account | No bookkeeping entry. Use `対象外` only when preserving the evidence is useful. |
| Source account or use is unknown | Ask the user before renaming or updating the monthly memo. |

## Examples

```text
2026-04-04-print-nikko-tbf20-155380-印刷費.png
2026-04-04-transfer-nikko-155380-事業主借.jpg
2026-04-11-transport-rakutravel-tbf20-8900-旅費交通費-技術書典20大阪東京バス.png
2026-07-26-withdrawal-bank-private-50000-事業主貸-私用現金引出.jpg
```
