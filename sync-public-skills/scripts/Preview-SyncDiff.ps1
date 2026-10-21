# Read-only preview of a public sync: pending diff per public-safe skill, leaks, stale directories, unclassified skills.
[CmdletBinding()]
param(
    [string]$PrivateRepo,
    [string]$PublicRepo,
    [switch]$Fetch
)

$ErrorActionPreference = 'Stop'

function Resolve-RepoPath([string]$Value, [string]$EnvName) {
    if ($Value) { return $Value }
    $v = [Environment]::GetEnvironmentVariable($EnvName, 'Process')
    if (-not $v) { $v = [Environment]::GetEnvironmentVariable($EnvName, 'User') }
    if (-not $v) { throw "$EnvName is not set; pass the path explicitly." }
    $v
}

$PrivateRepo = Resolve-RepoPath $PrivateRepo 'SYNC_PUBLIC_SKILLS_PRIVATE_REPO'
$PublicRepo = Resolve-RepoPath $PublicRepo 'SYNC_PUBLIC_SKILLS_PUBLIC_REPO'
foreach ($r in $PrivateRepo, $PublicRepo) { if (-not (Test-Path -LiteralPath $r)) { throw "Repository path not found: $r" } }

$configPath = Join-Path $PrivateRepo 'scripts/skill-distribution.json'
if (-not (Test-Path -LiteralPath $configPath)) { throw "Distribution config not found: $configPath" }
$cfg = Get-Content -LiteralPath $configPath -Raw -Encoding UTF8 | ConvertFrom-Json
$public = @($cfg.publicSkills)
$internal = @($cfg.internalSkills | ForEach-Object { $_.name })
$denied = @($cfg.deniedSkills)

if ($Fetch) { foreach ($r in $PrivateRepo, $PublicRepo) { git -C $r fetch --quiet origin } }

# Tracked blobs only: untracked build output (e.g. __pycache__) would show as phantom diffs.
function Get-Blobs([string]$Repo, [string]$Prefix, [string]$Skill) {
    $map = @{}
    foreach ($line in (git -C $Repo ls-files -s -- "$Prefix$Skill" 2>$null)) {
        if ($line -match '^\d+ ([0-9a-f]{40}) \d\t(.+)$') {
            $path = $Matches[2].Substring($Prefix.Length)
            if ($path -notmatch '\.skill-meta\.json$|__pycache__') { $map[$path] = $Matches[1] }
        }
    }
    $map
}

"== Repos: private=$(git -C $PrivateRepo status -sb | Select-Object -First 1) | public=$(git -C $PublicRepo status -sb | Select-Object -First 1)"

$pending = foreach ($skill in $public) {
    $src = Get-Blobs $PrivateRepo '.github/skills/' $skill
    $dst = Get-Blobs $PublicRepo '' $skill
    $add = @($src.Keys | Where-Object { -not $dst.ContainsKey($_) }).Count
    $del = @($dst.Keys | Where-Object { -not $src.ContainsKey($_) }).Count
    $mod = @($src.Keys | Where-Object { $dst.ContainsKey($_) -and $src[$_] -ne $dst[$_] }).Count
    if ($add + $del + $mod -gt 0) { [pscustomobject]@{ Skill = $skill; Add = $add; Mod = $mod; Del = $del } }
}
'== Public-safe skills with pending diff'
if ($pending) { $pending | Format-Table -AutoSize | Out-String } else { '(none)' }

'== Internal/denied skill directories present in public (leaks)'
$leaks = @(($internal + $denied) | Where-Object { Test-Path -LiteralPath (Join-Path $PublicRepo $_) })
if ($leaks) { $leaks -join ', ' } else { '(none)' }

'== Directories in public that are not public-safe skills (would be deleted)'
$stale = @(Get-ChildItem -LiteralPath $PublicRepo -Directory | Where-Object { $_.Name -notin '.git', '.github', 'assets' -and $_.Name -notin $public } | ForEach-Object { $_.Name })
if ($stale) { $stale -join ', ' } else { '(none)' }

'== Native skills missing from the distribution config (unclassified)'
$native = @(Get-ChildItem -LiteralPath (Join-Path $PrivateRepo '.github/skills') -Directory | Where-Object { $_.Name -ne 'assets' } | ForEach-Object { $_.Name })
$unknown = @($native | Where-Object { $_ -notin ($public + $internal + $denied) })
if ($unknown) { $unknown -join ', ' } else { '(none)' }
