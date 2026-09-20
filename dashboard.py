#!/usr/bin/env python3
"""
Quick Start - Dashboard Launcher
Uruchomienie: python dashboard.py
"""

import subprocess
import sys
import os

WORKING_DIR = os.path.dirname(os.path.abspath(__file__))

def check_deps():
    missing = []
    try:
        import websockets
    except ImportError:
        missing.append("websockets")
    try:
        import aiohttp
    except ImportError:
        missing.append("aiohttp")

    if missing:
        print(f"[*] Brakujące zależności: {', '.join(missing)}")
        print(f"[*] Instalacja...")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
        print(f"[OK] Zainstalowano!\n")

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║           UNIFIED CHAOS PLATFORM - DASHBOARD LAUNCHER       ║
║  Bezpieczeństwo: localhost only (127.0.0.1)                 ║
║  Port: auto-detect (8880, 8881, 8882...)                    ║
╚══════════════════════════════════════════════════════════════╝
    """)

    check_deps()

    print("[*] Uruchamiam serwer dashboard...")
    print("[*] Przeglądarka otworzy się automatycznie")
    print("[*] Ctrl+C aby zatrzymać\n")

    server_path = os.path.join(WORKING_DIR, "server.py")
    subprocess.run([sys.executable, server_path], cwd=WORKING_DIR)

if __name__ == "__main__":
    main()
