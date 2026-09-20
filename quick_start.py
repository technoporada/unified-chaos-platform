#!/usr/bin/env python3
"""
QUICK START GUIDE - Szybkie testy Unified Chaos Platform
=========================================================

Uruchom to: python quick_start.py
"""

import subprocess
import time
import os
from pathlib import Path

def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def run_test(num, name, command, description):
    print(f"\n[TEST {num}] {name}")
    print(f"Description: {description}")
    print(f"Command: {command}\n")
    
    response = input("Uruchomić? (y/n): ").strip().lower()
    if response == 'y':
        try:
            if isinstance(command, str):
                os.system(command)
            else:
                subprocess.run(command, check=True)
            print(f"\n✓ Test {num} zakończony")
        except Exception as e:
            print(f"\n✗ Error: {e}")
    else:
        print("• Pominięto")

def main():
    print_header("UNIFIED CHAOS PLATFORM - QUICK START TESTS")
    
    print("""
    Ten skrypt przeprowadzi Cię przez podstawowe testy każdego modułu.
    
    WYMAGANIA:
    ✓ Python 3.7+
    ✓ Porty 8888, 9000, 11111, 11112 dostępne
    ✓ Dwa terminale (dla client-server testów)
    
    WSKAZÓWKA:
    Otwórz 2-3 terminale obok siebie!
    """)
    
    input("\nWciśnij Enter aby zaciąć... ")
    
    # =====================================================================
    # TEST 1: BASIC SANITY CHECK
    # =====================================================================
    print_header("TEST 1: Sprawdzenie wstępne")
    print("""
    To sprawdzi czy Unified Chaos Platform załaduje się prawidłowo.
    """)
    
    run_test(1, "Import Test", 
        "python -c \"import UNIFIED_CHAOS_PLATFORM; print('[OK] Moduł załadowany')\"",
        "Sprawdzenie czy plik się importuje")
    
    # =====================================================================
    # TEST 2-10: Moduły
    # =====================================================================
    
    modules = [
        (2, "Chaos Proxy", 
         "1. Victim Server (Terminal 1): wpisz 9\n2. Chaos Proxy (Terminal 2): wpisz 1",
         "Uruchamia proxy z losową mutacją pakietów"),
        
        (3, "ISP Obfuscator",
         "1. Victim Server (Terminal 1): wpisz 9\n2. ISP Obfuscator (Terminal 2): wpisz 2",
         "Obfuskuje ruch przez padding + jitter"),
        
        (4, "HTTP Interceptor",
         "1. Victim Server (Terminal 1): wpisz 9\n2. HTTP Interceptor (Terminal 2): wpisz 3",
         "Przechwytuje HTTP i szuka keywords"),
        
        (5, "TCP Fragmenter",
         "1. Victim Server (Terminal 1): wpisz 9\n2. TCP Fragmenter (Terminal 2): wpisz 4",
         "Fragmentacja na 1-5 bajtowe kawałki"),
        
        (6, "Smuggling Probe",
         "Wybierz opcję 5 -> Wpisz host np. example.com",
         "Test HTTP Request Smuggling (CL.TE)"),
        
        (7, "Bulk Smuggling",
         "Wybierz opcję 6 -> Wpisz: example.com,google.com,github.com",
         "Masowy test wielu targets (20 wątków)"),
        
        (8, "Traffic Audit",
         "1. Victim Server (Terminal 1): wpisz 9\n2. Traffic Audit (Terminal 2): wpisz 7",
         "Szuka nieszyfrowanych wrażliwych danych"),
        
        (9, "Audit Scanner",
         "Wybierz opcję 8 -> Wpisz ścieżkę: d:\\Game",
         "Skan kodu źródłowego pod kątem vulnerabilities"),
        
        (10, "Super Mode",
         "Wybierz opcję 10 -> Uruchamia WSZYSTKO naraz",
         "Kombinowany test wszystkich modułów"),
    ]
    
    for num, name, steps, desc in modules:
        print_header(f"TEST {num}: {name}")
        print(f"Opis: {desc}\n")
        print(f"Kroki:\n{steps}\n")
        
        response = input("Przejść do tego testu? (y/n): ").strip().lower()
        if response == 'y':
            print("\nOtwórz: python UNIFIED_CHAOS_PLATFORM.py")
            print("w osobnym terminalu, następnie wykonaj kroki powyżej.\n")
            input("Wciśnij Enter po zakończeniu testu...")
        else:
            print("• Pominięto\n")
    
    # =====================================================================
    # SUMMARY
    # =====================================================================
    print_header("PODSUMOWANIE TESTÓW")
    
    print("""
    Ukończyłeś Quick Start! Oto co powinieneś wiedzieć:
    
    ✓ CHAOS PROXY - do testowania stabilności aplikacji
    ✓ ISP OBFUSCATOR - do omijania DPI (Deep Packet Inspection)
    ✓ HTTP INTERCEPTOR - do audytu bezpieczeństwa HTTP
    ✓ TCP FRAGMENTER - do fragementacji pakietów
    ✓ SMUGGLING PROBE - do testowania jednego hosta
    ✓ BULK SMUGGLING - do bug bounty (paralelne testy)
    ✓ TRAFFIC AUDIT - do monitorowania ruchu
    ✓ AUDIT SCANNER - do scanu kodu na wrażliwości
    ✓ SUPER MODE - do testy wszystkiego jednocześnie
    
    NASTĘPNE KROKI:
    1. Przeczytaj DOKUMENTACJA.md (płen opis)
    2. Eksperymentuj z różnymi konfiguracjami
    3. Dostosuj porty/parametry do Twoich potrzeb
    4. Dodaj własne moduły
    5. Integuj z Twoimi toolami (Burp, nmap, etc.)
    
    WSKAŹÓWKI:
    • Zawsze testuj na swoich systemach najpierw
    • Sprawdź legalność przed testowaniem systemów trzecich
    • Używaj Victim Server do testów
    • Monitoruj porty: netstat -ano | grep :PORT
    • Loguj wyniki do pliku
    
    TROUBLESHOOTING:
    • Port zajęty? Zmień numer w konfiguracji
    • Nie widać danych? Sprawdź czy traffic płynie przez proxy
    • SSL error? Użyj ssl.create_default_context()
    
    DOKUMENTACJA:
    - DOKUMENTACJA.md - kompleksowy opis
    - UNIFIED_CHAOS_PLATFORM.py - kod źródłowy
    - README.txt (jeśli istnieje)
    
    Powodzenia! 🚀
    """)
    
    print("\nWciśnij Enter aby zakończyć...")
    input()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[*] Quick Start przerwany.")
    except Exception as e:
        print(f"\n[!] Error: {e}")
