---
name: azure-advisor-report
description: "Generate Azure environment monthly report (Markdown + PowerPoint) from Azure Advisor and Cost Management API. Use when creating Advisor recommendations report, cost trend analysis, or security/reliability assessment for a customer subscription. Triggers on 'Advisor report', 'Azure monthly report', 'subscription report', 'Azure環境レポート', '簡易月次レポート'."
argument-hint: "Subscription ID(s) and Tenant ID(s), optionally target month (e.g., 2026-04)"
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

```powershell
py -3 generate_pptx.py --title "顧客名" --data-dir ./output --output report.pptx
```

### Phase 4: 検証

1. PPTX を開いて表示確認（要素の重なりがないか）
2. 数値の検算（コスト合計、変動率の基準月明示）
3. 社内情報・社内用語が含まれていないか最終チェック

## 品質基準（Lessons Learned）

### レポート構造の最低要件

初回作成時に以下のセクションを **この順序で** 含めること。不足・順序違いは手戻りが発生する:

1. **📋 対象サブスクリプション**（ID・テナント・用途推定）
2. **📈 コスト推移・分析**（月別テーブル + 前月比% + サービス別月次推移 Top5-7 + 変動インサイト）
3. **🔴 エグゼクティブサマリー**（優先度 🔴🟡⚪ 付き重要ポイント）
4. **💰 コスト最適化（Cost）**（Advisor Cost 件数 + 推定削減ポテンシャル + 代表リソース名）
5. **🔒 セキュリティ（Security）**（Advisor Security 件数 + 重要度分析）
6. **🛡️ 信頼性・可用性（Reliability）**（Advisor Reliability 件数 + Zone冗長/Backup 改善提案）
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

### 出力先のフォルダ配置

- 顧客管理フォルダがある場合、ファイル作成前に **顧客マッピング定義** で正しいフォルダ名を確認する
- 類似名の別顧客フォルダに誤配置しないこと（例: 富士通 ≠ 富士ソフト）

### PPTX 生成のルール

- **スライドノート必須**: 全コンテンツスライドに `add_notes()` で詳細な説明ノートを追加すること
  - データソース、キーテイクアウェイ、推奨アクション、プレゼンター向けの補足情報を含む
- **出力ファイル名**: 一時ファイル名（`.tmp.pptx`）で生成し、成功後にリネーム
  - VS Code / PowerPoint のプレビューによる PermissionError を回避
- **テンプレート流用**: ヘルパー関数（add_notes, add_shape_bg, tb, ap, tbl, hdr, ibox）のみ流用し、スライドデータ部分は新規記述
  - コピー＆置換は旧顧客のデータが残存するため禁止

### Advisor データ取得のルール

- **全 4 カテゴリを必ず取得**: Cost, Security, HighAvailability, **OperationalExcellence**
- 「未取得」「次回予定」は禁止。結果が 0 件なら 「0件（推奨なし）」 と記載
