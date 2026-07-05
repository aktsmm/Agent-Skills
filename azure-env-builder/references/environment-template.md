# 環境定義テンプレート

環境フォルダ (`Az-env/<environment>/`) を構成するためのテンプレート。

## 基本情報

```markdown
| 項目               | 値                           |
| ------------------ | ---------------------------- |
| 環境名             |                              |
| リソースグループ   |                              |
| Azure リージョン   |                              |
| サブスクリプション |                              |
| デプロイ方式       | Bicep / Azure CLI            |
| スコープ           | ResourceGroup / Subscription |
```

## 構成概要

| カテゴリ     | リソース | SKU | 備考 |
| ------------ | -------- | --- | ---- |
| 監視         |          |     |      |
| ネットワーク |          |     |      |
| コンピュート |          |     |      |
| データ       |          |     |      |
| セキュリティ |          |     |      |
| DR           |          |     |      |

→ ヒアリング詳細: [hearing-checklist.md](hearing-checklist.md)  
→ Bicep パターン: [resource-patterns.md](resource-patterns.md)

## フォルダ構造

```
Az-env/<environment>/
├── README.md          # この環境の概要
├── bicep/
│   ├── main.bicep     # メインテンプレート
│   ├── main.bicepparam # パラメータファイル
│   └── modules/       # モジュール (オプション)
├── config/
│   └── parameters.json # 環境固有の値
└── scripts/
    ├── deploy.ps1     # デプロイスクリプト
    └── validate.ps1   # 検証スクリプト
```

## 接続パターン

- [ ] パブリック
- [ ] 閉域 (Private Endpoint)
- [ ] ハイブリッド (VPN / ExpressRoute)

## 高可用性・DR

| 項目           | 設定                |
| -------------- | ------------------- |
| ゾーン冗長     | Yes / No            |
| ストレージ冗長 | LRS / GRS / ZRS     |
| バックアップ   | Azure Backup / 手動 |
| DR サイト      |                     |

## 命名規則

| リソース種別    | パターン                      | 例                |
| --------------- | ----------------------------- | ----------------- |
| Resource Group  | `rg-<env>-<region>-<purpose>` | `rg-prod-jpe-web` |
| Virtual Network | `vnet-<env>-<region>`         | `vnet-prod-jpe`   |
| Storage Account | `st<purpose><env>###`         | `stwebprod001`    |
| AKS             | `aks-<env>-<region>`          | `aks-prod-jpe`    |

## 使い方

1. このテンプレートを `Az-env/<environment>/README.md` にコピー
2. [hearing-checklist.md](hearing-checklist.md) でヒアリング実施
3. [resource-patterns.md](resource-patterns.md) から Bicep パターンを参照
4. `bicep/` フォルダにテンプレートを配置
5. 検証 & デプロイ実行
