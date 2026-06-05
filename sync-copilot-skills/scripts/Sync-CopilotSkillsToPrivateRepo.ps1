param(
    [string[]]$SkillName,
    [string]$PrivateRepo,
    [string[]]$SourceRoot,
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'

function Resolve-PrivateRepo {
    param([string]$ExplicitPrivateRepo)

    if ($ExplicitPrivateRepo) {
        return $ExplicitPrivateRepo
    }

    $repo = [Environment]::GetEnvironmentVariable('SYNC_PUBLIC_SKILLS_PRIVATE_REPO', 'Process')
    if (-not $repo) {
        $repo = [Environment]::GetEnvironmentVariable('SYNC_PUBLIC_SKILLS_PRIVATE_REPO', 'User')
    }
    if ($repo) {
        return $repo
    }

    $script = [Environment]::GetEnvironmentVariable('SYNC_PUBLIC_SKILLS_SCRIPT', 'Process')
    if (-not $script) {
        $script = [Environment]::GetEnvironmentVariable('SYNC_PUBLIC_SKILLS_SCRIPT', 'User')
    }
    if (-not $script) {
        throw 'private repo 未解決: SYNC_PUBLIC_SKILLS_PRIVATE_REPO or SYNC_PUBLIC_SKILLS_SCRIPT is required.'
    }

    $path = Split-Path -Parent $script
    while ($path) {
        if (Test-Path -Path (Join-Path $path '.git')) {
            return $path
        }
        $parent = Split-Path -Parent $path
        if ($parent -eq $path) {
            break
        }
        $path = $parent
    }

    throw 'private repo 未解決: could not infer repository root from SYNC_PUBLIC_SKILLS_SCRIPT.'
}

function Copy-SkillFolder {
    param(
        [string]$SourcePath,
        [string]$DestinationPath,
        [switch]$Preview
    )

    if ($Preview) {
        [pscustomobject]@{
            Action = 'WouldSync'
            Source = $SourcePath
            Destination = $DestinationPath
        }
        return
    }

    New-Item -ItemType Directory -Force -Path $DestinationPath | Out-Null
    Copy-Item -Path (Join-Path $SourcePath '*') -Destination $DestinationPath -Recurse -Force
    [pscustomobject]@{
        Action = 'Synced'
        Source = $SourcePath
        Destination = $DestinationPath
    }
}

$privateRepoRoot = Resolve-PrivateRepo -ExplicitPrivateRepo $PrivateRepo
$destinationRoot = Join-Path $privateRepoRoot '.github\skills'
if (-not (Test-Path -Path $destinationRoot)) {
    throw "private repo 未解決: .github\skills not found under $privateRepoRoot"
}

if (-not $SourceRoot -or $SourceRoot.Count -eq 0) {
    $SourceRoot = @(
        (Join-Path $env:USERPROFILE '.copilot\skills'),
        (Join-Path $env:USERPROFILE '.copilot\m-skills')
    )
}

$excludedSkillNames = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
$excludedSkillNames.Add('sync-copilot-skills') | Out-Null

$requestedSkillNames = $null
if ($SkillName -and $SkillName.Count -gt 0) {
    $requestedSkillNames = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    foreach ($name in $SkillName) {
        if (-not [string]::IsNullOrWhiteSpace($name)) {
            $requestedSkillNames.Add($name.Trim()) | Out-Null
        }
    }
}

$sourceSkills = foreach ($root in $SourceRoot) {
    if (-not (Test-Path -Path $root)) {
        continue
    }

    Get-ChildItem -Path $root -Directory | Where-Object {
        Test-Path -Path (Join-Path $_.FullName 'SKILL.md')
    }
}

$results = New-Object System.Collections.Generic.List[object]
$skipped = New-Object System.Collections.Generic.List[object]

foreach ($skill in $sourceSkills | Sort-Object Name, FullName -Unique) {
    if ($excludedSkillNames.Contains($skill.Name)) {
        $skipped.Add([pscustomobject]@{
            Name = $skill.Name
            Reason = 'self-excluded'
            Source = $skill.FullName
        }) | Out-Null
        continue
    }

    if ($requestedSkillNames -and -not $requestedSkillNames.Contains($skill.Name)) {
        $skipped.Add([pscustomobject]@{
            Name = $skill.Name
            Reason = 'not-requested'
            Source = $skill.FullName
        }) | Out-Null
        continue
    }

    $destinationPath = Join-Path $destinationRoot $skill.Name
    $results.Add((Copy-SkillFolder -SourcePath $skill.FullName -DestinationPath $destinationPath -Preview:$DryRun)) | Out-Null
}

[pscustomobject]@{
    PrivateRepo = $privateRepoRoot
    DestinationRoot = $destinationRoot
    DryRun = [bool]$DryRun
    SyncedCount = $results.Count
    SkippedCount = $skipped.Count
    Synced = $results
    Skipped = $skipped
} | ConvertTo-Json -Depth 5
