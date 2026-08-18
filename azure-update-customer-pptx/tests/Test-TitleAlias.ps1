param()

$ErrorActionPreference = 'Stop'
$skillRoot = Split-Path $PSScriptRoot -Parent
Import-Module (Join-Path $skillRoot 'scripts\PptxCommon.psm1') -Force

$items = @(
    [pscustomobject]@{ title = 'Generally Available: Example Firewall capability'; titleJa = 'Azure Firewallの新機能を提供' },
    [pscustomobject]@{ title = 'Public Preview: Example Gateway capability'; titleJa = 'Gatewayの新機能をプレビュー提供' }
)

function Assert-Equal {
    param($Actual, $Expected, [string]$Message)
    if ($Actual -ne $Expected) { throw "$Message (actual=$Actual, expected=$Expected)" }
}

function Assert-Throws {
    param([scriptblock]$Action, [string]$Message)
    try {
        & $Action
    } catch {
        return
    }
    throw $Message
}

$raw = Find-ClassificationItemBySlideTitle -SlideTitle 'Generally Available: Example Firewall capability' -Items $items
$display = Find-ClassificationItemBySlideTitle -SlideTitle 'Azure Firewallの新機能を提供' -Items $items
$unrelated = Find-ClassificationItemBySlideTitle -SlideTitle 'Azure Storageの新機能を提供' -Items $items
$shortCandidate = [pscustomobject]@{ title = 'Short source'; titleJa = '短題' }
$shortPrefixMatch = Test-ClassificationTitleMatch -SlideTitle '短題を拡張' -Item $shortCandidate

Assert-Equal $raw.title $items[0].title 'raw title must resolve'
Assert-Equal $display.title $items[0].title 'Japanese display title must resolve to raw join key'
Assert-Equal ($null -eq $unrelated) $true 'unrelated title must not resolve'
Assert-Equal $shortPrefixMatch $false 'short display title must not use prefix matching'

$prefixCollisionItems = @(
    [pscustomobject]@{ title = 'Raw capability alpha'; titleJa = 'ネットワーク接続の高度な機能' },
    [pscustomobject]@{ title = 'Raw capability beta'; titleJa = 'ネットワーク接続の高度な機能を管理' }
)
$prefixCollisionTitle = 'ネットワーク接続の高度な機能を管理'
$prefixCollisionMatches = @($prefixCollisionItems | Where-Object { Test-ClassificationTitleMatch -SlideTitle $prefixCollisionTitle -Item $_ -PrefixLength 25 })
$exactCollisionResolution = Find-ClassificationItemBySlideTitle -SlideTitle $prefixCollisionTitle -Items $prefixCollisionItems
Assert-Equal $prefixCollisionMatches.Count 2 'Fix-Labels must detect both prefix-collision candidates before moving a slide'
Assert-Equal $exactCollisionResolution.title 'Raw capability beta' 'exact display title must win over prefix fallback'

$duplicateItems = @(
    [pscustomobject]@{ title = 'Raw capability one'; titleJa = '共通の表示タイトル' },
    [pscustomobject]@{ title = 'Raw capability two'; titleJa = '共通の表示タイトル' }
)
Assert-Throws { Find-ClassificationItemBySlideTitle -SlideTitle '共通の表示タイトル' -Items $duplicateItems } 'duplicate display titles must throw'

Write-Host 'Title alias tests passed'