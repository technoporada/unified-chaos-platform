@echo off
REM ============================================================================
REM  UNIFIED CHAOS PLATFORM v1.0 - Windows Launcher
REM  Quick launcher for the integrated network security testing suite
REM ============================================================================

setlocal enabledelayedexpansion

REM ============================================================================
REM CHECK PYTHON INSTALLATION
REM ============================================================================

python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [!] ERROR: Python nie znaleziony.
    echo.
    echo Instalacja wymagana:
    echo   1. Pobierz z: https://python.org
    echo   2. Zainstaluj (Select: Add Python to PATH)
    echo   3. Uruchom ten plik ponownie
    echo.
    pause
    exit /b 1
)

REM ============================================================================
REM CLEAR SCREEN & DISPLAY BANNER
REM ============================================================================

cls
echo.
echo ════════════════════════════════════════════════════════════════════════════
echo     UNIFIED CHAOS PLATFORM v1.0
echo     Integrated Network Analysis ^& Security Testing Suite
echo ════════════════════════════════════════════════════════════════════════════
echo.

REM ============================================================================
REM DISPLAY MENU
REM ============================================================================

:menu
echo ──────────────────────────────────────────────────────────────────────────
echo  SELECT OPERATION:
echo ──────────────────────────────────────────────────────────────────────────
echo.
echo  [1] Quick Start (Interactive Tutorial)
echo  [2] Launch Platform (Main Application)
echo  [3] View Documentation
echo  [4] Edit Configuration (config.json)
echo  [5] Check Python Modules
echo  [6] Run Tests
echo  [7] Install Requirements
echo  [8] Dashboard (Web Interface)
echo  [9] Exit
echo.

set /p choice="Select option (1-9): "

if "%choice%"=="1" goto quickstart
if "%choice%"=="2" goto platform
if "%choice%"=="3" goto docs
if "%choice%"=="4" goto config
if "%choice%"=="5" goto modules
if "%choice%"=="6" goto tests
if "%choice%"=="7" goto install
if "%choice%"=="8" goto dashboard
if "%choice%"=="9" goto exit
if "%choice%"=="" goto menu

echo [!] Invalid option. Try again.
timeout /t 2 > nul
goto menu

REM ============================================================================
REM [1] QUICK START
REM ============================================================================

:quickstart
cls
echo.
echo [*] Starting Interactive Quick Start Tutorial...
echo.
python quick_start.py
echo.
echo [*] Tutorial completed.
pause
goto menu

REM ============================================================================
REM [2] MAIN PLATFORM
REM ============================================================================

:platform
cls
echo.
echo [*] Launching UNIFIED CHAOS PLATFORM...
echo [*] Press Ctrl+C to exit.
echo.
timeout /t 2 > nul
python UNIFIED_CHAOS_PLATFORM.py
pause
goto menu

REM ============================================================================
REM [3] DOCUMENTATION
REM ============================================================================

:docs
cls
echo.
echo ──────────────────────────────────────────────────────────────────────────
echo  AVAILABLE DOCUMENTATION
echo ──────────────────────────────────────────────────────────────────────────
echo.
echo  [1] README.txt (Quick Reference)
echo  [2] DOKUMENTACJA.md (Full Guide)
echo  [3] CHANGELOG.md (Version History)
echo  [4] SUMMARY.txt (Project Summary)
echo  [5] index.html (Online Docs)
echo  [0] Back to Menu
echo.

set /p docChoice="Select documentation (0-5): "

if "%docChoice%"=="1" (
    echo.
    more README.txt
    pause
) else if "%docChoice%"=="2" (
    echo.
    more DOKUMENTACJA.md
    pause
) else if "%docChoice%"=="3" (
    echo.
    more CHANGELOG.md
    pause
) else if "%docChoice%"=="4" (
    echo.
    more SUMMARY.txt
    pause
) else if "%docChoice%"=="5" (
    echo.
    echo [*] Opening index.html in default browser...
    start index.html
) else if "%docChoice%"=="0" (
    goto menu
) else (
    echo [!] Invalid option.
    timeout /t 1 > nul
)

goto docs

REM ============================================================================
REM [4] EDIT CONFIGURATION
REM ============================================================================

:config
cls
echo.
echo [*] Opening config.json in Notepad...
echo.
timeout /t 1 > nul
notepad config.json
goto menu

REM ============================================================================
REM [5] CHECK MODULES
REM ============================================================================

:modules
cls
echo.
echo ──────────────────────────────────────────────────────────────────────────
echo  CHECKING PYTHON MODULES
echo ──────────────────────────────────────────────────────────────────────────
echo.

python -c "import sys; print(f'Python Version: {sys.version}'); print(f'Executable: {sys.executable}')"
echo.

echo [*] Core modules (built-in):
python -c "
import socket, threading, time, random, struct, ssl, sys, os, re
print('  [OK] socket')
print('  [OK] threading')
print('  [OK] time')
print('  [OK] random')
print('  [OK] struct')
print('  [OK] ssl')
print('  [OK] sys')
print('  [OK] os')
print('  [OK] re')
"

echo.
echo [*] Optional modules:
python -c "
modules = ['requests', 'cryptography', 'paramiko', 'psutil']
for mod in modules:
    try:
        __import__(mod)
        print(f'  [OK] {mod}')
    except ImportError:
        print(f'  [--] {mod} (not installed)')
"

echo.
pause
goto menu

REM ============================================================================
REM [6] RUN TESTS
REM ============================================================================

:tests
cls
echo.
echo ──────────────────────────────────────────────────────────────────────────
echo  RUNNING PLATFORM TESTS
echo ──────────────────────────────────────────────────────────────────────────
echo.

echo [*] Test 1: Import main module...
python -c "import UNIFIED_CHAOS_PLATFORM; print('  [OK] Module imported')" 2>&1
if %errorlevel% neq 0 (
    echo  [!] Import failed. Check file syntax.
) else (
    echo  [OK] Import successful
)

echo.
echo [*] Test 2: Check configuration...
python -c "import json; json.load(open('config.json')); print('  [OK] Config valid')" 2>&1
if %errorlevel% neq 0 (
    echo  [!] Config invalid. Check JSON syntax.
) else (
    echo  [OK] Config valid
)

echo.
echo [*] Test 3: Network ports availability...
python -c "
import socket
ports = [8888, 9000, 11111, 11112]
for port in ports:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1', port))
        s.close()
        print(f'  [OK] Port {port} available')
    except:
        print(f'  [!] Port {port} in use')
"

echo.
echo [*] All tests completed.
echo.
pause
goto menu

REM ============================================================================
REM [7] INSTALL REQUIREMENTS
REM ============================================================================

:install
cls
echo.
echo ──────────────────────────────────────────────────────────────────────────
echo  INSTALL REQUIREMENTS
echo ──────────────────────────────────────────────────────────────────────────
echo.

echo [*] Note: Core platform requires NO external dependencies.
echo [*] All modules use Python built-in libraries.
echo.

echo Do you want to install optional packages? (requests, colorama, etc.)
set /p installChoice="Install optional packages? (y/n): "

if /i "%installChoice%"=="y" (
    echo.
    echo [*] Installing recommended packages...
    echo.
    pip install requests colorama loguru psutil --user
    echo.
    echo [*] Installation completed.
) else (
    echo [*] Skipped optional installation.
)

echo.
pause
goto menu

REM ============================================================================
REM [8] DASHBOARD (WEB INTERFACE)
REM ============================================================================

:dashboard
cls
echo.
echo [*] Starting Dashboard (Web Interface)...
echo [*] Browser will open automatically.
echo [*] Press Ctrl+C to stop server.
echo.
timeout /t 2 > nul
python dashboard.py
pause
goto menu

REM ============================================================================
REM EXIT
REM ============================================================================

:exit
cls
echo.
echo [*] Thank you for using Unified Chaos Platform v1.0
echo [*] For documentation: Read README.txt or run quick_start.py
echo [*] Stay ethical!
echo.
exit /b 0

REM ============================================================================
REM END OF SCRIPT
REM ============================================================================
