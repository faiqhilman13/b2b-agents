@echo off
rem ==============================================================
rem Malaysian Lead Generator - Web Scraper Execution Script
rem This script runs the web scraping modules to collect lead data
rem ==============================================================

echo.
echo Malaysian Lead Generator - Web Scraper
echo =====================================
echo.

setlocal EnableDelayedExpansion

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
set CONFIG_FILE=config\scraper_config.json
set OUTPUT_DIR=output
set LOG_FILE=logs\scraper_%date:~10,4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%.log
set LOG_FILE=%LOG_FILE: =0%
set SOURCES=all
set LIMIT=0
set HEADLESS=true
set PROXY=
set TARGET=
set DRY_RUN=false

rem Parse command line arguments
:parse_args
if "%~1"=="" goto run_scraper
if /i "%~1"=="--config" (
    set CONFIG_FILE=%~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--output" (
    set OUTPUT_DIR=%~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--log" (
    set LOG_FILE=%~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--sources" (
    set SOURCES=%~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--limit" (
    set LIMIT=%~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--visible" (
    set HEADLESS=false
    shift
    goto parse_args
)
if /i "%~1"=="--proxy" (
    set PROXY=%~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--target" (
    set TARGET=%~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--dry-run" (
    set DRY_RUN=true
    shift
    goto parse_args
)
echo WARNING: Unknown parameter: %~1
shift
goto parse_args

:run_scraper
rem Make sure output and log directories exist
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"
if not exist logs mkdir logs

rem Build command with parameters
set CMD=python -m lead_generator.scrapers.runner

if exist %CONFIG_FILE% (
    set CMD=!CMD! --config "%CONFIG_FILE%"
) else (
    echo WARNING: Config file %CONFIG_FILE% not found, using defaults.
)

set CMD=!CMD! --output "%OUTPUT_DIR%"
set CMD=!CMD! --log "%LOG_FILE%"

if not "%SOURCES%"=="all" (
    set CMD=!CMD! --sources "%SOURCES%"
)

if %LIMIT% GTR 0 (
    set CMD=!CMD! --limit %LIMIT%
)

if "%HEADLESS%"=="false" (
    set CMD=!CMD! --visible
)

if not "%PROXY%"=="" (
    set CMD=!CMD! --proxy "%PROXY%"
)

if not "%TARGET%"=="" (
    set CMD=!CMD! --target "%TARGET%"
)

if "%DRY_RUN%"=="true" (
    set CMD=!CMD! --dry-run
    echo Running in DRY RUN mode - no data will be saved.
)

rem Load environment variables if .env file exists
if exist .env (
    echo Loading environment from .env file...
    for /F "tokens=*" %%A in (.env) do (
        set %%A
    )
)

echo.
echo Running: !CMD!
echo Logging to: %LOG_FILE%
echo.

rem Execute the scraper script
call !CMD!

rem Check for errors
if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Scraper failed with error code %ERRORLEVEL%.
    goto :end
)

echo.
echo Scraping completed successfully.
echo Results saved to %OUTPUT_DIR%

:end
popd
echo.
pause 