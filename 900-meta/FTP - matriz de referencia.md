---
tipo: meta
aliases:
  - FTP - matriz
  - ftp cheatsheet
tags:
  - meta/referencia
  - dominio/post-explotacion
---

# FTP - matriz de referencia

> [!info] Referencia pura, no un zettel
> Las cuatro herramientas —`ftp` (cliente nativo), `nxc ftp` (NetExec), `curl`, `lftp`— comparadas en grid por tarea. FTP como canal de transferencia: [[Transferencia de archivos - matriz de referencia]] y [[MOC - Transferencia de archivos]].

`HOST`, `u`, `p` son marcadores. `—` = la herramienta no hace esa tarea. En `ftp` y `lftp` los verbos van **dentro** de la sesión; en `nxc` y `curl` son de una línea.

## Autenticar y conectar

| Forma | ftp | nxc ftp | curl | lftp |
|---|---|---|---|---|
| Anónimo | `ftp HOST` → user `anonymous`, pass vacío | `nxc ftp HOST -u anonymous -p ''` | `curl ftp://HOST/` | `lftp -u anonymous, HOST` |
| Usuario/contraseña | `ftp HOST` (pide user y pass) | `nxc ftp HOST -u u -p p` | `curl -u u:p ftp://HOST/` | `lftp -u u,p HOST` |
| Puerto no estándar | `ftp HOST 2121` | `nxc ftp HOST --port 2121 -u u -p p` | `curl ftp://HOST:2121/` | `lftp -p 2121 -u u,p HOST` |

Anónimo clásico: usuario `anonymous`, contraseña cualquiera (o vacía). Es la primera prueba en todo FTP.

## Listar y navegar

| Tarea | ftp | nxc ftp | curl | lftp |
|---|---|---|---|---|
| Listar | `ls` / `dir` | `nxc ftp HOST -u u -p p --ls` | `curl -u u:p ftp://HOST/` | `ls` |
| Cambiar directorio | `cd dir` | — | `curl -u u:p ftp://HOST/dir/` | `cd dir` |
| Recorrer todo | manual | — | — | `find` / `du -a` |

## Descargar

| Tarea | ftp | nxc ftp | curl | lftp |
|---|---|---|---|---|
| Un archivo | `get archivo` | `nxc ftp HOST -u u -p p --get archivo` | `curl -u u:p ftp://HOST/archivo -O` | `get archivo` |
| Varios | `prompt OFF; mget *` | — | — | `mget *` |
| Recursivo | — | — | — (usar `wget -r ftp://u:p@HOST/`) | `mirror dir local` |

## Subir

| Tarea | ftp | nxc ftp | curl | lftp |
|---|---|---|---|---|
| Un archivo | `put local` | `nxc ftp HOST -u u -p p --put local remoto` | `curl -T local -u u:p ftp://HOST/` | `put local` |
| Recursivo | — | — | — | `mirror -R local dir` |

Si el server permite subir a un directorio que luego sirve por web, subir una webshell es RCE — el equivalente FTP del [[MOC - File upload]].

## Modo de transferencia — los dos errores clásicos

| Cuestión | Qué hacer |
|---|---|
| Binario vs ASCII | `binary` antes de `get`/`put`, o el ejecutable/imagen se corrompe. `ascii` solo para texto |
| Pasivo vs activo | `passive` (toggle en `ftp`); `curl` usa pasivo por defecto. El activo necesita que el server reabra conexión hacia vos — muere detrás de NAT/firewall |

## Descubrir y forzar

| Tarea | Comando |
|---|---|
| Anónimo masivo | `nxc ftp 10.0.0.0/24 -u anonymous -p ''` |
| Password spraying | `nxc ftp HOST -u usuarios.txt -p pass.txt --continue-on-success` |
| Scripts nmap | `nmap --script ftp-anon,ftp-bounce,ftp-syst -p 21 HOST` |

`ftp-bounce`: abuso del comando `PORT` para escanear terceros desde el server FTP — raro hoy, pero es la señal de un FTP viejo.

## Errores frecuentes

| Síntoma | Causa | Salida |
|---|---|---|
| `425 Can't open data connection` | modo activo bloqueado por NAT/firewall | `passive` |
| archivo descargado corrupto | transferencia en modo ASCII | `binary` antes de `get`/`put` |
| `530 Login incorrect` | credencial mala o anónimo deshabilitado | probar `anonymous`, verificar usuario |
| `500 OOPS` (vsftpd) | restricción del server (chroot/seccomp) | del lado del server, no del cliente |
| listado vacío pero conecta | modo pasivo negociado mal | alternar `passive` / `--ftp-pasv` |
