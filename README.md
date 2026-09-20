# 🔥 Unified Chaos Platform v1.0

**Zintegrowana Platforma Analizy Sieci i Testów Bezpieczeństwa**

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

## 🎯 Co to jest?

Unified Chaos Platform to potężne narzędzie do testowania bezpieczeństwa sieci, składające się z **10 niezależnych modułów** połączonych w jedną platformę z dashboardem w przeglądarce, prawdziwym terminalem WebSocket i cyberpunkowym interfejsem.

## ⚡ Szybki Start

```bash
# 1. Klonuj repo
git clone https://github.com/technoporada/unified-chaos-platform.git
cd unified-chaos-platform

# 2. Uruchom dashboard ( automatycznie instaluje zależności )
python dashboard.py

# 3. Otwiera się przeglądarka → http://localhost:8880
```

**Lub uruchom CLI bezpośrednio:**
```bash
python UNIFIED_CHAOS_PLATFORM.py
```

## 🧩 Moduły

| # | Moduł | Opis | Port |
|---|-------|------|------|
| 1 | **Chaos Proxy** | Przechwytywanie + mutacja pakietów (10%) | 11112 → 11111 |
| 2 | **ISP Obfuscator** | Obfuskacja ruchu (padding + jitter) | 8888 → 9000 |
| 3 | **HTTP Interceptor** | Przechwytywanie HTTP + wyszukiwanie słów kluczowych | 8888 → 9000 |
| 4 | **TCP Fragmenter** | Fragmentacja na 1-5 bajtowe kawałki | 8888 → 9000 |
| 5 | **Smuggling Probe** | Test HTTP Request Smuggling (CL.TE) | 443 |
| 6 | **Bulk Smuggling** | Masowy test (20 wątków) | - |
| 7 | **Traffic Audit** | Monitorowanie wrażliwych danych | - |
| 8 | **Audit Scanner** | Skan kodu pod kątem luk bezpieczeństwa | - |
| 9 | **Victim Server** | Symulowany serwer testowy | 9000 |
| 10 | **Super Mode** | Uruchomienie wszystkich modułów naraz | - |

## 🖥️ Dashboard (Web Interface)

```bash
python dashboard.py
```

- **3 Tab'y:** Dashboard / Nauka / Guru
- **3 Motywy:** Matrix (zielony) / Synthwave (fioletowy) / Amber CRT (bursztynowy)
- **6 Języków:** PL, EN, DE, FR, ZH, RO
- **Prawdziwy terminal** z xterm.js + WebSocket
- **Easter Eggs** (ukryte!) 🥚

## 🧪 Testy

```bash
# Uruchom wszystkie testy
python -m unittest test_chaos_platform.py

# Uruchom z verbose
python -m unittest test_chaos_platform.py -v
```

**59 testów** pokrywających:
- Wszystkie 10 modułów
- Socket leak detection
- Config validation
- Rate limiting
- Error handling

## 🏗️ Architektura

```
unified-chaos-platform/
├── UNIFIED_CHAOS_PLATFORM.py   # Główna platforma (750+ linii)
├── server.py                   # Dashboard server (WebSocket + HTTP)
├── dashboard.py                # Launcher z auto-instalacją
├── index.html                  # Cyberpunk dashboard (3000+ linii)
├── test_chaos_platform.py      # 59 unit testów
├── config.json                 # Konfiguracja
├── requirements.txt            # Zależności
├── launch.bat                  # Launcher Windows (CLI)
├── launch.ps1                  # Launcher PowerShell (CLI)
├── .github/workflows/ci.yml   # CI/CD pipeline
│
├── chaos.py                    # Podstawowy proxy
├── chaos_toolset.py            # Proxy + stats
├── chaos_sniffer.py            # Sniffer z mutacją
├── ISP-Traffic-Obfuscator.py   # Obfuskacja ruchu
├── Request-Smuggling-Probe.py  # Test podatności
├── smuggler_engine.py          # Bulk test
├── interceptor.py              # Przechwytywacz
├── Transparent-Interceptor.py  # Pasywny listener
├── TCP-Fragmentation-Engine.py # Fragmentacja TCP
├── Target-Control-Audit.py     # Audyt celu
├── victim_server.py            # Serwer testowy
├── playground.py               # Test playground
└── szukaj.py                   # File scanner
```

## 🔒 Bezpieczeństwo

- **127.0.0.1 only** - binduje TYLKO do localhost
- **Rate limiting** - 30 komend/60s per klient
- **Config validation** - automatyczna walidacja przy starcie
- **Proper logging** - logi do pliku `chaos_server.log`
- **No bare except** - wszystkie excepty mają `Exception`

## 📦 Instalacja Zależności

```bash
# Minimalna (wbudowane moduły Python)
# Nie wymaga instalacji!

# Zalecane (dashboard server)
pip install websockets aiohttp

# Lub automatycznie przez launcher
python dashboard.py  # zainstaluje samo
```

## 🎮 Easter Eggs (Ukryte!)

1. Wejdź w tab **GURU**
2. Kliknij **[?]** na dole **10 razy**
3. Odblokuj strefę z:
   - 🎮 Konami Code
   - 💊 Matrix Rain
   - 💬 Hacker Quotes
   - 🏴‍☠️ Am I Pwned?
   - 💣 Self Destruct
   - 📺 Glitch Mode

**Secret terminal commands:** `matrix`, `hack`, `konami`, `42`, `whoami`, `sudo`

## 🛠️ Dla Deweloperów

```bash
# Lint
flake8 --select=E9,F63,F7,F82 *.py

# Type check (jeśli masz mypy)
mypy server.py

# Coverage
python -m pytest --cov=. --cov-report=html
```

## 🏷️ GitHub Topics

Dodaj te tagi w ustawieniach repo (`Settings → General → Topics`), aby zwiększyć widoczność:

```
cybersecurity  network-security  penetration-testing  http-smuggling
tcp-fragmentation  traffic-obfuscation  packet-inspection  security-toolkit
chaos-engineering  proxy-server  ctf  bug-bounty  ethical-hacking
python  websocket  cyberpunk  dashboard  network-analysis
```

## 📄 Licencja

**Educational / Research Use Only**

Narzędzie jest przeznaczone wyłącznie do:
- Testowania własnych systemów
- Bug Bounty (za zgodą właściciela)
- Penetration Testingu (na podstawie umowy)
- Celów edukacyjnych / CTF

**NIELEGALNE:** Ataki bez zgody, kradzież danych, DoS

## 👑 Autor

**Arkadiusz Słowik** - Security Architect

```
██╗   ██╗ █████╗ ██████╗  █████╗
██║   ██║██╔══██╗██╔══██╗██╔══██╗
██║   ██║███████║██████╔╝███████║
╚██╗ ██╔╝██╔══██║██╔══██╗██╔══██║
 ╚████╔╝ ██║  ██║██║  ██║██║  ██║
  ╚═══╝  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝
```

---

*Zbudowane z pasją do bezpieczeństwa sieci* 🚀
