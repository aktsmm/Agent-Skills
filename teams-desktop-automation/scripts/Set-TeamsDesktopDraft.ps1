[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateSet('Open', 'Inspect', 'Draft')]
    [string]$Mode,

    [Parameter(Mandatory)]
    [string]$RecipientDisplayName,

    [Parameter(Mandatory)]
    [string]$RecipientEmail,

    [Parameter(Mandatory)]
    [string]$ExpectedAccount,

    [string]$Message,

    [string]$ScreenshotPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Assert-EmailAddress {
    param([Parameter(Mandatory)][string]$Value)

    if ($Value -notmatch '^[^\s@]+@[^\s@]+\.[^\s@]+$') {
        throw "Invalid email address: $Value"
    }
}

function Save-WindowCapture {
    param(
        [Parameter(Mandatory)][IntPtr]$WindowHandle,
        [Parameter(Mandatory)][string]$Path
    )

    if ([IO.Path]::GetExtension($Path) -ne '.png') {
        throw 'ScreenshotPath must use the .png extension.'
    }

    Add-Type -AssemblyName System.Drawing
    if (-not ('TeamsDesktopNativeCapture' -as [type])) {
        Add-Type @'
using System;
using System.Runtime.InteropServices;
public static class TeamsDesktopNativeCapture {
    [DllImport("user32.dll")]
    public static extern bool PrintWindow(IntPtr hwnd, IntPtr hdcBlt, uint flags);
}
'@
    }

    $targetPath = [IO.Path]::GetFullPath($Path)
    $parent = Split-Path -Parent $targetPath
    if (-not (Test-Path -LiteralPath $parent)) {
        $null = New-Item -ItemType Directory -Path $parent
    }

    $element = [System.Windows.Automation.AutomationElement]::FromHandle($WindowHandle)
    $bounds = $element.Current.BoundingRectangle
    $bitmap = [Drawing.Bitmap]::new([int]$bounds.Width, [int]$bounds.Height)
    $graphics = [Drawing.Graphics]::FromImage($bitmap)
    $deviceContext = $graphics.GetHdc()
    try {
        if (-not [TeamsDesktopNativeCapture]::PrintWindow($WindowHandle, $deviceContext, 2)) {
            throw 'PrintWindow failed.'
        }
    }
    finally {
        $graphics.ReleaseHdc($deviceContext)
        $graphics.Dispose()
    }

    try {
        $bitmap.Save($targetPath, [Drawing.Imaging.ImageFormat]::Png)
    }
    finally {
        $bitmap.Dispose()
    }

    return $targetPath
}

Assert-EmailAddress -Value $RecipientEmail
Assert-EmailAddress -Value $ExpectedAccount

if ($RecipientDisplayName.Contains('|')) {
    throw 'RecipientDisplayName cannot contain a pipe character.'
}

if ($Mode -eq 'Draft' -and [string]::IsNullOrWhiteSpace($Message)) {
    throw 'Message is required in Draft mode.'
}

if ($Mode -eq 'Open') {
    $escapedEmail = [Uri]::EscapeDataString($RecipientEmail)
    Start-Process "msteams:/l/chat/0/0?users=$escapedEmail"
    [pscustomobject]@{
        Status              = 'chat-open-requested'
        RecipientEmail      = $RecipientEmail
        SendActionPerformed = $false
        NextAction          = 'Run Inspect after the target chat is visible.'
    } | ConvertTo-Json
    return
}

Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$expectedTitle = "$RecipientDisplayName | Microsoft | $ExpectedAccount | Microsoft Teams"
$matchingWindows = @(
    Get-Process -Name 'ms-teams' -ErrorAction SilentlyContinue |
        Where-Object { $_.MainWindowHandle -ne 0 -and $_.MainWindowTitle -eq $expectedTitle }
)

if ($matchingWindows.Count -ne 1) {
    throw "Expected exactly one Teams window titled '$expectedTitle'; found $($matchingWindows.Count)."
}

$teamsProcess = $matchingWindows[0]
$root = [System.Windows.Automation.AutomationElement]::FromHandle($teamsProcess.MainWindowHandle)
$allElements = $root.FindAll(
    [System.Windows.Automation.TreeScope]::Descendants,
    [System.Windows.Automation.Condition]::TrueCondition
)

$composers = @(
    for ($index = 0; $index -lt $allElements.Count; $index++) {
        $element = $allElements.Item($index)
        $isEdit = $element.Current.ControlType -eq [System.Windows.Automation.ControlType]::Edit
        $isComposer = $element.Current.AutomationId -like 'new-message-*' -or
            $element.Current.Name -in @('メッセージを入力', 'Type a message')
        if ($isEdit -and $isComposer) {
            $element
        }
    }
)

if ($composers.Count -ne 1) {
    throw "Expected exactly one Teams message composer; found $($composers.Count)."
}

$composer = $composers[0]
$valuePattern = $composer.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
$currentDraft = $valuePattern.Current.Value
$composerPlaceholders = @('メッセージを入力', 'Type a message')
if ($currentDraft.TrimEnd("`r", "`n") -in $composerPlaceholders) {
    $currentDraft = ''
}

$sendButtons = @(
    for ($index = 0; $index -lt $allElements.Count; $index++) {
        $element = $allElements.Item($index)
        $isButton = $element.Current.ControlType -eq [System.Windows.Automation.ControlType]::Button
        if ($isButton -and $element.Current.Name -match '^(送信|Send) \(Ctrl\+Enter\)$') {
            $element
        }
    }
)

if ($sendButtons.Count -ne 1) {
    throw "Expected exactly one Teams send button; found $($sendButtons.Count)."
}

$sendButton = $sendButtons[0]
$draftChanged = $false

if ($Mode -eq 'Draft') {
    if (-not [string]::IsNullOrEmpty($currentDraft) -and $currentDraft -cne $Message) {
        throw 'The composer contains a different draft. Refusing to overwrite it.'
    }

    if ([string]::IsNullOrEmpty($currentDraft)) {
        $valuePattern.SetValue($Message)
        $draftChanged = $true
    }

    $currentDraft = $valuePattern.Current.Value
    if ($currentDraft.TrimEnd("`r", "`n") -in $composerPlaceholders) {
        $currentDraft = ''
    }
    if ($currentDraft -cne $Message) {
        throw 'Draft verification failed after setting the message.'
    }
}

$savedScreenshot = $null
if (-not [string]::IsNullOrWhiteSpace($ScreenshotPath)) {
    $savedScreenshot = Save-WindowCapture -WindowHandle $teamsProcess.MainWindowHandle -Path $ScreenshotPath
}

[pscustomobject]@{
    Status              = if ($Mode -eq 'Draft') { 'ready-for-user-send' } else { 'inspected' }
    RecipientDisplayName = $RecipientDisplayName
    RecipientEmail      = $RecipientEmail
    ExpectedAccount     = $ExpectedAccount
    WindowTitleMatches  = $true
    ComposerFound       = $true
    DraftChanged        = $draftChanged
    DraftLength         = $currentDraft.Length
    DraftMatches        = if ($Mode -eq 'Draft') { $currentDraft -ceq $Message } else { $null }
    SendEnabled         = $sendButton.Current.IsEnabled
    SendActionPerformed = $false
    ScreenshotPath      = $savedScreenshot
} | ConvertTo-Json