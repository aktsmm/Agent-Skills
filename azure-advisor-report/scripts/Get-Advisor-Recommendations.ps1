param(
    [Parameter(Mandatory = $true)]
    [string]$SubscriptionId,

    [string]$OutputDir = "output",

    [string]$ApiVersion = "2025-01-01"
)

$ErrorActionPreference = "Stop"

$categories = @(
    @{ Name = "Cost"; File = "advisor-cost.json" },
    @{ Name = "Security"; File = "advisor-security.json" },
    @{ Name = "HighAvailability"; File = "advisor-reliability.json" },
    @{ Name = "OperationalExcellence"; File = "advisor-opex.json" }
)

New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null

$visible = az account list --all --query "[?id=='$SubscriptionId'].{name:name,id:id,tenantId:tenantId,state:state}" -o json | ConvertFrom-Json
if (-not $visible -or @($visible).Count -eq 0) {
    throw "Subscription '$SubscriptionId' is not visible in the current Azure CLI login context."
}

az account set --subscription $SubscriptionId | Out-Null
$account = az account show --query "{name:name,id:id,tenantId:tenantId}" -o json | ConvertFrom-Json
$account | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $OutputDir "advisor-preflight.json") -Encoding UTF8

$token = az account get-access-token --resource https://management.azure.com/ --query accessToken -o tsv
$httpClient = [System.Net.Http.HttpClient]::new()
$httpClient.Timeout = [TimeSpan]::FromSeconds(60)
$httpClient.DefaultRequestHeaders.Authorization = [System.Net.Http.Headers.AuthenticationHeaderValue]::new("Bearer", $token)

function Get-RecommendationsByCategory {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Category
    )

    $encodedFilter = [System.Uri]::EscapeDataString("Category eq '$Category'")
    $nextUrl = "https://management.azure.com/subscriptions/$SubscriptionId/providers/Microsoft.Advisor/recommendations?api-version=$ApiVersion&`$filter=$encodedFilter"
    $items = New-Object System.Collections.Generic.List[object]

    while ($nextUrl) {
        $json = $httpClient.GetStringAsync($nextUrl).GetAwaiter().GetResult()
        $response = $json | ConvertFrom-Json
        foreach ($item in @($response.value)) {
            $items.Add($item)
        }
        $nextUrl = $response.nextLink
    }

    return $items
}

try {
    foreach ($category in $categories) {
        $items = Get-RecommendationsByCategory -Category $category.Name
        $outputPath = Join-Path $OutputDir $category.File
        if (@($items).Count -eq 0) {
            Set-Content -LiteralPath $outputPath -Value '[]' -Encoding UTF8
        }
        else {
            $items | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $outputPath -Encoding UTF8
        }
        Write-Output ("{0}={1}" -f $category.Name, @($items).Count)
    }
}
finally {
    $httpClient.Dispose()
}