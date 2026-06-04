# レポート品質ルール

顧客に提示するレポート（Markdown / PowerPoint）生成時に適用するガードレール。

## 社内情報の除外（MANDATORY）

以下を顧客向けレポートに **含めてはならない**:

| 禁止項目             | 例                                     |
| -------------------- | -------------------------------------- |
| 社内ツール名・リンク | 社内専用の分析ツール・ダッシュボード等 |
| 社内用語             | ACR, TPID, TTM 等                      |
| CLI コマンド名       | `az advisor recommendation list` 等    |
| データソース詳細     | 「Cost Management API (ActualCost)」等 |
| 社内 URL             | 社内専用ポータルの URL 等              |
| 社内専用分析データ   | 社内ツールの Focus Areas 等            |

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

### 表紙スライド

表紙に以下の注記をグレー文字で含める:

```
※値はあくまで参考とし、実際の値は Azure Portal でご確認お願いします
```

### レポート末尾

レポート末尾（最終スライド / Markdown 末尾）に以下を含める:

```
コスト削減見込額は Azure Advisor の推定値に基づく概算値です。
実際の削減額は、利用状況・価格改定・為替変動等により異なる場合があります。
推奨事項の件数・対象リソースは日々変動するため、最新の状況は Azure Portal からご確認ください。
```

## インサイト・コメントの記載ルール（MANDATORY）

レポート内のインサイト・分析コメント・推奨アクションは、**取得した実データに基づいて記載**すること。

| ルール                   | 説明                                                                          |
| ------------------------ | ----------------------------------------------------------------------------- |
| **推測で書かない**       | データで裏付けられない仮説・憶測を「事実」として記載しない                    |
| **根拠を明示**           | 「XXが高い」ではなく「XXが N 件（Advisor 取得値）」のように数値・出典を付ける |
| **不確実な場合は明示**   | 「可能性があります」「確認推奨」等の表現を使い、断定しない                    |
| **原因推定は仮説と明記** | 「○○が原因です」→「○○が原因と推定されます。確認を推奨します」                 |

**禁止例**:

- ✘ 「Storage が減少したのはオンプレ回帰のためです」（証拠なしの断定）
- ✘ 「このリソースは不要です」（利用状況未確認の断定）

**良い例**:

- ○ 「Storage が 63% 減少しています。データ移行・削除・オンプレ回帰などの可能性があり、利用トレンドの確認を推奨します」
- ○ 「Advisor が 14 台の VM を低使用率と判定しています。利用率を確認のうえ、サイズダウンまたは停止スケジュールの設定をご検討ください」

### コスト上位リソースの扱い

- 上位リソース表には **リソース名だけでなく種類（例: Search service, Recovery Services vault, Container Registry, Cognitive Services）** を併記する
- MonthToDate のコストは発生済みコストであり、削除済み・削除中リソースも表示される。現在状態が分かる場合は `Current / Deleting / Deleted` を併記する
- ユーザーまたは運用担当が「アプリで使用中」と確認したリソースは、コスト上位でも削除候補と断定しない。推奨は「維持」「SKU/容量見直し」「利用量監視」に留める
- Backup / Recovery Services vault は削除要求後も `Deleting` が長く続くことがある。削除効果は即時ではなく、翌日以降または翌月のコストで確認する
- Backup Vault / Data Protection Backup Vault は soft-deleted backup instance の保持により、`scheduledPurgeTime` まで完全削除できないことがある。この場合は「削除失敗」ではなく「soft delete retention 待ち」として、purge 予定時刻を明記する

### WAF / CAF 観点の添え方

Executive Summary と推奨アクションでは、単に Advisor 件数を並べず、必要に応じて Microsoft Learn の公式フレームワークに沿って意味付けする。

- Well-Architected Framework: Reliability / Security / Cost Optimization / Operational Excellence / Performance Efficiency のどの柱に効くかを添える
- Cloud Adoption Framework: Govern / Secure / Manage / Ready など、運用・統制のどの活動に関係するかを添える
- WAF / CAF はコメントの補助軸であり、Advisor 取得値や Cost 実データを置き換える根拠にしない

## PowerPoint テンプレート設定

| 項目               | 値                                    |
| ------------------ | ------------------------------------- |
| フォント           | BIZ UDPゴシック                       |
| 本文サイズ         | 14pt 以上                             |
| テーブルサイズ     | 14pt 以上                             |
| インサイトボックス | 14pt 以上                             |
| ヘッダー           | 24pt                                  |
| サブヘッダー       | 14pt 以上                             |
| スライドサイズ     | 13.333 x 7.5 inch（ワイドスクリーン） |

### スライドノート（MANDATORY）

各カテゴリ（Cost / Security / Reliability）のスライドに、**件数 TOP3 の推奨事項の説明**をスライドノートに含める。

各推奨事項のノートには以下を含める:

- **何が問題か**: 具体的に何が未設定/未対応なのか
- **リスク**: 放置した場合に何が起きるか
- **推奨アクション**: 具体的に何をすればよいか

これにより発表者がスライドを説明する際の補足情報として活用できる。

```python
# python-pptx でのノート追加例
notes = slide.notes_slide
notes.notes_text_frame.text = "ノートテキスト"
```

### 複数サブスクリプションの PPTX 構成

複数サブスクリプションを扱う PowerPoint では、環境名だけでまとめず **Subscription ID ごとに章を分ける**。

推奨構成:

1. 表紙
2. エグゼクティブサマリー
3. 全体コスト推移
4. Subscription ID ごとのセクション区切り
5. 各サブスクリプションの Cost 状況
6. 各サブスクリプションの Advisor 推奨事項
7. 推奨アクション / 免責事項

章区切りスライドには Subscription ID と Tenant ID を明記し、発表時にどの環境の話か迷わないようにする。
Cost スライドには月別合計、明細件数、主要サービス別推移を入れる。Advisor Overview スライドにはカテゴリ別件数と件数上位の推奨事項を入れる。重要な推奨事項は個別ページを作り、英語原文、その直下の日本語訳、リスク、推奨アクション、メリット / デメリット、是正手順、Microsoft Learn URL を入れる。全体推奨アクションも別途まとめる。

是正手順は Microsoft Learn の公式 URL を根拠にする。コマンドや具体的な操作例を書く場合は `microsoft_code_sample_search` で公式サンプルを確認する。code sample search が不安定な場合でも、Docs search / fetch で取得できた公式ページを使い、根拠なしの手順やコマンド例を書かない。

英語の Advisor 推奨事項は、そのまま出さず必ず直下に日本語訳を添える。辞書未登録の場合でも「日本語訳未登録」と表示せず、最低限、自然な日本語要約へ置き換える。

### PPTX 生成後チェック

生成後は以下を確認してから完了扱いにする:

- PPTX ファイルが存在し、PowerPoint で開けること
- 全コンテンツスライドに speaker notes があること
- テーブルや RefURL がスライド外へはみ出していないこと
- PowerPoint COM で `TextRange.BoundHeight/BoundWidth` を確認し、実レンダリング上の overflow が 0 件であること
- 表・本文・参照 URL の表示テキストに 14pt 未満がないこと
- 旧顧客名・旧 Subscription ID・旧 URL が残っていないこと
- 生成に使った Cost / Advisor の JSON と PPTX 上の主要数値が一致すること

## ファイル命名規則

| ファイル           | 命名規則                      | 例                          |
| ------------------ | ----------------------------- | --------------------------- |
| PowerPoint         | `Azure-Brief-{YYYYMMDD}.pptx` | `Azure-Brief-20260331.pptx` |
| Markdown           | `Azure-Brief-{YYYYMMDD}.md`   | `Azure-Brief-20260331.md`   |
| PPTX生成スクリプト | `_gen_monthly_report.py`      | 固定名                      |

## Azure Portal リンク

テナント指定付きリンクを使用:

```
https://portal.azure.com/#@{tenantId}/blade/Microsoft_Azure_Expert/AdvisorMenuBlade/{category}/subscriptionId/{subscriptionId}
```
