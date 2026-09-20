import socket
import random
import time
import threading

# CEL: Przewaga nad systemami profilowania ISP (Deep Packet Inspection)
# Jak: Modyfikujemy pakiety tak, by nie pasowały do żadnych wzorców (VoIP, Video, Web).

class TrafficShaper:
    def __init__(self, listen_port=8888, target_host='127.0.0.1', target_port=9000):
        self.listen_port = listen_port
        self.target = (target_host, target_port)
        self.noise_enabled = True

    def _add_padding(self, data):
        """Dodaje losową ilość 'śmieci' na końcu pakietu, by ukryć jego prawdziwy rozmiar."""
        padding_size = random.randint(10, 500)
        return data + (b'\x00' * padding_size)

    def _apply_jitter(self):
        """Wprowadza losowe mikro-opóźnienie, by rozbić timing pakietów."""
        time.sleep(random.uniform(0.001, 0.05))

    def handle_traffic(self, source, destination):
        while True:
            try:
                data = source.recv(4096)
                if not data: break
                
                # CHAOS: Zmieniamy charakterystykę pakietu
                if self.noise_enabled:
                    data = self._add_padding(data)
                    self._apply_jitter()
                
                destination.sendall(data)
            except Exception:
                break
        source.close()
        destination.close()

    def start(self):
        proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        proxy.bind(('127.0.0.1', self.listen_port))
        proxy.listen(10)
        
        print(f"[*] ISP Obfuscator uzbrojony na porcie {self.listen_port}")
        print("[*] Każdy pakiet będzie miał teraz losowy rozmiar i czas dotarcia.")

        while True:
            client, addr = proxy.accept()
            target_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                target_sock.connect(self.target)
                # Dwa wątki dla pełnego dupleksu
                threading.Thread(target=self.handle_traffic, args=(client, target_sock)).start()
                threading.Thread(target=self.handle_traffic, args=(target_sock, client)).start()
            except Exception:
                client.close()

if __name__ == "__main__":
    shaper = TrafficShaper()
    shaper.start()
