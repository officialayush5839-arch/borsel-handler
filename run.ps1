<#
.SYNOPSIS
    Borsel Handler - Institutional Market Intelligence Platform
    Localhost Automated Full-Stack Launcher (PowerShell Edition)
#>

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location -LiteralPath $ScriptDir

Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host "       BORSEL HANDLER - AI-POWERED INDIAN FINANCIAL INTELLIGENCE" -ForegroundColor Cyan
Write-Host "                  Localhost Automated Full-Stack Launcher" -ForegroundColor Cyan
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Detect Python Executable
$PythonCmd = $null
if (Test-Path "$ScriptDir\.venv\Scripts\python.exe") {
    $PythonCmd = "$ScriptDir\.venv\Scripts\python.exe"
} elseif (Test-Path "$ScriptDir\venv\Scripts\python.exe") {
    $PythonCmd = "$ScriptDir\venv\Scripts\python.exe"
} else {
    foreach ($cmd in @("py -3", "py", "python", "python3")) {
        try {
            $parts = $cmd -split " "
            $exe = $parts[0]
            $args = if ($parts.Length -gt 1) { $parts[1..($parts.Length - 1)] + @("--version") } else { @("--version") }
            $proc = Start-Process -FilePath $exe -ArgumentList $args -NoNewWindow -PassThru -Wait -RedirectStandardError "nul" -RedirectStandardOutput "nul"
            if ($proc.ExitCode -eq 0) {
                $PythonCmd = $cmd
                break
            }
        } catch {
            # continue checking
        }
    }
}

if (-not $PythonCmd) {
    Write-Host "[ERROR] Python 3 was not detected on your system." -ForegroundColor Red
    Write-Host "Please install Python 3.11+ from https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

Write-Host "[OK] Python runtime detected:" -ForegroundColor Green
$pyParts = $PythonCmd -split " "
& $pyParts[0] ($pyParts[1..($pyParts.Length - 1)] + @("--version"))
Write-Host ""

# 2. Detect Node.js & npm
try {
    $nodeVer = & node -v
    Write-Host "[OK] Node.js detected: $nodeVer" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Node.js was not detected on your PATH." -ForegroundColor Red
    exit 1
}

try {
    $npmVer = & npm.cmd -v
    Write-Host "[OK] npm detected: $npmVer" -ForegroundColor Green
} catch {
    try {
        $npmVer = & npm -v
        Write-Host "[OK] npm detected: $npmVer" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] npm was not detected on your PATH." -ForegroundColor Red
        exit 1
    }
}
Write-Host ""

# 3. Environment Configuration
if (-not (Test-Path "$ScriptDir\.env")) {
    if (Test-Path "$ScriptDir\.env.example") {
        Write-Host "[INFO] .env not found. Creating from .env.example..." -ForegroundColor Yellow
        Copy-Item "$ScriptDir\.env.example" "$ScriptDir\.env"
        Write-Host "[OK] Created .env configuration." -ForegroundColor Green
    }
} else {
    Write-Host "[OK] .env configuration found." -ForegroundColor Green
}

# 4. Run Alembic Migrations
Write-Host ""
Write-Host "[INFO] Applying database migrations (Alembic)..." -ForegroundColor Yellow
$alembicArgs = ($pyParts[1..($pyParts.Length - 1)] + @("-m", "alembic", "upgrade", "head"))
& $pyParts[0] $alembicArgs
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARNING] Alembic reported non-zero status. Proceeding..." -ForegroundColor Yellow
} else {
    Write-Host "[OK] Database schema up to date." -ForegroundColor Green
}
Write-Host ""

# 5. Frontend Dependencies Check
$frontendNodeModules = "$ScriptDir\frontend\node_modules"
if (-not (Test-Path $frontendNodeModules)) {
    Write-Host "[INFO] Installing frontend dependencies (npm install)..." -ForegroundColor Yellow
    Push-Location "$ScriptDir\frontend"
    & npm.cmd install
    Pop-Location
    Write-Host "[OK] Frontend dependencies installed." -ForegroundColor Green
} else {
    Write-Host "[OK] Frontend dependencies already installed." -ForegroundColor Green
}

# 6. Launch Backend in New Window
Write-Host "[INFO] Launching FastAPI Backend and Ingestion Automation [Port 8000]..." -ForegroundColor Cyan
$backendArgs = "/k title Borsel Backend (Port 8000) ^&^& set ENABLE_AUTO_INGEST=true ^&^& $PythonCmd -m uvicorn borsel_handler.api.app:app --host 0.0.0.0 --port 8000 --reload"
Start-Process -FilePath "cmd.exe" -ArgumentList $backendArgs -WorkingDirectory $ScriptDir

# 7. Launch Frontend in New Window
Write-Host "[INFO] Launching React 19 Financial Dashboard [Port 5173]..." -ForegroundColor Cyan
$frontendArgs = "/k title Borsel Frontend (Port 5173) ^&^& call npm run dev"
Start-Process -FilePath "cmd.exe" -ArgumentList $frontendArgs -WorkingDirectory "$ScriptDir\frontend"

# 8. Wait and Open Browser
Write-Host ""
Write-Host "[INFO] Waiting 3 seconds for services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host "[INFO] Opening default browser to Dashboard (http://localhost:5173)..." -ForegroundColor Cyan
Start-Process "http://localhost:5173"

Write-Host ""
Write-Host "===============================================================================" -ForegroundColor Green
Write-Host "                        SYSTEM SUCCESSFULLY STARTED" -ForegroundColor Green
Write-Host "===============================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  * React Financial Dashboard:  http://localhost:5173" -ForegroundColor White
Write-Host "  * FastAPI REST Server:        http://localhost:8000" -ForegroundColor White
Write-Host "  * Interactive Swagger Docs:   http://localhost:8000/docs" -ForegroundColor White
Write-Host "  * Health Endpoint:            http://localhost:8000/health" -ForegroundColor White
Write-Host "  * Ingestion Automation:       ACTIVE (Automatic cycle after 5s + Every 60m)" -ForegroundColor White
Write-Host ""
Write-Host "===============================================================================" -ForegroundColor Green
Write-Host "  Keep the Backend and Frontend command windows open while working." -ForegroundColor Gray
Write-Host "  To shut down the platform, close the respective command windows." -ForegroundColor Gray
Write-Host "===============================================================================" -ForegroundColor Green
Write-Host ""
