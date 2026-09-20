import socket
import threading
import random
import time

# --- KONFIGURACJA ---
L_PORT, T_PORT, T_HOST = 11112, 11111, '127.0.0.1'

def inject(data):
    """Surowa manipulacja binarna."""
    r = random.random()
    if r < 0.05: return None # DROP (Pakiet znika)
    if r < 0.20: # MUTATE (Psucie bajtów)
        b = bytearray(data)
        for _ in range(random.randint(1, 5)):
            if len(b) > 0: 
                b[random.randint(0, len(b)-1)] = random.randint(0, 255)
        return bytes(b)
    return data

def bridge(s, d):
    """Przerzut danych bez zbędnego gadania."""
    while True:
        try:
            data = s.recv(16384)
            if not data: break
            p = inject(data)
            if p: d.sendall(p)
        except Exception:
            break
    try:
        s.close()
    except Exception:
        pass
    try:
        d.close()
    except Exception:
        pass

def start():
    """Odpalenie silnika."""
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(('127.0.0.1', L_PORT))
        s.listen(100)
    except Exception:
        s.close()
        return
    print(f"[*] SILNIK ON: {L_PORT}->{T_PORT}")
    try:
        while True:
            c = None
            try:
                c, _ = s.accept()
                t = socket.socket()
                try:
                    t.connect((T_HOST, T_PORT))
                    threading.Thread(target=bridge, args=(c, t), daemon=True).start()
                    threading.Thread(target=bridge, args=(t, c), daemon=True).start()
                except Exception:
                    try:
                        t.close()
                    except Exception:
                        pass
                    if c is not None:
                        try:
                            c.close()
                        except Exception:
                            pass
            except Exception:
                if c is not None:
                    try:
                        c.close()
                    except Exception:
                        pass
    except KeyboardInterrupt:
        pass
    finally:
        s.close()

if __name__ == "__main__":
    start()
