import socket
import threading
import time
import sys

# --- CONFIG ---
TARGET_PORT = 9000  # Port "ofiary" (serwera)
PROXY_PORT = 8888   # Port Twojego Chaos Engine

def start_victim_server():
    """Udaje 'poważny' serwer w korporacji."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', TARGET_PORT))
    server.listen(5)
    print(f"[*] [VICTIM] Serwer ofiary działa na porcie {TARGET_PORT}")

    try:
        while True:
            client, addr = server.accept()
            try:
                data = client.recv(1024)
                if data:
                    print(f"[*] [VICTIM] Odebrano dane: {data.decode(errors='ignore')}")
                    # Serwer zawsze odpowiada tym samym
                    client.send(b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nSYSTEM STATUS: SECURE")
            finally:
                client.close()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()

def start_attacker_client():
    """Twoja aplikacja, która chce pogadać z serwerem."""
    time.sleep(2) # Czekaj na start serwerów
    print(f"[*] [CLIENT] Próba połączenia z systemem przez PROXY (port {PROXY_PORT})...")
    
    while True:
        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('127.0.0.1', PROXY_PORT))
            s.send(b"GET /data_access HTTP/1.1\r\nHost: localhost\r\n\r\n")
            
            response = s.recv(1024)
            print(f"[!] [CLIENT] Odpowiedź systemu: {response.decode(errors='ignore')}")
            s.close()
        except Exception as e:
            print(f"[!] [CLIENT] BŁĄD POŁĄCZENIA: {e}")
            if s is not None:
                try:
                    s.close()
                except Exception:
                    pass
        
        print("-" * 40)
        time.sleep(3)

if __name__ == "__main__":
    # Uruchomienie ofiary i klienta w osobnych wątkach
    threading.Thread(target=start_victim_server, daemon=True).start()
    print("[!] Playground gotowy. Teraz w osobnym terminalu odpal auditor.py lub chaos_engine.py na portach 8888 -> 9000.")
    start_attacker_client()