<#
.SYNOPSIS
  Start or stop an owned Edge window with a CDP port and a throwaway profile (Windows).
.EXAMPLE
  ./browser_session.ps1 -Action Start      # port 9340, profile under %TEMP%
  ./browser_session.ps1 -Action Stop       # kills only this profile's Edge and deletes the profile (it holds sign-in tokens)
#>
param(
  [Parameter(Mandatory)][ValidateSet('Start', 'Stop')][string]$Action,
  [int]$Port = 9340,
  [string]$ProfileDir = (Join-Path $env:LOCALAPPDATA 'Temp\forms-automation-profile')
)

$marker = Split-Path $ProfileDir -Leaf
if ($Action -eq 'Start') {
  $edge = (Get-Command msedge -ErrorAction SilentlyContinue).Source
  if (-not $edge) { $edge = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe' }
  Start-Process -FilePath $edge -ArgumentList "--remote-debugging-port=$Port", '--remote-debugging-address=127.0.0.1', "--user-data-dir=$ProfileDir", '--no-first-run', '--no-default-browser-check', 'https://forms.cloud.microsoft/'
  Start-Sleep -Seconds 6
  "started on port $Port"
}
else {
  Get-CimInstance Win32_Process -Filter "Name='msedge.exe'" |
    Where-Object { $_.CommandLine -match [regex]::Escape($marker) } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
  Start-Sleep -Seconds 2
  if (Test-Path $ProfileDir) { Remove-Item $ProfileDir -Recurse -Force -ErrorAction SilentlyContinue }
  "stopped; profile removed: $(-not (Test-Path $ProfileDir))"
}
