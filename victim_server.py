import socket

# TO JEST TWOJA "OFIARA" TESTOWA.
# Symulujemy prosty serwer backendowy, który jest podatny na Smuggling,
# ponieważ nie radzi sobie z nagłówkami Transfer-Encoding.

def start_victim_server(port=9000):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', port))
    server.listen(5)
    print(f"[*] Serwer-Ofiara działa na porcie {port}...")
    print("[*] Czeka na 'ataki' z Twojego skryptu bounty_probe.py")

    try:
        while True:
            client, addr = server.accept()
            try:
                data = client.recv(4096).decode(errors='ignore')
                
                # Symulacja błędu: Serwer wypisuje wszystko, co dostał,
                # łącznie z "przemyconym" znakiem X, który zostaje w buforze.
                print(f"\n[ODBIÓR OD {addr}]:")
                print("-" * 20)
                print(data)
                print("-" * 20)
                
                # Odpowiedź serwera
                response = "HTTP/1.1 200 OK\r\nContent-Length: 13\r\n\r\nHello World!"
                client.sendall(response.encode())
            finally:
                client.close()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()

if __name__ == "__main__":
    start_victim_server()