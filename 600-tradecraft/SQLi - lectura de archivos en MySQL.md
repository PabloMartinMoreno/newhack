---
tipo: tradecraft
clase: "[[CWE-89 - SQL Injection]]"
eje: impacto
implementacion: "LOAD_FILE / INTO OUTFILE desde la inyección"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]"]
requisitos: [privilegio-FILE, secure_file_priv-permisivo]
coste: bajo
alternativas: ["[[SQLi - stacked queries en MSSQL]]"]
probado: 2026-08-06
contexto: [mysql8]
aliases:
  - SQLi file read MySQL
tags:
  - dominio/web
---

# SQLi - lectura de archivos en MySQL

## Cuándo lo elijo

Cuando ya tengo extracción y la cuenta de base de datos tiene privilegio `FILE` con `secure_file_priv` permisivo. Es un salto de eje: dejo de leer la base y paso a leer —y a veces escribir— el sistema de archivos del servidor.

El objetivo casi nunca es `/etc/passwd`: es la **config de la app** (`config.php`, `.env`), que suele traer credenciales que abren más que la propia base.

## Por qué funciona

`LOAD_FILE()` lee un archivo del disco como si fuera un valor de columna, así que sale por cualquier canal de extracción. `INTO OUTFILE`/`DUMPFILE` hace lo inverso: escribe el resultado a un archivo. Si el webroot es escribible, eso es una webshell y, por lo tanto, RCE.

## Cómo falla

- **`secure_file_priv` = NULL** — E/S de archivos deshabilitada por completo; no hay nada que hacer.
- **`secure_file_priv` = una ruta** — solo se lee/escribe ahí, casi nunca el webroot.
- **Sin privilegio `FILE`** — `LOAD_FILE` devuelve NULL en silencio.
- **Webroot no escribible** por el usuario de MySQL — se puede leer pero no plantar la shell.
- **AppArmor/SELinux** confinando a mysqld aunque los privilegios SQL alcancen.

## Coste

Bajo en peticiones. El requisito es lo caro: `FILE` + `secure_file_priv` permisivo es una mala configuración cada vez menos común. Se confirma en una petición (ver la sección de privilegios de [[SQLi UNION - matriz de referencia]]) antes de invertir tiempo.

## Huella esperada

- `LOAD_FILE`/`INTO OUTFILE` legibles en el [[Log de acceso del servidor web]].
- Un archivo nuevo en el webroot (la webshell) — artefacto en disco.

Payloads en [[SQLi impacto - matriz de referencia]] § Lectura/Escritura de archivos.
