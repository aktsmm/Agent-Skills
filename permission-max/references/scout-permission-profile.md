# Scout Permission Profile

Read this reference only when changing Microsoft Scout permissions.

## Safety Contract

`permissions.allow` is a full replacement. Read the current list first, merge it with the requested patterns, remove duplicates, and submit the union. Never replace it with only the defaults below.

## Broad Allow Patterns

```text
Add-Type *
Compress-Archive *
Copy-Item *
Expand-Archive *
Format-List *
Format-Table *
Get-ChildItem *
Get-Content *
Get-Item *
Get-Location *
Import-Module *
Invoke-RestMethod *
Invoke-WebRequest *
Join-Path *
Move-Item *
New-Item *
Remove-Item *
Rename-Item *
Resolve-Path *
Select-Object *
Set-Content *
Set-ExecutionPolicy *
Set-Location *
Sort-Object *
Start-Process *
Start-Sleep *
Stop-Process -Id *
Test-Path *
Where-Object *
az *
cmd *
code *
curl *
docker *
dotnet *
gh *
git *
go *
node *
npm *
npx *
pip *
pip3 *
pnpm *
powershell *
pwsh *
py *
py -m *
python *
python -m *
robocopy *
uv *
winget *
yarn *
```

## Escalation Payload Shape

Use the current settings as the base. Include only servers and tools available in the current environment; do not invent missing IDs.

```json
{
  "allow": ["existing item", "merged requested item"],
  "autoApproveReadOnly": true,
  "servers": {
    "filesystem": { "autoApprove": true },
    "playwright": { "autoApprove": true },
    "shell": { "autoApprove": true },
    "workiq": { "autoApprove": true }
  },
  "tools": {
    "tool:m_get_settings": true,
    "tool:read": true
  }
}
```

After approval, call `m_get_settings` again. Compare arrays as sets so ordering changes do not look like additions or removals. Report `added`, `preserved`, `removed`, and `not-approved`; any `removed` item prevents a success result.
