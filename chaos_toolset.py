import socket
import threading
import time
import random

# --- JEDYNA KONFIGURACJA (Porty powyżej 10000 dla Windows) ---
LISTEN_PORT = 11112  # Tu łączysz się aplikacją/przeglądarką
TARGET_PORT = 11111  # Tu odpalasz cel: python -m http.server 11111
TARGET_HOST = '127.0.0.1'

class ChaosStats:
    def __init__(self):
        self.bytes_sent = 0
        self.mutations_count = 0
        self.start_time = time.time()

    def update(self, size, mutated):
        self.bytes_sent += size
        if mutated: self.mutations_count += 1

    def show(self):
        elapsed = time.time() - self.start_time
        mbps = (self.bytes_sent * 8) / (1024 * 1024 * elapsed) if elapsed > 0 else 0
        print(f"\r[CHAOS STATUS] Speed: {mbps:.2f} Mbps | Mutations: {self.mutations_count} | Total: {self.bytes_sent} bytes", end="")

stats = ChaosStats()

def mutate(data):
    """Sypanie piachem w tryby - modyfikacja danych w locie."""
    if random.random() < 0.1: # 10% szans na mutację
        b = bytearray(data)
        if len(b) > 0:
            # Losowa zamiana bajtu na śmieci
            b[random.randint(0, len(b)-1)] = random.randint(0, 255)
            return bytes(b), True
    return data, False

def bridge(source, destination):
    """Przerzucanie danych między klientem a celem."""
    while True:
        try:
            data = source.recv(8192)
            if not data: break
            
            # Aplikacja chaosu
            processed_data, was_mutated = mutate(data)
            stats.update(len(data), was_mutated)
            
            destination.sendall(processed_data)
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

def start_engine():
    """Uruchomienie głównego silnika."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind(('127.0.0.1', LISTEN_PORT))
        server.listen(10)
        print(f"[*] UNIFIED CHAOS ENGINE ODPALONY")
        print(f"[*] NASŁUCH: {LISTEN_PORT} -> CEL: {TARGET_HOST}:{TARGET_PORT}")
    except PermissionError:
        print(f"[!] BŁĄD: Port {LISTEN_PORT} jest zablokowany przez Windows.")
        server.close()
        return

    try:
        while True:
            client = None
            target = None
            try:
                client, addr = server.accept()
                target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                target.connect((TARGET_HOST, TARGET_PORT))
                
                # Obsługa ruchu w obie strony
                threading.Thread(target=bridge, args=(client, target), daemon=True).start()
                threading.Thread(target=bridge, args=(target, client), daemon=True).start()
            except Exception as e:
                print(f"\n[!] Błąd połączenia: {e}")
                if target is not None:
                    try:
                        target.close()
                    except Exception:
                        pass
                if client is not None:
                    try:
                        client.close()
                    except Exception:
                        pass
    except KeyboardInterrupt:
        print("\n[!] Chaos zatrzymany.")
    finally:
        server.close()

if __name__ == "__main__":
    start_engine()
