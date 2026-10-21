@echo off
setlocal EnableDelayedExpansion

:: Ensure we are always in the project directory regardless of how run.bat was launched
cd /d "%~dp0"

title Borsel Handler — Institutional Market Intelligence Platform

echo ===============================================================================
echo        BORSEL HANDLER — AI-POWERED INDIAN FINANCIAL INTELLIGENCE
echo                   Localhost Automated Full-Stack Launcher
echo ===============================================================================
echo.

:: 1. Detect Python Executable (prioritize venv, then py launcher, then python)
set "PY_CMD="
if exist ".venv\Scripts\python.exe" (
    set "PY_CMD=.venv\Scripts\python.exe"
) else if exist "venv\Scripts\python.exe" (
    set "PY_CMD=venv\Scripts\python.exe"
) else (
    py -3 --version >nul 2>&1
    if !ERRORLEVEL! equ 0 (
        set "PY_CMD=py -3"
    ) else (
        py --version >nul 2>&1
        if !ERRORLEVEL! equ 0 (
            set "PY_CMD=py"
        ) else (
            python --version >nul 2>&1
            if !ERRORLEVEL! equ 0 (
                set "PY_CMD=python"
            ) else (
                python3 --version >nul 2>&1
                if !ERRORLEVEL! equ 0 (
                    set "PY_CMD=python3"
                )
            )
        )
    )
)

if "%PY_CMD%"=="" (
    echo [ERROR] Python 3 was not detected on your system.
    echo Please install Python 3.11+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [OK] Python runtime detected:
%PY_CMD% --version
echo.

:: 2. Detect Node.js and npm (use 'call' so npm.cmd does not terminate this batch script!)
node -v >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js was not detected on your PATH.
    echo Please install Node.js 20+ from https://nodejs.org/
    echo.
    pause
    exit /b 1
)

call npm -v >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] npm was not detected on your PATH.
    echo Please ensure npm is installed and added to PATH.
    echo.
    pause
    exit /b 1
)

echo [OK] Node.js detected:
node -v
echo [OK] npm detected:
call npm -v
echo.

:: 3. Environment Configuration
if not exist ".env" (
    if exist ".env.example" (
        echo [INFO] .env not found. Creating from .env.example...
        copy ".env.example" ".env" >nul
        echo [OK] Created .env configuration.
    ) else (
        echo [WARNING] .env.example not found, continuing with defaults.
    )
) else (
    echo [OK] .env configuration found.
)

:: Ensure ENABLE_AUTO_INGEST=true is active for localhost automation
set ENABLE_AUTO_INGEST=true

echo.
echo [INFO] Applying database migrations (Alembic)...
%PY_CMD% -m alembic upgrade head
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Alembic upgrade reported non-zero status. Proceeding with application startup...
) else (
    echo [OK] Database schema up to date.
)
echo.

:: 4. Frontend Dependencies Check
if not exist "frontend\node_modules" (
    echo [INFO] Installing frontend dependencies [npm install]...
    pushd frontend
    call npm install
    popd
    echo [OK] Frontend dependencies installed.
    echo.
) else (
    echo [OK] Frontend dependencies already installed.
)

:: 5. Launch Backend Server with Ingestion Automation in a New Window
echo [INFO] Launching FastAPI Backend and Ingestion Automation [Port 8000]...
start "Borsel Backend (Port 8000)" cmd /k "title Borsel Backend (Port 8000) && set ENABLE_AUTO_INGEST=true && %PY_CMD% -m uvicorn borsel_handler.api.app:app --host 0.0.0.0 --port 8000 --reload"

:: 6. Launch Frontend React Dashboard in a New Window
echo [INFO] Launching React 19 Financial Dashboard [Port 5173]...
start "Borsel Frontend (Port 5173)" cmd /k "title Borsel Frontend (Port 5173) && cd /d "%CD%\frontend" && call npm run dev"

:: 7. Wait briefly for services to initialize
echo.
echo [INFO] Waiting 3 seconds for services to initialize...
timeout /t 3 /nobreak >nul 2>&1 || ping -n 4 127.0.0.1 >nul

:: 8. Automatically open browser
echo [INFO] Opening default browser to Dashboard (http://localhost:5173)...
start http://localhost:5173

echo.
echo ===============================================================================
echo                         SYSTEM SUCCESSFULLY STARTED!
echo ===============================================================================
echo.
echo   * React Financial Dashboard:  http://localhost:5173
echo   * FastAPI REST Server:        http://localhost:8000
echo   * Interactive Swagger Docs:   http://localhost:8000/docs
echo   * Health Endpoint:            http://localhost:8000/health
echo   * Ingestion Automation:       ACTIVE (Automatic cycle after 5s + Every 60m)
echo.
echo ===============================================================================
echo   Keep the Backend and Frontend command windows open while working.
echo   To shut down the platform, close the respective command windows.
echo ===============================================================================
echo.
pause
