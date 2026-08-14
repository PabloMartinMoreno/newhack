---
tipo: tecnica
taxonomia: cwe
identificador: CWE-1385
wstg: WSTG-CLNT-10
tacticas: []
aliases:
  - CWE-1385
  - CSWSH
  - cross-site websocket hijacking
  - secuestro de WebSocket entre sitios
tags:
  - dominio/web
---

# CWE-1385 - Missing Origin Validation in WebSockets

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - WebSocket]]; la prueba, en [[WebSocket - secuestro entre sitios]]; el reconocimiento, en [[WebSocket - matriz de reconocimiento]].

## Qué es

Un WebSocket se abre con una petición HTTP normal —el `handshake`, un `GET` con `Upgrade: websocket`— y esa petición **lleva las cookies** de la víctima como cualquier otra. Si el servidor no valida el `Origin` de ese handshake, una página del atacante puede abrir un WebSocket contra el objetivo con la sesión de la víctima, y a partir de ahí **leer y enviar mensajes** en su nombre.

Es CSRF aplicado al handshake de WebSocket, con un agravante: una vez abierto el socket, el atacante no actúa a ciegas como en el CSRF clásico —**ve las respuestas**—, porque el mismo origen que abrió el socket lee lo que llega por él.

## Por qué es su propia clase y no solo CSRF

Comparte familia con [[CWE-352 - Cross-Site Request Forgery]] —falta una prueba de que la petición nació en la propia aplicación— pero tiene una CWE propia porque las defensas que cierran el CSRF clásico **no aplican al handshake**:

- **`SameSite` no lo cubre bien.** El handshake es una petición de subida iniciada por script, y su tratamiento respecto de `SameSite` es distinto del de un formulario; durante años fue una vía viva justamente por eso.
- **El token anti-CSRF rara vez está** en el handshake, porque no es un formulario y el que integra no piensa en protegerlo.
- **El control previo de CORS no aplica** al handshake de WebSocket de la forma en que aplica a `fetch`.

Por eso la única defensa real y específica es **validar el `Origin` del handshake** contra una lista blanca, y su ausencia es exactamente lo que nombra la CWE.

## Por qué el impacto supera al del CSRF

En el CSRF clásico se manda una petición a ciegas. Acá, con el socket abierto en el origen del atacante, se establece un **canal bidireccional autenticado**: se leen todos los mensajes que el servidor manda —datos privados, notificaciones, respuestas a consultas— y se envían mensajes en nombre de la víctima. Es lectura y escritura, no solo escritura ciega, y por eso se acerca más a [[MOC - CORS]] en impacto que al CSRF que le da la familia.

## Por qué la mitigación es validar el origen

- **Validar `Origin`** del handshake contra una lista blanca de orígenes permitidos. Es la defensa específica.
- **Token anti-CSRF** en el handshake, verificado del lado del servidor.
- No depender de la sesión por cookie sola para autenticar el socket: usar un token de sesión que el script legítimo conozca y el del atacante no.

## Referencias canónicas

- [CWE-1385](https://cwe.mitre.org/data/definitions/1385.html)
- [CWE-352](https://cwe.mitre.org/data/definitions/352.html) — CSRF, la familia
- WSTG-CLNT-10
- RFC 6455 § 10.2 — Origin Considerations
