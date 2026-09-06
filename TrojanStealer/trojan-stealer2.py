#!/usr/bin/env python3
"""
MALWARE EDUCACIONAL - Técnicas de Ofuscação e Dump
Para fins de aprendizado em cibersegurança e análise forense.

AVISO: Este código é apenas para estudo em ambientes controlados.
Nunca execute em sistemas de produção ou sem autorização.
"""

import os
import sys
import base64
import platform
import subprocess
from datetime import datetime

# ============================================
# CLASSE DE LOGGING LOCAL
# ============================================

class LocalLogger:
    """
    Implementa logging local em C:\Temp em vez de C2
    """
    
    def __init__(self, log_dir="C:\\Temp"):
        self.log_dir = log_dir
        self.ensure_log_directory()
        self.log_file = os.path.join(self.log_dir, f"malware_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    
    def ensure_log_directory(self):
        """Garante que o diretório de log exista"""
        if not os.path.exists(self.log_dir):
            try:
                os.makedirs(self.log_dir, exist_ok=True)
            except Exception as e:
                print(f"Erro ao criar diretório de log: {e}")
                # Fallback para diretório temporário do sistema
                self.log_dir = os.path.join(os.path.expanduser("~"), "temp_logs")
                os.makedirs(self.log_dir, exist_ok=True)
                self.log_file = os.path.join(self.log_dir, f"malware_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    
    def write_log(self, data, category="INFO"):
        """Escreve dados no arquivo de log local"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().isoformat()
                f.write(f"[{timestamp}] [{category}] {data}\n")
            return True
        except Exception as e:
            print(f"Erro ao escrever no log: {e}")
            return False
    
    def log_system_info(self, info):
        """Registra informações do sistema"""
        self.write_log("=== INFORMAÇÕES DO SISTEMA ===", "SYSTEM")
        for key, value in info.items():
            if key == 'environment_vars':
                self.write_log(f"{key}: {{...{len(value)} variáveis...}}", "SYSTEM")
            else:
                self.write_log(f"{key}: {value}", "SYSTEM")
    
    def log_network_info(self, info):
        """Registra informações de rede"""
        self.write_log("=== INFORMAÇÕES DE REDE ===", "NETWORK")
        for key, value in info.items():
            if isinstance(value, dict):
                self.write_log(f"{key}:", "NETWORK")
                for subkey, subvalue in value.items():
                    self.write_log(f"  {subkey}: {subvalue}", "NETWORK")
            else:
                self.write_log(f"{key}: {value}", "NETWORK")
    
    def log_obfuscation(self, original, obfuscated, decrypted):
        """Registra operações de ofuscação"""
        self.write_log("=== OFUSCAÇÃO XOR ===", "OBFUSCATION")
        self.write_log(f"Original: {original}", "OBFUSCATION")
        self.write_log(f"Ofuscado: {obfuscated}", "OBFUSCATION")
        self.write_log(f"Decodificado: {decrypted}", "OBFUSCATION")
    
    def log_persistence_methods(self, methods):
        """Registra métodos de persistência"""
        self.write_log("=== MÉTODOS DE PERSISTÊNCIA ===", "PERSISTENCE")
        for method in methods:
            self.write_log(f"  • {method}", "PERSISTENCE")
    
    def log_evasion_techniques(self, techniques):
        """Registra técnicas de evasão"""
        self.write_log("=== TÉCNICAS DE EVASÃO ===", "EVASION")
        for tech in techniques:
            self.write_log(f"  • {tech}", "EVASION")


# ============================================
# TÉCNICA 1: OFUSCAÇÃO DE STRINGS COM XOR
# ============================================

class StringObfuscator:
    """
    Demonstra como strings são ofuscadas em malware usando XOR.
    XOR é reversível: (A ^ B) ^ B = A
    """
    
    def __init__(self, key=0x42):
        self.key = key
    
    def xor_encrypt(self, data: bytes) -> bytes:
        """Cifra dados usando XOR com chave"""
        return bytes([b ^ self.key for b in data])
    
    def xor_decrypt(self, data: bytes) -> bytes:
        """Decifra dados XOR (mesma operação)"""
        return self.xor_encrypt(data)  # XOR é simétrico
    
    def obfuscate_string(self, text: str) -> str:
        """Ofusca string para base64 após XOR"""
        encrypted = self.xor_encrypt(text.encode('utf-8'))
        return base64.b64encode(encrypted).decode('utf-8')
    
    def deobfuscate_string(self, obfuscated: str) -> str:
        """Reverte ofuscação"""
        encrypted = base64.b64decode(obfuscated)
        return self.xor_decrypt(encrypted).decode('utf-8')


# ============================================
# TÉCNICA 2: DUMP DE INFORMAÇÕES DO SISTEMA
# ============================================

class SystemDumper:
    """
    Simula técnicas de coleta de informações (reconnaissance)
    comuns em malware para fingerprinting do alvo.
    """
    
    def __init__(self, logger=None):
        # Strings ofuscadas para evitar detecção por assinatura
        self._obf = StringObfuscator()
        self.cmd_whoami = self._obf.obfuscate_string("whoami")
        self.cmd_hostname = self._obf.obfuscate_string("hostname")
        self.cmd_uname = self._obf.obfuscate_string("uname -a")
        self.logger = logger
    
    def dump_system_info(self):
        """Coleta informações do sistema (técnica de reconnaissance)"""
        info = {
            'timestamp': datetime.now().isoformat(),
            'platform': platform.system(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'hostname': platform.node(),
            'username': os.getenv('USER') or os.getenv('USERNAME'),
            'python_version': platform.python_version(),
            'current_directory': os.getcwd(),
            'environment_vars': dict(os.environ)
        }
        
        # Envia para o log local em vez de C2
        if self.logger:
            self.logger.log_system_info(info)
        
        return info
    
    def dump_network_info(self):
        """Simula coleta de informações de rede"""
        # Em malware real, isso incluiria IPs, interfaces, rotas
        network_data = {
            'interfaces': self._get_network_interfaces(),
            'hosts_file': self._read_hosts_file(),
            'dns_servers': self._get_dns_servers()
        }
        
        # Envia para o log local em vez de C2
        if self.logger:
            self.logger.log_network_info(network_data)
        
        return network_data
    
    def _get_network_interfaces(self):
        """Lista interfaces de rede"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(["ipconfig", "/all"], 
                                      capture_output=True, text=True)
            else:
                result = subprocess.run(["ifconfig"], 
                                      capture_output=True, text=True)
            return result.stdout[:500]  # Limitado para exemplo
        except:
            return "N/A"
    
    def _read_hosts_file(self):
        """Lê arquivo hosts (técnica comum para ver redirecionamentos)"""
        hosts_paths = {
            'Windows': r'C:\Windows\System32\drivers\etc\hosts',
            'Linux': '/etc/hosts',
            'Darwin': '/etc/hosts'
        }
        try:
            path = hosts_paths.get(platform.system(), '/etc/hosts')
            with open(path, 'r') as f:
                return f.read()
        except:
            return "Acesso negado ou arquivo não encontrado"
    
    def _get_dns_servers(self):
        """Obtém servidores DNS configurados"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(["ipconfig", "/displaydns"], 
                                      capture_output=True, text=True)
                return "DNS cache disponível"
            else:
                with open('/etc/resolv.conf', 'r') as f:
                    return f.read()
        except:
            return "N/A"


# ============================================
# TÉCNICA 3: OFUSCAÇÃO DE CÓDIGO (POLIMORFISMO)
# ============================================

class CodeObfuscator:
    """
    Demonstra técnicas de ofuscação de código usadas
    para evadir análise estática em sandboxes.
    """
    
    def dynamic_api_resolve(self, api_name: str):
        """
        Resolução dinâmica de APIs - técnica para evitar
        importações óbvias que são detectadas por antivírus
        """
        # Simula GetProcAddress / dlsym
        import importlib
        try:
            module, func = api_name.rsplit('.', 1)
            mod = importlib.import_module(module)
            return getattr(mod, func)
        except:
            return None
    
    def junk_code_insertion(self, code_block: str, junk_ratio=0.3):
        """
        Simula inserção de código lixo (junk code) para
        dificultar análise e alterar hash do arquivo
        """
        junk_operations = [
            "x = 42 * 1337 // 100",
            "unused_var = 'obfuscation'[::-1]",
            "temp = sum([i**2 for i in range(10)])",
            "flag = (True and False) or (not False)",
        ]
        
        lines = code_block.split('\n')
        import random
        for _ in range(int(len(lines) * junk_ratio)):
            pos = random.randint(0, len(lines))
            lines.insert(pos, f"    # {random.choice(junk_operations)}")
        
        return '\n'.join(lines)
    
    def string_concatenation(self, secret: str):
        """
        Quebra strings em partes para evitar detecção
        por assinatura de string
        """
        chunks = [secret[i:i+3] for i in range(0, len(secret), 3)]
        reconstruction = " + ".join([f"'{c}'" for c in chunks])
        return f"({reconstruction})"


# ============================================
# TÉCNICA 4: PERSISTÊNCIA (CONCEITO)
# ============================================

class PersistenceManager:
    """
    Demonstra técnicas de persistência usadas por malware
    para sobreviver a reinicializações.
    """
    
    def __init__(self, logger=None):
        self.logger = logger
    
    def show_persistence_methods(self):
        """Lista métodos comuns de persistência por SO"""
        methods = {
            'Windows': [
                'Registry: HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run',
                'Scheduled Tasks (schtasks)',
                'Startup Folder: %APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup',
                'WMI Event Subscriptions',
                'DLL Hijacking'
            ],
            'Linux': [
                'Crontab: crontab -e',
                'Systemd services: /etc/systemd/system/',
                'Bashrc: ~/.bashrc',
                'Init scripts: /etc/init.d/',
                'LD_PRELOAD hooking'
            ],
            'Darwin': [
                'LaunchAgents: ~/Library/LaunchAgents/',
                'LaunchDaemons: /Library/LaunchDaemons/',
                'LoginItems via osascript',
                'Cron jobs'
            ]
        }
        
        platform_methods = methods.get(platform.system(), {})
        
        # Envia para o log local em vez de C2
        if self.logger:
            self.logger.log_persistence_methods(platform_methods)
        
        return platform_methods


# ============================================
# DEMONSTRAÇÃO PRINCIPAL
# ============================================

def main():
    print("=" * 60)
    print("DEMONSTRAÇÃO DE TÉCNICAS DE OFUSCAÇÃO E DUMP")
    print("Fins educacionais - Análise de Malware")
    print("=" * 60)
    
    # Inicializa o logger local
    logger = LocalLogger()
    logger.write_log("Iniciando execução do malware educacional", "INIT")
    
    # 1. Demonstração de XOR
    print("\n[1] OFUSCAÇÃO XOR")
    print("-" * 40)
    obf = StringObfuscator(key=0x42)
    
    secret = "cmd.exe /c calc.exe"
    encrypted = obf.obfuscate_string(secret)
    decrypted = obf.deobfuscate_string(encrypted)
    
    print(f"Original:    {secret}")
    print(f"Ofuscado:    {encrypted}")
    print(f"Decodificado:{decrypted}")
    
    # Registra no log local
    logger.log_obfuscation(secret, encrypted, decrypted)
    
    # 2. Dump de informações
    print("\n[2] DUMP DE INFORMAÇÃO DO SISTEMA")
    print("-" * 40)
    dumper = SystemDumper(logger=logger)
    
    sys_info = dumper.dump_system_info()
    for key, value in sys_info.items():
        if key == 'environment_vars':
            print(f"{key}: {{...{len(value)} variáveis...}}")
        else:
            print(f"{key}: {value}")
    
    # 3. Ofuscação de código
    print("\n[3] TÉCNICAS DE OFUSCAÇÃO DE CÓDIGO")
    print("-" * 40)
    code_obf = CodeObfuscator()
    
    sample_code = """
    def malicious_action():
        data = steal_data()
        exfiltrate(data)
    """
    
    obfuscated = code_obf.junk_code_insertion(sample_code, junk_ratio=0.5)
    print("Código com junk code inserido:")
    print(obfuscated)
    
    # String splitting
    payload = "http://evil.com/c2"
    split_payload = code_obf.string_concatenation(payload)
    print(f"\nString split: {split_payload}")
    
    # Registra no log local
    logger.write_log("Código com junk code inserido", "OBFUSCATION")
    logger.write_log(f"String split: {split_payload}", "OBFUSCATION")
    
    # 4. Persistência
    print("\n[4] MÉTODOS DE PERSISTÊNCIA")
    print("-" * 40)
    persist = PersistenceManager(logger=logger)
    methods = persist.show_persistence_methods()
    for method in methods:
        print(f"  • {method}")
    
    # 5. Análise de detecção
    print("\n[5] TÉCNICAS DE EVASÃO DE DETECÇÃO")
    print("-" * 40)
    evasion_techniques = [
        "Verificação de sandbox (timing, processos)",
        "Verificação de VM (MAC addresses, drivers)",
        "Delay de execução (sleep, timers)",
        "Ofuscação de imports (LoadLibrary dinâmico)",
        "Criptografia de payload (AES, RC4, XOR)",
        "Process hollowing/injection",
        "Direct syscalls (bypass hooks)"
    ]
    
    # Registra no log local
    logger.log_evasion_techniques(evasion_techniques)
    
    for tech in evasion_techniques:
        print(f"  • {tech}")
    
    # 6. Simulação de exfiltração de dados (agora local)
    print("\n[6] SIMULAÇÃO DE EXFILTRAÇÃO DE DADOS (LOCAL)")
    print("-" * 40)
    
    # Coleta de dados sensíveis simulados
    sensitive_data = {
        "user_credentials": "user:password_hash",
        "system_keys": "encryption_keys_here",
        "browser_history": "visited_sites_data"
    }
    
    # Em vez de enviar para C2, salva no log local
    logger.write_log("=== DADOS SENSÍVEIS COLETADOS ===", "EXFILTRATION")
    for key, value in sensitive_data.items():
        logger.write_log(f"{key}: {value}", "EXFILTRATION")
    
    print(f"Dados sensíveis salvos em: {logger.log_file}")
    
    print("\n" + "=" * 60)
    print("ANÁLISE COMPLETA - Use para estudar defesas")
    print(f"Logs salvos em: {logger.log_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()