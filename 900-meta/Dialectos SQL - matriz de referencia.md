---
tipo: meta
aliases:
  - Dialectos SQL
tags:
  - meta/referencia
  - dominio/web
---

# Dialectos SQL - matriz de referencia

> [!info] Esto es referencia pura, no un zettel
> Se consulta, no se lee. No responde "cuándo elijo esto en vez de la alternativa" — por eso vive en `900-meta/` y no en `600-tradecraft/`. La decisión vive en [[MOC - SQL injection]]; la sintaxis vive acá.

## Concatenación y comentarios

| | MySQL | MSSQL | PostgreSQL | Oracle | SQLite |
|---|---|---|---|---|---|
| Concatenar | `CONCAT(a,b)` / `a b` | `a+b` | `a\|\|b` | `a\|\|b` | `a\|\|b` |
| Comentario | `-- ` `#` `/**/` | `-- ` `/**/` | `-- ` `/**/` | `-- ` `/**/` | `-- ` `/**/` |
| Consulta sin tabla | `SELECT 1` | `SELECT 1` | `SELECT 1` | `SELECT 1 FROM dual` | `SELECT 1` |
| Stacked queries | Depende del driver | Sí | Sí | No | Depende |

## Retardo temporal

| Motor | Primitiva |
|---|---|
| MySQL | `SLEEP(5)` · `BENCHMARK(...)` si `SLEEP` está filtrado |
| MSSQL | `WAITFOR DELAY '0:0:5'` |
| PostgreSQL | `pg_sleep(5)` |
| Oracle | `dbms_pipe.receive_message(('a'),5)` |
| SQLite | Pesado con `randomblob()` — no hay `sleep` nativo |

## Metadatos

| Motor | Versión | Tablas |
|---|---|---|
| MySQL | `@@version` | `information_schema.tables` |
| MSSQL | `@@version` | `information_schema.tables` |
| PostgreSQL | `version()` | `information_schema.tables` |
| Oracle | `banner FROM v$version` | `all_tables` |
| SQLite | `sqlite_version()` | `sqlite_master` |

## Lectura/escritura de archivos

| Motor | Lectura | Escritura |
|---|---|---|
| MySQL | `LOAD_FILE()` (limitado por `secure_file_priv`) | `INTO OUTFILE` |
| MSSQL | `OPENROWSET(BULK ...)` | `xp_cmdshell` (si está habilitado) |
| PostgreSQL | `pg_read_file()` (superusuario) | `COPY ... TO` / `COPY ... FROM PROGRAM` |
| Oracle | `UTL_FILE` | `UTL_FILE` |
| SQLite | `readfile()` (solo CLI) | `writefile()` (solo CLI) |

## Relacionadas

[[MOC - SQL injection]] · [[CWE-89 - SQL Injection]]
