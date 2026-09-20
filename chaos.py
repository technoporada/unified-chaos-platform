import socket
import threading
import time

# --- KONFIGURACJA OMIJAJĄCA BLOKADY WINDOWS ---
# Skonfigurowane na porty powyżej 11000, które u Ciebie działają.
TARGET_PORT = 11111  # Tu odpalasz: python -m http.server 11111
PROXY_PORT = 11112   # Tu słucha Twój interceptor

class ChaosEngine:
    """
    Silnik do przechwytywania i analizy ruchu. 
    Działa jako przezroczyste proxy między Twoim skryptem a serwerem.
    """
    def __init__(self):
        self.running = True

    def proxy_handler(self, client_sock, target_host, target_port):
        target_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            target_sock.connect((target_host, target_port))
        except Exception as e:
            print(f"\n[!] Nie można połączyć z celem na porcie {target_port}: {e}")
            target_sock.close()
            client_sock.close()
            return

        def bridge(src, dst, label):
            while self.running:
                try:
                    data = src.recv(4096)
                    if not data: break
                    
                    # LOGIKA DEVELOPERA CHAOSU: Szukanie wzorców w locie
                    if b"GET" in data or b"POST" in data:
                        print(f"\n[*] Przechwycono żądanie HTTP ({label})")
                    
                    dst.sendall(data)
                except Exception:
                    break
            try:
                src.close()
            except Exception:
                pass
            try:
                dst.close()
            except Exception:
                pass

        threading.Thread(target=bridge, args=(client_sock, target_sock, "CLIENT->TARGET"), daemon=True).start()
        threading.Thread(target=bridge, args=(target_sock, client_sock, "TARGET->CLIENT"), daemon=True).start()

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server.bind(('127.0.0.1', PROXY_PORT))
            server.listen(5)
            print(f"[*] SILNIK ODPALONY. Słucham na porcie {PROXY_PORT}")
            print(f"[*] CEL: localhost:{TARGET_PORT}")
        except PermissionError:
            print(f"[!] BŁĄD UPRAWNIEŃ: Port {PROXY_PORT} jest zajęty. Zmień na inny powyżej 10000.")
            server.close()
            return

        try:
            while self.running:
                client_sock, addr = server.accept()
                print(f"[*] Nowe połączenie z: {addr}")
                self.proxy_handler(client_sock, '127.0.0.1', TARGET_PORT)
        except KeyboardInterrupt:
            self.running = False
            print("\n[*] Zamykanie silnika...")
        finally:
            server.close()

if __name__ == "__main__":
    engine = ChaosEngine()
    engine.start()
