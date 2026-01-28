---
name: azure-env-builder
description: "[Alpha] エンタープライズ Azure 環境構築スキル。AVM 活用、VM アプリ初期化、App Service/AKS/Container Apps へのアプリデプロイ、サービス間設定連携、CI/CD 生成をサポート。Hub-Spoke, AKS, AI Foundry 等の複合アーキテクチャに対応。Bicep MCP と Microsoft Learn Docs MCP で最新スキーマを取得。"
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# Azure Environment Builder

エンタープライズ向け Azure 環境を効率的に構築するスキル。

## When to Use

- エンタープライズ向け Azure 環境の新規構築や再構成
- AVM モジュールを活用した Bicep 設計・実装
- Hub-Spoke/AKS/AI Foundry など複合アーキテクチャの設計

## 機能一覧

| カテゴリ       | 機能                               |
| -------------- | ---------------------------------- |
| Architecture   | Hub-Spoke, Web+DB, AKS, AI Foundry |
| AVM Modules    | 200+ Azure Verified Modules        |
| VM Init        | Squid, Nginx, Docker, IIS 初期化   |
| Config Linking | SQL/Storage/Redis 接続、MI RBAC    |
| CI/CD          | GitHub Actions / Azure Pipelines   |

## ワークフロー

1. **ヒアリング** - 基本情報 + アーキテクチャパターン選択
2. **MCP ツール実行** - 最新 AVM/スキーマ取得
3. **環境フォルダ生成** - `scripts/scaffold_environment.ps1`
4. **Bicep 実装** - AVM モジュール + VM 初期化
5. **CI/CD 生成** - パイプラインテンプレート
6. **検証 → デプロイ** - what-if → 実行

## 必須: MCP ツール

**Bicep コード生成前に必ず実行:**

```
mcp_bicep_experim_get_bicep_best_practices
mcp_bicep_experim_list_avm_metadata
mcp_bicep_experim_get_az_resource_type_schema(azResourceType, apiVersion)
microsoft_docs_search(query: "Private Endpoint Bicep")
```

## ヒアリング項目

→ **[references/hearing-checklist.md](references/hearing-checklist.md)**

| 項目               | 確認内容                    |
| ------------------ | --------------------------- |
| サブスクリプション | ID または `az account show` |
| 環境名             | dev / staging / prod        |
| リージョン         | japaneast / japanwest       |
| デプロイ方式       | Azure CLI / Bicep           |

## アーキテクチャパターン

→ **[references/architecture-patterns.md](references/architecture-patterns.md)**

| パターン   | 用途                     |
| ---------- | ------------------------ |
| Hub-Spoke  | 大規模エンタープライズ   |
| Web + DB   | 一般的な Web アプリ      |
| AKS        | コンテナマイクロサービス |
| AI Foundry | AI/ML ワークロード       |
| Proxy VM   | 閉域ネットワーク送信制御 |

## コマンド

```powershell
# 環境フォルダ生成
pwsh scripts/scaffold_environment.ps1 -Environment <env> -Location <region>

# 検証
az deployment group what-if --resource-group <rg> --template-file main.bicep

# デプロイ
az deployment group create --resource-group <rg> --template-file main.bicep
```

## 参照ファイル

| ファイル                                                              | 用途                   |
| --------------------------------------------------------------------- | ---------------------- |
| [architecture-patterns.md](references/architecture-patterns.md)       | アーキテクチャパターン |
| [avm-modules.md](references/avm-modules.md)                           | AVM モジュールカタログ |
| [vm-app-scripts.md](references/vm-app-scripts.md)                     | VM 初期化スクリプト    |
| [app-deploy-patterns.md](references/app-deploy-patterns.md)           | アプリデプロイパターン |
| [service-config-templates.md](references/service-config-templates.md) | サービス間設定連携     |
| [cicd-templates/](references/cicd-templates/)                         | CI/CD テンプレート     |
