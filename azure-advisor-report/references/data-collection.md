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

## Step 3: Advisor 推奨取得

各カテゴリごとに取得:

```powershell
az advisor recommendation list --category Cost -o json > advisor-cost.json
az advisor recommendation list --category Security -o json > advisor-security.json
az advisor recommendation list --category HighAvailability -o json > advisor-reliability.json
az advisor recommendation list --category OperationalExcellence -o json > advisor-opex.json
```

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

```powershell
$subId = "{subscriptionId}"
$bodyFile = Join-Path $env:TEMP "cost-query.json"
@{
    type = "ActualCost"
    dataSet = @{
        granularity = "Monthly"
        aggregation = @{ totalCost = @{ name = "Cost"; function = "Sum" } }
        grouping = @(@{ type = "Dimension"; name = "ServiceName" })
    }
    timeframe = "Custom"
    timePeriod = @{ from = "{6ヶ月前の月初}"; to = "{対象月末}" }
} | ConvertTo-Json -Depth 5 | Set-Content $bodyFile -Encoding utf8

az rest --method post `
    --url "https://management.azure.com/subscriptions/$subId/providers/Microsoft.CostManagement/query?api-version=2023-11-01" `
    --body "@$bodyFile" --headers "Content-Type=application/json" -o json > cost-monthly.json
```

> 通貨は日本リージョンの場合 **JPY** で返る。

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
