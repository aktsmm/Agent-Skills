param()

$ErrorActionPreference = 'Stop'
$skillRoot = Split-Path $PSScriptRoot -Parent
Import-Module (Join-Path $skillRoot 'scripts\PptxCommon.psm1') -Force

function Assert-Equal {
    param($Actual, $Expected, [string]$Message)
    if ($Actual -ne $Expected) { throw "$Message (actual=$Actual, expected=$Expected)" }
}

function New-RegionData {
    param([string]$Status, [bool]$Verified, [string]$Evidence)
    return [pscustomobject]@{
        regions = [pscustomobject]@{
            sample = [pscustomobject]@{
                status = $Status
                verified = $Verified
                source = 'https://learn.microsoft.com/azure/example'
                evidence = $Evidence
            }
        }
    }
}

$resolved = Get-RegionReviewIssues -RegionData (New-RegionData 'Japan East / West 対応' $true '【判定レベル: リージョン限定記載なし】制限なし') -DeliveryMode
$unknown = Get-RegionReviewIssues -RegionData (New-RegionData 'unknown' $true '確認済み') -DeliveryMode
$missingEvidence = Get-RegionReviewIssues -RegionData (New-RegionData 'Japan East / West 対応' $true '【判定レベル: 根拠未取得】') -DeliveryMode
$unverified = Get-RegionReviewIssues -RegionData (New-RegionData 'Japan East / West 対応' $false '確認済み') -DeliveryMode
$draftUnknown = Get-RegionReviewIssues -RegionData (New-RegionData 'unknown' $true '確認中')

Assert-Equal @($resolved).Count 0 'resolved review must pass delivery mode'
Assert-Equal @($unknown).Count 1 'unknown status must fail delivery mode'
Assert-Equal @($missingEvidence).Count 1 'missing evidence tier must fail delivery mode'
Assert-Equal @($unverified).Count 1 'unverified review must fail'
Assert-Equal @($draftUnknown).Count 0 'draft mode may retain unresolved status'

Write-Host 'Region review tests passed'