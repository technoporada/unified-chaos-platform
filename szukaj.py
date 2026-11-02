import os
import re

# KONFIGURACJA
TARGET_DIR = os.getcwd()  # domyślnie bieżący katalog
PATTERNS = {
    "SENSITIVE_DATA": r"(password|secret|api_key|token|access_key|private_key)[\s]*[:=][\s]*['\"].*['\"]",
    "SHELL_INJECTION": r"(os\.system|subprocess\.Popen|exec\(|eval\()",
    "NETWORK_SOCKETS": r"(socket\.socket|requests\.|urllib\.)",
    "FILE_DESTRUCTION": r"(os\.remove|os\.rmdir|shutil\.rmtree)",
    "EXPLOIT_MARKERS": r"(payload|shellcode|exploit|backdoor|reverse_shell)",
    "PATH_TRAVERSAL": r"\.\./\.\./",
}

COMPILED_PATTERNS = {key: re.compile(pattern, re.IGNORECASE) for key, pattern in PATTERNS.items()}

def audit_files(directory):
    # Zabezpieczenie przed path traversal
    base_real = os.path.realpath(os.path.dirname(os.path.abspath(__file__)))
    target_real = os.path.realpath(directory)
    if not (target_real == base_real or target_real.startswith(base_real + os.sep)):
        print(f"[!] Odmowa dostępu: ścieżka poza dozwolonym katalogiem ({base_real})")
        return

    print(f"[*] ROZPOCZYNAM AUDYT TECHNICZNY W: {os.path.abspath(directory)}")
    print("-" * 60)
    
    found_issues = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(('.py', '.js', '.sh', '.c', '.cpp', '.asm', '.php')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for i, line in enumerate(f):
                            for key, compiled_pattern in COMPILED_PATTERNS.items():
                                if compiled_pattern.search(line):
                                    print(f"[{key}] {file_path}:{i+1} -> {line.strip()}")
                                    found_issues += 1
                except Exception as e:
                    print(f"[!] BŁĄD DOSTĘPU: {file_path} - {e}")

    print("-" * 60)
    print(f"[*] AUDYT ZAKOŃCZONY. ZNALEZIONO PUNKTÓW ZAPALNYCH: {found_issues}")

if __name__ == "__main__":
    import sys
    directory = sys.argv[1] if len(sys.argv) > 1 else TARGET_DIR
    audit_files(directory)