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
- Rate limiting na WebSocket (anty-spam)
- Proper logging zamiast print()
- Type hints dla	code readability
"""

import asyncio
import json
import logging
import os
import signal
import socket
import subprocess
import sys
import time
import webbrowser
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import websockets
except ImportError:
    print("[!] Brak biblioteki 'websockets'. Instalacja...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "websockets"])
    import websockets

try:
    from aiohttp import web
except ImportError:
    print("[!] Brak biblioteki 'aiohttp'. Instalacja...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp"])
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
SHELL: str = "/bin/bash" if sys.platform != "win32" else "cmd.exe"

# Rate limiting
RATE_LIMIT_COMMANDS: int = 30  # max commands per minute
RATE_LIMIT_WINDOW: float = 60.0  # window in seconds

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
# RATE LIMITER
# ============================================================================
class RateLimiter:
    """Token bucket rate limiter for WebSocket commands."""

    def __init__(self, max_commands: int = RATE_LIMIT_COMMANDS, window: float = RATE_LIMIT_WINDOW):
        self.max_commands = max_commands
        self.window = window
        self.clients: Dict[str, list] = defaultdict(list)

    def is_allowed(self, client_id: str) -> bool:
        """Check if client is within rate limit."""
        now = time.time()
        # Remove old entries
        self.clients[client_id] = [
            t for t in self.clients[client_id] if now - t < self.window
        ]
        if len(self.clients[client_id]) >= self.max_commands:
            return False
        self.clients[client_id].append(now)
        return True

    def get_remaining(self, client_id: str) -> int:
        """Get remaining commands for client."""
        now = time.time()
        self.clients[client_id] = [
            t for t in self.clients[client_id] if now - t < self.window
        ]
        return max(0, self.max_commands - len(self.clients[client_id]))

    def remove_client(self, client_id: str) -> None:
        """Clean up client data."""
        self.clients.pop(client_id, None)

rate_limiter = RateLimiter()

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
║                                                              ║
║  Nie uruchamiam drugiej kopii.                               ║
╚══════════════════════════════════════════════════════════════╝{C.RESET}
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
# TERMINAL MANAGER
# ============================================================================
class TerminalManager:
    """Manage terminal sessions for WebSocket clients."""

    def __init__(self):
        self.processes: Dict[int, asyncio.subprocess.Process] = {}

    async def create_session(self, session_id: int) -> asyncio.subprocess.Process:
        """Create a new terminal session."""
        if sys.platform == "win32":
            proc = await asyncio.create_subprocess_shell(
                "cmd.exe",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=WORKING_DIR,
            )
        else:
            proc = await asyncio.create_subprocess_shell(
                "/bin/bash",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=WORKING_DIR,
            )
        self.processes[session_id] = proc
        logger.info(f"Created terminal session {session_id}")
        return proc

    async def execute(self, session_id: int, command: str) -> str:
        """Execute command in terminal session."""
        proc = self.processes.get(session_id)
        if not proc or proc.returncode is not None:
            proc = await self.create_session(session_id)

        try:
            cmd = command.strip()
            if not cmd:
                return ""

            if cmd.startswith("cd "):
                path = cmd[3:].strip()
                try:
                    os.chdir(path)
                    return f"[OK] cd -> {os.getcwd()}\n"
                except FileNotFoundError:
                    return f"[ERROR] Directory not found: {path}\n"

            if cmd == "cd":
                return os.getcwd() + "\n"

            if cmd in ("exit", "quit"):
                return "[INFO] Session ended. Refresh to restart.\n"

            proc.stdin.write((cmd + "\n").encode())
            await proc.stdin.drain()

            output = ""
            try:
                output = await asyncio.wait_for(
                    proc.stdout.read(65536), timeout=30.0
                )
            except asyncio.TimeoutError:
                output = "[TIMEOUT] Command took too long (>30s)\n"

            return output.decode(errors="ignore")

        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return f"[ERROR] {str(e)}\n"

    async def close_all(self) -> None:
        """Close all terminal sessions."""
        for session_id, proc in self.processes.items():
            try:
                proc.terminate()
                logger.info(f"Terminated session {session_id}")
            except Exception as e:
                logger.debug(f"Failed to terminate session {session_id}: {e}")

terminal = TerminalManager()

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
    """Serve static files."""
    filename = request.match_info["filename"]
    filepath = os.path.join(WORKING_DIR, filename)
    if os.path.exists(filepath) and os.path.isfile(filepath):
        return web.FileResponse(filepath)
    return web.Response(status=404)

# ============================================================================
# WEBSOCKET TERMINAL HANDLER
# ============================================================================
async def websocket_handler(request: web.Request) -> web.WebSocketResponse:
    """Handle WebSocket connections for terminal."""
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    session_id = id(ws)
    client_ip = request.remote or "unknown"
    logger.info(f"WebSocket connected: {client_ip} (session {session_id})")

    proc = await terminal.create_session(session_id)

    welcome = (
        "╔══════════════════════════════════════════════════════════╗\n"
        "║  Unified Chaos Platform v1.0 - Terminal (PRO)          ║\n"
        "║  Workspace: " + WORKING_DIR[:44].ljust(44) + "║\n"
        "║  Wpisz 'help' aby zobaczyć komendy dashboard           ║\n"
        "╚══════════════════════════════════════════════════════════╝\n\n"
        f"{os.getcwd()}$ "
    )
    await ws.send_str(welcome)

    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                # Rate limiting
                if not rate_limiter.is_allowed(str(session_id)):
                    remaining = rate_limiter.get_remaining(str(session_id))
                    await ws.send_str(
                        f"\033[91m[RATE LIMIT] Too many commands. Wait {RATE_LIMIT_WINDOW}s or {remaining} commands left.\033[0m\n"
                        f"{os.getcwd()}$ "
                    )
                    continue

                data = json.loads(msg.data)
                cmd = data.get("command", "").strip()

                if not cmd:
                    await ws.send_str(f"{os.getcwd()}$ ")
                    continue

                logger.info(f"[{session_id}] Command: {cmd[:50]}...")

                # DASHBOARD COMMANDS
                if cmd == "help":
                    response = (
                        "\n=== DASHBOARD COMMANDS ===\n"
                        "  status     - Pokaż status platformy\n"
                        "  modules    - Lista dostępnych modułów\n"
                        "  test       - Uruchom testy (unittest)\n"
                        "  config     - Pokaż config.json\n"
                        "  install    - Zainstaluj zależności\n"
                        "  platform   - Uruchom UNIFIED_CHAOS_PLATFORM.py\n"
                        "  clear      - Wyczyść terminal\n"
                        "  pwd        - Pokaż aktualny katalog\n"
                        "  ls         - Lista plików\n"
                        "  help       - Ta pomoc\n"
                        "\n=== SECRET COMMANDS (Easter Eggs) ===\n"
                        "  matrix     - Take the red pill\n"
                        "  hack       - Initiate hack sequence\n"
                        "  konami     - Konami code hint\n"
                        "  42         - The meaning of life\n"
                        "  whoami     - Who are you?\n"
                        "  sudo       - Try sudo\n"
                        "\n=== SYSTEM COMMANDS ===\n"
                        "  Wszystkie komendy systemowe (bash/cmd) działają!\n"
                        "  Przykłady: python3, pip, git, ls, cat, grep...\n\n"
                    )
                    await ws.send_str(response + f"{os.getcwd()}$ ")
                    continue

                elif cmd == "status":
                    py_files = [f for f in os.listdir(WORKING_DIR) if f.endswith(".py")]
                    html_files = [f for f in os.listdir(WORKING_DIR) if f.endswith(".html")]
                    response = (
                        f"\n=== PLATFORM STATUS ===\n"
                        f"  Workspace:    {WORKING_DIR}\n"
                        f"  Python files: {len(py_files)}\n"
                        f"  HTML files:   {len(html_files)}\n"
                        f"  Platform:     {sys.platform}\n"
                        f"  Python:       {sys.version.split()[0]}\n"
                        f"  Status:       READY\n\n"
                    )
                    await ws.send_str(response + f"{os.getcwd()}$ ")
                    continue

                elif cmd == "modules":
                    response = (
                        "\n=== AVAILABLE MODULES ===\n"
                        "  1. Chaos Proxy        - Packet mutation (10%)\n"
                        "  2. ISP Obfuscator     - Padding + jitter\n"
                        "  3. HTTP Interceptor   - Keyword detection\n"
                        "  4. TCP Fragmenter     - 1-5 byte chunks\n"
                        "  5. Smuggling Probe    - CL.TE test\n"
                        "  6. Bulk Smuggling     - 20 threads\n"
                        "  7. Traffic Audit      - Leak detection\n"
                        "  8. Audit Scanner      - Code vulnerability scan\n"
                        "  9. Victim Server      - Test target\n"
                        " 10. Super Mode         - All modules at once\n\n"
                    )
                    await ws.send_str(response + f"{os.getcwd()}$ ")
                    continue

                elif cmd == "test":
                    await ws.send_str("\n[*] Running tests...\n")
                    result = await terminal.execute(session_id, f"cd {WORKING_DIR} && python3 -m unittest test_chaos_platform.py 2>&1")
                    await ws.send_str(result + f"\n{os.getcwd()}$ ")
                    continue

                elif cmd == "config":
                    config_path = os.path.join(WORKING_DIR, "config.json")
                    if os.path.exists(config_path):
                        with open(config_path) as f:
                            content = f.read()
                        await ws.send_str(f"\n=== config.json ===\n{content}\n\n{os.getcwd()}$ ")
                    else:
                        await ws.send_str("\n[INFO] config.json not found. Using defaults.\n\n" + f"{os.getcwd()}$ ")
                    continue

                elif cmd == "install":
                    await ws.send_str("\n[*] Installing dependencies...\n")
                    result = await terminal.execute(session_id, f"cd {WORKING_DIR} && pip install -r requirements.txt 2>&1 || pip install websockets aiohttp 2>&1")
                    await ws.send_str(result + f"\n{os.getcwd()}$ ")
                    continue

                elif cmd == "platform":
                    await ws.send_str("\n[*] Starting UNIFIED_CHAOS_PLATFORM.py...\n")
                    if sys.platform == "win32":
                        subprocess.Popen(
                            [sys.executable, os.path.join(WORKING_DIR, "UNIFIED_CHAOS_PLATFORM.py")],
                            cwd=WORKING_DIR,
                            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                        )
                    else:
                        subprocess.Popen(
                            [sys.executable, os.path.join(WORKING_DIR, "UNIFIED_CHAOS_PLATFORM.py")],
                            cwd=WORKING_DIR,
                            preexec_fn=os.setsid,
                        )
                    await ws.send_str("[OK] Platform started in background.\n\n" + f"{os.getcwd()}$ ")
                    continue

                elif cmd == "clear":
                    await ws.send_str("__CLEAR__")
                    continue

                # SECRET COMMANDS (Easter Eggs)
                elif cmd == "matrix":
                    await ws.send_str("\033[92m💊 Wake up, Neo...\033[0m\n")
                    await ws.send_str("\033[92mThe Matrix has you...\033[0m\n")
                    await ws.send_str("\033[92mFollow the white rabbit.\033[0m\n\n")
                    await ws.send_str(f"{os.getcwd()}$ ")
                    continue

                elif cmd == "hack":
                    await ws.send_str("\033[91m🏴‍☠️ INITIATING HACK SEQUENCE...\033[0m\n")
                    await ws.send_str("\033[93m[1/3] Scanning ports... \033[0m")
                    await asyncio.sleep(0.5)
                    await ws.send_str("DONE\n")
                    await ws.send_str("\033[93m[2/3] Exploiting vulnerability... \033[0m")
                    await asyncio.sleep(0.5)
                    await ws.send_str("FAKE! 😄\n")
                    await ws.send_str("\033[92mJust kidding! This is a test platform.\033[0m\n\n")
                    await ws.send_str(f"{os.getcwd()}$ ")
                    continue

                elif cmd == "konami":
                    await ws.send_str("\033[93m🎮 KONAMI CODE SEQUENCE:\033[0m\n")
                    await ws.send_str("  ↑ ↑ ↓ ↓ ← → ← → B A\n\n")
                    await ws.send_str("Wciśnij tę sekwencję na klawiaturze w dashboard!\n\n")
                    await ws.send_str(f"{os.getcwd()}$ ")
                    continue

                elif cmd == "42":
                    await ws.send_str("\033[92m42\033[0m\n")
                    await ws.send_str("\033[93mThe Answer to the Ultimate Question of Life,\033[0m\n")
                    await ws.send_str("\033[93mthe Universe, and Everything.\033[0m\n\n")
                    await ws.send_str(f"{os.getcwd()}$ ")
                    continue

                elif cmd == "whoami":
                    await ws.send_str("\033[92mguru\033[0m\n")
                    await ws.send_str("\033[93mUID=1337(guru) GID=1337(hackers)\033[0m\n\n")
                    await ws.send_str(f"{os.getcwd()}$ ")
                    continue

                elif cmd == "sudo":
                    await ws.send_str("\033[91mNice try! But you need root for that. 🤓\033[0m\n")
                    await ws.send_str("\033[93mSPOILER: Nie masz roota.\033[0m\n\n")
                    await ws.send_str(f"{os.getcwd()}$ ")
                    continue

                elif cmd == "sudo rm -rf /":
                    await ws.send_str("\033[91mNOPE. Nie w mojej platformie! 🛡️\033[0m\n\n")
                    await ws.send_str(f"{os.getcwd()}$ ")
                    continue

                # System command
                output = await terminal.execute(session_id, cmd)
                await ws.send_str(output + f"{os.getcwd()}$ ")

            elif msg.type == web.WSMsgType.ERROR:
                logger.error(f"WebSocket error: {ws.exception()}")
                break

    finally:
        logger.info(f"WebSocket disconnected: {client_ip} (session {session_id})")
        rate_limiter.remove_client(str(session_id))
        await terminal.close_all()

    return ws

# ============================================================================
# MAIN
# ============================================================================
def main() -> None:
    """Main entry point."""
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
╠══════════════════════════════════════════════════════════════╣
║  Dashboard:  http://localhost:{port:<5}                          ║
║  Terminal:   WebSocket ws://localhost:{port}/ws                 ║
║  Workspace:  {WORKING_DIR[:48]:<48}║
║  Bind:       127.0.0.1 (localhost only - BEZPIECZNE)         ║
║  Rate Limit: {RATE_LIMIT_COMMANDS} cmds/{int(RATE_LIMIT_WINDOW)}s per client                       ║
║  Logging:    chaos_server.log                                ║
║  Status:     READY                                          ║
╚══════════════════════════════════════════════════════════════╝{C.RESET}
    """)

    app = web.Application()

    app.router.add_get("/", handle_index)
    app.router.add_get("/ws", websocket_handler)
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
        loop.run_until_complete(terminal.close_all())
        logger.info("Server stopped.")

if __name__ == "__main__":
    main()
