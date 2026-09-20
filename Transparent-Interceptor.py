import socket
import threading
import sys

# Konfiguracja: Przekierowujemy ruch z 8888 na 9000 (Twoja usługa testowa)
LISTEN_PORT = 8888
TARGET_HOST = '127.0.0.1'
TARGET_PORT = 9000

def log_interesting_stuff(data, direction):
    """Analizuje strumień danych w poszukiwaniu wrażliwych informacji."""
    # Szukamy słów kluczowych, które mogą być interesujące w surowym ruchu
    keywords = [b'user', b'pass', b'token', b'auth', b'key', b'secret']
    
    for key in keywords:
        if key in data.lower():
            print(f"\n[!!!] {direction} - WYKRYTO DOPASOWANIE ({key.decode()}):")
            # Wyświetlamy dane w formacie hex dla precyzyjnej analizy binarnej
            print(data.hex(' '))
            break

def bridge(source, destination, direction):
    """Przerzuca pakiety między źródłem a celem, działając jako pasywny podsłuch."""
    while True:
        try:
            data = source.recv(4096)
            if not data:
                break
            
            # Analiza danych bez wpływania na ich treść (tryb niewidoczny)
            log_interesting_stuff(data, direction)
            
            # Przesyłamy dalej do faktycznego odbiorcy
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

def start_proxy():
    """Inicjalizuje serwer pośredniczący (proxy)."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', LISTEN_PORT))
    server.listen(5)
    print(f"[*] Interceptor aktywny na porcie {LISTEN_PORT}")
    print(f"[*] Cel analizy: {TARGET_HOST}:{TARGET_PORT}")

    try:
        while True:
            client_sock, addr = server.accept()
            print(f"[*] Przechwycono połączenie z: {addr}")
            
            target_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                target_sock.connect((TARGET_HOST, TARGET_PORT))
            except Exception as e:
                print(f"[!] Cel jest nieosiągalny: {e}")
                try:
                    target_sock.close()
                except Exception:
                    pass
                try:
                    client_sock.close()
                except Exception:
                    pass
                continue

            # Pełny dupleks: nasłuchujemy w obu kierunkach jednocześnie
            threading.Thread(target=bridge, args=(client_sock, target_sock, "KLIENT -> SERWER")).start()
            threading.Thread(target=bridge, args=(target_sock, client_sock, "SERWER -> KLIENT")).start()
    except KeyboardInterrupt:
        print("\n[!] Zatrzymywanie analizy.")
    finally:
        server.close()

if __name__ == "__main__":
    start_proxy()
