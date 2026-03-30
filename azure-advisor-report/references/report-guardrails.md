# レポート品質ルール

顧客に提示するレポート（Markdown / PowerPoint）生成時に適用するガードレール。

## 社内情報の除外（MANDATORY）

以下を顧客向けレポートに **含めてはならない**:

| 禁止項目             | 例                                     |
| -------------------- | -------------------------------------- |
| 社内ツール名・リンク | 社内専用の分析ツール・ダッシュボード等       |
| 社内用語             | ACR, TPID, TTM 等                      |
| CLI コマンド名       | `az advisor recommendation list` 等    |
| データソース詳細     | 「Cost Management API (ActualCost)」等 |
| 社内 URL             | 社内専用ポータルの URL 等                 |
| 社内専用分析データ   | 社内ツールの Focus Areas 等 |

**代替表記**:

- ACR → 「年間利用額」
- 取得方法 → 記載しない

> 理由: 社内ツールで取得したデータは顧客がアクセスできない。**顧客自身が Azure Portal で確認可能な情報のみ** をレポートに含めること。

## 数値の正確性

### Azure Advisor コスト推奨

- **SSOT は Azure Portal の Advisor 画面**
- CLI は RI 推奨を lookback×term の組み合わせ別に返すため、単純合計すると過大評価になる
- Portal の値と差異がある場合は **Portal を優先**
- Portal 確認できない場合は CLI 値 + 「概算値」注記

### 通貨

- Cost Management API は **JPY** で返す（日本リージョン）
- レポート内で通貨を必ず明示し、混在させない

### 変動率

- テーブルの「変動」列には **比較基準を明記** する（例:「変動（10月→3月）」）

## 免責事項（MANDATORY）

レポート末尾に以下を含める:

```
コスト削減見込額は Azure Advisor の推定値に基づく概算値です。
実際の削減額は、利用状況・価格改定・為替変動等により異なる場合があります。
推奨事項の件数・対象リソースは日々変動するため、最新の状況は Azure Portal からご確認ください。
```

## PowerPoint テンプレート設定

| 項目               | 値                                    |
| ------------------ | ------------------------------------- |
| フォント           | BIZ UDPゴシック                       |
| 本文サイズ         | 12pt                                  |
| テーブルサイズ     | 11pt                                  |
| インサイトボックス | 11pt                                  |
| ヘッダー           | 24pt                                  |
| サブヘッダー       | 13pt                                  |
| スライドサイズ     | 13.333 x 7.5 inch（ワイドスクリーン） |

## Azure Portal リンク

テナント指定付きリンクを使用:

```
https://portal.azure.com/#@{tenantId}/blade/Microsoft_Azure_Expert/AdvisorMenuBlade/{category}/subscriptionId/{subscriptionId}
```
