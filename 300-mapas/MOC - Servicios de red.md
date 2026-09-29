---
tipo: moc
dominio: red
aliases:
  - Servicios
  - Servicios de red
  - Enumeración de servicios
  - puertos y servicios
tags:
  - dominio/red
---

# MOC - Servicios de red

> [!abstract] El puente entre el escaneo y la enumeración
> El escaneo ([[MOC - Reconocimiento de red]]) devuelve puertos abiertos e identifica el servicio. Acá vive **qué hacer con cada servicio**: puerto → protocolo → su matriz de enumeración. Es la tabla puerto→servicio que [[Estructura del vault]] dice que **no** debe vivir en la matriz de un escáner —sirve sin importar quién encontró el puerto—, así que tiene casa propia. No va en [[Inicio]]: se llega desde el reconocimiento.

No es fase ni árbol de ataque: es un **directorio**. La decisión de qué servicio priorizar es simple y se dice una vez: **primero los que dan acceso sin credencial** (login anónimo, sesión nula, community pública), que son el fruto más bajo; después los que piden material que todavía no tenés.

## Por dónde empezar
```
¿Qué servicio ataco primero de los que el escaneo encontró?
├─ ¿Alguno permite acceso anónimo / nulo?
│  └─ Sí → ahí primero: FTP anónimo · SMB sesión nula · NFS export abierto · SNMP community 'public' · rsync sin auth
└─ No → los que piden credencial, empezando por los que más rinden si cae una:
        bases de datos (RCE directo), SMB/WinRM/WMI (exec), SSH/RDP (sesión)
```
## Compartición de archivos

| Servicio | Puerto | Qué se saca | Matriz |
|---|---|---|---|
| FTP | 21 | login anónimo, subir/bajar, modo binario | [[FTP - matriz de referencia]] |
| SMB | 139 · 445 | sesión nula, shares, usuarios (RID cycling), archivos, exec | [[SMB - matriz de referencia]] |
| NFS | 2049 | montar exports, UID spoofing, `no_root_squash` → root | [[NFS - matriz de referencia]] |
| rsync | 873 | listar módulos, bajar/subir (anónimo o `rsyncd.secrets`) | [[rsync - matriz de referencia]] |


## Correo

| Servicio | Puerto | Qué se saca | Matriz |
|---|---|---|---|
| SMTP | 25 · 465 · 587 | enum de usuarios (VRFY/EXPN/RCPT), open relay, spoofing con `swaks` | [[SMTP - matriz de referencia]] |
| IMAP / POP3 | 143 · 110 · 993 · 995 | leer buzones, `SEARCH` de IMAP, TLS, fuerza bruta | [[IMAP y POP3 - matriz de referencia]] |


## Bases de datos

| Servicio | Puerto | Qué se saca | Matriz |
|---|---|---|---|
| MySQL | 3306 | `LOAD_FILE`/`OUTFILE` (webshell → RCE), credenciales en config | [[MySQL - matriz de referencia]] |
| MSSQL | 1433 | `xp_cmdshell` (RCE), impersonación, linked servers, captura/relay de NetNTLM | [[MSSQL - matriz de referencia]] |
| Oracle TNS | 1521 | adivinar el SID, `odat` para credenciales y RCE (utlfile/scheduler) | [[Oracle TNS - matriz de referencia]] |


## Acceso y administración remota

| Servicio | Puerto | Qué se saca | Matriz |
|---|---|---|---|
| SSH | 22 | métodos de auth, brute, clave privada (+ crack), túneles/pivoting, `sshd_config` | [[SSH - matriz de referencia]] |
| RDP | 3389 | PtH con Restricted Admin, BlueKeep, robo de sesión con `tscon` | [[RDP - matriz de referencia]] · cliente en [[xfreerdp - matriz de referencia]] |
| WinRM | 5985 · 5986 | `evil-winrm`, PtH nativo, `nxc winrm` (Pwn3d!) | [[WinRM - matriz de referencia]] |
| WMI | 135 | `wmiexec` (exec sin servicio), WQL, persistencia fileless por eventos | [[WMI - matriz de referencia]] |
| R-services | 512 – 514 | rlogin/rsh/rexec: confianza por `.rhosts`, acceso sin contraseña | [[R-services - matriz de referencia]] |


## Nombres y directorio

| Servicio | Puerto | Qué se saca | Matriz |
|---|---|---|---|
| DNS | 53 | registros (incluido `SRV` para ubicar el DC), transferencia de zona (AXFR), brute de subdominios | [[DNS - matriz de referencia]] |
| LDAP | 389 · 636 | el directorio como base de datos → enumeración del dominio | [[MOC - AD enumeración]] |


## Gestión de hardware y red

| Servicio | Puerto | Qué se saca | Matriz |
|---|---|---|---|
| SNMP | 161/udp | community brute, enum por OID (fuga de credenciales en la línea de comando), escritura con RW | [[SNMP - matriz de referencia]] |
| IPMI | 623/udp | BMC (iDRAC/iLO/Supermicro): volcado de hash RAKP, cipher zero, credenciales por defecto | [[IPMI - matriz de referencia]] |


## Relación con otras fases y dominios

- **Antes:** [[MOC - Reconocimiento de red]] identifica el servicio y la versión; esta nota es el paso siguiente. Ambas se llegan desde [[MOC - Reconocimiento]].
- **Hacia AD:** SMB, WMI, WinRM, RDP y LDAP son también la puerta de entrada de la cadena de Active Directory — enumeración en [[MOC - AD enumeración]], movimiento lateral en [[MOC - AD movimiento lateral]].
- **Hacia RCE:** MySQL/MSSQL/Oracle desembocan en ejecución; de ahí a [[MOC - Post-explotación]].

## Huecos conocidos

- [x] Diecisiete servicios con matriz, por categoría, con puerto y qué rinde cada uno
- [ ] Sin matriz todavía: Kerberos (88), Redis (6379), MongoDB (27017), Telnet (23), VNC (5900), Docker API (2375). Entran acá cuando se escriban

