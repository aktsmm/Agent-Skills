# データ取得手順

## 前提条件

- Azure CLI (`az`) がインストール済み
- 対象サブスクリプションへの Reader 以上の権限（Azure Copilot 経由含む）

## Step 1: 日付確認・対象月設定

```powershell
Get-Date -Format "yyyy-MM-dd (ddd)"
```

引数で対象月が指定されていればその月を使用、省略時は当月。
コスト取得期間: 対象月の6ヶ月前〜対象月末。

## Step 2: テナント/サブスクリプション切替

```powershell
az login --tenant {tenantId}
az account set --subscription {subscriptionId}
az account show --query "{name:name, id:id, tenantId:tenantId}" -o json
```

> ⚠️ 複数サブスクリプションが別テナントにある場合、テナントごとに `az login` が必要。

## Step 2.5: 事前チェック（API 経路の確定）

コスト系 API は「サブスクリプションが見えている」だけでは足りない。**対象テナントで見えているか / offer type は何か / どの API がその offer type をサポートするか** を先に確定する。

### 2.5.1 サブスクリプション可視性チェック

```powershell
az account list --all --query "[?id=='{subscriptionId}'].{name:name,id:id,tenantId:tenantId,state:state}" -o json
```

- 空配列なら、まず tenant を見直す
- `az account set --subscription {subscriptionId}` が失敗する状態では、後続のコスト API を叩かない

### 2.5.2 offer type / billing 情報チェック

```powershell
az rest --method get `
    --url "https://management.azure.com/subscriptions/{subscriptionId}/providers/Microsoft.Billing/billingProperty/default?api-version=2024-04-01" `
    -o json > billing-property.json
```

- `billing-property.json` で billing 系の前提を保存しておく
- 詳細レポート API 可否に迷う場合は、この時点で subscription type / offer type を確認する

### 2.5.3 API 選択の決定木

1. まず `Microsoft.CostManagement/query` を試す
2. `429 Too many requests` なら短時間の多重再試行はせず、**別経路へ切り替える**
3. `generateCostDetailsReport` が `422 Unsupported request` かつ `offer type: WebDirect` なら、**Cost Details API は使えない前提**で legacy Usage Details API に切り替える
4. WebDirect では、月次総額と TopN 集計は `Microsoft.Consumption/usageDetails` のページング取得を使う

> 実績ベースの知見: WebDirect では `CostManagement/query` が 429、`generateCostDetailsReport` が 422 で塞がるケースがある。その場合でも legacy Usage Details API から月次集計は取得できる。

## Step 3: Advisor 推奨取得

Advisor 取得も、コスト取得と同様に **subscription 可視性と取得経路の確定** を先に行う。

### Step 3.1: Advisor preflight

```powershell
az account list --all --query "[?id=='{subscriptionId}'].{name:name,id:id,tenantId:tenantId,state:state}" -o json
az account set --subscription {subscriptionId}
az account show --query "{name:name,id:id,tenantId:tenantId}" -o json
```

- 空配列なら tenant を見直す
- `az account set --subscription {subscriptionId}` が失敗する状態では Advisor 取得も進めない
- 取得前に subscription context がズレていないことを毎回確認する

### Step 3.2: CLI と REST の役割分担

- `az advisor recommendation list` は手軽だが、CLI help 上の `--category` は `Cost`, `HighAvailability`, `Performance`, `Security` しか出ない
- 一方、REST の recommendation list は `OperationalExcellence` を正式サポートする
- **4 カテゴリ完全取得が必要なこの skill では、REST を正本の取得経路とする**

> 実績ベースの知見: CLI help に `OperationalExcellence` が出ないため、CLI だけに依存すると OpEx を取り漏らすリスクがある。

各カテゴリごとに取得:

```powershell
az advisor recommendation list --category Cost -o json > advisor-cost.json
az advisor recommendation list --category Security -o json > advisor-security.json
az advisor recommendation list --category HighAvailability -o json > advisor-reliability.json
az advisor recommendation list --category OperationalExcellence -o json > advisor-opex.json
```

> ただし `OperationalExcellence` は CLI help と不整合があるため、実運用では下記 REST helper を優先する。

### Step 3.3: 推奨取得（推奨: REST helper）

```powershell
.\scripts\Get-Advisor-Recommendations.ps1 -SubscriptionId {subscriptionId} -OutputDir output
```

出力ファイル:

- `advisor-cost.json`
- `advisor-security.json`
- `advisor-reliability.json`
- `advisor-opex.json`
- `advisor-preflight.json`

### Step 3.4: REST fallback

REST endpoint は次を使う。

```http
GET https://management.azure.com/subscriptions/{subscriptionId}/providers/Microsoft.Advisor/recommendations?api-version=2025-01-01&$filter=Category eq 'OperationalExcellence'
```

- filter 対象は `Category`
- category 値は `Cost`, `Security`, `HighAvailability`, `OperationalExcellence`
- `OperationalExcellence` は REST の正式カテゴリとして扱う
- ページングがある場合は `nextLink` をたどる

### Step 3.5: 失敗時の切り分け

- `az advisor recommendation list` が category 不正扱い、または help に category が出ない:
  - REST helper に切り替える
- `az account set --subscription ...` 失敗:
  - tenant / subscription 可視性の問題。Step 2 へ戻る
- 一部カテゴリだけ 0 件:
  - 取得失敗と決め打ちせず、まず `0件（推奨なし）` を候補にする
  - ただし OpEx だけ 0 件で CLI 経路を使っていた場合は REST で再確認する

### カテゴリ別集計

```powershell
$data = Get-Content "advisor-{category}.json" -Raw | ConvertFrom-Json
$data | Group-Object impact | ForEach-Object {
    Write-Host "$($_.Name): $($_.Count)"
}
```

### High Impact の推奨別グルーピング

```powershell
$data | Where-Object { $_.impact -eq 'High' } |
    Group-Object { $_.shortDescription.problem } |
    Sort-Object Count -Descending |
    ForEach-Object {
        Write-Host "[$($_.Count)件] $($_.Name)"
        $_.Group | Select-Object -First 3 | ForEach-Object {
            Write-Host "  -> $($_.impactedValue)"
        }
    }
```

### RI 推奨の注意

CLI は lookback(7/30/60日) × term(P1Y/P3Y) の組み合わせ別にレコードを返す。
**Portal の値を SSOT とし、CLI は参考値として使用する。**

## Step 4: Cost Management API（月別・サービス別）

> まずは `Microsoft.CostManagement/query` を使う。`Get-AzConsumptionUsageDetail` は subscription scope で `BadRequest` や `Subscription scope usage is not supported for current api version` になることがあり、その場合は legacy cmdlet で粘らず REST に切り替える。

### Step 4.1: 半年コスト分析の推奨取得順

半年分のコスト分析では、最初から `ResourceId` / `ResourceGroupName` / `ResourceType` まで全月分を一括取得しない。Cost Management Query API は短時間に粒度の細かい query を連打すると `429 Too Many Requests` になりやすいため、次の順序で段階的に取得する。

1. **月次 × ServiceName** を各月 1 クエリで取得する
   - `timeframe=Custom`
   - `timePeriod.from={YYYY-MM-01}`
   - `timePeriod.to={翌月のYYYY-MM-01}`（終了日は排他的に扱う）
   - `granularity=None`
   - `grouping=ServiceName`
2. 月別合計は、`total` query が 429 になる場合でも **ServiceName 行の合計を正本**として算出する
3. サービス別推移でスパイク月・支配サービスを特定する
4. 深掘りはスパイク月だけ `ResourceGroupName` → `ResourceId` の順で取得する
5. `ResourceId` / `ResourceGroupName` の全月一括取得は最後の手段にし、実行する場合は月ごとに十分な待機時間を入れる

この順序にすると、まず「何が何割を占めるか」を安定して把握でき、詳細 API のスロットリングで分析全体が止まるリスクを下げられる。

実績ベースの注意:

- `Azure Firewall`、`VPN Gateway`、`Load Balancer`、`Microsoft Defender for Cloud`、`Virtual Network`、`Storage`、`Backup` はコスト上位になりやすいため、月次推移に必ず含める
- `VPN Gateway` や `Azure Firewall` は短期間でも大きな割合を占めるため、スパイク月では優先して RG / ResourceId 明細を確認する
- `Azure Cognitive Search`、`Recovery Services vault`、`Container Registry`、`Cognitive Services S0` は小規模環境でも上位に出ることがある。上位表では **ServiceName だけでなく ResourceType / リソース種類** も併記する
- 削除候補を出す場合でも、この skill は読み取り専用レポート生成用である。`Do Not Delete` タグ、削除ロック、Backup vault、Activity Log Alerts、NetworkWatcher、managed resource group（`MC_*`, `ME_*`, Databricks managed RG など）は「要確認」または「親リソースから確認」として扱い、削除実行はしない
- ユーザーまたは運用担当が「アプリで使用中」と明言したリソースは、コスト上位でも削除候補にしない。レポートでは「利用中のため維持」「必要ならSKU/容量見直し」として扱う

```powershell
$subId = "{subscriptionId}"
$bodyFile = Join-Path $env:TEMP "cost-query.json"
@{
    type = "ActualCost"
    dataset = @{
        granularity = "None"
        aggregation = @{ totalCost = @{ name = "PreTaxCost"; function = "Sum" } }
        grouping = @(@{ type = "Dimension"; name = "ServiceName" })
    }
    timeframe = "Custom"
    timePeriod = @{ from = "{YYYY-MM-01}"; to = "{翌月のYYYY-MM-01}" }
} | ConvertTo-Json -Depth 5 | Set-Content $bodyFile -Encoding utf8

az rest --method post `
    --url "https://management.azure.com/subscriptions/$subId/providers/Microsoft.CostManagement/query?api-version=2025-03-01" `
    --body "@$bodyFile" --headers "Content-Type=application/json" -o json > cost-monthly.json
```

> 通貨は日本リージョンの場合 **JPY** で返る。
> 既存環境で `2025-03-01` が通らない場合は `2023-11-01` または `2023-03-01` を試す。

### Step 4.2: 上位リソース分析（ResourceId + 種類の併記）

サービス別の支配要因が分かったら、対象月または当月 MTD だけ `ResourceId` 粒度で取得する。レポートの上位リソース表には、最低限 `Cost`, `割合`, `ResourceGroupName`, `ServiceName`, `ResourceName`, `ResourceType`, `現在状態` を含める。

```powershell
$bodyFile = Join-Path $env:TEMP "cost-resource-query.json"
@{
    type = "ActualCost"
    timeframe = "MonthToDate"
    dataset = @{
        granularity = "None"
        aggregation = @{ totalCost = @{ name = "PreTaxCost"; function = "Sum" } }
        grouping = @(
            @{ type = "Dimension"; name = "ResourceId" },
            @{ type = "Dimension"; name = "ResourceGroupName" },
            @{ type = "Dimension"; name = "ServiceName" }
        )
    }
} | ConvertTo-Json -Depth 8 | Set-Content $bodyFile -Encoding utf8

az rest --method post `
    --url "https://management.azure.com/subscriptions/$subId/providers/Microsoft.CostManagement/query?api-version=2025-03-01" `
    --body "@$bodyFile" --headers "Content-Type=application/json" -o json > cost-resource-mtd.json

az resource list --subscription $subId `
    --query "[].{id:id,type:type,name:name,resourceGroup:resourceGroup,sku:sku.name,kind:kind}" `
    -o json > current-resources.json
```

集計時は `ResourceId` を `current-resources.json` に join し、次を判定する。

- `current`: 現在も存在する
- `deleting`: Resource Group が `Deleting`
- `deletedOrNotFound`: MTD コストには残るが、現在は存在しない

注意: Cost Management の MonthToDate / 過去月データは **発生済みコスト** であり、削除済みリソースも当月明細に残る。削除後の効果を見る場合は、当月 MTD だけでなく翌日以降または翌月の発生額で確認する。

### Step 4.3: Backup / RSV 系リソースの削除完了判定

Recovery Services vault / Backup vault / Data Protection Backup Vault は、削除要求が通っても即時に RG から消えないことがある。コスト削減レポートや削除後確認では、次の順で状態を分けて記録する。

1. `Microsoft.RecoveryServices/vaults` が残っているか確認する
2. `Microsoft.DataProtection/backupVaults` が残っているか確認する
3. Recovery Services vault は protected item / container / storage account registration が残っていないか確認する
4. Backup vault は `deletedBackupInstances` を確認し、`SoftDeleted` と `scheduledPurgeTime` を記録する
5. `scheduledPurgeTime` がある場合、削除は「完了」ではなく **soft delete retention 待ち** として扱う

```powershell
# Recovery Services / Data Protection の残存確認
az resource list --subscription $subId `
    --query "[?contains(type, 'RecoveryServices') || contains(type, 'DataProtection')].{RG:resourceGroup,Type:type,Name:name}" `
    -o table

# Data Protection Backup Vault の soft-deleted backup instance 確認
$vaultId = "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroup}/providers/Microsoft.DataProtection/backupVaults/{backupVaultName}"
az rest --method get `
    --url "https://management.azure.com${vaultId}/deletedBackupInstances?api-version=2023-01-01" `
    --query "value[].{name:name,state:properties.currentProtectionState,purge:properties.deletionInfo.scheduledPurgeTime,billingEnd:properties.deletionInfo.billingEndDate}" `
    -o table
```

実績ベースの注意:

- Recovery Services vault は、VM backup / Azure Files backup などの保護停止 + backup data 削除後も、container / storage account registration が残ると vault delete が拒否される
- Data Protection Backup Vault は、backup instance 削除後に `SoftDeleted` として残り、`scheduledPurgeTime` まで vault delete が拒否されることがある
- RG が `Deleting` になっている間は vault の soft delete 設定変更が `ResourceGroupBeingDeleted` で拒否されることがある
- 最新 API では Backup Vault の soft delete が Always-On 前提になる場合があり、`DppAlwaysOnSoftDeleteStateMandatory` が出たら即時削除ではなく retention 待ちとして報告する
- レポートでは「削除要求済み」「保護項目削除済み」「soft delete retention 待ち」「完全削除済み」を分けて書く

公式 Docs:

- Delete Azure Backup Recovery Services vault: https://learn.microsoft.com/en-us/azure/backup/backup-azure-delete-vault
- Azure Backup soft delete / secure by default: https://learn.microsoft.com/en-us/azure/backup/backup-azure-security-feature-cloud

### `query` が 429 のとき

- `429 Too many requests` が返る環境では、同一ターン内での短時間連打を避ける
- その場で必要な値が「月次総額」「サービス別 TopN」であれば、まず **月次 × ServiceName の単月 query** に絞る
- `ResourceId` / `ResourceGroupName` / `ResourceType` の細粒度 query は、スパイク月が特定できるまで実行しない
- `ServiceName` query が 429 でも、時間を空けた `ResourceId + ResourceGroupName + ServiceName` query が通る場合がある。失敗結果は保存し、API バージョン変更だけを連打しない
- 単月 ServiceName query でも 429 が続く場合は、後述の legacy Usage Details 集計へ切り替える
- デバッグ証跡は JSON に保存し、チャットには値だけを出す

## Step 4.5: Cost Details API（使える offer type の場合のみ）

`Microsoft.CostManagement/generateCostDetailsReport` は非同期で詳細 CSV を返す。
ただし **offer type により非対応** があるため、`422 Unsupported request` を返したら粘らず fallback する。

```powershell
$token = az account get-access-token --resource https://management.azure.com/ --query accessToken -o tsv
$headers = @{ Authorization = "Bearer $token"; 'Content-Type' = 'application/json' }
$body = '{"metric":"ActualCost","timePeriod":{"start":"{YYYY-MM-01}","end":"{YYYY-MM-DD}"}}'

$resp = Invoke-WebRequest -Method Post `
    -Uri "https://management.azure.com/subscriptions/{subscriptionId}/providers/Microsoft.CostManagement/generateCostDetailsReport?api-version=2025-03-01" `
    -Headers $headers -Body $body

$resp.Headers.Location
$resp.Headers.'Retry-After'
```

- `Location` が返れば poll して CSV を取得する
- `422` で `offer type: WebDirect` が含まれる場合は **この経路を打ち切る**

## Step 4.6: legacy Usage Details API（WebDirect / fallback 用）

`query` が 429、Cost Details API が offer type 非対応のときは、legacy の `Microsoft.Consumption/usageDetails` で月次集計を作る。

### 1件サンプル取得

```powershell
$token = az account get-access-token --resource https://management.azure.com/ --query accessToken -o tsv
$headers = @{ Authorization = "Bearer $token" }
$uri = "https://management.azure.com/subscriptions/{subscriptionId}/providers/Microsoft.Consumption/usageDetails?metric=ActualCost&`$filter=properties%2FusageStart%20ge%20'{YYYY-MM-01}'%20and%20properties%2FusageEnd%20le%20'{YYYY-MM-DD}'&`$top=1&api-version=2019-10-01"

Invoke-RestMethod -Method Get -Uri $uri -Headers $headers |
    ConvertTo-Json -Depth 20 |
    Set-Content usage-details-top1.json -Encoding utf8
```

確認ポイント:

- `properties.cost`
- `properties.billingCurrency`
- `properties.consumedService`
- `nextLink`

### 全ページ集計（推奨: Python helper）

```powershell
$env:AZURE_ACCESS_TOKEN = az account get-access-token --resource https://management.azure.com/ --query accessToken -o tsv
py -3 .\scripts\get-legacy-usage-summary.py {subscriptionId} {YYYY-MM-01} {YYYY-MM-DD} usage-summary.json

# ページングやローカル接続枯渇が不安定な場合は、単月単発 + 大きめ page size でページングを避ける
py -3 .\scripts\get-legacy-usage-summary.py {subscriptionId} {YYYY-MM-01} {YYYY-MM-DD} usage-summary.json 5000
```

- 出力は `usage-summary.json` に保存する
- `nextLink` をたどって全ページ集計する
- 集計キーは `consumedService` を優先し、欠損時のみ `product` / `resourceName` にフォールバックする
- 通貨は `billingCurrency` を使う

### 実装上の注意

- page size は 100 程度から始める。ページングで `WinError 10048` が出る場合は、単月単発で `5000` 程度へ上げ、1ページ取得を優先する
- `nextLink` は相対 URL を返すことがあるため、`https://management.azure.com` を補う
- `nextLink` 内に空白が残る場合があるので `%20` へエンコードする
- Windows / GSA 環境では `az rest` や Azure CLI Python module を月ごと・ページごとに連打すると `WinError 10048` になることがある。`az account get-access-token` はトークン取得だけに使い、Usage Details は Python `http.client` で単月単発取得する
- 複数 tenant を同時ログインできない環境では、tenant ごとに MFA → その tenant のサブスクだけ収集 → 次 tenant へ切り替える。未認証 tenant を混ぜて一括収集しない
- 件数が多いサブスクリプションではページ数と総件数も一緒に保存する

### 失敗時の切り分け

- `429 Too many requests`:
  - 同じ月・同じ scope で query を連打しない
  - 月次レポート用途なら legacy `usageDetails` へ切り替えて総額と TopN を先に確定する
- `422 Unsupported request. offer type: WebDirect ...`:
  - `generateCostDetailsReport` はこのサブスクでは使わない
  - legacy `usageDetails` を使う
- `The subscription ... doesn't exist in cloud 'AzureCloud'`:
  - サブスク未可視。tenant 切り替えからやり直す

- Usage Details が 200 + `value: []` / `itemCount: 0`:
  - 認証エラーではなく、subscription scope に billed usage 明細が無い可能性が高い
  - Azure RBAC を確認し、Owner / Contributor / Reader があるなら resource/subscription 権限不足とは切り分ける
  - MCA / Internal / DevTest / Sandbox などでは billing profile / invoice section scope 側に費用が寄る可能性があるため、`billingProperty.default` の `billingProfileId` / `invoiceSectionId` を確認する
- billing role assignments API が `403 Forbidden`:
  - subscription RBAC ではなく billing scope の権限不足。Billing account / Billing profile / Invoice section の Reader 以上に相当する権限を持つアカウントで確認する

### 実務で使う集計列

- `Cost` または `PreTaxCost` のどちらが返っているかを確認する
- `Currency` を必ず併記する
- サービス別集計は `ServiceName`、月別集計は `Month` または `UsageStartTime` を使う

### 月別合計の集計

```powershell
$raw = Get-Content "cost-monthly.json" -Raw | ConvertFrom-Json
$monthly = @{}
foreach ($row in $raw.properties.rows) {
    $month = ($row[1] -split ' ')[0]
    $cost = [double]$row[0]
    if ($monthly.ContainsKey($month)) { $monthly[$month] += $cost }
    else { $monthly[$month] = $cost }
}
$monthly.GetEnumerator() | Sort-Object Name | ForEach-Object {
    Write-Host ("{0}: {1:N0}" -f $_.Name, $_.Value)
}
```

## Step 5: 全サブスクリプションで繰り返し

複数サブスクリプションがある場合、Step 2〜4 を各サブスクで実行する。

> ただしサブスクごとに offer type と API の通り方が違う。**Step 2.5 の事前チェックを各サブスクで毎回実施**してから取得経路を選ぶこと。
