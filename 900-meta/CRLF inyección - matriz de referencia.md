---
tipo: meta
aliases:
  - codificaciones CRLF
  - CRLF encodings
  - CRLF bypass
tags:
  - meta/referencia
  - dominio/web
---

# CRLF inyección - matriz de referencia

> [!info] Referencia pura, no un zettel
> Cómo hacer que el `\r\n` pase el filtro y dónde ubicarlo. Los payloads de impacto están en [[CRLF impacto - matriz de referencia]]; el criterio, en [[MOC - CRLF injection]].

## 0. El átomo y sus codificaciones

`\r` = retorno de carro = `%0d` = ``
`\n` = salto de línea = `%0a` = `
`
`\r\n` = `%0d%0a` — la secuencia que separa cabeceras.

## 1. Confirmar la inyección

Inyectar una cabecera canario en un parámetro que se refleje en una cabecera de respuesta:

```
?param=x%0d%0aX-Inyectado:%20si
```

Si `X-Inyectado: si` aparece en la respuesta, hay CRLF injection. Empezar por los parámetros de redirección (`url`, `next`, `redirect`) — son los que más caen.

## 2. Codificaciones, por si el filtro bloquea `%0d%0a`

Una por línea, según dónde se decodifique la entrada:

`%0d%0a`          estándar
`%0a`             solo salto de línea — muchos servidores lo aceptan
`%0d`             solo retorno — a veces basta
`%0d%0a%20`       con espacio, evade algunos filtros
`%23%0d%0a`       con `#` previo
`%25%30%64%25%30%61`  doble codificación (%0d%0a codificado otra vez)
`%E5%98%8D%E5%98%8A`  unicode que algunos parsers normalizan a CRLF
`%u000d%u000a`    codificación unicode estilo IIS
`\r\n`            literal, si la entrada no se codifica
`%0d%0a` en distintos casos según el punto de decodificación

La doble codificación rinde cuando hay dos capas —un proxy y la app— que decodifican en momentos distintos, igual que en [[Path traversal - matriz de referencia]].

## 3. Dónde cae la entrada

| La entrada se refleja en | Vector |
|---|---|
| `Location` de una redirección | El más común: `?url=`, `?next=` |
| `Set-Cookie` construido con input | Un parámetro que fija preferencia/idioma |
| Una cabecera de rastreo o de idioma | `Accept-Language`, cabeceras propias |
| El cuerpo (no cabecera) | No es CRLF, es XSS directo — otra rama |

Confirmar que cae en una **cabecera**, no en el cuerpo: si cae en el cuerpo, es XSS y no hace falta CRLF.

## 4. Bypass de filtros

Cuando filtra `\r` o `\n`:

- Probar `%0a` solo — muchos filtros bloquean `%0d` y dejan `%0a`, y el servidor acepta el salto solo.
- Doble codificación si hay una capa que decodifica dos veces.
- Unicode `%E5%98%8D` — Firefox/algunos parsers lo normalizan a `\r`.
- Inyectar en un punto donde la entrada se decodifica **después** del filtro.

Cuando filtra el nombre de la cabecera:
- Espacios y tabulaciones en el nombre inyectado.
- Envolver el valor.

## 5. Ubicar el corte

En `Location: /ruta?param=INPUT`, el `INPUT` cae **después** del destino, así que se controla lo que sigue. En `Location: INPUT`, se controla el destino entero —redirección abierta directa, ver [[CWE-601 - URL Redirection to Untrusted Site]]—.

Saber qué parte de la cabecera se controla decide si se puede solo agregar cabeceras (input al final) o también manipular el destino (input al principio).

## 6. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| El canario no aparece en la respuesta | No se refleja en cabecera, o se filtra. Probar codificaciones |
| `%0d%0a` se refleja literal en el cuerpo | Cae en el cuerpo: es XSS, no CRLF |
| `%0d` bloqueado | Probar `%0a` solo |
| El filtro quita el salto de línea | Doble codificación, o unicode |
| La cabecera inyectada aparece pero rota | El servidor la re-escapa parcialmente; ajustar |
| Funciona en un parámetro y no en otro | Solo uno cae en una cabecera. Es lo normal |

## Relacionadas

[[MOC - CRLF injection]] · [[CRLF impacto - matriz de referencia]] · [[Path traversal - matriz de referencia]] · [[CWE-601 - URL Redirection to Untrusted Site]]
