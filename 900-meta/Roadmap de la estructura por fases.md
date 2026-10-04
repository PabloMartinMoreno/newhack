---
tipo: meta
aliases:
  - Roadmap
  - Estructura objetivo
  - Roadmap rojo
tags:
  - meta/roadmap
---

# Roadmap de la estructura por fases

> [!abstract] La estructura roja objetivo, a nivel hoja, para tildar de a poco
> El árbol completo al que apunta el vault del lado rojo, por **fases** (el orden de [[Inicio]]). Tomado de una estructura de referencia por fases y adaptado a las reglas del vault. `✓` existe · `~` parcial (cubierto dentro de otra nota) · `○` hueco por escribir. Modelo detrás: [[Estructura del vault]] § Capas de MOCs. Bitácora: [[Avances]].

## Reglas que fija esta estructura

- **100% rojo, y sigue así.** La fusión con azul no entra en esta capa.
- **Fases arriba, superficie/necesidad adentro.** [[Inicio]] lista solo MOCs de fase.
- **MOC = vista, no contenedor.** Un dominio aparece en varias fases (Shells en Pre- y Post-explotación; servicios en Reconocimiento y Explotación). La repetición es válida.
- **Nada por producto.** No hay "nota de WordPress": la *enumeración* de un producto es una matriz; la *explotación* es un CVE o un mecanismo ya cubierto. Web se organiza por **mecanismo**.
- **Herramientas = entidades** en `400-entidades/`, enlazadas; **nunca** una sección "Tools" por fase.
- Sección que pasa de ~6 hijos → hub. `higiene` indexa MOCs transitivo.

---

## 🟢 Reconocimiento — [[MOC - Reconocimiento]] ✓

**Enumeración de AD** → [[MOC - AD enumeración]]
- ✓ Hosts · ✓ usuarios y grupos · ✓ política de contraseñas · ✓ permisos de objeto (ACLs)
- ○ entidad BloodHound/SharpHound (herramienta muy nombrada, sin nota en `400-entidades/`)

**Enumeración de infraestructura**
- ~ Identificación pasiva → [[Footprinting pasivo - matriz de referencia]] · [[Enumeración pasiva de subdominios - matriz de referencia]]
- ✓ Google dorking → [[Google dorking - matriz de referencia]] · ✓ GitHub dorking → [[GitHub dorking - matriz de referencia]] · ○ CanaryTokens (entidad)

**Reverse engineering** (no amerita MOC: RE de binarios fuera de alcance)
- ✓ Deofuscación de JavaScript → [[JavaScript deobfuscation - matriz de referencia]] (vive en recon web, no en un MOC de RE)

**Enumeración de servicios** → [[MOC - Servicios de red]]
- ✓ FTP(21) · SSH(22) · SMTP(25) · DNS(53) · POP3(110/995) · NFS(2049) · SMB(139/445) · IMAP(143/993) · SNMP(161) · LDAP(389) · IPMI(623) · rsync(873) · MSSQL(1433) · Oracle(1521) · MySQL(3306) · RDP(3389)
- ○ TFTP(69) · Finger(79) · Kerberos(88) · Redis(6379) · MongoDB(27017) · Telnet(23) · VNC(5900) · Docker API(2375)
- ○ entidades: Nmap ✓(existe) · tcpdump · "Windows LOTL port scanning"

**Enumeración web** → [[MOC - Reconocimiento web]]
- ✓ Fuzzing de directorios/páginas · ✓ fuzzing de parámetros · ✓ subdominios pasivos · ✓ subdominios/vhosts · ✓ web server enum (fingerprint)
- ○ Enum por producto (ColdFusion, Drupal, GitLab, IIS, Jenkins, Joomla, Magento, osTicket, PRTG, Splunk, Tomcat, WordPress) → **una matriz de enum por producto**, no un MOC por producto
- ○ entidades: EyeWitness · git-dumper · nikto

**Wi-Fi** ○ (aircrack setup, monitoring, connect) — ¿fuera de alcance del vault?

---

## 🟠 Pre-explotación — [[MOC - Pre-explotación]] ✓  (weaponización)

- ✓ Shells (reverse/bind/webshell) → [[MOC - Shells]]
- ✓ Payloads → [[msfvenom - matriz de referencia]] · [[Payload generado con msfvenom]] · [[metasploit]] · [[Metasploit - matriz de referencia]]
- ○ Cross-compiling de exploits
- ○ Búsqueda/adaptación de exploits (searchsploit — entidad)
- ○ Preparación anti-AV real (Shellter — entidad; más allá de encoders)

---

## 🔴 Explotación — [[MOC - Explotación]] ✓

**Explotación de AD**
- ✓ ADCS → [[MOC - ADCS]]
- ✓ AS-REP roasting · ✓ Kerberoasting → [[MOC - AD roasting]]
- ✓ Delegación (unconstrained/constrained/RBCD) → [[MOC - AD delegaciones]]
- ✓ DCSync → [[MOC - AD volcado de credenciales]]
- ✓ Trust abuse (child→parent, interforest) → [[MOC - AD confianzas]]
- ~ Password spraying (existe la cara web en [[MOC - Autenticación]]; la de AD no como nota)
- ○ ACL abuse (cadenas de BloodHound) · ○ GPP passwords · ○ Silver tickets (tenemos golden, no silver)

**Acceso inicial client-side** ○ (rama entera sin abrir)
- ○ Macro de Office · ○ Windows Library file · ○ iCalendar · ○ JScript (+ cradle a shellcode C#) · ○ Zip → DLL hijacking
- ○ Shellcode runners (VBA · PowerShell · C# · Win32 desde VBA)

**Explotación de servicios**
- ~ SSH · ~ MSSQL (`xp_cmdshell`) · ~ RDP (PtH) — hoy dentro de sus matrices en [[MOC - Servicios de red]]; ¿agrupar como rama de Explotación?
- ✓ entidad sqlmap

**Explotación web** → [[MOC - Explotación web]]
- ✓ CSRF · XSS · directory traversal · file upload · HTTP brute forcing · LFI (+ PHP filters) · OS command injection · SQLi (enum/RCE/read-write/union) · XXE — todo cubierto por las 34 familias
- ○ Por producto (Artifactory, IIS, Joomla, WordPress exploitation) → es CVE/mecanismo, **no** nota por producto

**Wi-Fi** ○ (WEP, WPA/WPA2-PSK, Evil Twin, WPA-Enterprise, WPS)
**Kiosk breakout** ○

---

## ⚪ Post-explotación — [[MOC - Post-explotación]] ✓

- ✓ Operar la sesión → [[MOC - Shells]]  ·  ✓ transferencia → [[MOC - Transferencia de archivos]]

**Volcado de credenciales** → [[MOC - AD volcado de credenciales]]
- ✓ SAM & LSA · ✓ LSASS memory · ✓ NTDS
- ○ Credential Guard bypass · ○ LSA Protection bypass

**Privesc Linux** ○ — ★ el hueco más grande  ·  búsquedas de vectores: ✓ [[Enumeración de privesc Linux - matriz de referencia]] (el abuso de cada uno todavía sin tradecraft)
- ✓ SUID/`cap_setuid` de un intérprete → [[Python SUID y setuid capability - matriz de referencia]]
- ○ /etc/passwd·shadow (readable shadow, writeable passwd/shadow) · ○ resto de capabilities · ○ cron · ~ NFS `no_root_squash` (está en [[NFS - matriz de referencia]]) · ○ PATH hijacking
- ○ grupos privilegiados (adm, disk, docker, lxc/lxd, shadow) · ○ PwnKit · ○ Python library hijacking · ○ shared object hijacking
- ○ sudo abuse (LD_PRELOAD/LD_LIBRARY_PATH, versiones vulnerables) · ○ SUID/SGID · ○ tmux hijack · ○ wildcard injection
- ○ credential hunting Linux · ○ payloads de privesc

**Privesc Windows** ○ — ★
- ○ grupos privilegiados (Backup Operators, DnsAdmins, Event Log Readers, Hyper-V Admins, Print Operators, Server Operators)
- ○ privilegios de token (SeBackup/SeRestore, SeDebug, SeImpersonate/SeAssignPrimaryToken, SeLoadDriver, SeTakeOwnership)
- ○ AlwaysInstallElevated · ○ DLL hijacking (+ proxying) · ○ SCF/LNK maliciosos · ○ scheduled tasks · ○ unquoted service paths · ○ VMDK/VHD/VHDX · ○ weak service permissions
- ○ credential hunting Windows · ○ payloads · ○ version exploits

**Enumeración local** previa a la escalada — ✓ Linux → [[Enumeración de privesc Linux - matriz de referencia]] · ○ Windows

**Evasión (Windows)** ○
- ○ VBA stomping · ○ AMSI bypass (assembly patch, header corruption, JScript, write raid) · ○ AppLocker & CLM bypass · ○ UAC bypass (FodHelper)

**Ataques de contraseña** (transversal) → [[MOC - Ataques de contraseña]]
- ✓ Cracking offline → [[Cracking offline - matriz de referencia]] con [[hashcat]] / [[john]] (+ `*2john`)
- ✓ online enrutado (spraying/stuffing en [[MOC - Autenticación]], brute por servicio); ○ fuerza bruta online consolidada · ○ generación de wordlists (cewl/crunch)

---

## 🟤 Movimiento lateral — [[MOC - Movimiento lateral]] ✓

**AD / Windows** → [[MOC - AD movimiento lateral]]
- ✓ NTLM pass-the-hash · ✓ Kerberos pass-the-ticket · ✓ SMB Net-NTLM relay ([[Relay de NTLM]]) · ✓ LLMNR/NBT-NS ([[MOC - AD envenenamiento y relay]])
- ~ WMI y WinRM (en sus matrices) · ~ PsExec (en la matriz de lateral)

**Linux**
- ○ Pass-the-ticket Linux (CCache files, KeyTab files)

**Pivoting** ○
- ~ vía Metasploit (autoroute/portfwd/socks) → [[Metasploit - matriz de referencia]] § pivoting · ○ nota dedicada (recon de pivoting, port forwarding, proxy chaining) sin herramienta

**Tunneling** ○
- ~ DNS tunneling (existe [[Exfiltración por canal encubierto]], no como túnel de sesión) · ○ HTTP tunneling

---

## 🟣 Persistencia — [[MOC - Persistencia]] ✓

- ✓ AD → [[MOC - AD persistencia]] (golden, SID history) · [[MOC - ADCS]] (cert) · [[MOC - AD confianzas]]
- ○ no-AD: Linux (cron, claves SSH, servicios) · Windows (Run keys, tareas programadas)

---

## 📋 Procedimientos — [[MOC - Procedimientos]] ✓  (stub)

- ✓ [[Validación de tradecraft en laboratorio]]
- ○ Playbook: compromiso de AD · ○ pentest web · ○ enum&privesc Linux · ○ enum&privesc Windows

---

## Vistas paralelas (no en Inicio, se llegan desde las fases)

- Superficie: [[MOC - Explotación web]] · [[MOC - Active Directory]] (la cadena entera)
- Teoría/sustrato: [[MOC - Red]] · [[MOC - HTTP]]

## Prioridad sugerida

1. **★ Privesc local (Linux/Windows)** — el hueco más grande y el más desarrollado en la referencia.
2. **Pivoting y tunneling** — cierra movimiento lateral.
3. **Client-side initial access** — rama entera sin abrir en Explotación.
4. **Playbooks de Procedimientos** — convierte el stub en la fase de metodología.
5. Entidades pendientes (BloodHound, hashcat, John, nikto…) y servicios que faltan, por demanda.
