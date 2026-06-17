# D365 Expense Guide

Receipt OCR Sorter でリネームしたファイルを D365 Finance Expense Report に載せるための運用ガイド。

## Country Codes

| コード | 国             |
| ------ | -------------- |
| jpn    | 日本           |
| us     | アメリカ       |
| cn     | 中国           |
| gb     | イギリス       |
| sg     | シンガポール   |
| kr     | 韓国           |
| au     | オーストラリア |
| xx     | 不明           |

## Receipt Categories

| 分類             | 日本語             | トリガーキーワード              |
| ---------------- | ------------------ | ------------------------------- |
| shinkansen       | 新幹線             | 新幹線, のぞみ, ひかり, EX予約  |
| hotel            | 宿泊               | ホテル, HOTEL, MARRIOTT, HILTON |
| airline          | 航空               | ANA, JAL, DELTA, UNITED         |
| transport        | 交通               | TRANSIT, METRO, Suica, PASMO    |
| taxi             | タクシー           | TAXI, UBER, LYFT                |
| meal-starbucks   | 食費（スタバ）     | STARBUCKS                       |
| meal-restaurant  | 食費（レストラン） | RESTAURANT, DINING              |
| meal-convenience | 食費（コンビニ）   | 7-ELEVEN, LAWSON, FAMILYMART    |
| meal-supermarket | 食費（スーパー）   | COSTCO, WHOLE FOODS, SAFEWAY    |
| meal             | 食費               | MEAL, LUNCH, DINNER             |
| seminar          | セミナー           | SEMINAR, CONFERENCE             |
| shopping         | 買い物             | AMAZON, APPLE STORE             |

## D365 Category Mapping

| OCR分類        | D365 Expense Category         | 備考                     |
| -------------- | ----------------------------- | ------------------------ |
| shinkansen     | Ground Transportation         | 国内鉄道全般             |
| hotel          | Hotel                         |                          |
| airline        | Airfare \| International      | 国際線。国内線は Airfare |
| transport      | Ground Transportation         | 電車・バス等             |
| taxi           | Ground Transportation \| Taxi |                          |
| meal-\*        | Meals \| Employee Travel      | 全食費サブカテゴリ共通   |
| seminar        | Admin Services - Misc.        |                          |
| shopping       | Admin Services - Misc.        |                          |
| esim / telecom | Internet/Online Fees - Travel | eSIM・通信費             |

## Attach Receipt

1. Expense line を選択する
2. `Receipts` セクションの `Edit` を押す
3. `Add receipts` -> `Browse` でリネーム済みファイルを選ぶ
4. `Upload` -> `OK` -> `Close`

## Replace Receipt

1. `Receipts` の `Edit` を開く
2. 誤レシートを選択して `Remove`
3. 正しいファイルを `Add receipts` で再アップロード
4. `Close` -> `Save and continue`

## Mandatory Matching Checks

添付や差し替えの前に、以下を必ず照合する。

| チェック項目 | 照合対象                                    |
| ------------ | ------------------------------------------- |
| 金額         | ファイル名の金額 ≒ 経費行の Amount          |
| 日付         | ファイル名の日付 ≒ 経費行の Date            |
| マーチャント | ファイル名の分類 / 店名 ∈ 経費行の Merchant |

不一致のまま添付すると監査で差し戻されやすい。

## Change Category

1. Expense line を選択して `Edit`
2. Category コンボボックスへカテゴリ名を入力
3. `Tab` で確定して `Close`

## Browser Automation Note

D365 のブラウザ操作は MCP Playwright tools (`browser_type` / `browser_click` / `browser_snapshot`) が安定しやすい。Playwright 直接スクリプトは動的 DOM で壊れやすい。
