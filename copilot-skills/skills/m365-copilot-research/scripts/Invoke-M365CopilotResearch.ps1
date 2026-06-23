[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [ValidateSet('root', 'retrieve', 'chat')]
    [string]$Mode = 'retrieve',

    [Parameter(Mandatory = $false)]
    [string]$Query,

    [Parameter(Mandatory = $false)]
    [ValidateSet('sharePoint', 'oneDriveBusiness', 'externalItem')]
    [string]$DataSource = 'sharePoint',

    [Parameter(Mandatory = $false)]
    [ValidateRange(1, 25)]
    [int]$MaxResults = 5,

    [Parameter(Mandatory = $false)]
    [string]$TenantId,

    [Parameter(Mandatory = $false)]
    [string]$AccessToken,

    [Parameter(Mandatory = $false)]
    [switch]$Beta,

    [Parameter(Mandatory = $false)]
    [switch]$Raw
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-GraphAccessToken {
    param(
        [string]$ProvidedToken,
        [string]$RequestedTenantId
    )

    if ($ProvidedToken) {
        return $ProvidedToken
    }

    if ($env:M365_COPILOT_GRAPH_TOKEN) {
        return $env:M365_COPILOT_GRAPH_TOKEN
    }

    $az = Get-Command az -ErrorAction SilentlyContinue
    if (-not $az) {
        throw 'No access token was provided and Azure CLI was not found. Provide -AccessToken or set M365_COPILOT_GRAPH_TOKEN.'
    }

    $args = @('account', 'get-access-token', '--resource', 'https://graph.microsoft.com/', '--query', 'accessToken', '-o', 'tsv')
    if ($RequestedTenantId) {
        $args = @('account', 'get-access-token', '--tenant', $RequestedTenantId, '--resource', 'https://graph.microsoft.com/', '--query', 'accessToken', '-o', 'tsv')
    }

    $token = & az @args
    if ($LASTEXITCODE -ne 0 -or -not $token) {
        throw 'Failed to acquire a Microsoft Graph access token. Use a dedicated Entra app/MSAL flow with the required delegated scopes.'
    }

    return ($token | Select-Object -First 1)
}

function Invoke-GraphJson {
    param(
        [ValidateSet('GET', 'POST')]
        [string]$Method,
        [string]$Uri,
        [hashtable]$Headers,
        [object]$Body
    )

    try {
        if ($Body) {
            $json = $Body | ConvertTo-Json -Depth 20
            return Invoke-RestMethod -Method $Method -Uri $Uri -Headers $Headers -Body $json -ContentType 'application/json' -TimeoutSec 120
        }

        return Invoke-RestMethod -Method $Method -Uri $Uri -Headers $Headers -TimeoutSec 120
    }
    catch {
        $message = $_.ErrorDetails.Message
        if (-not $message) {
            $message = $_.Exception.Message
        }

        throw "Graph request failed: $Method $Uri`n$message"
    }
}

function ConvertTo-EvidencePack {
    param(
        [object]$Response,
        [string]$ResearchQuery,
        [string]$Source
    )

    $hits = @()
    if ($Response.retrievalHits) {
        $hits = @($Response.retrievalHits)
    }

    $lines = New-Object System.Collections.Generic.List[string]
    $lines.Add('## M365 Copilot Evidence Pack')
    $lines.Add('')
    $lines.Add("Query: $ResearchQuery")
    $lines.Add('Mode: retrieve')
    $lines.Add("Data source: $Source")
    $lines.Add('')
    $lines.Add('### Findings')
    $lines.Add('')

    if ($hits.Count -eq 0) {
        $lines.Add('No retrieval hits were returned.')
    }
    else {
        $index = 1
        foreach ($hit in $hits) {
            $url = if ($hit.webUrl) { $hit.webUrl } else { '(no URL returned)' }
            $label = '(none returned)'
            if ($hit.sensitivityLabel -and $hit.sensitivityLabel.displayName) {
                $label = $hit.sensitivityLabel.displayName
            }

            $excerpt = ''
            if ($hit.extracts) {
                $extract = @($hit.extracts) | Sort-Object -Property relevanceScore -Descending | Select-Object -First 1
                if ($extract -and $extract.text) {
                    $excerpt = ($extract.text -replace '\s+', ' ').Trim()
                }
            }

            if ($excerpt.Length -gt 700) {
                $excerpt = $excerpt.Substring(0, 700) + '...'
            }

            $lines.Add("$index. Retrieved evidence")
            $lines.Add("   Source: $url")
            $lines.Add("   Evidence: `"$excerpt`"")
            $lines.Add("   Label: $label")
            $lines.Add('')
            $index++
        }
    }

    $lines.Add('### Gaps / Caveats')
    $lines.Add('')
    $lines.Add('- Retrieval API returns evidence chunks, not a fully verified final answer.')
    $lines.Add('- Results depend on Microsoft 365 permissions, semantic index coverage, and API preview behavior.')

    return ($lines -join [Environment]::NewLine)
}

if ($Mode -ne 'root' -and -not $Query) {
    throw 'Query is required for retrieve and chat modes.'
}

$version = if ($Beta -or $Mode -eq 'chat') { 'beta' } else { 'v1.0' }
$baseUri = "https://graph.microsoft.com/$version/copilot"
$token = Get-GraphAccessToken -ProvidedToken $AccessToken -RequestedTenantId $TenantId
$headers = @{ Authorization = "Bearer $token" }

switch ($Mode) {
    'root' {
        $response = Invoke-GraphJson -Method GET -Uri $baseUri -Headers $headers
        if ($Raw) {
            $response | ConvertTo-Json -Depth 20
        }
        else {
            $response
        }
    }
    'retrieve' {
        $body = @{
            queryString = $Query
            dataSource = $DataSource
            maximumNumberOfResults = $MaxResults
        }

        $response = Invoke-GraphJson -Method POST -Uri "$baseUri/retrieval" -Headers $headers -Body $body
        if ($Raw) {
            $response | ConvertTo-Json -Depth 20
        }
        else {
            ConvertTo-EvidencePack -Response $response -ResearchQuery $Query -Source $DataSource
        }
    }
    'chat' {
        $body = @{
            messages = @(
                @{
                    role = 'user'
                    content = $Query
                }
            )
        }

        $response = Invoke-GraphJson -Method POST -Uri "$baseUri/conversations" -Headers $headers -Body $body
        if ($Raw) {
            $response | ConvertTo-Json -Depth 20
        }
        else {
            $response | ConvertTo-Json -Depth 20
        }
    }
}
