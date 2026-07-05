<#
.SYNOPSIS
    レビューで特定した不要・重複アーティファクトを安全に削除する。

.DESCRIPTION
    既定はドライラン（何も削除しない）。実削除は -Apply を付けたときだけ。
    OneDrive のスペース入りパス対策で -LiteralPath を使用。
    重複 PPTX は SHA256 ハッシュが正本と一致した場合のみ削除する。

    削除対象は安全度でグループ分けしている:
      - SafeJunk   : 重複・コピーマーカー。既定で対象。
      - Regenerable: 再生成可能なダンプ/漏れ生成物。-IncludeRegenerable で対象。
    スクリプト(*.ps1)は対象に含めない（手動ツールキットのため）。

.EXAMPLE
    .\scripts\Remove-StaleArtifacts.ps1
    # ドライラン。削除予定を表示するだけ。

.EXAMPLE
    .\scripts\Remove-StaleArtifacts.ps1 -IncludeRegenerable -Apply
    # 再生成可能ファイルも含めて実削除。
#>
[CmdletBinding()]
param(
    [switch]$Apply,
    [switch]$IncludeRegenerable
)

$ErrorActionPreference = 'Stop'
$basePath = Split-Path -Parent $PSScriptRoot

function Resolve-Target {
    param([string]$Relative)
    Join-Path $basePath $Relative
}

# --- SafeJunk: 重複・コピーマーカー（既定で削除対象） ---
# repo ごとに対象を列挙する。例: '0330\<output>_20260330 - コピー.pptx'
$safeJunk = @(
)

# --- 重複 PPTX: 正本とハッシュ一致時のみ削除 ---
# 例: @{ Candidate = '<output>_20260202.pptx'; Canonical = '0202\<output>_20260202.pptx' }
$dupPptx = @(
)

# --- Regenerable: 再生成可能 / 生成漏れ（-IncludeRegenerable 時のみ） ---
$regenerable = @(
    'vm_skus.txt',
    'vm_skus_all.txt',
    '0120\manifest\analysis.json'
)

$toDelete = [System.Collections.Generic.List[string]]::new()

Write-Host "=== Remove-StaleArtifacts (Apply=$Apply, IncludeRegenerable=$IncludeRegenerable) ===" -ForegroundColor Cyan

foreach ($rel in $safeJunk) {
    $path = Resolve-Target $rel
    if (Test-Path -LiteralPath $path) {
        Write-Host "[SafeJunk]    $rel" -ForegroundColor Yellow
        $toDelete.Add($path)
    } else {
        Write-Host "[skip:absent] $rel" -ForegroundColor DarkGray
    }
}

foreach ($pair in $dupPptx) {
    $cand = Resolve-Target $pair.Candidate
    $canon = Resolve-Target $pair.Canonical
    if (-not (Test-Path -LiteralPath $cand)) {
        Write-Host "[skip:absent] $($pair.Candidate)" -ForegroundColor DarkGray
        continue
    }
    if (-not (Test-Path -LiteralPath $canon)) {
        Write-Host "[KEEP:no-canonical] $($pair.Candidate) (正本が見つからないため温存)" -ForegroundColor Red
        continue
    }
    $hCand = (Get-FileHash -LiteralPath $cand -Algorithm SHA256).Hash
    $hCanon = (Get-FileHash -LiteralPath $canon -Algorithm SHA256).Hash
    if ($hCand -eq $hCanon) {
        Write-Host "[DupPptx:hash-match] $($pair.Candidate)" -ForegroundColor Yellow
        $toDelete.Add($cand)
    } else {
        Write-Host "[KEEP:hash-differ] $($pair.Candidate) (正本と内容が異なる。手動確認推奨)" -ForegroundColor Red
    }
}

if ($IncludeRegenerable) {
    foreach ($rel in $regenerable) {
        $path = Resolve-Target $rel
        if (Test-Path -LiteralPath $path) {
            Write-Host "[Regenerable] $rel" -ForegroundColor Yellow
            $toDelete.Add($path)
        } else {
            Write-Host "[skip:absent] $rel" -ForegroundColor DarkGray
        }
    }
}

Write-Host ""
if ($toDelete.Count -eq 0) {
    Write-Host "削除対象なし。" -ForegroundColor Green
    return
}

if (-not $Apply) {
    Write-Host "DRY-RUN: 上記 $($toDelete.Count) 件が削除対象。実削除は -Apply を付与。" -ForegroundColor Cyan
    return
}

foreach ($path in $toDelete) {
    Remove-Item -LiteralPath $path -Force
    Write-Host "DELETED: $path" -ForegroundColor Green
}
Write-Host "完了: $($toDelete.Count) 件削除。" -ForegroundColor Green
