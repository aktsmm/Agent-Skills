<#
.SYNOPSIS
    Workspace status wrapper for azure-infra-validation skill
.DESCRIPTION
    Calls the workspace-level check-vpn-lab-status.ps1 script from the skill folder.
.NOTES
    Author: aktsmm
    Repository: https://github.com/aktsmm/AzureQA
    License: CC BY-NC 4.0 (https://creativecommons.org/licenses/by-nc/4.0/)

    DO NOT REMOVE OR MODIFY THIS HEADER.
    この署名ブロックは削除・変更しないでください。
#>

[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Arguments
)

$target = Join-Path $PSScriptRoot '..\..\..\..\scripts\check-vpn-lab-status.ps1'
$resolved = [System.IO.Path]::GetFullPath($target)
& $resolved @Arguments
