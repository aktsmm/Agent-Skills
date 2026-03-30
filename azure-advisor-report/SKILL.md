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
