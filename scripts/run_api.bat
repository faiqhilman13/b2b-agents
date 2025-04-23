@echo off
rem ==============================================================
rem Malaysian Lead Generator - API Server Startup Script
rem This script starts the FastAPI server for lead management
rem ==============================================================

echo.
echo Malaysian Lead Generator - API Server
echo ====================================
echo.

setlocal

rem Check if Python is available
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python is not found in PATH.
    echo Please ensure Python is installed and added to your PATH.
    goto :end
)

rem Set working directory to script location
pushd %~dp0

rem Default values
set PORT=8000
set HOST=0.0.0.0
set DEV_MODE=true
set LOG_LEVEL=info

rem Parse command line arguments
:parse_args
if "%~1"=="" goto start_server
if /i "%~1"=="--port" (
    set PORT=%~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--host" (
    set HOST=%~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--production" (
    set DEV_MODE=false
    shift
    goto parse_args
)
if /i "%~1"=="--log-level" (
    set LOG_LEVEL=%~2
    shift
    shift
    goto parse_args
)
echo WARNING: Unknown parameter: %~1
shift
goto parse_args

:start_server
echo Starting API server on %HOST%:%PORT% (Log level: %LOG_LEVEL%)

rem Load environment variables if .env file exists
if exist .env (
    echo Loading environment from .env file...
    for /F "tokens=*" %%A in (.env) do (
        set %%A
    )
)

rem Start the API server
if %DEV_MODE%==true (
    echo Running in development mode with auto-reload
    python -m uvicorn lead_generator.api.main:app --host %HOST% --port %PORT% --reload --log-level %LOG_LEVEL%
) else (
    echo Running in production mode
    python -m uvicorn lead_generator.api.main:app --host %HOST% --port %PORT% --log-level %LOG_LEVEL%
)

rem Check for errors
if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: API server failed to start with error code %ERRORLEVEL%.
    goto :end
)

:end
popd
echo.
pause 