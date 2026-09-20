#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                    UNIFIED CHAOS PLATFORM v1.0                          ║
║               Integrated Network Analysis & Security Tool               ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import socket
import threading
import time
import random
import struct
import ssl
import sys
import os
import re
from queue import Queue
from enum import Enum

# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class EngineMode(Enum):
    CHAOS_PROXY = "Chaos Proxy - Mutacja i logowanie ruchu"
    ISP_OBFUSCATOR = "ISP Obfuscator - Obfuskacja ruchu"
    HTTP_INTERCEPTOR = "HTTP Interceptor - Przechwytywanie"
    TCP_FRAGMENTER = "TCP Fragmenter - Fragmentacja pakietów"
    SMUGGLING_PROBE = "Smuggling Probe - Test podatności"
    BULK_SMUGGLING = "Bulk Smuggling - Masowy test"
    TRAFFIC_AUDIT = "Traffic Audit - Audyt bezpieczeństwa"
    AUDIT_SCANNER = "Audit Scanner - Skan plików"
    VICTIM_SERVER = "Victim Server - Serwer testowy"
    COMBINED_MODE = "Super Mode - Kombinowany"

# ============================================================================
# SHARED STATISTICS & LOGGING
# ============================================================================

class ChaosStats:
    def __init__(self):
        self.bytes_sent = 0
        self.bytes_received = 0
        self.mutations_count = 0
        self.vulnerabilities_found = []
        self.connections = 0
        self.start_time = time.time()
        self.lock = threading.Lock()

    def update_bytes(self, sent=0, received=0):
        with self.lock:
            self.bytes_sent += sent
            self.bytes_received += received

    def add_mutation(self):
        with self.lock:
            self.mutations_count += 1

    def add_vulnerability(self, vuln):
        with self.lock:
            self.vulnerabilities_found.append(vuln)

    def get_stats(self):
        elapsed = time.time() - self.start_time
        return {
            'elapsed': elapsed,
            'bytes_sent': self.bytes_sent,
            'bytes_received': self.bytes_received,
            'mutations': self.mutations_count,
            'vulnerabilities': len(self.vulnerabilities_found),
            'mbps': (self.bytes_sent * 8) / (1024 * 1024 * elapsed) if elapsed > 0 else 0
        }

    def print_stats(self):
        stats = self.get_stats()
        print(f"\r[STATS] Speed: {stats['mbps']:.2f} Mbps | Mutations: {stats['mutations']} | Total: {stats['bytes_sent']} bytes", end="")

# ============================================================================
# 1. CHAOS PROXY ENGINE
# ============================================================================

class ChaosProxyEngine:
    def __init__(self, listen_port=11112, target_host='127.0.0.1', target_port=11111, stats=None):
        self.listen_port = listen_port
        self.target = (target_host, target_port)
        self.running = True
        self.stats = stats or ChaosStats()

    def mutate(self, data):
        if random.random() < 0.1:
            b = bytearray(data)
            if len(b) > 0:
                b[random.randint(0, len(b)-1)] = random.randint(0, 255)
                self.stats.add_mutation()
                return bytes(b), True
        return data, False

    def bridge(self, source, destination):
        while self.running:
            try:
                data = source.recv(8192)
                if not data:
                    break
                processed_data, _ = self.mutate(data)
                self.stats.update_bytes(sent=len(processed_data))
                destination.sendall(processed_data)
                self.stats.print_stats()
            except Exception:
                break
        try:
            source.close()
        except Exception:
            pass
        try:
            destination.close()
        except Exception:
            pass

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server.bind(('127.0.0.1', self.listen_port))
            server.listen(10)
            print(f"\n[*] CHAOS PROXY aktywny na porcie {self.listen_port}")
            print(f"[*] Cel: {self.target[0]}:{self.target[1]}")
        except PermissionError:
            print(f"[!] Błąd: Port {self.listen_port} jest zajęty")
            server.close()
            return

        try:
            while self.running:
                client, addr = server.accept()
                target_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    target_sock.connect(self.target)
                    threading.Thread(target=self.bridge, args=(client, target_sock), daemon=True).start()
                    threading.Thread(target=self.bridge, args=(target_sock, client), daemon=True).start()
                except Exception:
                    try:
                        target_sock.close()
                    except Exception:
                        pass
                    try:
                        client.close()
                    except Exception:
                        pass
        except KeyboardInterrupt:
            self.running = False
            print("\n[*] Chaos Proxy zatrzymany")
        finally:
            server.close()

# ============================================================================
# 2. ISP TRAFFIC OBFUSCATOR
# ============================================================================

class ISPObfuscator:
    def __init__(self, listen_port=8888, target_host='127.0.0.1', target_port=9000, stats=None):
        self.listen_port = listen_port
        self.target = (target_host, target_port)
        self.stats = stats or ChaosStats()

    def _add_padding(self, data):
        padding_size = random.randint(10, 500)
        return data + (b'\x00' * padding_size)

    def _apply_jitter(self):
        time.sleep(random.uniform(0.001, 0.05))

    def handle_traffic(self, source, destination):
        while True:
            try:
                data = source.recv(4096)
                if not data:
                    break
                data = self._add_padding(data)
                self._apply_jitter()
                self.stats.update_bytes(sent=len(data))
                destination.sendall(data)
            except Exception:
                break
        try:
            source.close()
        except Exception:
            pass
        try:
            destination.close()
        except Exception:
            pass

    def start(self):
        proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        proxy.bind(('127.0.0.1', self.listen_port))
        proxy.listen(10)
        print(f"\n[*] ISP Obfuscator aktywny na porcie {self.listen_port}")
        print("[*] Każdy pakiet będzie obfuskowany (padding + jitter)")

        try:
            while True:
                client, _ = proxy.accept()
                target_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    target_sock.connect(self.target)
                    threading.Thread(target=self.handle_traffic, args=(client, target_sock), daemon=True).start()
                    threading.Thread(target=self.handle_traffic, args=(target_sock, client), daemon=True).start()
                except Exception:
                    try:
                        target_sock.close()
                    except Exception:
                        pass
                    try:
                        client.close()
                    except Exception:
                        pass
        except KeyboardInterrupt:
            print("\n[*] ISP Obfuscator zatrzymany")
        finally:
            proxy.close()

# ============================================================================
# 3. HTTP INTERCEPTOR
# ============================================================================

class HTTPInterceptor:
    def __init__(self, listen_port=8888, target_host='127.0.0.1', target_port=9000, stats=None):
        self.listen_port = listen_port
        self.target = (target_host, target_port)
        self.stats = stats or ChaosStats()

    def log_interesting_stuff(self, data, direction):
        keywords = [b'user', b'pass', b'token', b'auth', b'key', b'secret']
        for key in keywords:
            if key in data.lower():
                print(f"\n[!!!] {direction} - KEYWORD: {key.decode()}")
                return True
        return False

    def bridge(self, source, destination, direction):
        while True:
            try:
                data = source.recv(4096)
                if not data:
                    break
                self.log_interesting_stuff(data, direction)
                self.stats.update_bytes(sent=len(data))
                destination.sendall(data)
            except Exception:
                break
        try:
            source.close()
        except Exception:
            pass
        try:
            destination.close()
        except Exception:
            pass

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('127.0.0.1', self.listen_port))
        server.listen(5)
        print(f"\n[*] HTTP Interceptor aktywny na porcie {self.listen_port}")

        try:
            while True:
                client_sock, addr = server.accept()
                target_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    target_sock.connect(self.target)
                    threading.Thread(target=self.bridge, args=(client_sock, target_sock, "C->S"), daemon=True).start()
                    threading.Thread(target=self.bridge, args=(target_sock, client_sock, "S->C"), daemon=True).start()
                except Exception:
                    try:
                        target_sock.close()
                    except Exception:
                        pass
                    try:
                        client_sock.close()
                    except Exception:
                        pass
        except KeyboardInterrupt:
            print("\n[*] HTTP Interceptor zatrzymany")
        finally:
            server.close()

# ============================================================================
# 4. TCP FRAGMENTER
# ============================================================================

class TCPFragmenter:
    def __init__(self, target_host, target_port, listen_port=8888, stats=None):
        self.target = (target_host, target_port)
        self.listen_port = listen_port
        self.stats = stats or ChaosStats()

    def chaos_loop(self, client, target):
        client.setblocking(False)
        target.setblocking(False)

        while True:
            try:
                data = client.recv(4096)
                if not data:
                    break

                i = 0
                while i < len(data):
                    chunk_size = random.randint(1, 5)
                    chunk = data[i:i+chunk_size]
                    target.sendall(chunk)
                    time.sleep(0.0001)
                    i += chunk_size

            except BlockingIOError:
                pass
            except Exception:
                break

            try:
                resp = target.recv(4096)
                if not resp:
                    break
                self.stats.update_bytes(received=len(resp))
                client.sendall(resp)
            except BlockingIOError:
                pass
            except Exception:
                break

        try:
            client.close()
        except Exception:
            pass
        try:
            target.close()
        except Exception:
            pass

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('127.0.0.1', self.listen_port))
        server.listen(1)
        print(f"[*] TCP Fragmenter gotowy na porcie {self.listen_port}")

        try:
            while True:
                client, addr = server.accept()
                target_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    target_sock.connect(self.target)
                    self.chaos_loop(client, target_sock)
                except Exception as e:
                    print(f"[!] Błąd: {e}")
                    try:
                        target_sock.close()
                    except Exception:
                        pass
                    try:
                        client.close()
                    except Exception:
                        pass
        except KeyboardInterrupt:
            print("\n[*] TCP Fragmenter zatrzymany")
        finally:
            server.close()

# ============================================================================
# 5. SMUGGLING PROBE
# ============================================================================

class SmugglingProbe:
    def __init__(self, stats=None):
        self.stats = stats or ChaosStats()

    def probe_single(self, target_host, target_port=80):
        payload = (
            "POST / HTTP/1.1\r\n"
            f"Host: {target_host}\r\n"
            "Content-Length: 4\r\n"
            "Transfer-Encoding: chunked\r\n"
            "\r\n"
            "0\r\n"
            "X"
        )

        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)

            start_time = time.time()
            sock.connect((target_host, target_port))
            sock.sendall(payload.encode())

            try:
                response = sock.recv(4096)
                duration = time.time() - start_time

                if duration >= 3.0:
                    vuln = f"{target_host} - CL.TE (Duration: {duration:.2f}s)"
                    self.stats.add_vulnerability(vuln)
                    print(f"\n[!!!] SMUGGLING FOUND: {vuln}")
                    return True
            except socket.timeout:
                vuln = f"{target_host} - TIMEOUT (definite CL.TE)"
                self.stats.add_vulnerability(vuln)
                print(f"\n[!!!] TIMEOUT DETECTED: {vuln}")
                return True

            sock.close()
        except Exception as e:
            print(f"[!] Błąd: {e}")
            if sock is not None:
                try:
                    sock.close()
                except Exception:
                    pass
        return False

# ============================================================================
# 6. BULK SMUGGLING TESTER
# ============================================================================

class BulkSmugglingTester:
    def __init__(self, threads=20, timeout=7, stats=None):
        self.threads = threads
        self.timeout = timeout
        self.stats = stats or ChaosStats()
        self.queue = Queue()

    def create_payload(self, host):
        return (
            f"POST / HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            f"Content-Length: 4\r\n"
            f"Transfer-Encoding: chunked\r\n"
            f"\r\n"
            f"0\r\n"
            f"X"
        ).encode()

    def attack(self, host):
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            conn = context.wrap_socket(sock, server_hostname=host)

            start = time.time()
            conn.connect((host, 443))
            conn.sendall(self.create_payload(host))

            try:
                conn.recv(1024)
                return False
            except socket.timeout:
                duration = time.time() - start
                vuln = f"{host} - TIMEOUT ({duration:.2f}s)"
                self.stats.add_vulnerability(vuln)
                print(f"\n[!!!] VULNERABLE: {vuln}")
                return True
            finally:
                conn.close()
        except Exception:
            try:
                sock.close()
            except Exception:
                pass
            return False

    def worker(self):
        while not self.queue.empty():
            target = self.queue.get()
            print(f"[*] Testing: {target}...", end="\r")
            self.attack(target)
            self.queue.task_done()

    def run(self, targets):
        for t in targets:
            self.queue.put(t.strip())

        print(f"\n[*] Uruchamianie {self.threads} wątków...")
        for _ in range(self.threads):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()

        self.queue.join()
        print(f"\n[*] Test zakończony.")
        print(f"[*] Znalezione podatności: {len(self.stats.vulnerabilities_found)}")
        for vuln in self.stats.vulnerabilities_found:
            print(f"    - {vuln}")

# ============================================================================
# 7. TRAFFIC AUDIT
# ============================================================================

class TrafficAudit:
    def __init__(self, listen_port=8888, target_host='127.0.0.1', target_port=9000, stats=None):
        self.listen_port = listen_port
        self.target = (target_host, target_port)
        self.stats = stats or ChaosStats()

    def check_unencrypted_leak(self, data):
        sensitive = [b'password', b'login', b'session', b'cookie', b'key', b'secret']
        for pattern in sensitive:
            if pattern in data.lower():
                return pattern
        return None

    def bridge(self, source, destination):
        while True:
            try:
                data = source.recv(4096)
                if not data:
                    break

                leak = self.check_unencrypted_leak(data)
                if leak:
                    vuln = f"Unencrypted leak: {leak.decode()}"
                    self.stats.add_vulnerability(vuln)
                    print(f"\n[!!!] {vuln}")

                self.stats.update_bytes(sent=len(data))
                destination.sendall(data)
            except Exception:
                break
        try:
            source.close()
        except Exception:
            pass
        try:
            destination.close()
        except Exception:
            pass

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('127.0.0.1', self.listen_port))
        server.listen(1)
        print(f"\n[*] Traffic Audit aktywny na porcie {self.listen_port}")

        try:
            while True:
                conn, _ = server.accept()
                target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    target.connect(self.target)
                    threading.Thread(target=self.bridge, args=(conn, target), daemon=True).start()
                    threading.Thread(target=self.bridge, args=(target, conn), daemon=True).start()
                except Exception:
                    try:
                        target.close()
                    except Exception:
                        pass
                    try:
                        conn.close()
                    except Exception:
                        pass
        except KeyboardInterrupt:
            print("\n[*] Traffic Audit zatrzymany")
        finally:
            server.close()

# ============================================================================
# 8. FILE AUDIT SCANNER
# ============================================================================

class AuditScanner:
    PATTERNS = {
        "SENSITIVE_DATA": r"(password|secret|api_key|token|access_key)[\s]*[:=][\s]*['\"].*['\"]",
        "SHELL_INJECTION": r"(os\.system|subprocess|exec\(|eval\()",
        "NETWORK_SOCKETS": r"(socket\.socket|requests\.|urllib\.)",
        "EXPLOIT_MARKERS": r"(payload|shellcode|exploit|backdoor)",
    }

    def audit_files(self, directory):
        print(f"\n[*] AUDYT PLIKÓW: {os.path.abspath(directory)}")
        print("-" * 60)

        found_issues = 0
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(('.py', '.js', '.sh', '.php')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            for i, line in enumerate(f):
                                for key, pattern in self.PATTERNS.items():
                                    if re.search(pattern, line, re.IGNORECASE):
                                        print(f"[{key}] {file_path}:{i+1}")
                                        print(f"  -> {line.strip()[:80]}")
                                        found_issues += 1
                    except Exception as e:
                        print(f"[!] Error: {file_path}")

        print("-" * 60)
        print(f"[*] ZNALEZIONO PROBLEMÓW: {found_issues}")

# ============================================================================
# 9. VICTIM SERVER (Test target)
# ============================================================================

class VictimServer:
    def __init__(self, port=9000):
        self.port = port

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('127.0.0.1', self.port))
        server.listen(5)
        print(f"\n[*] VICTIM SERVER aktywny na porcie {self.port}")

        try:
            while True:
                client, addr = server.accept()
                try:
                    data = client.recv(1024)
                    if data:
                        print(f"\n[VICTIM] Odebrano z {addr}: {data[:50].decode(errors='ignore')}...")
                    response = b"HTTP/1.1 200 OK\r\nContent-Length: 13\r\n\r\nSystem Secure"
                    client.sendall(response)
                finally:
                    client.close()
        except KeyboardInterrupt:
            print("\n[*] Victim Server zatrzymany")
        finally:
            server.close()

# ============================================================================
# MAIN CONTROLLER
# ============================================================================

class UnifiedChaos:
    def __init__(self):
        self.stats = ChaosStats()
        self.threads = []

    def print_banner(self):
        print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                    UNIFIED CHAOS PLATFORM v1.0                          ║
║        Integrated Network Analysis & Security Testing Suite             ║
╚═══════════════════════════════════════════════════════════════════════════╝
        """)

    def print_menu(self):
        print("\n--- MENU GŁÓWNE ---")
        for i, mode in enumerate(EngineMode, 1):
            print(f"{i}. {mode.value}")
        print("0. Wyjście")

    def run_single_mode(self, mode):
        engines = {
            EngineMode.CHAOS_PROXY: lambda: ChaosProxyEngine(stats=self.stats).start(),
            EngineMode.ISP_OBFUSCATOR: lambda: ISPObfuscator(stats=self.stats).start(),
            EngineMode.HTTP_INTERCEPTOR: lambda: HTTPInterceptor(stats=self.stats).start(),
            EngineMode.TCP_FRAGMENTER: lambda: TCPFragmenter('127.0.0.1', 9000, stats=self.stats).start(),
            EngineMode.SMUGGLING_PROBE: self.run_smuggling_probe,
            EngineMode.BULK_SMUGGLING: self.run_bulk_smuggling,
            EngineMode.TRAFFIC_AUDIT: lambda: TrafficAudit(stats=self.stats).start(),
            EngineMode.AUDIT_SCANNER: self.run_audit_scanner,
            EngineMode.VICTIM_SERVER: lambda: VictimServer().start(),
        }

        if mode in engines:
            engine = engines[mode]
            thread = threading.Thread(target=engine, daemon=True)
            thread.start()
            self.threads.append(thread)

    def run_smuggling_probe(self):
        probe = SmugglingProbe(stats=self.stats)
        target = input("[?] Cel (host): ").strip()
        port = int(input("[?] Port [80]: ") or "80")
        if target:
            probe.probe_single(target, port)

    def run_bulk_smuggling(self):
        tester = BulkSmugglingTester(stats=self.stats)
        targets_str = input("[?] Targets (comma-separated): ").strip()
        if targets_str:
            targets = targets_str.split(",")
            tester.run(targets)

    def run_audit_scanner(self):
        scanner = AuditScanner()
        path = input("[?] Ścieżka [d:\\Game]: ").strip() or "d:\\Game"
        scanner.audit_files(path)

    def run_combined_mode(self):
        print("\n[*] TRYB KOMBINOWANY - Uruchamianie wszystkich silników...")
        for mode in list(EngineMode)[:-1]:  # Skip Combined Mode
            print(f"[*] Startuje: {mode.value}")
            try:
                self.run_single_mode(mode)
                time.sleep(1)
            except Exception as e:
                print(f"[!] Error: {e}")

    def print_stats(self):
        stats = self.stats.get_stats()
        print(f"""
--- STATYSTYKI ---
Czas: {stats['elapsed']:.2f}s
Wysłano: {stats['bytes_sent']} bajtów
Odebrano: {stats['bytes_received']} bajtów
Mutacji: {stats['mutations']}
Podatności: {stats['vulnerabilities']}
Prędkość: {stats['mbps']:.2f} Mbps
Znalezione: {len(self.stats.vulnerabilities_found)} luk
        """)
        for vuln in self.stats.vulnerabilities_found[:5]:
            print(f"  - {vuln}")

    def run(self):
        self.print_banner()

        while True:
            self.print_menu()
            choice = input("[?] Opcja: ").strip()

            if choice == "0":
                print("[*] Wyjście...")
                break
            elif choice == "10":
                self.run_combined_mode()
                input("[*] Wciśnij Enter aby kontynuować...")
            elif choice in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                try:
                    mode = list(EngineMode)[int(choice)-1]
                    self.run_single_mode(mode)
                    input("[*] Wciśnij Enter aby zatrzymać...")
                except (ValueError, IndexError):
                    print("[!] Błędna opcja")
            else:
                print("[!] Błędna opcja")

            self.print_stats()

if __name__ == "__main__":
    try:
        chaos = UnifiedChaos()
        chaos.run()
    except KeyboardInterrupt:
        print("\n\n[*] Platform zamknięty.")

