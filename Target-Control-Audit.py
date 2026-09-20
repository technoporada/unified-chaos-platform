import socket
import sys

# KONKRETNIE: Nad kim zyskujesz przewagę tym skryptem?

class ControlAudit:
    def __init__(self):
        # 1. PRZEWAGA NAD ADMINEM (Wykrywanie braku szyfrowania)
        self.admin_advantage = "Przechwytywanie danych w czystym tekście (Brak TLS)"
        
        # 2. PRZEWAGA NAD DEWELOPEREM (Wstrzykiwanie chaosu w logikę)
        self.dev_advantage = "Wywoływanie błędów, których nie ma w testach (Logic Bomb)"
        
        # 3. PRZEWAGA NAD SECURITY (Niewidzialność dla skanerów)
        self.sec_advantage = "Działanie poza sygnaturami ataków (Custom Payload)"

    def check_unencrypted_leak(self, data):
        """Dowód dla Admina: Jeśli to czytasz, on przegrał."""
        sensitive_patterns = [b'password', b'login', b'session_id', b'cookie']
        for pattern in sensitive_patterns:
            if pattern in data.lower():
                return True
        return False

    def check_buffer_vulnerability(self, data):
        """Dowód dla Dewelopera: Jeśli serwer padnie od tego, on przegrał."""
        # Wysyłamy gigantyczny nagłówek, którego nikt nie testował
        return data + (b"A" * 5000)

def run_audit_proxy(listen_port=8888, target_host='127.0.0.1', target_port=9000):
    audit = ControlAudit()
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', listen_port))
    server.listen(1)
    
    print(f"--- RAPORT PRZEWAGI ---")
    print(f"[1] Nad Adminem: {audit.admin_advantage}")
    print(f"[2] Nad Deweloperem: {audit.dev_advantage}")
    print(f"[3] Nad Security: {audit.sec_advantage}")
    print(f"------------------------")

    while True:
        conn, addr = server.accept()
        data = conn.recv(4096)
        
        if audit.check_unencrypted_leak(data):
            print("[DOWÓD] Admin przegrał: Przechwycono wrażliwe dane w locie!")
            
        # Tutaj modyfikujemy dane, żeby sprawdzić dewelopera
        malformed_data = audit.check_buffer_vulnerability(data)
        
        # Wysłanie tego dalej do celu pokazałoby, czy system 'pęknie'
        print(f"[DOWÓD] Deweloper zagrożony: Przygotowano pakiet o rozmiarze {len(malformed_data)} bajtów.")
        
        conn.close()

if __name__ == "__main__":
    run_audit_proxy()
