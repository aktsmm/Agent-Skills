[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$initializer = Join-Path $PSScriptRoot 'Initialize-CustomerWorkspace.ps1'
$skillRoot = Split-Path -Parent $PSScriptRoot
$names = @('inbox', 'convert-meeting-minutes', 'extract-questions', 'triage-workstream-update')
$testRoot = Join-Path ([IO.Path]::GetTempPath()) ('customer-workspace-setup-' + [guid]::NewGuid().ToString('N'))

function Assert-Condition {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { throw $Message }
}

function Get-TreeSignature {
    param([string]$Root)
    $rows = Get-ChildItem -LiteralPath $Root -File -Recurse | ForEach-Object {
        $_.FullName.Substring($Root.Length) + ':' + (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash
    }
    return (@($rows | Sort-Object) -join "`n")
}

function Assert-ExistingWorkspaceRejected {
    param([string]$Target)
    $before = Get-TreeSignature -Root $Target
    try {
        & $initializer -CustomerName 'Example Customer' -WorkspacePath $Target | Out-Null
        throw 'Existing workspace was unexpectedly initialized.'
    }
    catch {
        if ($_.Exception.Message -notlike 'Existing workspace assets detected:*') { throw }
    }
    Assert-Condition ((Get-TreeSignature -Root $Target) -ceq $before) 'Rejected setup changed existing files.'
}

try {
    $fresh = Join-Path $testRoot 'fresh'
    & $initializer -CustomerName 'Example Customer' -WorkspacePath $fresh | Out-Null
    Assert-Condition (-not (Test-Path -LiteralPath (Join-Path $fresh '.github\prompts'))) 'Setup generated a legacy prompt folder.'
    Assert-Condition (@(Get-ChildItem -LiteralPath $fresh -Recurse -Filter '*.prompt.md').Count -eq 0) 'Setup generated prompt files.'

    foreach ($name in $names) {
        $source = Join-Path $skillRoot "assets\workspace-skills\$name"
        $target = Join-Path $fresh ".github\skills\$name"
        Assert-Condition ((Get-TreeSignature -Root $source) -ceq (Get-TreeSignature -Root $target)) "Copied skill differs: $name"
        $entry = Get-Content -LiteralPath (Join-Path $target 'SKILL.md') -Raw -Encoding UTF8
        Assert-Condition ($entry -match "(?m)^name: $name`r?$") "Wrong skill name: $name"
        Assert-Condition ($entry -match '(?m)^user-invocable: true\r?$') "Manual entry unavailable: $name"
        Assert-Condition ($entry -notmatch '(?m)^disable-model-invocation: true\r?$') "Automatic routing disabled: $name"
        $instructions = Get-Content -LiteralPath (Join-Path $fresh '.github\copilot-instructions.md') -Raw -Encoding UTF8
        $readme = Get-Content -LiteralPath (Join-Path $fresh 'README.md') -Raw -Encoding UTF8
        Assert-Condition ($instructions.Contains("skills/$name/SKILL.md")) "Instructions omit skill: $name"
        Assert-Condition ($readme.Contains(".github/skills/$name/SKILL.md")) "README omits skill: $name"
    }
    $generatedMarkdown = Get-ChildItem -LiteralPath $fresh -File -Recurse -Filter '*.md' |
        Select-String -Pattern '\.prompt\.md|/prompt\b|\.github[/\\]prompts'
    Assert-Condition (-not $generatedMarkdown) 'Generated current instructions still depend on prompts.'
    Assert-ExistingWorkspaceRejected -Target $fresh
    Write-Output 'PASS: fresh setup creates four complete operating skills, no prompts, and rejects an unapproved rerun.'

    $profile = Join-Path $fresh '_customer\profile.md'
    $profileHash = (Get-FileHash -LiteralPath $profile -Algorithm SHA256).Hash
    & $initializer -CustomerName 'Example Customer' -WorkspacePath $fresh -Force | Out-Null
    Assert-Condition ((Get-FileHash -LiteralPath $profile -Algorithm SHA256).Hash -eq $profileHash) 'Force overwrote the customer profile.'
    Assert-Condition (@(Get-ChildItem -LiteralPath (Join-Path $fresh '.github\skills') -Filter SKILL.md -Recurse).Count -eq 4) 'Force nested duplicate skill directories.'
    Write-Output 'PASS: explicit Force preserves live profile data and does not nest skill folders.'

    foreach ($marker in @('_inbox', '.github\skills', '.github\prompts')) {
        $target = Join-Path $testRoot ([guid]::NewGuid().ToString('N'))
        $markerPath = Join-Path $target $marker
        New-Item -ItemType Directory -Path $markerPath -Force | Out-Null
        Set-Content -LiteralPath (Join-Path $markerPath 'keep.txt') -Value 'Existing data' -Encoding UTF8
        Assert-ExistingWorkspaceRejected -Target $target
    }
    Write-Output 'PASS: existing records, workspace skills, and legacy prompt-only workspaces remain protected.'

    $broken = Join-Path $testRoot 'broken-scaffold'
    New-Item -ItemType Directory -Path (Join-Path $broken 'scripts') -Force | Out-Null
    Copy-Item -LiteralPath $initializer -Destination (Join-Path $broken 'scripts')
    Copy-Item -LiteralPath (Join-Path $skillRoot 'assets') -Destination $broken -Recurse
    Remove-Item -LiteralPath (Join-Path $broken 'assets\workspace-skills\inbox\references\workflow.md')
    $target = Join-Path $testRoot 'missing-resource-target'
    try {
        & (Join-Path $broken 'scripts\Initialize-CustomerWorkspace.ps1') -CustomerName 'Example Customer' -WorkspacePath $target | Out-Null
        throw 'Setup unexpectedly accepted a missing required resource.'
    }
    catch {
        if ($_.Exception.Message -notlike 'Required workspace skill asset not found:*') { throw }
    }
    Assert-Condition (-not (Test-Path -LiteralPath $target)) 'Missing-resource failure left a partial workspace.'
    Write-Output 'PASS: missing bundled resources fail before workspace creation.'
}
finally {
    if (Test-Path -LiteralPath $testRoot) {
        Remove-Item -LiteralPath $testRoot -Recurse -Force
    }
}
