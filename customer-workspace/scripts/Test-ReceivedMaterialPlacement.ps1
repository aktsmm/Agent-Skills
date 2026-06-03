param(
    [string]$RootPath = (Get-Location).Path
)

$knownRootFiles = @(
    'AGENTS.md',
    'README.md',
    'workspace-summary.md',
    'advisor-all.json'
)

$receivedExtensions = @(
    '.pdf', '.ppt', '.pptx', '.doc', '.docx', '.xls', '.xlsx',
    '.png', '.jpg', '.jpeg', '.vsdx', '.drawio'
)

function Get-FileSignature {
    param([Parameter(Mandatory)][string]$LiteralPath)

    $stream = [System.IO.File]::OpenRead($LiteralPath)
    try {
        $buffer = New-Object byte[] 8
        $count = $stream.Read($buffer, 0, $buffer.Length)
        if ($count -lt 2) { return 'Unknown' }

        if ($buffer[0] -eq 0x25 -and $buffer[1] -eq 0x50 -and $buffer[2] -eq 0x44 -and $buffer[3] -eq 0x46) { return 'PDF' }
        if ($buffer[0] -eq 0x50 -and $buffer[1] -eq 0x4B) { return 'ZIP/OpenXML' }
        if ($buffer[0] -eq 0xD0 -and $buffer[1] -eq 0xCF -and $buffer[2] -eq 0x11 -and $buffer[3] -eq 0xE0) { return 'OLE/LegacyOffice' }
        return 'Unknown'
    }
    finally {
        $stream.Dispose()
    }
}

Get-ChildItem -LiteralPath $RootPath -File |
    Where-Object {
        $knownRootFiles -notcontains $_.Name -and
        $receivedExtensions -contains $_.Extension.ToLowerInvariant()
    } |
    ForEach-Object {
        $signature = Get-FileSignature -LiteralPath $_.FullName
        $note = switch ($true) {
            { $_.Extension -eq '.pptx' -and $signature -eq 'OLE/LegacyOffice' } { 'Extension is .pptx but the file is legacy Office/OLE. Consider storing as .ppt.'; break }
            { $_.Extension -in @('.pptx', '.docx', '.xlsx') -and $signature -ne 'ZIP/OpenXML' } { 'File may not be OpenXML. Verify extension and actual format.'; break }
            { $_.Extension -eq '.pdf' -and $signature -ne 'PDF' } { 'File does not start with a PDF header. Verify actual format.'; break }
            default { '' }
        }

        [pscustomobject]@{
            Name = $_.Name
            Extension = $_.Extension
            DetectedFormat = $signature
            Length = $_.Length
            LastWriteTime = $_.LastWriteTime
            PlacementHint = '_received/incoming/ or a classified _received/* folder'
            Note = $note
        }
    }
