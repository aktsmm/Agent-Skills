---
name: azure-advisor-report
description: "Generate Azure environment monthly report (Markdown + PowerPoint) from Azure Advisor and Cost Management API. Use when creating Advisor recommendations report, cost trend analysis, or security/reliability assessment for a customer subscription. Triggers on 'Advisor report', 'Azure monthly report', 'subscription report', 'Azure環境レポート', '簡易月次レポート'."
argument-hint: "Subscription ID(s) and Tenant ID(s), optionally target month (e.g., 2026-04)"
user-invocable: true
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Azure Advisor 簡易月次レポート生成

Azure Advisor 推奨事項・コスト推移を分析し、顧客向けの簡易月次レポート（Markdown + PowerPoint）を生成するスキル。

## When to Use

- 顧客の Azure 環境の Advisor 推奨事項をレポートにまとめたいとき
- コスト推移・サービス別内訳を可視化したいとき
- セキュリティ・信頼性の推奨事項を優先順位付きで報告したいとき

## When NOT to Use

- Azure 環境の構築・変更作業（このスキルは読み取り専用のレポート生成のみ）
- 社内用の詳細分析（このスキルは顧客向けレポートに特化）

## 入力パラメータ

| パラメータ      | 必須 | 説明                                           |
| --------------- | ---- | ---------------------------------------------- |
| Subscription ID | ✅   | 対象サブスクリプション（複数可）               |
| Tenant ID       | ✅   | 各サブスクリプションのテナント ID              |
| 対象月          | ❌   | `YYYY-MM` 形式。省略時は当月                   |
| 顧客名          | ❌   | レポートタイトルに使用。省略時は「Azure 環境」 |

## ガードレール

[レポート品質ルール](./references/report-guardrails.md) を適用すること。

## 手順

### Phase 1: データ取得

[データ取得手順](./references/data-collection.md) を参照。

### Phase 2: Markdown レポート生成

[Markdown テンプレート](./assets/report-template.md) をベースに生成。

出力先: 任意のパス（例: `{customer}/monthly-report_{YYYYMMDD}.md`）

### Phase 3: PowerPoint レポート生成

[PPTX 生成スクリプト](./scripts/generate_pptx.py) を使用。
複数サブスクリプションの場合は Subscription ID ごとに章を分ける。重要な推奨事項は個別ページを作り、英語原文、日本語訳、リスク、推奨アクション、メリット / デメリット、是正手順、Microsoft Learn URL を入れる。
Executive Summary と推奨アクションでは、必要に応じて WAF / CAF の観点も添える。

```powershell
py -3 generate_pptx.py --title "顧客名" --data-dir ./output --output report.pptx
```

### Phase 4: 検証

1. PPTX を開いて表示確認（要素の重なりがないか）
2. 全コンテンツスライドに speaker notes があるか確認
3. 表・本文・参照 URL が 14pt 未満になっていないか確認
4. 数値の検算（コスト合計、変動率の基準月明示）
5. 英語推奨事項に日本語訳があり、「日本語訳未登録」のような placeholder が残っていないか確認
6. 社内情報・社内用語が含まれていないか最終チェック

## 品質基準（Lessons Learned）

### レポート構造の最低要件

初回作成時に以下のセクションを **この順序で** 含めること。不足・順序違いは手戻りが発生する:

1. **📋 対象サブスクリプション**（ID・テナント・用途推定）
2. **📈 コスト推移・分析**（月別テーブル + 前月比% + サービス別月次推移 Top5-7 + 変動インサイト）
3. **🔴 エグゼクティブサマリー**（優先度 🔴🟡⚪ 付き重要ポイント）
4. **💰 コスト最適化（Cost）**（Advisor Cost 件数 + 推定削減ポテンシャル + 代表リソース名）
5. **🔒 セキュリティ（Security）**（Advisor Security 件数 + 重要度分析）
6. **⚡ 信頼性・可用性（Reliability）**（Advisor Reliability 件数 + Zone冗長/Backup 改善提案）
7. **⚙️ オペレーショナルエクセレンス**（Advisor OpEx 件数。**必ず取得すること**。「未取得」「次回予定」は禁止。結果が0件なら「0件（推奨なし）」と記載）
8. **📊 全体サマリー**（サブスク × カテゴリ一覧 + グループ別集計）
9. **🎯 推奨アクション（優先順）**（優先度付き・具体的・actionable）
10. **📎 参考リンク**（Azure Portal Advisor 直リンク）

### データ処理の注意事項

- Azure CLI 出力は **ファイルに直接保存** し、チャットに表示しない
  ```powershell
  az rest ... -o json 2>$null | Set-Content output/xxx.json
  ```
- JSON の集計・ピボット処理は **Python を優先**（`json` + `collections.defaultdict`）
  - PowerShell は DateTime 型の自動変換で `.SubString()` エラーが頻発するため回避
- Cost Management API は **JPY**（日本リージョン）、C360 CSV は **USD** — 通貨を必ず明示
- Cost Management Query API は 429 になりやすいため、半年分析では **月次 × ServiceName** を先に取得し、合計は ServiceName 行の合算で検算する。ResourceGroup / ResourceId の深掘りはスパイク月に限定する
- コスト削減候補を提示する場合は、削除実行ではなく「要確認」「親リソースから確認」「削除候補」に分類する。`Do Not Delete` タグ、削除ロック、Backup vault、Activity Log Alerts、NetworkWatcher、managed resource group は安全側に倒して扱う
- コスト上位リソース表では **リソース種類・現在状態** を併記する。MTD コストには削除済み/削除中リソースも残るため、現存リソース一覧と join して誤解を避ける
- 利用中アプリに紐づくことが確認されたリソースは、コスト上位でも削除候補にしない。維持または SKU/容量見直しとして扱う

### PPTX 生成のルール

- **スライドノート必須**: 全コンテンツスライドに `add_notes()` で詳細な説明ノートを追加すること
  - データソース、キーテイクアウェイ、推奨アクション、プレゼンター向けの補足情報を含む
- **データソース取得日必須**: PowerPoint の表紙または補足で、各データソースの取得日を明示すること
- **既存フル構成の継承**: 既存顧客に過去の完成度が高い PPTX / generator がある場合、別の薄い新規 deck を作らず、既存のフル構成へ最新データを差し替えること。理由: 比較軸・カテゴリ別章・speaker notes が落ちると、前回品質より劣化するため
- **ワイドスクリーン PPTX のフォントサイズ下限**: 表・本文・参照 URL は 14pt 以上、スライドタイトルは 24pt 以上。14pt 未満は顧客向け PPTX では原則使わない
- **テーブル列幅の明示指定**: 番号・件数・影響度のような短い列はデフォルト等幅だと無駄に広くなる。`col_widths` パラメータで短い列を狭め、推奨事項・リソース名列に幅を配分する
- **出力ファイル名**: 一時ファイル名（`.tmp.pptx`）で生成し、成功後にリネーム
  - VS Code / PowerPoint のプレビューによる PermissionError を回避
- **テンプレート流用**: ヘルパー関数（add_notes, add_shape_bg, tb, ap, tbl, hdr, ibox）のみ流用し、スライドデータ部分は新規記述
  - コピー＆置換は旧顧客のデータが残存するため禁止

### Advisor データ取得のルール

- **全 4 カテゴリを必ず取得**: Cost, Security, HighAvailability, **OperationalExcellence**
- 「未取得」「次回予定」は禁止。結果が 0 件なら 「0件（推奨なし）」 と記載
