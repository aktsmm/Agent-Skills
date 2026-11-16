param(
    [ValidateSet('https://timetreeapp.com/calendars')]
    [string]$Url = 'https://timetreeapp.com/calendars'
)

$ErrorActionPreference = 'Stop'
$port = 9331
$profile = Join-Path $env:USERPROFILE '.scout\calendar-browser-profile'
$endpoint = "http://127.0.0.1:$port"
$edge = Join-Path ${env:ProgramFiles(x86)} 'Microsoft\Edge\Application\msedge.exe'
if (-not (Test-Path $edge)) { throw 'Microsoft Edge was not found.' }

function Get-CalendarListener {
    Get-NetTCPConnection -State Listen -ErrorAction Stop |
        Where-Object { $_.LocalPort -eq $port } |
        Select-Object -First 1
}

function Assert-CalendarOwner($listener) {
    $owner = Get-CimInstance Win32_Process -Filter "ProcessId=$($listener.OwningProcess)"
    if ($owner.Name -ne 'msedge.exe' -or
        $owner.CommandLine -notmatch ('--user-data-dir="?{0}"?(?:\s|$)' -f [regex]::Escape($profile)) -or
        $owner.CommandLine -notmatch "--remote-debugging-port=$port(?:\s|$)") {
        throw "Port $port is not owned by the dedicated calendar browser."
    }
    if ($listener.LocalAddress -notin @('127.0.0.1', '::1')) {
        throw 'The debugging endpoint is not restricted to loopback.'
    }
    return $owner
}

$listener = Get-CalendarListener
$launched = $false
if (-not $listener) {
    $running = Get-CimInstance Win32_Process |
        Where-Object {
            $_.Name -eq 'msedge.exe' -and $_.CommandLine -notmatch '--type=' -and
            $_.CommandLine -match ('--user-data-dir="?{0}"?(?:\s|$)' -f [regex]::Escape($profile))
        }
    if ($running) {
        throw 'The dedicated profile is already running without a usable debugging endpoint. No browser was stopped.'
    }
    New-Item -ItemType Directory -Path $profile -Force | Out-Null
    Start-Process -FilePath $edge -ArgumentList @(
        "--remote-debugging-port=$port",
        '--remote-debugging-address=127.0.0.1',
        ('"--user-data-dir={0}"' -f $profile),
        '--no-first-run',
        '--no-default-browser-check',
        $Url
    ) | Out-Null
    $launched = $true
    $deadline = (Get-Date).AddSeconds(20)
    do {
        Start-Sleep -Milliseconds 250
        $listener = Get-CalendarListener
    } while (-not $listener -and (Get-Date) -lt $deadline)
    if (-not $listener) { throw 'The dedicated browser did not open its debugging endpoint.' }
}

$owner = Assert-CalendarOwner $listener
$version = Invoke-RestMethod -Uri "$endpoint/json/version"
$targets = Invoke-RestMethod -Uri "$endpoint/json/list"
[pscustomobject]@{
    profile = $profile
    endpoint = $endpoint
    processId = $owner.ProcessId
    launched = $launched
    browser = $version.Browser
    pages = @($targets | Where-Object { $_.type -eq 'page' } | Select-Object id, url, title)
} | ConvertTo-Json -Depth 5
