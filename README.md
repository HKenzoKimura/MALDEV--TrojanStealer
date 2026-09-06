# 🧬 Educational Malware — Obfuscation, Recon & Evasion Techniques

> **Context:** Demonstração didática de técnicas usadas por malware real — XOR obfuscation, system fingerprinting, code obfuscation, persistence mechanisms e evasion techniques — com **logging exclusivamente local** (sem C2, sem exfiltração real). Desenvolvido para análise de malware, purple team e construção de detecções.
>
> ⚠️ *Código de estudo. Nenhuma funcionalidade de C2 ou exfiltração real foi implementada — todos os dados são salvos localmente em `C:\Temp`.*

## `Developed by: HKK`
---

## `$ cat ./objective.txt`

Implementar e documentar as **camadas técnicas** que compõem um infostealer moderno, para:

- Entender como cada técnica funciona internamente (não apenas o conceito)
- Construir **regras de detecção** baseadas nos artefatos gerados
- Desenvolver contramedidas realistas para cada estágio
- Servir como base para análise de amostras reais com as mesmas TTPs

---

## `$ cat ./architecture.txt`

```
┌──────────────────────────────────────────────────────────────────────────┐
│              EDUCATIONAL MALWARE — COMPONENT MAP                         │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                         main()                                   │    │
│  │  Orquestra todos os módulos em sequência demonstrativa           │    │
│  └──┬──────────┬──────────┬──────────┬──────────┬──────────────────┘    │
│     │          │          │          │          │                        │
│     ▼          ▼          ▼          ▼          ▼                        │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────────┐                  │
│  │String│  │System│  │ Code │  │Persis│  │  Local   │                  │
│  │Obfus-│  │Dumper│  │Obfus-│  │tence │  │  Logger  │                  │
│  │cator │  │      │  │cator │  │Manage│  │          │                  │
│  │[XOR] │  │[Recon│  │[Junk/│  │r     │  │C:\Temp\  │                  │
│  │      │  │]     │  │Split]│  │[List]│  │*.txt     │                  │
│  └──────┘  └──────┘  └──────┘  └──────┘  └──────────┘                  │
│                                                                          │
│  EM MALWARE REAL:              NESTA IMPLEMENTAÇÃO:                      │
│  └──► C2 remoto (exfil)        └──► LocalLogger (C:\Temp)               │
│  └──► Payload executável       └──► Demonstração conceitual             │
│  └──► AES/RC4 encryption       └──► XOR simples (didático)              │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## `$ cat ./design_decisions.md`

### 1. `StringObfuscator` — XOR Encryption

```python
def xor_encrypt(self, data: bytes) -> bytes:
    return bytes([b ^ self.key for b in data])

def xor_decrypt(self, data: bytes) -> bytes:
    return self.xor_encrypt(data)  # XOR é simétrico
```

**Por que XOR é a base da obfuscação em malware?**

XOR tem uma propriedade matemática fundamental: `(A ^ B) ^ B = A`. Isso significa que **a operação de encrypt e decrypt é idêntica** — o mesmo código serve para as duas direções. Em malware:

```
"cmd.exe"  → XOR(0x42) → bytes cifrados → base64 → string armazenada no binário
                                                            ↓
                                              Antivírus não encontra "cmd.exe"
```

O binário armazena apenas o payload cifrado. A chave (`0x42`) está no código, mas separada da string — scanners baseados em assinatura que procuram por `cmd.exe`, `powershell.exe`, `Invoke-WebRequest` não encontram nada.

**Pipeline completo:**
```
plaintext → XOR(key) → base64encode → stored_obfuscated_string
stored    → base64decode → XOR(key) → plaintext em runtime
```

**Limitação didática:** XOR com chave estática é trivialmente reversível por ferramentas como Ghidra/IDA Pro. Malware real usa AES-256, RC4 ou ChaCha20 com chaves derivadas dinamicamente.

---

### 2. `SystemDumper` — Reconnaissance & Fingerprinting

```python
info = {
    'platform':     platform.system(),
    'architecture': platform.machine(),
    'hostname':     platform.node(),
    'username':     os.getenv('USER') or os.getenv('USERNAME'),
    'environment_vars': dict(os.environ),
    ...
}
```

**Por que malware coleta essas informações antes de agir?**

O fingerprinting do sistema serve a três propósitos distintos:

| Dado coletado | Propósito para o atacante |
|---------------|--------------------------|
| `platform` + `architecture` | Escolher payload correto (x86 vs x64, Windows vs Linux) |
| `hostname` + `username` | Identificar se é sandbox ou máquina de analista |
| `environment_vars` | Encontrar credenciais, tokens e paths relevantes (`AWS_ACCESS_KEY`, `GITHUB_TOKEN`) |
| Arquivo `hosts` | Detectar redirecionamentos de segurança (ex: sinkholing de domínios C2) |
| DNS servers | Identificar ambiente corporativo vs. doméstico |

**Strings ofuscadas no `SystemDumper`:**

```python
self.cmd_whoami   = self._obf.obfuscate_string("whoami")
self.cmd_hostname = self._obf.obfuscate_string("hostname")
```

Os comandos são armazenados cifrados nos atributos da classe e decodificados apenas em runtime — um scanner estático que procura por `"whoami"` no binário não encontra a string.

**`_read_hosts_file()`** é uma técnica real: malware verifica o `hosts` para saber se domínios de C2 conhecidos foram bloqueados/redirecionados por ferramentas de segurança.

---

### 3. `CodeObfuscator` — Evasão de Análise Estática

#### 3a. Junk Code Insertion

```python
junk_operations = [
    "x = 42 * 1337 // 100",
    "unused_var = 'obfuscation'[::-1]",
    "temp = sum([i**2 for i in range(10)])",
]
```

**O que é junk code e por que funciona?**

Inserir código morto (que não altera o comportamento) serve para:

1. **Alterar o hash do arquivo** — cada inserção muda o SHA256, tornando assinaturas baseadas em hash ineficazes
2. **Dificultar análise humana** — o analista precisa separar código real de junk
3. **Confundir análise de fluxo estático** — ferramentas que analisam grafos de controle encontram mais nós

Ferramentas como **sandboxes automatizadas** que analisam o fluxo lógico não são afetadas — mas humanos e scanners de assinatura são.

#### 3b. Dynamic API Resolution

```python
def dynamic_api_resolve(self, api_name: str):
    module, func = api_name.rsplit('.', 1)
    mod = importlib.import_module(module)
    return getattr(mod, func)
```

**Equivalente Python de `GetProcAddress` no Windows.**

Em vez de `import subprocess` no topo do arquivo (visível em análise estática de imports), o código carrega o módulo dinamicamente. Scanners que procuram por `import subprocess` ou `import winreg` nos imports estáticos não encontram nada.

Equivalente em C/Windows:
```c
// Estático (detectável):
HANDLE h = CreateFile(...);

// Dinâmico (evasão):
FARPROC pCreateFile = GetProcAddress(GetModuleHandle("kernel32"), "CreateFile");
```

#### 3c. String Concatenation / Splitting

```python
def string_concatenation(self, secret: str):
    chunks = [secret[i:i+3] for i in range(0, len(secret), 3)]
    reconstruction = " + ".join([f"'{c}'" for c in chunks])
    return f"({reconstruction})"
```

`"http://evil.com/c2"` → `('htt' + 'p:/' + '/ev' + 'il.' + 'com' + '/c2')`

O scanner procura por `"http://evil.com/c2"` — não encontra. A string só existe completa em **runtime**, na memória.

---

### 4. `PersistenceManager` — Mecanismos por SO

```python
methods = {
    'Windows': [
        'Registry: HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run',
        'Scheduled Tasks (schtasks)',
        'WMI Event Subscriptions',
        'DLL Hijacking'
    ],
    'Linux': ['Crontab', 'Systemd services', 'LD_PRELOAD hooking'],
    'Darwin': ['LaunchAgents', 'LaunchDaemons', 'LoginItems']
}
```

**Por que múltiplos métodos de persistência?**

Malware sofisticado implementa **múltiplas camadas de persistência** — se um método é detectado e removido, o outro garante sobrevivência. A ordem de preferência em ambiente Windows:

```
Registry Run Key    → mais simples, mais monitorado
Scheduled Task      → mais flexível, permite delay
WMI Subscription    → mais difícil de detectar, sobrevive a remoção manual
DLL Hijacking       → sem entrada óbvia no registro, mais furtivo
```

**`LD_PRELOAD` no Linux:** carrega uma biblioteca maliciosa antes de qualquer outra em cada processo — permite hookar funções como `read()`, `write()`, `open()` de forma transparente.

---

### 5. `LocalLogger` — Adaptação Educacional

```python
TOR_PROXIES = {}       # Em malware real: SOCKS5 para C2
self.log_file = ...    # Nesta versão: C:\Temp\malware_log_*.txt
```

O `LocalLogger` substitui o componente de exfiltração real. Em um infostealer funcional, os dados coletados seriam:

```
Sistema Real:
  dados → cifrar(AES) → comprimir(GZIP) → HTTP POST → C2 remoto

Esta Implementação:
  dados → LocalLogger.write_log() → C:\Temp\malware_log_*.txt
```

A interface dos métodos (`log_system_info`, `log_network_info`, `log_obfuscation`) espelha o que seria uma classe de exfiltração real — facilitando o entendimento da arquitetura sem implementar C2.

---

## `$ cat ./mitre_mapping.yml`

```yaml
tactics:
  defense_evasion:
    - T1027       # Obfuscated Files or Information
                  # StringObfuscator: XOR + Base64 em todas as strings críticas

    - T1027.001   # Binary Padding (conceito do junk_code_insertion)
                  # Inserção de código morto altera hash sem mudar comportamento

    - T1140       # Deobfuscate/Decode Files or Information
                  # xor_decrypt() em runtime: decode das strings antes do uso

    - T1574.002   # Hijack Execution Flow: DLL Side-Loading
                  # PersistenceManager documenta DLL Hijacking como método

    - T1218       # System Binary Proxy Execution
                  # dynamic_api_resolve(): carrega módulos sem import estático

  discovery:
    - T1082       # System Information Discovery
                  # SystemDumper.dump_system_info(): platform, arch, hostname

    - T1016       # System Network Configuration Discovery
                  # _get_network_interfaces(): ipconfig /all ou ifconfig

    - T1016.001   # Internet Connection Discovery
                  # _get_dns_servers(): resolv.conf ou ipconfig /displaydns

    - T1083       # File and Directory Discovery
                  # _read_hosts_file(): leitura de C:\Windows\System32\drivers\etc\hosts

    - T1552.007   # Unsecured Credentials: Container API
                  # dump_system_info() → environment_vars: busca tokens/keys em variáveis

  persistence:
    - T1053.005   # Scheduled Task/Job: Scheduled Task
                  # PersistenceManager → Windows: schtasks

    - T1547.001   # Boot or Logon Autostart: Registry Run Keys
                  # HKCU\Software\Microsoft\Windows\CurrentVersion\Run

    - T1546.003   # Event Triggered Execution: WMI Event Subscription
                  # PersistenceManager → Windows: WMI subscriptions

    - T1574.006   # Hijack Execution Flow: LD_PRELOAD
                  # PersistenceManager → Linux: LD_PRELOAD hooking

  collection:
    - T1005       # Data from Local System
                  # dump_system_info() + dump_network_info()

    - T1552.001   # Unsecured Credentials: Credentials In Files
                  # Conceito de busca em environment_vars e arquivos locais
```

---

## `$ cat ./detection_opportunities.md`

> Blue team — artefatos gerados e onde detectar cada técnica.

| Técnica | Artefato Gerado | Detecção |
|---------|----------------|----------|
| XOR + Base64 em runtime | Strings decodificadas em memória | Memory scanning (YARA em memória) |
| Dynamic import (`importlib`) | `__import__` ou `importlib.import_module` em bytecode | SAST / bytecode analysis |
| Junk code | SHA256 muda a cada geração | Detecção por comportamento, não por hash |
| `ipconfig /all` via `subprocess` | Process creation: `cmd.exe` filho de `python.exe` | Sysmon Event ID 1 |
| Leitura do `hosts` file | File read em `C:\Windows\System32\drivers\etc\hosts` | Sysmon Event ID 11 |
| `environment_vars` dump | Acesso a variáveis de ambiente em massa | Behavioral analysis em sandbox |
| Registry Run Key | `HKCU\...\CurrentVersion\Run` write | Sysmon Event ID 13 |
| WMI subscription | `wmic` ou `Win32_EventFilter` criação | Sysmon Event ID 19/20/21 |
| `LD_PRELOAD` | `/etc/ld.so.preload` modificado | File integrity monitoring (auditd) |
| Log em `C:\Temp` | Arquivo `malware_log_*.txt` | DLP / file monitoring em %TEMP% |

**Regra YARA conceitual para XOR + Base64:**
```yara
rule XOR_B64_Obfuscation {
    meta:
        description = "Detecta padrão XOR + Base64 em strings"
    strings:
        $b64_decode = "base64.b64decode" ascii
        $xor_loop   = "b ^ self.key" ascii
        $xor_loop2  = "^ 0x" ascii
    condition:
        $b64_decode and ($xor_loop or $xor_loop2)
}
```

---

## `$ cat ./usage.sh`

```bash
# Instalar dependências (todas stdlib — sem pip necessário)
python --version  # Python 3.6+

# Executar a demonstração
python educational_malware.py
```

```
# Output esperado:
============================================================
DEMONSTRAÇÃO DE TÉCNICAS DE OFUSCAÇÃO E DUMP
Fins educacionais - Análise de Malware
============================================================

[1] OFUSCAÇÃO XOR
----------------------------------------
Original:    cmd.exe /c calc.exe
Ofuscado:    ISMHJSsmIiMlJSM=
Decodificado:cmd.exe /c calc.exe

[2] DUMP DE INFORMAÇÃO DO SISTEMA
----------------------------------------
platform: Windows
architecture: AMD64
hostname: DESKTOP-XYZ
...

[3] TÉCNICAS DE OFUSCAÇÃO DE CÓDIGO
...
Logs salvos em: C:\Temp\malware_log_20240115_103201.txt
```

```bash
# Analisar o log gerado
cat C:\Temp\malware_log_*.txt
# ou no Linux/macOS: ~/temp_logs/malware_log_*.txt
```

---

## `$ cat ./analysis_exercises.md`

> Exercícios para aprofundar o entendimento.

**1. Reverse a obfuscação manualmente**
```python
import base64
key = 0x42
obfuscated = "ISMHJSsmIiMlJSM="  # output do script
encrypted = base64.b64decode(obfuscated)
plaintext = bytes([b ^ key for b in encrypted]).decode()
print(plaintext)  # → "cmd.exe /c calc.exe"
```

**2. Escrever uma regra YARA para detectar o XOR key 0x42**

**3. Analisar o log gerado em `C:\Temp` e identificar quais dados um analista priorizaria**

**4. Propor uma detecção no Sysmon para `subprocess.run(["ipconfig", "/all"])`**

**5. Comparar o `junk_code_insertion` com técnicas de polimorfismo reais (ex: Virut, Metamorphic engines)**

---

## `$ cat ./lessons_learned.txt`

```
[+] XOR é o ponto de entrada para entender obfuscação — simples o suficiente para dissecar
[+] Dynamic API resolution é a técnica mais comum em malware profissional — vale estudar a fundo
[+] environment_vars é um vetor subestimado — tokens AWS/GitHub/Slack frequentemente vazam por lá
[+] Persistência em WMI é das mais furtivas no Windows — poucos EDRs cobrem bem Event Subscriptions
[+] Separar logger (C2) do core facilita adaptar o código para diferentes cenários de lab
[-] XOR com chave estática é trivialmente reversível — não representa malware moderno
[-] Junk code em Python é menos efetivo que em binários compilados (bytecode é legível)
[-] dynamic_api_resolve() com importlib é detectável por análise de bytecode — GetProcAddress em C é mais furtivo
[-] LD_PRELOAD como persistência é detectado por qualquer ferramenta de FIM decente
[→] Próximo nível: implementar AES-256 no lugar do XOR, shellcode injection em Python via ctypes
```

---

<p align="center">
  <i>Educational only · No C2 · No real exfiltration · Local logging only · MITRE ATT&CK mapped</i>
</p>
