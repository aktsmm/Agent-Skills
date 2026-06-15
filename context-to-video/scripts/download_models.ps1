$ErrorActionPreference = 'Stop'

$ROOT = if ($env:SADTALKER_ROOT) { $env:SADTALKER_ROOT } else { Join-Path (Get-Location) "SadTalker" }

New-Item -ItemType Directory -Force -Path "$ROOT\checkpoints", "$ROOT\gfpgan\weights" | Out-Null

$files = @(
  @{ url='https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00109-model.pth.tar';        out="$ROOT\checkpoints\mapping_00109-model.pth.tar" }
  @{ url='https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00229-model.pth.tar';        out="$ROOT\checkpoints\mapping_00229-model.pth.tar" }
  @{ url='https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V0.0.2_256.safetensors';   out="$ROOT\checkpoints\SadTalker_V0.0.2_256.safetensors" }
  @{ url='https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V0.0.2_512.safetensors';   out="$ROOT\checkpoints\SadTalker_V0.0.2_512.safetensors" }
  @{ url='https://github.com/xinntao/facexlib/releases/download/v0.1.0/alignment_WFLW_4HG.pth';                    out="$ROOT\gfpgan\weights\alignment_WFLW_4HG.pth" }
  @{ url='https://github.com/xinntao/facexlib/releases/download/v0.1.0/detection_Resnet50_Final.pth';              out="$ROOT\gfpgan\weights\detection_Resnet50_Final.pth" }
  @{ url='https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth';                           out="$ROOT\gfpgan\weights\GFPGANv1.4.pth" }
  @{ url='https://github.com/xinntao/facexlib/releases/download/v0.2.2/parsing_parsenet.pth';                      out="$ROOT\gfpgan\weights\parsing_parsenet.pth" }
)

foreach ($f in $files) {
  if (Test-Path $f.out) {
    Write-Host "[skip] $($f.out)"
    continue
  }
  Write-Host "[get ] $($f.out)"
  curl.exe -L --silent --show-error -o $f.out $f.url
}

Write-Host "`n--- sizes ---"
Get-ChildItem "$ROOT\checkpoints", "$ROOT\gfpgan\weights" | Select-Object Name, @{n='MB';e={[math]::Round($_.Length/1MB,1)}}
