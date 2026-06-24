$ErrorActionPreference = "Stop"
$PackageRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PidFile = Join-Path $PackageRoot "logs\pids.json"

if (-not (Test-Path -LiteralPath $PidFile)) {
    Write-Host "No pid file found. Nothing to stop."
    exit 0
}

$items = Get-Content -LiteralPath $PidFile -Encoding UTF8 | ConvertFrom-Json
foreach ($item in $items) {
    try {
        $process = Get-Process -Id $item.pid -ErrorAction Stop
        Stop-Process -Id $process.Id -Force
        Write-Host "Stopped $($item.name) pid=$($item.pid)"
    } catch {
        Write-Host "Process $($item.name) pid=$($item.pid) is not running."
    }
}
