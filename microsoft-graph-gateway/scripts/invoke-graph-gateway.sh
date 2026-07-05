#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v pwsh >/dev/null 2>&1; then
  echo "pwsh was not found. Install PowerShell 7+ to use the Microsoft Graph gateway on macOS or Linux." >&2
  exit 1
fi

pwsh -NoLogo -NoProfile -File "$SCRIPT_DIR/Invoke-GraphGateway.ps1" "$@"