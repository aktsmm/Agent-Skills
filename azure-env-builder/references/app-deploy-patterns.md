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

### 1. kubectl 直接デプロイ

#### Kubernetes マニフェスト

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
        - name: myapp
          image: myacr.azurecr.io/myapp:v1.0.0
          ports:
            - containerPort: 8080
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "256Mi"
              cpu: "500m"
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: myapp-secrets
                  key: database-url
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: myapp-service
  namespace: production
spec:
  type: ClusterIP
  selector:
    app: myapp
  ports:
    - port: 80
      targetPort: 8080
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp-ingress
  namespace: production
  annotations:
    kubernetes.io/ingress.class: azure/application-gateway
    appgw.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
    - hosts:
        - myapp.example.com
      secretName: myapp-tls
  rules:
    - host: myapp.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: myapp-service
                port:
                  number: 80
```

```bash
# AKS 認証情報取得
az aks get-credentials --resource-group rg-aks-prod --name aks-prod

# デプロイ
kubectl apply -f k8s/deployment.yaml

# 確認
kubectl get pods -n production
kubectl get svc -n production
```

### 2. Helm チャートデプロイ

#### Chart 構造

```
helm/myapp/
├── Chart.yaml
├── values.yaml
├── values-dev.yaml
├── values-prod.yaml
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    ├── ingress.yaml
    ├── configmap.yaml
    └── secret.yaml
```

#### Chart.yaml

```yaml
apiVersion: v2
name: myapp
description: My Application Helm Chart
version: 1.0.0
appVersion: "1.0.0"
```

#### values.yaml (デフォルト)

```yaml
# アプリケーション設定
replicaCount: 2

image:
  repository: myacr.azurecr.io/myapp
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 80
  targetPort: 8080

ingress:
  enabled: true
  className: azure-application-gateway
  annotations:
    appgw.ingress.kubernetes.io/ssl-redirect: "true"
  hosts:
    - host: myapp.example.com
      paths:
        - path: /
          pathType: Prefix

resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "256Mi"
    cpu: "500m"

# 環境変数
env:
  - name: ASPNETCORE_ENVIRONMENT
    value: Production

# ConfigMap から読み込む設定
configMap:
  enabled: true
  data:
    APP_CONFIG: "production"

# Secrets (外部参照推奨)
secrets:
  enabled: false

# Azure Key Vault CSI Driver
keyVault:
  enabled: true
  name: kv-myapp-prod
  tenantId: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  secrets:
    - name: database-connection-string
      alias: DATABASE_URL
```

#### values-prod.yaml (本番オーバーライド)

```yaml
replicaCount: 5

image:
  tag: v1.2.0

resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "1000m"

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
```

#### templates/deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "myapp.fullname" . }}
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "myapp.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "myapp.selectorLabels" . | nindent 8 }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - containerPort: {{ .Values.service.targetPort }}
          {{- if .Values.env }}
          env:
            {{- toYaml .Values.env | nindent 12 }}
          {{- end }}
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
          {{- if .Values.keyVault.enabled }}
          volumeMounts:
            - name: secrets-store
              mountPath: "/mnt/secrets-store"
              readOnly: true
          {{- end }}
      {{- if .Values.keyVault.enabled }}
      volumes:
        - name: secrets-store
          csi:
            driver: secrets-store.csi.k8s.io
            readOnly: true
            volumeAttributes:
              secretProviderClass: {{ include "myapp.fullname" . }}-secrets
      {{- end }}
```

```bash
# Helm デプロイ
helm upgrade --install myapp ./helm/myapp \
  --namespace production \
  --create-namespace \
  -f ./helm/myapp/values-prod.yaml \
  --set image.tag=v1.2.0

# ロールバック
helm rollback myapp 1 --namespace production

# 履歴確認
helm history myapp --namespace production
```

### 3. Kustomize デプロイ

```
kustomize/
├── base/
│   ├── kustomization.yaml
│   ├── deployment.yaml
│   └── service.yaml
└── overlays/
    ├── dev/
    │   ├── kustomization.yaml
    │   └── patch-replicas.yaml
    └── prod/
        ├── kustomization.yaml
        └── patch-replicas.yaml
```

#### base/kustomization.yaml

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - deployment.yaml
  - service.yaml

commonLabels:
  app: myapp
```

#### overlays/prod/kustomization.yaml

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: production

resources:
  - ../../base

images:
  - name: myacr.azurecr.io/myapp
    newTag: v1.2.0

replicas:
  - name: myapp
    count: 5

patches:
  - path: patch-replicas.yaml
```

```bash
# Kustomize でデプロイ
kubectl apply -k kustomize/overlays/prod/
```

### 4. GitOps (Flux v2)

#### Flux インストール

```bash
# Flux CLI インストール
curl -s https://fluxcd.io/install.sh | sudo bash

# AKS に Flux 拡張機能インストール
az k8s-extension create \
  --resource-group rg-aks-prod \
  --cluster-name aks-prod \
  --cluster-type managedClusters \
  --name flux \
  --extension-type microsoft.flux
```

#### GitRepository & Kustomization

```yaml
# flux-system/git-repository.yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: myapp-repo
  namespace: flux-system
spec:
  interval: 1m
  url: https://github.com/myorg/myapp-k8s
  ref:
    branch: main
  secretRef:
    name: github-token
---
# flux-system/kustomization.yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: myapp-production
  namespace: flux-system
spec:
  interval: 5m
  path: ./kustomize/overlays/prod
  prune: true
  sourceRef:
    kind: GitRepository
    name: myapp-repo
  healthChecks:
    - apiVersion: apps/v1
      kind: Deployment
      name: myapp
      namespace: production
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

### GitHub Actions - App Service

```yaml
# .github/workflows/deploy-appservice.yml
name: Deploy to App Service

on:
  push:
    branches: [main]
    paths: ["src/**"]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # ビルド
      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: "8.0.x"

      - name: Build and publish
        run: |
          dotnet publish -c Release -o ./publish
          cd publish && zip -r ../app.zip .

      # Azure ログイン
      - uses: azure/login@v2
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      # デプロイ (スロット)
      - name: Deploy to staging slot
        run: |
          az webapp deploy \
            --resource-group ${{ vars.RESOURCE_GROUP }} \
            --name ${{ vars.APP_NAME }} \
            --slot staging \
            --src-path app.zip

      # スワップ
      - name: Swap to production
        run: |
          az webapp deployment slot swap \
            --resource-group ${{ vars.RESOURCE_GROUP }} \
            --name ${{ vars.APP_NAME }} \
            --slot staging \
            --target-slot production
```

### GitHub Actions - AKS

```yaml
# .github/workflows/deploy-aks.yml
name: Deploy to AKS

on:
  push:
    branches: [main]
    paths: ["src/**", "helm/**"]

env:
  ACR_NAME: myacr
  IMAGE_NAME: myapp
  CLUSTER_NAME: aks-prod
  RESOURCE_GROUP: rg-aks-prod

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      image_tag: ${{ steps.meta.outputs.tags }}
    steps:
      - uses: actions/checkout@v4

      - uses: azure/login@v2
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      # ACR ログイン
      - name: Login to ACR
        run: az acr login --name ${{ env.ACR_NAME }}

      # Docker ビルド & プッシュ
      - name: Build and push
        id: meta
        run: |
          IMAGE_TAG="${{ env.ACR_NAME }}.azurecr.io/${{ env.IMAGE_NAME }}:${{ github.sha }}"
          docker build -t $IMAGE_TAG .
          docker push $IMAGE_TAG
          echo "tags=$IMAGE_TAG" >> $GITHUB_OUTPUT

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: azure/login@v2
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      # AKS 認証
      - name: Get AKS credentials
        run: |
          az aks get-credentials \
            --resource-group ${{ env.RESOURCE_GROUP }} \
            --name ${{ env.CLUSTER_NAME }}

      # Helm デプロイ
      - name: Deploy with Helm
        run: |
          helm upgrade --install myapp ./helm/myapp \
            --namespace production \
            --create-namespace \
            -f ./helm/myapp/values-prod.yaml \
            --set image.tag=${{ github.sha }} \
            --wait --timeout 5m

      # デプロイ確認
      - name: Verify deployment
        run: |
          kubectl rollout status deployment/myapp -n production
          kubectl get pods -n production -l app=myapp
```

### GitHub Actions - Container Apps

```yaml
# .github/workflows/deploy-containerapp.yml
name: Deploy to Container Apps

on:
  push:
    branches: [main]

env:
  ACR_NAME: myacr
  IMAGE_NAME: myapp
  CONTAINERAPP_NAME: ca-myapp-prod
  RESOURCE_GROUP: rg-myapp-prod

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: azure/login@v2
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      # ACR ビルド (サーバーサイドビルド)
      - name: Build on ACR
        run: |
          az acr build \
            --registry ${{ env.ACR_NAME }} \
            --image ${{ env.IMAGE_NAME }}:${{ github.sha }} \
            .

      # Container App 更新
      - name: Update Container App
        run: |
          az containerapp update \
            --resource-group ${{ env.RESOURCE_GROUP }} \
            --name ${{ env.CONTAINERAPP_NAME }} \
            --image ${{ env.ACR_NAME }}.azurecr.io/${{ env.IMAGE_NAME }}:${{ github.sha }}

      # リビジョン確認
      - name: Check revision
        run: |
          az containerapp revision list \
            --resource-group ${{ env.RESOURCE_GROUP }} \
            --name ${{ env.CONTAINERAPP_NAME }} \
            --output table
```

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
