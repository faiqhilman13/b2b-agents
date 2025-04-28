@echo off
REM Malaysian Lead Generator - API Server Runner
REM This script launches the FastAPI server for the lead generator API

REM Set default values
SET HOST=127.0.0.1
SET PORT=8000
SET RELOAD=--reload
SET WORKERS=1
SET LOG_LEVEL=info
SET PRODUCTION=

REM Parse command line arguments
:parse_args
IF "%~1"=="" GOTO run
IF /I "%~1"=="--host" (
    SET HOST=%~2
    SHIFT
    SHIFT
    GOTO parse_args
)
IF /I "%~1"=="--port" (
    SET PORT=%~2
    SHIFT
    SHIFT
    GOTO parse_args
)
IF /I "%~1"=="--workers" (
    SET WORKERS=%~2
    SHIFT
    SHIFT
    GOTO parse_args
)
IF /I "%~1"=="--no-reload" (
    SET RELOAD=
    SHIFT
    GOTO parse_args
)
IF /I "%~1"=="--production" (
    SET PRODUCTION=--production
    SET RELOAD=
    SET WORKERS=4
    SHIFT
    GOTO parse_args
)
IF /I "%~1"=="--help" (
    ECHO Malaysian Lead Generator API - Server Runner
    ECHO.
    ECHO Usage: run_api.bat [options]
    ECHO.
    ECHO Options:
    ECHO   --host IP       Host IP to bind to (default: 127.0.0.1)
    ECHO   --port N        Port to listen on (default: 8000)
    ECHO   --workers N     Number of worker processes (default: 1)
    ECHO   --no-reload     Disable auto-reload on code changes
    ECHO   --production    Run in production mode (implies --no-reload and workers=4)
    ECHO   --help          Show this help message
    ECHO.
    ECHO Examples:
    ECHO   run_api.bat
    ECHO   run_api.bat --host 0.0.0.0 --port 5000
    ECHO   run_api.bat --production
    EXIT /B
)

SHIFT
GOTO parse_args

:run
ECHO Starting Malaysian Lead Generator API Server...
ECHO Host: %HOST%
ECHO Port: %PORT%
ECHO Workers: %WORKERS%
IF NOT "%RELOAD%"=="" (
    ECHO Mode: Development (auto-reload enabled)
) ELSE (
    IF "%PRODUCTION%"=="" (
        ECHO Mode: Development
    ) ELSE (
        ECHO Mode: Production
    )
)
ECHO.

uvicorn lead_generator.api.app:app --host %HOST% --port %PORT% --workers %WORKERS% %RELOAD% %PRODUCTION%

IF %ERRORLEVEL% NEQ 0 (
    ECHO.
    ECHO Error: API server failed with exit code %ERRORLEVEL%
    EXIT /B %ERRORLEVEL%
) 