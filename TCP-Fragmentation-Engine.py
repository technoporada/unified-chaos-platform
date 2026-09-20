import socket
import random
import time

# TO JEST RZECZYWISTOŚĆ:
# Systemy DPI u ISP mają ograniczony bufor pamięci na składanie pakietów.
# Jeśli wyślemy dane w kawałkach po 1-5 bajtów, w złej kolejności,
# ich procesory nie nadążą z analizą treści przed wysłaniem ich dalej.

class Fragmenter:
    def __init__(self, target_host, target_port, listen_port=8888):
        self.target = (target_host, target_port)
        self.listen_port = listen_port

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('127.0.0.1', self.listen_port))
        server.listen(1)
        print(f"[*] Fragmentator gotowy na porcie {self.listen_port}")

        while True:
            client, addr = server.accept()
            target_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                target_sock.connect(self.target)
                self.chaos_loop(client, target_sock)
            except Exception as e:
                print(f"[!] Błąd połączenia: {e}")
                client.close()

    def chaos_loop(self, client, target):
        client.setblocking(False)
        target.setblocking(False)
        
        while True:
            try:
                # Czytamy dane od Ciebie
                data = client.recv(4096)
                if not data: break
                
                # RZECZYWISTA PRZEWAGA: Rozbijanie danych na mikro-fragmenty
                # ISP widzi tysiące małych paczek zamiast jednego strumienia.
                i = 0
                while i < len(data):
                    chunk_size = random.randint(1, 5) # Ekstremalnie małe kawałki
                    chunk = data[i:i+chunk_size]
                    target.sendall(chunk)
                    # Wprowadzamy mikro-opóźnienie, by wymusić oddzielne pakiety IP
                    time.sleep(0.0001) 
                    i += chunk_size
                    
            except BlockingIOError:
                pass
            except Exception:
                break

            try:
                # Odpowiedź od celu przesyłamy normalnie
                resp = target.recv(4096)
                if not resp: break
                client.sendall(resp)
            except BlockingIOError:
                pass
            except Exception:
                break

        client.close()
        target.close()

if __name__ == "__main__":
    # Testuj na lokalnym porcie, zanim wypuścisz to na ISP
    f = Fragmenter('127.0.0.1', 9000)
    f.start()
