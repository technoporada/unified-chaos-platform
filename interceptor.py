import socket
import threading
import time

# Ten skrypt pokazuje wydajność Twojej przewagi.
# Liczymy przechwycone bajty, żeby udowodnić skalę.

class Stats:
    def __init__(self):
        self.total_bytes = 0
        self.matches = 0
        self.start_time = time.time()

    def update(self, size, found):
        self.total_bytes += size
        if found: self.matches += 1

    def report(self):
        elapsed = time.time() - self.start_time
        mbps = (self.total_bytes * 8) / (1024 * 1024 * elapsed)
        print(f"\r[STATYSTYKI] Prędkość: {mbps:.2f} Mbps | Przechwycono wzorców: {self.matches}", end="")

stats = Stats()

def log_and_bridge(source, destination, direction):
    keywords = [b'user', b'pass', b'auth']
    while True:
        try:
            data = source.recv(8192)
            if not data: break
            
            found = any(key in data.lower() for key in keywords)
            stats.update(len(data), found)
            
            destination.sendall(data)
            stats.report()
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

def start_perf_test(listen_port=8888, target_port=9000):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', listen_port))
    server.listen(100)
    print(f"[*] Wydajnościowy Interceptor na porcie {listen_port}")

    try:
        while True:
            client, _ = server.accept()
            target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                target.connect(('127.0.0.1', target_port))
                threading.Thread(target=log_and_bridge, args=(client, target, "C->S"), daemon=True).start()
                threading.Thread(target=log_and_bridge, args=(target, client, "S->C"), daemon=True).start()
            except Exception:
                try:
                    target.close()
                except Exception:
                    pass
                try:
                    client.close()
                except Exception:
                    pass
    except KeyboardInterrupt:
        pass
    finally:
        server.close()

if __name__ == "__main__":
    start_perf_test()
