# ============================================================================
# UNIFIED CHAOS PLATFORM v1.0 - PowerShell Launcher
# Quick launcher for the integrated network security testing suite
# ============================================================================

# Set console properties
$Host.UI.RawUI.ForegroundColor = 'Green'
$Host.UI.RawUI.BackgroundColor = 'Black'
Clear-Host

# ============================================================================
# FUNCTIONS
# ============================================================================

function Show-Banner {
    Write-Host "════════════════════════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host "     UNIFIED CHAOS PLATFORM v1.0" -ForegroundColor Green
    Write-Host "     Integrated Network Analysis & Security Testing Suite" -ForegroundColor Green
    Write-Host "════════════════════════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host ""
}

function Show-Menu {
    Write-Host "──────────────────────────────────────────────────────────────────────────" -ForegroundColor Cyan
    Write-Host " SELECT OPERATION:" -ForegroundColor Cyan
    Write-Host "──────────────────────────────────────────────────────────────────────────" -ForegroundColor Cyan
    Write-Host ""
    Write-Host " [1] Quick Start (Interactive Tutorial)"
    Write-Host " [2] Launch Platform (Main Application)"
    Write-Host " [3] View Documentation"
    Write-Host " [4] Edit Configuration (config.json)"
    Write-Host " [5] Check Python Modules"
    Write-Host " [6] Run Tests"
    Write-Host " [7] System Information"
    Write-Host " [8] Dashboard (Web Interface)"
    Write-Host " [9] Exit"
    Write-Host ""
}

function Start-QuickStart {
    Clear-Host
    Write-Host "[*] Starting Interactive Quick Start Tutorial..." -ForegroundColor Yellow
    Write-Host ""
    & python quick_start.py
    Write-Host ""
    Read-Host "Press Enter to continue"
}

function Start-Platform {
    Clear-Host
    Write-Host "[*] Launching UNIFIED CHAOS PLATFORM..." -ForegroundColor Yellow
    Write-Host "[*] Type 'exit' in menu to return here" -ForegroundColor Yellow
    Write-Host ""
    Start-Sleep -Seconds 2
    & python UNIFIED_CHAOS_PLATFORM.py
    Write-Host ""
    Read-Host "Press Enter to continue"
}

function Show-Documentation {
    $docMenu = $true
    while ($docMenu) {
        Clear-Host
        Write-Host "──────────────────────────────────────────────────────────────────────────" -ForegroundColor Cyan
        Write-Host " AVAILABLE DOCUMENTATION" -ForegroundColor Cyan
        Write-Host "──────────────────────────────────────────────────────────────────────────" -ForegroundColor Cyan
        Write-Host ""
        Write-Host " [1] README.txt (Quick Reference)"
        Write-Host " [2] DOKUMENTACJA.md (Full Guide)"
        Write-Host " [3] CHANGELOG.md (Version History)"
        Write-Host " [4] SUMMARY.txt (Project Summary)"
        Write-Host " [5] index.html (Online Docs)"
        Write-Host " [0] Back to Menu"
        Write-Host ""
        
        $docChoice = Read-Host "Select documentation (0-5)"
        
        switch ($docChoice) {
            "1" { 
                Get-Content README.txt | less
            }
            "2" { 
                Get-Content DOKUMENTACJA.md | less
            }
            "3" { 
                Get-Content CHANGELOG.md | less
            }
            "4" { 
                Get-Content SUMMARY.txt | less
            }
            "5" { 
                Write-Host "[*] Opening index.html in default browser..." -ForegroundColor Yellow
                Start-Process index.html
            }
            "0" { 
                $docMenu = $false
            }
            default { 
                Write-Host "[!] Invalid option" -ForegroundColor Red
                Start-Sleep -Seconds 1
            }
        }
    }
}

function Edit-Configuration {
    Write-Host "[*] Opening config.json in Notepad..." -ForegroundColor Yellow
    Start-Sleep -Seconds 1
    & notepad config.json
}

function Check-Modules {
    Clear-Host
    Write-Host "──────────────────────────────────────────────────────────────────────────" -ForegroundColor Cyan
    Write-Host " CHECKING PYTHON MODULES" -ForegroundColor Cyan
    Write-Host "──────────────────────────────────────────────────────────────────────────" -ForegroundColor Cyan
    Write-Host ""
    
    # Check Python version
    Write-Host "[*] Python Version:" -ForegroundColor Yellow
    & python --version
    Write-Host ""
    
    # Check core modules
    Write-Host "[*] Core modules (built-in):" -ForegroundColor Yellow
    $coreModules = @('socket', 'threading', 'time', 'random', 'struct', 'ssl', 'sys', 'os', 're')
    foreach ($mod in $coreModules) {
        try {
            python -c "import $mod" -ErrorAction Stop
            Write-Host "  [OK] $mod" -ForegroundColor Green
        } catch {
            Write-Host "  [!] $mod (failed)" -ForegroundColor Red
        }
    }
    
    Write-Host ""
    Write-Host "[*] Optional modules:" -ForegroundColor Yellow
    $optionalModules = @('requests', 'cryptography', 'paramiko', 'psutil')
    foreach ($mod in $optionalModules) {
        try {
            python -c "import $mod" -ErrorAction Stop
            Write-Host "  [OK] $mod" -ForegroundColor Green
        } catch {
            Write-Host "  [--] $mod (not installed)" -ForegroundColor Yellow
        }
    }
    
    Write-Host ""
    Read-Host "Press Enter to continue"
}

function Run-Tests {
    Clear-Host
    Write-Host "──────────────────────────────────────────────────────────────────────────" -ForegroundColor Cyan
    Write-Host " RUNNING PLATFORM TESTS" -ForegroundColor Cyan
    Write-Host "──────────────────────────────────────────────────────────────────────────" -ForegroundColor Cyan
    Write-Host ""
    
    # Test 1: Import
    Write-Host "[*] Test 1: Import main module..." -ForegroundColor Yellow
    try {
        python -c "import UNIFIED_CHAOS_PLATFORM" -ErrorAction Stop
        Write-Host "  [OK] Module imported" -ForegroundColor Green
    } catch {
        Write-Host "  [!] Import failed" -ForegroundColor Red
    }
    
    # Test 2: Config
    Write-Host "[*] Test 2: Check configuration..." -ForegroundColor Yellow
    try {
        python -c "import json; json.load(open('config.json'))" -ErrorAction Stop
        Write-Host "  [OK] Config valid" -ForegroundColor Green
    } catch {
        Write-Host "  [!] Config invalid" -ForegroundColor Red
    }
    
    # Test 3: Ports
    Write-Host "[*] Test 3: Network ports availability..." -ForegroundColor Yellow
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
    
    Write-Host ""
    Write-Host "[*] All tests completed." -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Press Enter to continue"
}

function Show-SystemInfo {
    Clear-Host
    Write-Host "──────────────────────────────────────────────────────────────────────────" -ForegroundColor Cyan
    Write-Host " SYSTEM INFORMATION" -ForegroundColor Cyan
    Write-Host "──────────────────────────────────────────────────────────────────────────" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "Computer Name: " -NoNewline -ForegroundColor Yellow
    Write-Host $env:COMPUTERNAME
    
    Write-Host "OS: " -NoNewline -ForegroundColor Yellow
    Write-Host (Get-WmiObject Win32_OperatingSystem).Caption
    
    Write-Host "Architecture: " -NoNewline -ForegroundColor Yellow
    Write-Host ([System.Environment]::Is64BitOperatingSystem ? "64-bit" : "32-bit")
    
    Write-Host "Available Memory: " -NoNewline -ForegroundColor Yellow
    $memory = (Get-WmiObject Win32_ComputerSystem).TotalPhysicalMemory / 1GB
    Write-Host "$([math]::Round($memory, 2)) GB"
    
    Write-Host "Processors: " -NoNewline -ForegroundColor Yellow
    Write-Host (Get-WmiObject Win32_Processor).Name
    
    Write-Host "PowerShell Version: " -NoNewline -ForegroundColor Yellow
    Write-Host $PSVersionTable.PSVersion
    
    Write-Host ""
    Read-Host "Press Enter to continue"
}

function Start-Dashboard {
    Clear-Host
    Write-Host "[*] Starting Dashboard (Web Interface)..." -ForegroundColor Yellow
    Write-Host "[*] Browser will open automatically" -ForegroundColor Yellow
    Write-Host "[*] Press Ctrl+C to stop server" -ForegroundColor Yellow
    Write-Host ""
    Start-Sleep -Seconds 2
    & python dashboard.py
    Write-Host ""
    Read-Host "Press Enter to continue"
}

# ============================================================================
# MAIN LOOP
# ============================================================================

$running = $true
while ($running) {
    Show-Banner
    Show-Menu
    
    $choice = Read-Host "Select option (1-8)"
    
    switch ($choice) {
        "1" { Start-QuickStart }
        "2" { Start-Platform }
        "3" { Show-Documentation }
        "4" { Edit-Configuration }
        "5" { Check-Modules }
        "6" { Run-Tests }
        "7" { Show-SystemInfo }
        "8" { Start-Dashboard }
        "9" { 
            $running = $false
            Clear-Host
            Write-Host "[*] Thank you for using Unified Chaos Platform v1.0" -ForegroundColor Green
            Write-Host "[*] Stay ethical!" -ForegroundColor Green
            Write-Host ""
        }
        default { 
            Write-Host "[!] Invalid option. Try again." -ForegroundColor Red
            Start-Sleep -Seconds 2
            Clear-Host
        }
    }
}

# ============================================================================
# END OF SCRIPT
# ============================================================================
