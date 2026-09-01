---
tipo: teoria
habilita: ["[[Request smuggling - CL.TE y TE.CL]]", "[[Race - superación de límite]]", "[[Web cache - envenenamiento por entrada sin clave]]"]
relacionadas: ["[[HTTP - delimitación del cuerpo]]", "[[HTTP - el modelo de caché]]", "[[TCP - establecimiento de la conexión]]"]
aliases:
  - keep-alive
  - connection reuse
tags: []
---

# HTTP - el modelo de conexión

## Qué dice la especificación

HTTP/1.0 abría una conexión TCP por petición. HTTP/1.1 la deja abierta por defecto (`keep-alive`) y envía varias peticiones seguidas por el mismo socket, con las respuestas en el mismo orden. HTTP/2 va más lejos: multiplexa peticiones concurrentes en marcos sobre una sola conexión, sin orden garantizado entre ellas.

Debajo de todo eso hay una conexión TCP que costó un handshake y que no marca el final de ningún mensaje — ver [[TCP - establecimiento de la conexión]]. Ese es el motivo de que HTTP reutilice el socket y de que tenga que delimitar sus mensajes por su cuenta.

La consecuencia estructural: **la conexión es un recurso compartido y con estado, aunque el protocolo se describa como sin estado**. Lo que no tiene estado es el par petición/respuesta; el canal por el que viaja sí lo tiene, y es un canal que la cadena de intermediarios reutiliza entre usuarios distintos.

## Dónde el estándar deja lugar

- **Quién comparte la conexión.** Un proxy inverso suele mantener un pool de conexiones hacia el back y meter en ellas peticiones de usuarios distintos. La especificación no lo prohíbe y es lo que hace que un desync afecte a un tercero en vez de al atacante.
- **Cuándo se cierra.** `Connection: close`, timeouts de inactividad y límites de peticiones por conexión son configuración de cada implementación, no del protocolo.
- **Cuánta concurrencia real hay.** HTTP/2 permite enviar peticiones en marcos que caben en un mismo paquete TCP, colapsando la ventana de tiempo entre ellas por debajo de la variación de red.

## Qué habilita

- **Alcance del smuggling.** Que el sobrante de una petición se anteponga a la de otra persona depende de que la conexión al back se reutilice entre usuarios → [[Request smuggling - CL.TE y TE.CL]]. Sin pool compartido, el desync se envenena a sí mismo y deja de ser un ataque.
- **Concurrencia sin jitter de red.** La multiplexación de HTTP/2 es lo que convierte una race condition teórica en explotable: varias peticiones llegan efectivamente juntas → [[Race - superación de límite]].
- **Persistencia del efecto.** Una respuesta envenenada sobrevive a la conexión si además queda en una caché compartida → [[Web cache - envenenamiento por entrada sin clave]].

## Cómo se ve en la práctica

El modelo de conexión es casi invisible en el log de la aplicación, que registra peticiones sueltas y no el socket que las trajo. Es un punto ciego estructural, no una omisión de configuración: para correlacionar dos peticiones por conexión hace falta telemetría del frente, y el frente suele registrar la suya y descartar el resto.

## Fuente

RFC 9112 §9 (Connection Management), RFC 9113 §5 (Streams and Multiplexing).
