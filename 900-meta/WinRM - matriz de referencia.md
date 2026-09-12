---
tipo: meta
aliases:
  - WinRM - matriz
  - winrm cheatsheet
  - evil-winrm - matriz
tags:
  - meta/referencia
  - dominio/red
---

# WinRM - matriz de referencia

> [!info] Referencia pura, no un zettel
> **Puertos: 5985/tcp** (HTTP) y **5986/tcp** (HTTPS). Windows Remote Management = PowerShell remoting. Da **shell directa** si la cuenta es admin local o está en *Remote Management Users*. Cliente de cabecera: `evil-winrm`. Muy ligado a AD. Criterio de recon en [[MOC - Reconocimiento de red]].

`HOST`, `u`, `p`, `DOM` son marcadores.

## Reconocimiento

| Comando | Qué da |
|---|---|
| `nmap -sV -p5985,5986 HOST` | Detecta el servicio WinRM |
| `nxc winrm HOST -u u -p p` | Valida el acceso — **`(Pwn3d!)` = shell disponible** |

`nxc winrm` es el filtro: si una credencial da `Pwn3d!`, esa cuenta abre `evil-winrm`.

## Conectar (evil-winrm)

| Caso | Comando |
|---|---|
| Con contraseña | `evil-winrm -i HOST -u u -p 'p'` |
| Pass-the-hash | `evil-winrm -i HOST -u u -H NTHASH` |
| Sobre HTTPS (5986) | `evil-winrm -i HOST -u u -p 'p' -S` |
| Kerberos | `evil-winrm -i HOST -u u -r DOM.LOCAL` |
| Cargar scripts/exes | `evil-winrm -i HOST -u u -p p -s /ruta/scripts -e /ruta/exes` |

WinRM acepta **PtH nativo** (es NTLM) — no necesita Restricted Admin como RDP. Es de las formas más limpias de usar un hash.

## Ejecutar sin abrir shell

| Comando | Qué hace |
|---|---|
| `nxc winrm HOST -u u -p p -x 'whoami /all'` | Comando único (cmd) |
| `nxc winrm HOST -u u -p p -X '$PSVersionTable'` | Comando en PowerShell |

## Fuerza bruta / spray

| Comando | Qué hace |
|---|---|
| `nxc winrm HOST -u users.txt -p pass.txt --continue-on-success` | Spray de credenciales |
| `nxc winrm HOST -u u -H hashes.txt` | Spray de hashes (PtH) |

## Dentro de evil-winrm

| Comando | Qué hace |
|---|---|
| `upload local remoto` · `download remoto local` | Transferencia integrada |
| `menu` | Lista las funciones cargadas (`-s`/`-e`) |
| `Invoke-Binary /ruta.exe` | Ejecuta un binario .NET en memoria |
| `Bypass-4MSI` | Intenta desactivar AMSI en la sesión |

## Configuraciones peligrosas

| Config | Por qué importa |
|---|---|
| Listener HTTP (5985) con `AllowUnencrypted=true` | Credenciales y comandos viajan en claro — capturables |
| `Basic` auth habilitada sin TLS | El usuario/contraseña va en base64 sniffable |
| Cuentas de más en *Remote Management Users* | Amplía quién obtiene shell remota |

## Errores frecuentes

| Síntoma | Causa | Salida |
|---|---|---|
| `WinRMAuthorizationError` | la cuenta no es admin ni está en Remote Management Users | usar otra cuenta; `nxc winrm` dice cuál da `Pwn3d!` |
| `could not resolve` con `-r` | falta el realm/DNS para Kerberos | apuntar el DNS al DC, usar el FQDN |
| conecta a 5986 y falla TLS | cert autofirmado | agregar `-S` (evil-winrm ignora el cert) |
| PtH rechazado | hash mal formado | pasar solo el NT (`-H NTHASH`), sin el `LM:` |
