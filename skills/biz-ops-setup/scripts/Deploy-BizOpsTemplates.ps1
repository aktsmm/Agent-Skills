<#
.SYNOPSIS
    Deploy agent and prompt templates to workspace

.DESCRIPTION
    Copies all agent and prompt templates from skill assets to the target workspace.
    Optionally customizes customer mappings.

.PARAMETER WorkspacePath
    Target workspace path (default: current directory)

.PARAMETER SkillPath
    Path to biz-ops-setup skill (default: tries to find in .github/skills)

.PARAMETER Customers
    Hashtable of customer mappings (e.g., @{"Contoso" = "contoso"; "Fabrikam" = "fabrikam"})

.PARAMETER Contacts
    Hashtable of contact-to-customer mappings (e.g., @{"John Doe" = "contoso"})

.EXAMPLE
    .\Deploy-BizOpsTemplates.ps1 -WorkspacePath "D:\my-biz-ops"

.EXAMPLE
    .\Deploy-BizOpsTemplates.ps1 -Customers @{"Contoso Inc" = "contoso"} -Contacts @{"John Doe" = "contoso"}
#>

param(
    [string]$WorkspacePath = (Get-Location).Path,
    [string]$SkillPath = "",
    [hashtable]$Customers = @{},
    [hashtable]$Contacts = @{}
)

$ErrorActionPreference = "Stop"

# Find skill path if not provided
if (-not $SkillPath) {
    $possiblePaths = @(
        (Join-Path $WorkspacePath ".github\skills\biz-ops-setup"),
        (Join-Path $PSScriptRoot "..")
    )
    foreach ($path in $possiblePaths) {
        if (Test-Path (Join-Path $path "SKILL.md")) {
            $SkillPath = $path
            break
        }
    }
}

if (-not $SkillPath -or -not (Test-Path $SkillPath)) {
    Write-Error "Could not find biz-ops-setup skill. Please specify -SkillPath"
    exit 1
}

Write-Host "🚀 Deploying Biz-Ops Templates" -ForegroundColor Cyan
Write-Host "   Skill: $SkillPath" -ForegroundColor Gray
Write-Host "   Target: $WorkspacePath" -ForegroundColor Gray
Write-Host ""

$assetsPath = Join-Path $SkillPath "assets"

# ============================================
# 1. Deploy Agent Templates
# ============================================

Write-Host "🤖 Deploying agents..." -ForegroundColor Yellow

$agentsSource = Join-Path $assetsPath "agents"
$agentsTarget = Join-Path $WorkspacePath ".github\agents"

if (-not (Test-Path $agentsTarget)) {
    New-Item -ItemType Directory -Path $agentsTarget -Force | Out-Null
}

$agentFiles = Get-ChildItem -Path $agentsSource -Filter "*.template.md" -ErrorAction SilentlyContinue
foreach ($file in $agentFiles) {
    $targetName = $file.Name -replace "\.template\.md$", ".md"
    $targetPath = Join-Path $agentsTarget $targetName
    
    if (-not (Test-Path $targetPath)) {
        Copy-Item -Path $file.FullName -Destination $targetPath
        Write-Host "   ✅ Deployed: $targetName" -ForegroundColor Green
    } else {
        Write-Host "   ⏭️ Exists: $targetName" -ForegroundColor Gray
    }
}

# Also copy report-generator from root assets if exists
$reportGenTemplate = Join-Path $assetsPath "report-generator.agent.template.md"
if (Test-Path $reportGenTemplate) {
    $targetPath = Join-Path $agentsTarget "report-generator.agent.md"
    if (-not (Test-Path $targetPath)) {
        Copy-Item -Path $reportGenTemplate -Destination $targetPath
        Write-Host "   ✅ Deployed: report-generator.agent.md" -ForegroundColor Green
    }
}

# ============================================
# 2. Deploy Prompt Templates
# ============================================

Write-Host ""
Write-Host "📝 Deploying prompts..." -ForegroundColor Yellow

$promptsSource = Join-Path $assetsPath "prompts"
$promptsTarget = Join-Path $WorkspacePath ".github\prompts"

if (-not (Test-Path $promptsTarget)) {
    New-Item -ItemType Directory -Path $promptsTarget -Force | Out-Null
}

$promptFiles = Get-ChildItem -Path $promptsSource -Filter "*.template.md" -ErrorAction SilentlyContinue
foreach ($file in $promptFiles) {
    $targetName = $file.Name -replace "\.template\.md$", ".md"
    $targetPath = Join-Path $promptsTarget $targetName
    
    if (-not (Test-Path $targetPath)) {
        Copy-Item -Path $file.FullName -Destination $targetPath
        Write-Host "   ✅ Deployed: $targetName" -ForegroundColor Green
    } else {
        Write-Host "   ⏭️ Exists: $targetName" -ForegroundColor Gray
    }
}

# Create prompts README
$promptsReadme = Join-Path $promptsTarget "README.md"
if (-not (Test-Path $promptsReadme)) {
    @"
# Prompts

Prompt templates for report generation.

## Available Prompts

| Prompt | Description |
|--------|-------------|
| daily-report.prompt.md | Daily activity report generation |
| weekly-report.prompt.md | Weekly summary generation |
| monthly-report.prompt.md | Monthly overview generation |
| review-report.prompt.md | IMPACT framework report review |

## Usage

Use with corresponding agent:
- Reports: `@report-generator`
- Review: `@report-reviewer`
"@ | Out-File -FilePath $promptsReadme -Encoding utf8
    Write-Host "   ✅ Created: README.md" -ForegroundColor Green
}

# ============================================
# 3. Deploy Configuration Templates
# ============================================

Write-Host ""
Write-Host "⚙️ Deploying configuration..." -ForegroundColor Yellow

# copilot-instructions.md
$copilotSource = Join-Path $assetsPath "copilot-instructions.template.md"
$copilotTarget = Join-Path $WorkspacePath ".github\copilot-instructions.md"
if ((Test-Path $copilotSource) -and -not (Test-Path $copilotTarget)) {
    Copy-Item -Path $copilotSource -Destination $copilotTarget
    Write-Host "   ✅ Deployed: copilot-instructions.md" -ForegroundColor Green
}

# AGENTS.md
$agentsSource = Join-Path $assetsPath "AGENTS.template.md"
$agentsTarget = Join-Path $WorkspacePath "AGENTS.md"
if ((Test-Path $agentsSource) -and -not (Test-Path $agentsTarget)) {
    Copy-Item -Path $agentsSource -Destination $agentsTarget
    Write-Host "   ✅ Deployed: AGENTS.md" -ForegroundColor Green
}

# DASHBOARD.md
$dashSource = Join-Path $assetsPath "DASHBOARD.template.md"
$dashTarget = Join-Path $WorkspacePath "DASHBOARD.md"
if ((Test-Path $dashSource) -and -not (Test-Path $dashTarget)) {
    Copy-Item -Path $dashSource -Destination $dashTarget
    Write-Host "   ✅ Deployed: DASHBOARD.md" -ForegroundColor Green
}

# external-paths.md
$extSource = Join-Path $assetsPath "external-paths.template.md"
$extTarget = Join-Path $WorkspacePath "_datasources\external-paths.md"
if ((Test-Path $extSource) -and -not (Test-Path $extTarget)) {
    Copy-Item -Path $extSource -Destination $extTarget
    Write-Host "   ✅ Deployed: _datasources/external-paths.md" -ForegroundColor Green
}

# workiq-spec.md
$workiqSource = Join-Path $assetsPath "_datasources\workiq-spec.template.md"
$workiqTarget = Join-Path $WorkspacePath "_datasources\workiq-spec.md"
if ((Test-Path $workiqSource) -and -not (Test-Path $workiqTarget)) {
    Copy-Item -Path $workiqSource -Destination $workiqTarget
    Write-Host "   ✅ Deployed: _datasources/workiq-spec.md" -ForegroundColor Green
}

# ============================================
# 4. Apply Customer Mappings (if provided)
# ============================================

if ($Customers.Count -gt 0 -or $Contacts.Count -gt 0) {
    Write-Host ""
    Write-Host "👥 Applying customer mappings..." -ForegroundColor Yellow
    
    # Build customer mapping table
    $customerTable = ""
    foreach ($entry in $Customers.GetEnumerator()) {
        $customerTable += "| $($entry.Key) | $($entry.Value) | Customers/$($entry.Value) |`n"
    }
    
    # Build contact mapping table
    $contactTable = ""
    foreach ($entry in $Contacts.GetEnumerator()) {
        $contactTable += "| $($entry.Key) | $($entry.Value) |`n"
    }
    
    # Update data-collector agent
    $dataCollectorPath = Join-Path $WorkspacePath ".github\agents\data-collector.agent.md"
    if (Test-Path $dataCollectorPath) {
        $content = Get-Content $dataCollectorPath -Raw
        
        if ($customerTable) {
            $content = $content -replace "(\| Detection Pattern \| Customer ID \| Folder \|`n\| [-]+ \| [-]+ \| [-]+ \|)`n", "`$1`n$customerTable"
        }
        if ($contactTable) {
            $content = $content -replace "(\| Contact Name \| Customer \|`n\| [-]+ \| [-]+ \|)`n", "`$1`n$contactTable"
        }
        
        $content | Out-File -FilePath $dataCollectorPath -Encoding utf8 -NoNewline
        Write-Host "   ✅ Updated: data-collector.agent.md with customer mappings" -ForegroundColor Green
    }
}

# ============================================
# 5. Summary
# ============================================

Write-Host ""
Write-Host "✅ Template deployment complete!" -ForegroundColor Green
Write-Host ""

# Count deployed files
$agentCount = (Get-ChildItem (Join-Path $WorkspacePath ".github\agents") -Filter "*.agent.md" -ErrorAction SilentlyContinue).Count
$promptCount = (Get-ChildItem (Join-Path $WorkspacePath ".github\prompts") -Filter "*.prompt.md" -ErrorAction SilentlyContinue).Count

Write-Host "📊 Summary:" -ForegroundColor Cyan
Write-Host "   Agents: $agentCount" -ForegroundColor White
Write-Host "   Prompts: $promptCount" -ForegroundColor White
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Review and customize copilot-instructions.md" -ForegroundColor White
Write-Host "   2. Add customer mappings to data-collector agent" -ForegroundColor White
Write-Host "   3. Configure external paths in _datasources/external-paths.md" -ForegroundColor White
Write-Host "   4. Copy holiday file to _workiq/" -ForegroundColor White
Write-Host "   5. Test with 'Create daily report' command" -ForegroundColor White
