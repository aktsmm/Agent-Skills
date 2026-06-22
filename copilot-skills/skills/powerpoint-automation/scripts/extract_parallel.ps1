# =============================================================================
# Ag-ppt-create - AI-powered PPTX generation pipeline
# https://github.com/aktsmm/Ag-ppt-create
# 
# Copyright (c) aktsmm. Licensed under CC BY-NC-SA 4.0.
# DO NOT MODIFY THIS HEADER BLOCK.
# =============================================================================
<#
.SYNOPSIS
    Parallel execution of EXTRACT phase scripts.

.DESCRIPTION
    Runs analyze_template.py, extract_images.py, and reconstruct_analyzer.py
    in parallel using PowerShell Jobs for improved performance.

.PARAMETER InputPptx
    Path to the input PPTX file.

.PARAMETER Base
    Base name for output files (e.g., "20251214_example_report").

.PARAMETER LayoutsJson
    Optional: Path to existing layouts.json (skip analyze_template if provided).

.EXAMPLE
    .\extract_parallel.ps1 -InputPptx "input/presentation.pptx" -Base "20251214_example_report"

.EXAMPLE
    .\extract_parallel.ps1 -InputPptx "input/presentation.pptx" -Base "20251214_example_report" -LayoutsJson "output_manifest/template_layouts.json"

.NOTES
    Exit codes:
        0: All jobs succeeded
        1: One or more jobs failed
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$InputPptx,
    
    [Parameter(Mandatory=$true)]
    [string]$Base,
    
    [string]$LayoutsJson = ""
)

# Resolve paths
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$InputPptxFull = Resolve-Path $InputPptx -ErrorAction Stop

# Output paths
$ContentJson = Join-Path $ProjectRoot "output_manifest/${Base}_content.json"
$ImagesDir = Join-Path $ProjectRoot "images"

Write-Host "=== EXTRACT Phase (Parallel) ===" -ForegroundColor Cyan
Write-Host "Input: $InputPptxFull"
Write-Host "Base:  $Base"
Write-Host ""

# Define jobs
$jobs = @()

# Job 1: analyze_template.py (skip if layouts.json provided)
if (-not $LayoutsJson) {
    $analyzeJob = Start-Job -Name "analyze_template" -ScriptBlock {
        param($ProjectRoot, $InputPptx)
        Set-Location $ProjectRoot
        & python scripts/analyze_template.py $InputPptx 2>&1
        return $LASTEXITCODE
    } -ArgumentList $ProjectRoot, $InputPptxFull
    $jobs += $analyzeJob
    Write-Host "[Started] analyze_template.py" -ForegroundColor Yellow
} else {
    Write-Host "[Skipped] analyze_template.py (using existing layouts.json)" -ForegroundColor DarkGray
}

# Job 2: extract_images.py
$extractImagesJob = Start-Job -Name "extract_images" -ScriptBlock {
    param($ProjectRoot, $InputPptx, $ImagesDir)
    Set-Location $ProjectRoot
    & python scripts/extract_images.py $InputPptx $ImagesDir 2>&1
    return $LASTEXITCODE
} -ArgumentList $ProjectRoot, $InputPptxFull, $ImagesDir
$jobs += $extractImagesJob
Write-Host "[Started] extract_images.py" -ForegroundColor Yellow

# Job 3: reconstruct_analyzer.py
$reconstructJob = Start-Job -Name "reconstruct_analyzer" -ScriptBlock {
    param($ProjectRoot, $InputPptx, $ContentJson)
    Set-Location $ProjectRoot
    & python scripts/reconstruct_analyzer.py $InputPptx $ContentJson 2>&1
    return $LASTEXITCODE
} -ArgumentList $ProjectRoot, $InputPptxFull, $ContentJson
$jobs += $reconstructJob
Write-Host "[Started] reconstruct_analyzer.py" -ForegroundColor Yellow

Write-Host ""
Write-Host "Waiting for jobs to complete..." -ForegroundColor Cyan

# Wait for all jobs with progress
$completed = @()
while ($completed.Count -lt $jobs.Count) {
    foreach ($job in $jobs) {
        if ($job.State -eq "Completed" -and $job.Name -notin $completed) {
            $completed += $job.Name
            $result = Receive-Job -Job $job
            $exitCode = $result | Select-Object -Last 1
            
            if ($exitCode -eq 0) {
                Write-Host "[Done] $($job.Name) - SUCCESS" -ForegroundColor Green
            } else {
                Write-Host "[Done] $($job.Name) - FAILED (exit: $exitCode)" -ForegroundColor Red
                # Print output for debugging
                $result | ForEach-Object { Write-Host "  $_" -ForegroundColor DarkRed }
            }
        }
    }
    Start-Sleep -Milliseconds 500
}

# Cleanup
$jobs | Remove-Job -Force

# Check results
$failed = $jobs | Where-Object { 
    $result = Receive-Job -Job $_ -Keep
    ($result | Select-Object -Last 1) -ne 0
}

Write-Host ""
if ($failed.Count -eq 0) {
    Write-Host "=== EXTRACT Phase Complete ===" -ForegroundColor Green
    Write-Host "Output: $ContentJson"
    exit 0
} else {
    Write-Host "=== EXTRACT Phase Failed ===" -ForegroundColor Red
    Write-Host "Failed jobs: $($failed.Name -join ', ')"
    exit 1
}
