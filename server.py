#!/usr/bin/env python3
"""
Unified Chaos Platform - Dashboard Server (PRO Version)
========================================================
Uruchomienie: python server.py
Otwórz: http://localhost:8880

Bezpieczeństwo:
- Binduje TYLKO do localhost (127.0.0.1) - brak wycieków danych
- Sprawdza port przed startem
- Auto-skip gdy port zajęty przez inną aplikację
- Brak WebSocket, brak terminala, brak wykonywania komend w systemie (zero RCE)
- Proper logging zamiast print()
- Type hints dla code readability
"""

import logging
import os
import socket
import sys
import time
import webbrowser
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from aiohttp import web
except ImportError:
    print("[!] Brak biblioteki 'aiohttp'. Instalacja...")
    subprocess_check = __import__("subprocess")
    subprocess_check.check_call([sys.executable, "-m", "pip", "install", "aiohttp"])
    from aiohttp import web

# ============================================================================
# LOGGING CONFIG
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("chaos_server.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("ChaosServer")

# ============================================================================
# CONFIG
# ============================================================================
DASHBOARD_PORT: int = 8880
DASHBOARD_PORT_MAX: int = 8890
WORKING_DIR: str = os.path.dirname(os.path.abspath(__file__))

# ANSI Colors
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    CYAN    = "\033[96m"
    DIM     = "\033[2m"

# ============================================================================
# CONFIG VALIDATOR
# ============================================================================
class ConfigValidator:
    """Validate config.json at startup."""

    REQUIRED_KEYS = {
        "chaos_proxy": {"listen_port": int, "target_host": str, "target_port": int, "mutation_rate": float},
        "smuggling": {"threads": int, "timeout": int},
    }

    def validate(self, config_path: str) -> tuple:
        """Validate config file. Returns (is_valid, errors_list)."""
        errors = []

        if not os.path.exists(config_path):
            logger.warning(f"Config not found: {config_path} - using defaults")
            return True, []

        try:
            with open(config_path) as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            return False, [f"Invalid JSON: {e}"]

        for section, keys in self.REQUIRED_KEYS.items():
            if section not in config:
                errors.append(f"Missing section: {section}")
                continue
            for key, expected_type in keys.items():
                if key not in config[section]:
                    errors.append(f"Missing key: {section}.{key}")
                elif not isinstance(config[section][key], expected_type):
                    errors.append(f"Wrong type: {section}.{key} should be {expected_type.__name__}")

        # Validate port ranges
        if "chaos_proxy" in config:
            port = config["chaos_proxy"].get("listen_port", 0)
            if port < 1024 or port > 65535:
                errors.append(f"Invalid port: {port} (should be 1024-65535)")
            rate = config["chaos_proxy"].get("mutation_rate", 0)
            if rate < 0 or rate > 1:
                errors.append(f"Invalid mutation_rate: {rate} (should be 0.0-1.0)")

        if "smuggling" in config:
            threads = config["smuggling"].get("threads", 0)
            if threads < 1 or threads > 100:
                errors.append(f"Invalid threads: {threads} (should be 1-100)")

        return len(errors) == 0, errors

# ============================================================================
# PORT DETECTION
# ============================================================================
def is_port_free(port: int) -> bool:
    """Check if port is free."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex(("127.0.0.1", port)) != 0

def is_our_platform(port: int) -> bool:
    """Check if the service on this port is OUR dashboard."""
    import urllib.request
    import urllib.error
    try:
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/",
            headers={"User-Agent": "UnifiedChaosPlatform/1.0"}
        )
        resp = urllib.request.urlopen(req, timeout=2)
        body = resp.read().decode(errors="ignore").lower()
        return "unified chaos" in body or "chaos platform" in body
    except (urllib.error.URLError, socket.timeout, ConnectionRefusedError, OSError):
        return False

def get_process_on_port(port: int) -> Optional[str]:
    """Try to find what process is using this port."""
    try:
        import subprocess as sp
        if sys.platform == "win32":
            result = sp.run(
                ["netstat", "-ano"],
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.splitlines():
                if f":{port}" in line and "LISTENING" in line:
                    parts = line.split()
                    pid = parts[-1]
                    result2 = sp.run(
                        ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
                        capture_output=True, text=True, timeout=5
                    )
                    if result2.stdout:
                        name = result2.stdout.split(",")[0].strip('"')
                        return f"{name} (PID: {pid})"
                    return f"PID: {pid}"
        else:
            result = sp.run(
                ["lsof", "-i", f":{port}", "-sTCP:LISTEN", "-n", "-P"],
                capture_output=True, text=True, timeout=5
            )
            lines = result.stdout.strip().splitlines()
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 2:
                    return f"{parts[0]} (PID: {parts[1]})"
    except Exception as e:
        logger.debug(f"Port detection failed: {e}")
    return None

def find_free_port() -> Optional[int]:
    """Smart port detection with status messages."""
    logger.info(f"Checking port {DASHBOARD_PORT}...")

    if is_port_free(DASHBOARD_PORT):
        logger.info(f"Port {DASHBOARD_PORT} is free - using it")
        return DASHBOARD_PORT

    logger.warning(f"Port {DASHBOARD_PORT} is busy...")

    if is_our_platform(DASHBOARD_PORT):
        logger.info(f"Platform already running on port {DASHBOARD_PORT}")
        print(f"""
{C.GREEN}{C.BOLD}╔══════════════════════════════════════════════════════════════╗
║  ✓ PLATFORMA JUŻ DZIAŁA!                                   ║
║                                                              ║
║  Dashboard jest już uruchomiony na porcie {DASHBOARD_PORT}          ║
║  Otwórz: http://localhost:{DASHBOARD_PORT}                          ║
║  Nie uruchamiam drugiej kopii.                               ║
╚═══════════════════════════════════════════════════════════════╝{C.RESET}
        """)
        return None

    proc_info = get_process_on_port(DASHBOARD_PORT)
    proc_str = f" via: {proc_info}" if proc_info else ""

    logger.error(f"Port {DASHBOARD_PORT} occupied{proc_str}")

    for port in range(DASHBOARD_PORT + 1, DASHBOARD_PORT_MAX + 1):
        if is_port_free(port):
            logger.info(f"Port {port} is free - using it")
            print(f"{C.YELLOW}[*] Dashboard: http://localhost:{port}{C.RESET}\n")
            return port

    logger.critical(f"No free ports available ({DASHBOARD_PORT}-{DASHBOARD_PORT_MAX})")
    return None

# ============================================================================
# HTTP HANDLERS
# ============================================================================
async def handle_index(request: web.Request) -> web.Response:
    """Serve index.html."""
    index_path = os.path.join(WORKING_DIR, "index.html")
    if os.path.exists(index_path):
        return web.FileResponse(index_path)
    return web.Response(text="index.html not found", status=404)

async def handle_static(request: web.Request) -> web.Response:
    """Serve static files (confined to WORKING_DIR)."""
    raw_filename = request.match_info["filename"]
    filename = os.path.basename(raw_filename)
    if filename != raw_filename or filename in {".", ".."}:
        return web.Response(status=404)
    # Contain the path: reject anything that escapes WORKING_DIR (path traversal).
    base = os.path.realpath(WORKING_DIR)
    filepath = os.path.realpath(os.path.join(base, filename))
    if not (filepath == base or filepath.startswith(base + os.sep)):
        return web.Response(status=404)
    if os.path.isfile(filepath):
        return web.FileResponse(filepath)
    return web.Response(status=404)

# ============================================================================
# MAIN
# ============================================================================
def main() -> None:
    """Main entry point."""
    import json
    # Validate config
    config_path = os.path.join(WORKING_DIR, "config.json")
    validator = ConfigValidator()
    is_valid, errors = validator.validate(config_path)
    if not is_valid:
        logger.warning("Config validation warnings:")
        for error in errors:
            logger.warning(f"  - {error}")

    # Find available port
    port = find_free_port()
    if port is None:
        sys.exit(1)

    print(f"""
{C.GREEN}{C.BOLD}╔══════════════════════════════════════════════════════════════╗
║            UNIFIED CHAOS PLATFORM - DASHBOARD SERVER        ║
╠═══════════════════════════════════════════════════════════════╣
║  Dashboard:  http://localhost:{port:<5}                          ║
║  Terminal:   USUNIĘTY - brak wykonywania komend (zero RCE)  ║
║  Workspace:  {WORKING_DIR[:48]:<48}║
║  Bind:       127.0.0.1 (localhost only - BEZPIECZNE)         ║
║  Logging:    chaos_server.log                                ║
║  Status:     READY                                          ║
╚═══════════════════════════════════════════════════════════════╝{C.RESET}
    """)

    app = web.Application()

    app.router.add_get("/", handle_index)
    app.router.add_get("/{filename}", handle_static)

    def open_browser():
        webbrowser.open(f"http://localhost:{port}")

    loop = asyncio.get_event_loop()
    loop.call_later(1.0, open_browser)

    logger.info(f"Opening browser: http://localhost:{port}")
    logger.info("Press Ctrl+C to stop server")

    try:
        web.run_app(app, host="127.0.0.1", port=port, print=None)
    except OSError as e:
        if "Address already in use" in str(e):
            logger.critical(f"Port {port} already in use")
        else:
            logger.critical(f"Server error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        logger.info("Server stopped.")

if __name__ == "__main__":
    main()