param(
    [switch]$SkipAgent,
    [switch]$NoInstallAgentDeps,
    [int]$BackendPort = 8080,
    [int]$AgentPort = 9001,
    [int]$FrontendPort = 5173
)

$ErrorActionPreference = "Stop"
$PackageRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogDir = Join-Path $PackageRoot "logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Import-DotEnv {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }
    Get-Content -LiteralPath $Path -Encoding UTF8 | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith("#") -or -not $line.Contains("=")) {
            return
        }
        $parts = $line.Split("=", 2)
        $name = $parts[0].Trim()
        $value = $parts[1].Trim().Trim('"').Trim("'")
        if ($name) {
            [System.Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
}

function Resolve-Java {
    if ($env:JAVA_HOME) {
        $candidate = Join-Path $env:JAVA_HOME "bin\java.exe"
        if (Test-Path -LiteralPath $candidate) {
            return $candidate
        }
    }
    $cmd = Get-Command java.exe -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }
    throw "Java 21 not found. Install JDK 21 or set JAVA_HOME before running this script."
}

function Resolve-Python {
    $cmd = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }
    $cmd = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }
    throw "Python 3.11+ not found. Install Python before starting the resource agent."
}

Import-DotEnv (Join-Path $PackageRoot ".env")

if (-not $env:SOFTWARECUP_AGENT_RESOURCE_BASE_URL) {
    $env:SOFTWARECUP_AGENT_RESOURCE_BASE_URL = "http://localhost:$AgentPort"
}
if (-not $env:SOFTWARECUP_AGENT_PROVIDER) {
    $env:SOFTWARECUP_AGENT_PROVIDER = "xfyun_spark"
}
if (-not $env:RESOURCE_AGENT_PROVIDER) {
    $env:RESOURCE_AGENT_PROVIDER = "xfyun_spark"
}
if (-not $env:RESOURCE_AGENT_TIMEOUT_SECONDS) {
    $env:RESOURCE_AGENT_TIMEOUT_SECONDS = "120"
}
if (-not $env:RESOURCE_AGENT_RETRY_ATTEMPTS) {
    $env:RESOURCE_AGENT_RETRY_ATTEMPTS = "3"
}

if (-not $env:XFYUN_API_PASSWORD -and -not ($env:XFYUN_API_KEY -and $env:XFYUN_API_SECRET)) {
    Write-Warning "XFYUN credentials are not configured. Copy .env.example to .env and fill XFYUN_API_PASSWORD or XFYUN_API_KEY/XFYUN_API_SECRET before formal judging."
}

$java = Resolve-Java
$backendJar = Join-Path $PackageRoot "backend\backend.jar"
if (-not (Test-Path -LiteralPath $backendJar)) {
    throw "Backend jar not found: $backendJar"
}

$processes = @()
$backendArgs = @(
    "-Dserver.port=$BackendPort",
    "-jar",
    $backendJar
)
$backend = Start-Process -FilePath $java -ArgumentList $backendArgs -WorkingDirectory $PackageRoot -PassThru -WindowStyle Hidden -RedirectStandardOutput (Join-Path $LogDir "backend.log") -RedirectStandardError (Join-Path $LogDir "backend.err.log")
$processes += [pscustomobject]@{ name = "backend"; pid = $backend.Id; url = "http://localhost:$BackendPort/api/health" }

if (-not $SkipAgent) {
    $python = Resolve-Python
    $agentDir = Join-Path $PackageRoot "agent"
    $venvPython = Join-Path $agentDir ".venv\Scripts\python.exe"
    if (-not (Test-Path -LiteralPath $venvPython)) {
        & $python -m venv (Join-Path $agentDir ".venv")
    }
    if (-not $NoInstallAgentDeps) {
        & $venvPython -m pip install -r (Join-Path $agentDir "requirements.txt")
    }
    $agentArgs = @("-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$AgentPort")
    $agent = Start-Process -FilePath $venvPython -ArgumentList $agentArgs -WorkingDirectory $agentDir -PassThru -WindowStyle Hidden -RedirectStandardOutput (Join-Path $LogDir "agent.log") -RedirectStandardError (Join-Path $LogDir "agent.err.log")
    $processes += [pscustomobject]@{ name = "agent"; pid = $agent.Id; url = "http://localhost:$AgentPort/health" }
}

$serveScript = Join-Path $PackageRoot "serve-spa.ps1"
$frontendRoot = Join-Path $PackageRoot "frontend"
$frontendArgs = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $serveScript, "-Root", $frontendRoot, "-Port", "$FrontendPort")
$frontend = Start-Process -FilePath "powershell.exe" -ArgumentList $frontendArgs -WorkingDirectory $PackageRoot -PassThru -WindowStyle Hidden -RedirectStandardOutput (Join-Path $LogDir "frontend.log") -RedirectStandardError (Join-Path $LogDir "frontend.err.log")
$processes += [pscustomobject]@{ name = "frontend"; pid = $frontend.Id; url = "http://localhost:$FrontendPort/" }

$pidFile = Join-Path $LogDir "pids.json"
$processes | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $pidFile -Encoding UTF8

Write-Host "智学工坊 has been started."
$processes | Format-Table -AutoSize
Write-Host "Open http://localhost:$FrontendPort/ in your browser."
Write-Host "Default accounts: zhang.student / student@2026, li.teacher / teacher@2026"
Write-Host "Use stop-zhixue-workshop.ps1 to stop all processes."
