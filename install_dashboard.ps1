$ErrorActionPreference = 'Stop'
$root = (Get-Location).Path
if (-not (Test-Path (Join-Path $root 'run.py'))) { throw 'Run this installer from the P1 project root (the folder containing run.py).' }
if (-not (Test-Path (Join-Path $root 'dashboard\dashboard.py'))) { throw 'Extract the package so dashboard\dashboard.py is in the P1 folder.' }
$backup = Join-Path $root 'run_s14_13_backup.py'
if (-not (Test-Path $backup)) { Copy-Item (Join-Path $root 'run.py') $backup }
@'
from dashboard.dashboard import main

if __name__ == "__main__":
    main()
'@ | Set-Content -Encoding UTF8 (Join-Path $root 'run.py')
Write-Host 'Dashboard launcher installed.' -ForegroundColor Green
Write-Host 'Original S14.13 entry point backup: run_s14_13_backup.py'
Write-Host 'Launch with: & $py .\run.py'
