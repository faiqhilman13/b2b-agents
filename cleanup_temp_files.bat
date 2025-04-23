@echo off
rem ==========================================================================
rem Cleanup Script for Malaysian Lead Generator
rem This batch file runs the cleanup_temp_files.py script to remove temporary
rem files and compress logs. Can be scheduled as a Windows task.
rem ==========================================================================

echo.
echo Malaysian Lead Generator - Cleanup Utility
echo ===========================================
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

rem Check if the cleanup script exists
if not exist cleanup_temp_files.py (
    echo ERROR: cleanup_temp_files.py not found in the current directory.
    goto :end
)

rem Set default values
set CONFIG_FILE=config\cleanup_config.json
set DRY_RUN=false
set VERBOSE=false
set FORCE=false

rem Parse arguments
:parse_args
if "%~1"=="" goto run_cleanup
if /i "%~1"=="--dry-run" (
    set DRY_RUN=true
    shift
    goto parse_args
)
if /i "%~1"=="--verbose" (
    set VERBOSE=true
    shift
    goto parse_args
)
if /i "%~1"=="--force" (
    set FORCE=true
    shift
    goto parse_args
)
if /i "%~1"=="--config" (
    set CONFIG_FILE=%~2
    shift
    shift
    goto parse_args
)
echo WARNING: Unknown parameter: %~1
shift
goto parse_args

:run_cleanup
rem Build command with parameters
set CMD=python cleanup_temp_files.py

if exist %CONFIG_FILE% (
    set CMD=!CMD! --config %CONFIG_FILE%
) else (
    echo WARNING: Config file %CONFIG_FILE% not found, using defaults.
)

if %DRY_RUN%==true (
    set CMD=!CMD! --dry-run
    echo Running in DRY RUN mode - no files will be deleted.
)

if %VERBOSE%==true (
    set CMD=!CMD! --verbose
    echo Verbose output enabled.
)

if %FORCE%==true (
    set CMD=!CMD! --force
    echo Force mode enabled - age thresholds will be ignored.
)

echo.
echo Running: !CMD!
echo.

rem Execute the cleanup script
call !CMD!

rem Check for errors
if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Cleanup script failed with error code %ERRORLEVEL%.
    goto :end
)

echo.
echo Cleanup completed successfully.

:end
popd
echo.
pause 