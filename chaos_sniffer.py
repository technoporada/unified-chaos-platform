import socket
import struct
import random

# Ten skrypt pokazuje Ci, co lata w Twojej sieci, zanim to zepsujesz.
# To nie jest tutorial. To jest narzędzie do binarnej sekcji zwłok.

def hex_dump(data):
    """Pokazuje surowe dane tak, jak widzi je procesor."""
    return ' '.join(f'{b:02x}' for b in data)

def chaos_mutate(data):
    """Mutacja celowana: szukamy 'czułych' punktów w tekście."""
    if b'GET' in data or b'POST' in data:
        # Jeśli to ruch HTTP, psujemy nagłówki
        return data.replace(b'Keep-Alive', b'Close').replace(b'gzip', b'none')
    
    # Dla reszty - losowy 'bit-flip' w pierwszym bajcie
    b = bytearray(data)
    if len(b) > 0:
        b[0] ^= 0xFF
    return bytes(b)

def start_listening(port=8888):
    # Tworzymy gniazdo, które przechwytuje wszystko na danym porcie
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(('127.0.0.1', port))
        sock.listen(1)
    except Exception:
        sock.close()
        return
    
    print(f"[!] Sniffer/Mutator aktywny na porcie {port}")
    
    try:
        while True:
            conn, addr = sock.accept()
            print(f"\n[*] Przechwycono połączenie od: {addr}")
            
            try:
                data = conn.recv(4096)
                if data:
                    print(f"[RAW DATA]: {hex_dump(data[:32])}...")
                    
                    # Tu dzieje się to, co daje Ci przewagę:
                    # Widzisz dane ZANIM trafią do celu i możesz je zmienić.
                    mutated = chaos_mutate(data)
                    
                    if mutated != data:
                        print("[CHAOS] Pakiet zmutowany przed wysłaniem dalej.")
                    
                    # W prawdziwym ataku tutaj wysyłasz to do 'target_sock'
                    # Na potrzeby testu po prostu odsyłamy 'fake response'
                    conn.sendall(b"HTTP/1.1 418 I'm a teapot\r\n\r\nChaos Reigned.")
            finally:
                conn.close()
    except KeyboardInterrupt:
        pass
    finally:
        sock.close()

if __name__ == "__main__":
    start_listening()
