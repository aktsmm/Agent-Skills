# アプリデプロイパターン

Azure App Service、AKS、Container Apps へのアプリケーションデプロイパターン。

## 目次

1. [App Service デプロイ](#app-service-デプロイ)
2. [AKS デプロイ](#aks-デプロイ)
3. [Container Apps デプロイ](#container-apps-デプロイ)
4. [CI/CD 統合](#cicd-統合)

---

## App Service デプロイ

### デプロイ方式一覧

| 方式             | 用途                       | 推奨シナリオ               |
| ---------------- | -------------------------- | -------------------------- |
| ZIP デプロイ     | コードパッケージ           | .NET, Node.js, Python 等   |
| コンテナデプロイ | Docker イメージ            | カスタムランタイム         |
| GitHub Actions   | CI/CD 自動化               | 継続的デプロイ             |
| スロットデプロイ | Blue-Green / Canary        | 本番環境のゼロダウンタイム |
| Run From Package | 読み取り専用パッケージ実行 | 高速起動、一貫性           |

### 1. ZIP デプロイ (コードベース)

```bash
# ビルド & ZIP 作成
dotnet publish -c Release -o ./publish
cd publish && zip -r ../app.zip .

# Azure CLI でデプロイ
az webapp deploy \
  --resource-group rg-myapp-prod \
  --name app-web-prod \
  --src-path app.zip \
  --type zip
```

### 2. コンテナデプロイ

#### Bicep でコンテナ App Service 構成

```bicep
// App Service (Linux Container)
module appService 'br/public:avm/res/web/site:0.15.1' = {
  name: 'appServiceDeployment'
  params: {
    name: 'app-${environment}-${location}'
    kind: 'app,linux,container'
    serverFarmResourceId: appServicePlan.outputs.resourceId

    // コンテナ設定
    siteConfig: {
      linuxFxVersion: 'DOCKER|${acrName}.azurecr.io/${imageName}:${imageTag}'
      acrUseManagedIdentityCreds: true  // ACR への MI 認証
      appSettings: [
        {
          name: 'WEBSITES_PORT'
          value: '8080'
        }
        {
          name: 'DOCKER_REGISTRY_SERVER_URL'
          value: 'https://${acrName}.azurecr.io'
        }
      ]
    }

    // Managed Identity (ACR Pull 用)
    managedIdentities: {
      systemAssigned: true
    }
  }
}

// ACR への AcrPull ロール割り当て
module acrRoleAssignment 'br/public:avm/ptn/authorization/resource-role-assignment:0.1.1' = {
  name: 'acrPullRoleAssignment'
  params: {
    principalId: appService.outputs.systemAssignedMIPrincipalId
    roleDefinitionId: '7f951dda-4ed3-4680-a7ca-43fe172d538d'  // AcrPull
    resourceId: acr.outputs.resourceId
  }
}
```

### 3. スロットデプロイ (Blue-Green)

```bicep
// デプロイスロット定義
module stagingSlot 'br/public:avm/res/web/site/slot:0.4.0' = {
  name: 'stagingSlotDeployment'
  params: {
    name: 'staging'
    appServiceName: appService.outputs.name
    kind: 'app,linux,container'
    siteConfig: {
      linuxFxVersion: 'DOCKER|${acrName}.azurecr.io/${imageName}:${newImageTag}'
    }
  }
}
```

```bash
# スロットへデプロイ
az webapp deploy \
  --resource-group rg-myapp-prod \
  --name app-web-prod \
  --slot staging \
  --src-path app.zip

# スワップ（本番切り替え）
az webapp deployment slot swap \
  --resource-group rg-myapp-prod \
  --name app-web-prod \
  --slot staging \
  --target-slot production
```

### 4. Run From Package

```bicep
// Run From Package 設定
siteConfig: {
  appSettings: [
    {
      name: 'WEBSITE_RUN_FROM_PACKAGE'
      value: '1'  // または Blob URL
    }
  ]
}
```

---

## AKS デプロイ

### デプロイ方式一覧

| 方式      | 用途                 | 複雑度 | 推奨シナリオ         |
| --------- | -------------------- | ------ | -------------------- |
| kubectl   | 直接マニフェスト適用 | 低     | シンプルなアプリ     |
| Helm      | パッケージ管理       | 中     | 再利用可能なチャート |
| Kustomize | 環境別オーバーレイ   | 中     | 環境差分管理         |
| GitOps    | Git ベース自動同期   | 高     | 大規模運用、監査要件 |

### Azure 固有の要点

マニフェスト / Helm chart / Kustomize overlay 自体は汎用の書き方でよい。Azure で外しやすい点だけ押さえる。

- ACR 連携: `az aks update -g <rg> -n <aks> --attach-acr <acr>`（imagePullSecret 不要）
- 認証情報: `az aks get-credentials -g <rg> -n <aks>`
- AGIC の Ingress: 非推奨の annotation `kubernetes.io/ingress.class` ではなく `spec.ingressClassName: azure-application-gateway`
- Key Vault: アドオン `azure-keyvault-secrets-provider` + `SecretProviderClass`（CSI driver `secrets-store.csi.k8s.io`）。tenantId などは values に直書きせず CI から渡す
- Pod からの Azure 認証: Workload Identity
- GitOps (Flux v2) は AKS 拡張で入れる:

```bash
az k8s-extension create \
  --resource-group <rg> \
  --cluster-name <aks> \
  --cluster-type managedClusters \
  --name flux \
  --extension-type microsoft.flux
```

---

## Container Apps デプロイ

### Bicep でアプリデプロイ

```bicep
// Container Apps 環境
module containerAppsEnv 'br/public:avm/res/app/managed-environment:0.8.1' = {
  name: 'containerAppsEnvDeployment'
  params: {
    name: 'cae-${environment}-${location}'
    logAnalyticsWorkspaceResourceId: logAnalytics.outputs.resourceId
    infrastructureSubnetId: subnet.outputs.resourceId
  }
}

// Container App
module containerApp 'br/public:avm/res/app/container-app:0.12.0' = {
  name: 'containerAppDeployment'
  params: {
    name: 'ca-myapp-${environment}'
    environmentResourceId: containerAppsEnv.outputs.resourceId

    // コンテナ設定
    containers: [
      {
        name: 'myapp'
        image: '${acrName}.azurecr.io/myapp:${imageTag}'
        resources: {
          cpu: json('0.5')
          memory: '1Gi'
        }
        env: [
          {
            name: 'DATABASE_URL'
            secretRef: 'database-url'
          }
          {
            name: 'REDIS_URL'
            secretRef: 'redis-url'
          }
        ]
      }
    ]

    // スケール設定
    scaleMinReplicas: 1
    scaleMaxReplicas: 10
    scaleRules: [
      {
        name: 'http-scaling'
        http: {
          metadata: {
            concurrentRequests: '100'
          }
        }
      }
    ]

    // Ingress 設定
    ingressExternal: true
    ingressTargetPort: 8080
    ingressTransport: 'auto'

    // シークレット
    secrets: {
      secureList: [
        {
          name: 'database-url'
          keyVaultUrl: '${keyVault.properties.vaultUri}secrets/database-url'
          identity: 'system'
        }
        {
          name: 'redis-url'
          keyVaultUrl: '${keyVault.properties.vaultUri}secrets/redis-url'
          identity: 'system'
        }
      ]
    }

    // Managed Identity
    managedIdentities: {
      systemAssigned: true
    }

    // Dapr 設定 (オプション)
    dapr: {
      enabled: true
      appId: 'myapp'
      appPort: 8080
      appProtocol: 'http'
    }
  }
}
```

### az containerapp コマンド

```bash
# イメージ更新
az containerapp update \
  --resource-group rg-myapp-prod \
  --name ca-myapp-prod \
  --image myacr.azurecr.io/myapp:v1.2.0

# リビジョン確認
az containerapp revision list \
  --resource-group rg-myapp-prod \
  --name ca-myapp-prod \
  --output table

# トラフィック分割 (Canary)
az containerapp ingress traffic set \
  --resource-group rg-myapp-prod \
  --name ca-myapp-prod \
  --revision-weight myapp--v1=90 myapp--v2=10
```

---

## CI/CD 統合

Bicep 用パイプラインは [cicd-templates/](cicd-templates/README.md)。アプリ配備ワークフローで Azure 固有に押さえる点:

- 認証は OIDC（federated credential）。`azure/login@v2` に `client-id` / `tenant-id` / `subscription-id`、job に `permissions: id-token: write`。SP + シークレット（`creds: ${{ secrets.AZURE_CREDENTIALS }}`）は非推奨（[Use GitHub Actions to connect to Azure](https://learn.microsoft.com/azure/developer/github/connect-from-azure)）
- App Service: `az webapp deploy --slot staging --src-path app.zip --type zip` → `az webapp deployment slot swap --slot staging --target-slot production`
- AKS: `az acr build --registry <acr> --image <name>:${{ github.sha }} .` → `az aks get-credentials` → `helm upgrade --install ... --set image.tag=${{ github.sha }} --wait` → `kubectl rollout status`
- Container Apps: `az acr build ...` → `az containerapp update --image <acr>.azurecr.io/<name>:${{ github.sha }}` → `az containerapp revision list -o table`

---

## 設定連携チェックリスト

### App Service デプロイ時

| 項目               | 確認内容                          |
| ------------------ | --------------------------------- |
| ACR 認証           | Managed Identity + AcrPull ロール |
| App Settings       | Key Vault 参照または環境変数      |
| Connection Strings | SQL/Redis/Storage の接続文字列    |
| Startup Command    | コンテナ起動コマンド              |
| Health Check       | /health エンドポイント設定        |

### AKS デプロイ時

| 項目         | 確認内容                                   |
| ------------ | ------------------------------------------ |
| ACR 統合     | `az aks update --attach-acr`               |
| Namespace    | 環境別 namespace 分離                      |
| Secrets      | Key Vault CSI Driver または Sealed Secrets |
| Ingress      | AGIC または Nginx Ingress                  |
| Pod Identity | Workload Identity 設定                     |
| HPA          | CPU/メモリ/カスタムメトリクス              |

### Container Apps デプロイ時

| 項目          | 確認内容                      |
| ------------- | ----------------------------- |
| Environment   | VNet 統合、Log Analytics 接続 |
| Secrets       | Key Vault 参照                |
| Scale Rules   | HTTP / CPU / KEDA             |
| Dapr          | サイドカー有効化              |
| Revision Mode | Single / Multiple             |
