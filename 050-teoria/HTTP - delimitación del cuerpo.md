---
tipo: teoria
habilita: ["[[Request smuggling - CL.TE y TE.CL]]", "[[Request smuggling - desincronización del cliente]]", "[[Request smuggling - degradación de HTTP2]]", "[[CWE-444 - Inconsistent Interpretation of HTTP Requests]]"]
relacionadas: ["[[HTTP - el modelo de conexión]]"]
aliases:
  - message body framing
  - Content-Length vs Transfer-Encoding
tags: []
---

# HTTP - delimitación del cuerpo

## Qué dice la especificación

HTTP/1.1 es un protocolo de texto sobre un flujo de bytes sin marcas de fin. El receptor tiene que **calcular** dónde termina el cuerpo de un mensaje, y la especificación le da tres formas de hacerlo, en este orden de precedencia:

1. `Transfer-Encoding: chunked` — el cuerpo llega en trozos, cada uno precedido por su tamaño en hexadecimal, y termina con un trozo de tamaño `0`.
2. `Content-Length: N` — el cuerpo son exactamente los `N` bytes siguientes.
3. Ninguno de los dos — el cuerpo termina cuando se cierra la conexión.

`Transfer-Encoding` **gana** sobre `Content-Length` si están los dos. La especificación además ordena rechazar el mensaje si aparecen ambos, precisamente porque previó el problema.

## Dónde el estándar deja lugar

En que "rechazar" es una instrucción que cada implementación cumple a su manera, y en la cadena hay más de una implementación.

- Un servidor que no implementa `chunked` ignora `Transfer-Encoding` y usa `Content-Length`, invirtiendo la precedencia.
- `Transfer-Encoding: xchunked`, con espacio antes de los dos puntos, con tabulación, duplicado, o en una segunda línea plegada — cada parser decide distinto si eso todavía es `chunked`.
- Un endpoint que no lee cuerpos ignora el `Content-Length` entero y trata los bytes siguientes como una petición nueva.

Ninguna de esas lecturas viola la especificación de forma evidente. **Todas son válidas por separado; el problema aparece cuando dos servidores en serie eligen distinto.**

## Qué habilita

La delimitación es la pieza sobre la que se apoya el dominio entero de smuggling. Sin desacuerdo sobre dónde termina el cuerpo no hay sobrante que anteponer a la petición siguiente:

- Precedencia invertida entre frente y back → [[Request smuggling - CL.TE y TE.CL]].
- Un solo servidor que ignora el cuerpo (`CL.0`) → [[Request smuggling - desincronización del cliente]].
- HTTP/2 tiene largo explícito en el marco, así que no sufre esto; **la degradación a HTTP/1.1 lo reintroduce** al reconstruir cabeceras de largo desde datos que el frente no normalizó → [[Request smuggling - degradación de HTTP2]].

La consecuencia que ordena el resto: **el ataque no manipula un dato de la aplicación, manipula el límite entre dos mensajes**. Por eso afecta a otros usuarios y por eso la mitigación es de arquitectura.

## Cómo se ve en la práctica

Un mensaje con las dos cabeceras de largo se ve trivial en un log y es la firma más directa del dominio — pero sólo lo ve quien registre las cabeceras crudas, y el frente normalmente las normaliza antes de que el back las escriba. El artefacto observable no es la petición: es la **respuesta desplazada** que recibe el usuario siguiente en la misma conexión.

## Fuente

RFC 9112 §6 (Message Body Length). Consecuencias ofensivas destiladas en [[MOC - Request smuggling]].
