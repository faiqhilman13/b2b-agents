@echo off
REM Malaysian Lead Generator - Batch script to run the lead generator
REM This script launches the lead generator tool with specified arguments

REM Set default values
SET OUTPUT_DIR=output
SET VERBOSE=
SET SCRAPE_YP=--scrape-yellow-pages
SET SCRAPE_GOV=
SET SCRAPE_UNI=
SET MAX_PAGES=5
SET MIN_DELAY=2.0
SET MAX_DELAY=5.0
SET GEN_EMAILS=
SET SEND_EMAILS=
SET TEST_MODE=--test-mode
SET PACKAGE=

REM Parse command line arguments
:parse_args
IF "%~1"=="" GOTO run
IF /I "%~1"=="--all" (
    SET SCRAPE_YP=--scrape-yellow-pages
    SET SCRAPE_GOV=--scrape-gov
    SET SCRAPE_UNI=--scrape-universities
    SHIFT
    GOTO parse_args
)
IF /I "%~1"=="--yp" (
    SET SCRAPE_YP=--scrape-yellow-pages
    SHIFT
    GOTO parse_args
)
IF /I "%~1"=="--gov" (
    SET SCRAPE_GOV=--scrape-gov
    SHIFT
    GOTO parse_args
)
IF /I "%~1"=="--uni" (
    SET SCRAPE_UNI=--scrape-universities
    SHIFT
    GOTO parse_args
)
IF /I "%~1"=="--pages" (
    SET MAX_PAGES=%~2
    SHIFT
    SHIFT
    GOTO parse_args
)
IF /I "%~1"=="--generate" (
    SET GEN_EMAILS=--generate-emails
    SHIFT
    GOTO parse_args
)
IF /I "%~1"=="--send" (
    SET GEN_EMAILS=--generate-emails
    SET SEND_EMAILS=--send-emails
    SHIFT
    GOTO parse_args
)
IF /I "%~1"=="--package" (
    SET PACKAGE=--package %~2
    SHIFT
    SHIFT
    GOTO parse_args
)
IF /I "%~1"=="--live" (
    SET TEST_MODE=
    SHIFT
    GOTO parse_args
)
IF /I "%~1"=="--verbose" (
    SET VERBOSE=--verbose
    SHIFT
    GOTO parse_args
)
IF /I "%~1"=="--help" (
    ECHO Malaysian Lead Generator - Batch Helper Script
    ECHO.
    ECHO Usage: run_lead_generator.bat [options]
    ECHO.
    ECHO Options:
    ECHO   --all        Scrape all sources (Yellow Pages, Government, Universities)
    ECHO   --yp         Scrape Yellow Pages
    ECHO   --gov        Scrape Government websites
    ECHO   --uni        Scrape University websites
    ECHO   --pages N    Number of pages to scrape per source (default: 5)
    ECHO   --generate   Generate emails for collected leads
    ECHO   --send       Generate and send emails
    ECHO   --package X  Specify proposal package (e.g., meeting, seminar)
    ECHO   --live       Live mode - actually sends emails (default: test mode)
    ECHO   --verbose    Increase output verbosity
    ECHO   --help       Show this help message
    ECHO.
    ECHO Examples:
    ECHO   run_lead_generator.bat --all --pages 3
    ECHO   run_lead_generator.bat --yp --gov --generate
    ECHO   run_lead_generator.bat --send --package meeting --live
    EXIT /B
)

SHIFT
GOTO parse_args

:run
ECHO Running Malaysian Lead Generator...
ECHO.

python -m lead_generator.main ^
    --output-dir %OUTPUT_DIR% ^
    %VERBOSE% ^
    %SCRAPE_YP% ^
    %SCRAPE_GOV% ^
    %SCRAPE_UNI% ^
    --max-pages-per-source %MAX_PAGES% ^
    --min-delay %MIN_DELAY% ^
    --max-delay %MAX_DELAY% ^
    %GEN_EMAILS% ^
    %SEND_EMAILS% ^
    %TEST_MODE% ^
    %PACKAGE%

IF %ERRORLEVEL% NEQ 0 (
    ECHO.
    ECHO Error: Lead Generator failed with exit code %ERRORLEVEL%
    EXIT /B %ERRORLEVEL%
)

ECHO.
ECHO Lead Generator completed successfully.
ECHO. 