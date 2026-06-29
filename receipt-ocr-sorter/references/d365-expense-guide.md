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

### Line-Level Receipt Matching

D365 は report-level receipt と line-level receipt を別に扱う。report header の `Receipts = Yes` だけでは完了にせず、各 expense line の `Receipts attached = Yes` を確認する。

1. 1つの receipt を選択する
2. `Attach to expense` を押す
3. 候補一覧で、金額・日付・merchant が一致する1行の `+` だけを押す
4. 右下の選択済みリストに対象行が1件だけ入ったことを確認する
5. `Next` で確定する
6. Expense lines に戻り、その行の `Receipts attached = Yes` を確認する

`+` を複数回押して右下リストへ複数行が増えた場合は誤紐付けの可能性がある。`Next` へ進まず、余分な行を外してから続ける。

## Replace Receipt

1. `Receipts` の `Edit` を開く
2. 誤レシートを選択して `Remove`
3. 確認ダイアログが出たら、対象ファイル名を再確認してから `Yes`
4. 正しいファイルが report-level に既にある場合は `Add receipts` -> `Select existing` -> 対象ファイルを1件だけ選択 -> `Add`
5. 正しいファイルが未アップロードの場合だけ `Add receipts` -> `Add new` でアップロード
6. `Close` -> `Save and continue`

既存 receipt 一覧には古い同名・近似名・別案件の候補が混在することがある。ファイル名、金額、用途が一致する1件だけを選び、同じ receipt を複数行へ誤って残さない。

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

### Required Line Fields

Expense line は1行単位で、以下を全部そろえてから保存する。部分保存や高速連続操作は、validation や別フィールドへの誤入力を起こしやすい。

| 項目                 | 期待値                                 |
| -------------------- | -------------------------------------- |
| 新幹線カテゴリ       | `Ground Transportation`                |
| タクシーカテゴリ     | `Ground Transportation \| Taxi`        |
| Country/region       | `JPN`                                  |
| Currency             | `JPY`                                  |
| Item sales tax group | 通常 `2J`                              |
| Description          | 目的、交通手段、区間、金額が分かる短文 |

`Country/region` と `Item sales tax group` は別項目。`JPN` を税グループへ入れてしまった場合は `2J` に戻してから保存する。

Description は実態を推測して書かない。顧客訪問、出張先、イベント名、会議名などは、ユーザー提供の文脈を正として反映し、曖昧なら保存前に確認する。

## Browser Automation Note

D365 のブラウザ操作は MCP Playwright tools (`browser_type` / `browser_click` / `browser_snapshot`) が安定しやすい。Playwright 直接スクリプトは動的 DOM で壊れやすい。

### Async UI Gotchas

- checkbox 選択と右ペインの active row は別物。編集前に Amount / Merchant / date-category が対象行と一致することを screenshot または DOM で確認する
- `fastEditRailsMode`、`ShellBlockingDiv`、`Your last action is still being worked on` が見える間は次の操作へ進まない。Wait / overlay 消失 / 値反映を確認する
- 右ペインの receipt summary は stale になり得る。line-level の証跡検証は Expense lines の `Receipts attached`、必要なら該当行の Receipts Edit の file name で確認する
- receipt 差し替え後の正本確認は、右ペイン summary ではなく該当行の `Receipts` -> `Edit` に表示される `File name` で行う。summary が前行や古い添付を表示することがある
- Document Type は既存 receipt 一覧で編集できないことがある。画像 receipt はアップロード時に `Image` を選択し、アップロード後は File name と Notes を主証跡として確認する
- receipt 修正中は `Submit` を進捗確認や保存代わりに押さない。明示指示がない限り、保存は `Save and continue` までに留める
