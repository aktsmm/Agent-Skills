# CI/CD テンプレート

Azure Bicep デプロイ用の CI/CD パイプラインテンプレート。

## テンプレート一覧

| ファイル                                   | プラットフォーム | 用途                      |
| ------------------------------------------ | ---------------- | ------------------------- |
| [github-actions.yml](github-actions.yml)   | GitHub Actions   | GitHub リポジトリ用       |
| [azure-pipelines.yml](azure-pipelines.yml) | Azure DevOps     | Azure DevOps リポジトリ用 |

## 機能比較

| 機能               | GitHub Actions | Azure Pipelines |
| ------------------ | -------------- | --------------- |
| Bicep Lint         | ✅             | ✅              |
| ARM 検証           | ✅             | ✅              |
| What-If プレビュー | ✅             | ✅              |
| 環境別デプロイ     | ✅             | ✅              |
| 承認ゲート         | ✅             | ✅              |
| PR コメント        | ✅             | ❌              |
| Slack 通知         | ✅             | ❌ (拡張可能)   |
| パイプライン変数   | ✅             | ✅              |

## クイックスタート

### GitHub Actions

```bash
# 1. ワークフローファイルをコピー
mkdir -p .github/workflows
cp references/cicd-templates/github-actions.yml .github/workflows/deploy-azure.yml

# 2. シークレット設定
gh secret set AZURE_CREDENTIALS < service-principal.json

# 3. 変数設定
gh variable set RESOURCE_GROUP --body "rg-myapp-prod"
gh variable set AZURE_SUBSCRIPTION_ID --body "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

### Azure Pipelines

```bash
# 1. パイプラインファイルをコピー
cp references/cicd-templates/azure-pipelines.yml azure-pipelines.yml

# 2. Azure DevOps で設定
#    - Service Connection 作成
#    - Variable Group 作成
#    - Environment 作成
```

## サービスプリンシパル作成

```bash
# Contributor ロールでサービスプリンシパル作成
az ad sp create-for-rbac \
  --name "cicd-deployment-sp" \
  --role Contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group} \
  --sdk-auth

# 出力例 (これを AZURE_CREDENTIALS シークレットに設定)
{
  "clientId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "clientSecret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "subscriptionId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "tenantId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  ...
}
```

## 環境保護ルール (推奨)

### GitHub

1. Settings > Environments
2. 「New environment」で `prod` 作成
3. 「Required reviewers」で承認者を追加

### Azure DevOps

1. Pipelines > Environments
2. `production` 環境を選択
3. 「Approvals and checks」で承認者を追加

## ブランチ戦略

```
main (protected)
  ├── PR マージ時に dev 自動デプロイ
  │
feature/*
  ├── PR 作成時に What-If プレビュー
  │
release/*
  └── staging/prod への手動デプロイ
```

## トラブルシューティング

### よくあるエラー

| エラー                    | 原因             | 解決策                                           |
| ------------------------- | ---------------- | ------------------------------------------------ |
| `AuthorizationFailed`     | SP の権限不足    | Contributor ロールを確認                         |
| `ResourceGroupNotFound`   | RG が存在しない  | 先に RG を作成するか Subscription スコープに変更 |
| `InvalidTemplate`         | Bicep 構文エラー | `az bicep build` でローカル検証                  |
| `DeploymentQuotaExceeded` | デプロイ履歴上限 | 古いデプロイを削除                               |

### デバッグコマンド

```bash
# デプロイ履歴確認
az deployment group list --resource-group {rg} --query "[].{name:name,state:properties.provisioningState,time:properties.timestamp}" --output table

# 失敗したデプロイの詳細
az deployment group show --resource-group {rg} --name {deployment-name} --query "properties.error"

# リソースグループの現在状態
az resource list --resource-group {rg} --output table
```
