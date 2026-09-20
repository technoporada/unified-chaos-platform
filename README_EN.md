# 🔥 Unified Chaos Platform v1.0

**Integrated Network Analysis & Security Testing Suite**

[![CI/CD](https://github.com/technoporada/unified-chaos-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/technoporada/unified-chaos-platform/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![Tests](https://img.shields.io/badge/tests-59%20passed-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-Educational%2FResearch-yellow.svg)]()
[![Security](https://img.shields.io/badge/security-network%20testing-red.svg)]()
[![WebSocket](https://img.shields.io/badge/WebSocket-real%20terminal-purple.svg)]()
[![Dashboard](https://img.shields.io/badge/dashboard-cyberpunk-00ff41.svg)]()
[![Platforms](https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey.svg)]()

> **Keywords:** `cybersecurity` `network-security` `penetration-testing` `http-smuggling` `tcp-fragmentation` `traffic-obfuscation` `packet-inspection` `security-toolkit` `ctf` `bug-bounty` `ethical-hacking` `proxy-server` `chaos-engineering`

---

## 🎯 What is it?

Unified Chaos Platform is a powerful network security testing toolkit consisting of **10 independent modules** integrated into a single platform with a web dashboard, real WebSocket terminal, and cyberpunk interface.

## ⚡ Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/technoporada/unified-chaos-platform.git
cd unified-chaos-platform

# 2. Run dashboard (auto-installs dependencies)
python dashboard.py

# 3. Browser opens → http://localhost:8880
```

**Or run CLI directly:**
```bash
python UNIFIED_CHAOS_PLATFORM.py
```

## 🧩 Modules

| # | Module | Description | Port |
|---|--------|-------------|------|
| 1 | **Chaos Proxy** | Packet interception + mutation (10%) | 11112 → 11111 |
| 2 | **ISP Obfuscator** | Traffic obfuscation (padding + jitter) | 8888 → 9000 |
| 3 | **HTTP Interceptor** | HTTP interception + keyword search | 8888 → 9000 |
| 4 | **TCP Fragmenter** | Fragmentation into 1-5 byte chunks | 8888 → 9000 |
| 5 | **Smuggling Probe** | HTTP Request Smuggling test (CL.TE) | 443 |
| 6 | **Bulk Smuggling** | Mass test (20 threads) | - |
| 7 | **Traffic Audit** | Sensitive data monitoring | - |
| 8 | **Audit Scanner** | Code vulnerability scanner | - |
| 9 | **Victim Server** | Simulated test server | 9000 |
| 10 | **Super Mode** | Run all modules at once | - |

## 🖥️ Dashboard (Web Interface)

```bash
python dashboard.py
```

- **3 Tabs:** Dashboard / Learn / Guru
- **3 Themes:** Matrix (green) / Synthwave (purple) / Amber CRT
- **6 Languages:** PL, EN, DE, FR, ZH, RO
- **Real terminal** with xterm.js + WebSocket
- **Easter Eggs** (hidden!) 🥚

## 🧪 Tests

```bash
# Run all tests
python -m unittest test_chaos_platform.py

# Run with verbose
python -m unittest test_chaos_platform.py -v
```

**59 tests** covering:
- All 10 modules
- Socket leak detection
- Config validation
- Rate limiting
- Error handling

## 🏗️ Architecture

```
unified-chaos-platform/
├── UNIFIED_CHAOS_PLATFORM.py   # Main platform (750+ lines)
├── server.py                   # Dashboard server (WebSocket + HTTP)
├── dashboard.py                # Launcher with auto-install
├── index.html                  # Cyberpunk dashboard (3000+ lines)
├── test_chaos_platform.py      # 59 unit tests
├── config.json                 # Configuration
├── requirements.txt            # Dependencies
├── launch.bat                  # Windows launcher (CLI)
├── launch.ps1                  # PowerShell launcher (CLI)
├── .github/workflows/ci.yml   # CI/CD pipeline
│
├── chaos.py                    # Basic proxy
├── chaos_toolset.py            # Proxy + stats
├── chaos_sniffer.py            # Sniffer with mutation
├── ISP-Traffic-Obfuscator.py   # Traffic obfuscation
├── Request-Smuggling-Probe.py  # Vulnerability test
├── smuggler_engine.py          # Bulk test
├── interceptor.py              # Interceptor
├── Transparent-Interceptor.py  # Passive listener
├── TCP-Fragmentation-Engine.py # TCP fragmentation
├── Target-Control-Audit.py     # Target audit
├── victim_server.py            # Test server
├── playground.py               # Test playground
└── szukaj.py                   # File scanner
```

## 🔒 Security

- **127.0.0.1 only** - binds to localhost only
- **Rate limiting** - 30 commands/60s per client
- **Config validation** - automatic validation at startup
- **Proper logging** - logs to `chaos_server.log`
- **No bare except** - all excepts have `Exception`

## 📦 Installation

```bash
# Minimal (built-in Python modules)
# No installation needed!

# Recommended (dashboard server)
pip install websockets aiohttp

# Or automatically via launcher
python dashboard.py  # installs automatically
```

## 🎮 Easter Eggs (Hidden!)

1. Go to **GURU** tab
2. Click **[?]** at the bottom **10 times**
3. Unlock zone with:
   - 🎮 Konami Code
   - 💊 Matrix Rain
   - 💬 Hacker Quotes
   - 🏴‍☠️ Am I Pwned?
   - 💣 Self Destruct
   - 📺 Glitch Mode

**Secret terminal commands:** `matrix`, `hack`, `konami`, `42`, `whoami`, `sudo`

## 🛠️ For Developers

```bash
# Lint
flake8 --select=E9,F63,F7,F82 *.py

# Type check (if you have mypy)
mypy server.py

# Coverage
python -m pytest --cov=. --cov-report=html
```

## 🏷️ GitHub Topics

Add these tags in repo settings (`Settings → General → Topics`) for better discoverability:

```
cybersecurity  network-security  penetration-testing  http-smuggling
tcp-fragmentation  traffic-obfuscation  packet-inspection  security-toolkit
chaos-engineering  proxy-server  ctf  bug-bounty  ethical-hacking
python  websocket  cyberpunk  dashboard  network-analysis
```

## 📄 License

**Educational / Research Use Only**

This tool is intended solely for:
- Testing your own systems
- Bug Bounty (with upstream permission)
- Penetration Testing (under contract)
- Educational / CTF competitions

**ILLEGAL:** Unauthorized attacks, data theft, DoS

## 👑 Author

**Arkadiusz Słowik** - Security Architect

```
██╗   ██╗ █████╗ ██████╗  █████╗
██║   ██║██╔══██╗██╔══██╗██╔══██╗
██║   ██║███████║██████╔╝███████║
╚██╗ ██╔╝██╔══██║██╔══██╗██╔══██╗
 ╚████╔╝ ██║  ██║██║  ██║██║  ██║
  ╚═══╝  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝
```

---

*Built with passion for network security* 🚀
