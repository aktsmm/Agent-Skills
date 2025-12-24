# 環境定義テンプレート

## 基本情報

| 項目                     | 値                                          |
| ------------------------ | ------------------------------------------- |
| 環境名                   | <!-- dev / staging / prod など -->          |
| リソースグループ名       | <!-- rg-<environment>-<region>-001 など --> |
| Azure リージョン         | <!-- japaneast / japanwest など -->         |
| Azure サブスクリプション | <!-- サブスクリプション名 or GUID -->       |
| デプロイ方式             | <!-- Azure CLI / Bicep -->                  |

## 目的・スコープ

<!-- この環境で実現したいことを簡潔に記載 -->

## 構成リソース一覧

| リソース種別         | リソース名パターン  | SKU / Tier   | 備考                             |
| -------------------- | ------------------- | ------------ | -------------------------------- |
| App Service Plan     | asp-<env>-<region>  | S1           |                                  |
| App Service          | app-<env>-<region>  | -            | Managed Identity 有効化          |
| Storage Account      | st<env><region>001  | Standard_LRS |                                  |
| Key Vault            | kv-<env>-<region>   | Standard     | RBAC モード                      |
| Application Insights | appi-<env>-<region> | -            | Log Analytics ワークスペース連携 |

## ネットワーク / セキュリティ

- VNet 統合の要否: <!-- Yes / No -->
- Private Endpoint: <!-- 対象サービス -->
- 既存の Hub VNet / Firewall: <!-- あれば記載 -->
- NSG / UDR: <!-- 必要なルール概要 -->

## パラメータ / シークレット管理

- 環境変数: `env/<environment>/config/*.json`
- シークレット: Key Vault に一括格納、App Service は `@Microsoft.KeyVault(...)` で参照

## 備考 / 前提条件

<!-- 既存の Policy、Blueprint、RBAC アサインメントなど -->

---

このテンプレートを `env/<environment>/README.md` にコピーして編集してください。
