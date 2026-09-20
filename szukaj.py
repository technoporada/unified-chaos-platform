import os
import re

# KONFIGURACJA
TARGET_DIR = r"D:\Technoporada"  # Ścieżka do analizowanego kodu
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
    print(f"[*] ROZPOCZYNAM AUDYT TECHNICZNY W: {os.path.abspath(directory)}")
    print("-" * 60)
    
    found_issues = 0
    for root, _, files in os.walk(directory):
        for file in files:
            # Rozszerzenia warte uwagi
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
    audit_files(TARGET_DIR)