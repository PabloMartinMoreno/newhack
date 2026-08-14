---
tipo: tradecraft
clase: "[[CWE-862 - Missing Authorization]]"
eje: fase
implementacion: "Manipular los mensajes de un socket ya abierto, aprovechando que el servidor no revalida autorización ni sanea por mensaje"
opsec: limpio
telemetria: ["[[Log de auditoría de la aplicación]]"]
requisitos: [socket-propio-abierto, servidor-que-confía-en-los-mensajes]
coste: medio
alternativas: ["[[WebSocket - secuestro entre sitios]]", "[[Control de acceso - IDOR]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - message tampering
  - WebSocket injection
  - autorización por mensaje
tags:
  - dominio/web
---

# WebSocket - confianza del canal

## Cuándo lo elijo

Cuando ya hay un socket abierto —con la propia sesión, legítimamente— y el objetivo es manipular lo que viaja por él. Es la rama que no necesita secuestrar nada: se usa el cliente propio y se editan los mensajes que se mandan, apostando a que el servidor **confíe en el canal** una vez establecido.

Se elige después de [[WebSocket - secuestro entre sitios]] cuando aquella no aplica —el socket no se puede abrir de forma cruzada— pero el canal propio sí se puede abusar. Cubre tres abusos que comparten la misma causa: el servidor trata el socket abierto como confiable.

## Por qué funciona

El error de fondo es asumir que, una vez autenticado el handshake, todo lo que llega por el socket es confiable y bien formado. De ahí tres abusos:

- **Autorización no revalidada por mensaje.** El handshake autenticó al usuario, pero cada mensaje debería comprobar que la acción que pide le corresponde. Muchos servidores lo comprueban una vez y confían después: un mensaje `{"action":"deleteUser","id":"otro"}` o `{"getMessages":"chatAjeno"}` pasa porque el socket ya está autenticado. Es [[Control de acceso - IDOR]] y [[Control de acceso - escalada vertical]] sobre el canal, y por eso la `clase:` es `CWE-862`.
- **Inyección por mensaje.** Los datos de un mensaje llegan a un sink —una consulta, una plantilla, otro cliente— sin sanear. La clase entonces es la del sink: [[MOC - SQL injection]], [[MOC - Cross-site scripting]] si el mensaje se reenvía a otros clientes de un chat, [[MOC - NoSQL injection]]. GraphQL fue el precedente: el canal es el vector, la clase es la del sink. Los payloads salen del dominio correspondiente.
- **Manipulación de estructura.** Cambiar tipos y campos del mensaje —un precio, un rol, un identificador— que el servidor no valida porque confía en su propio cliente.

Lo que agrava las tres: **el WAF y las fuentes de tráfico casi nunca inspeccionan los mensajes de WebSocket**. Ven el handshake y después son ciegos. Un payload que un WAF bloquearía en una petición HTTP normal pasa sin problema si viaja por el socket. Es el mismo punto ciego de fuente que aprovecha [[Request smuggling - degradación de HTTP2]] con un WAF que solo mira HTTP/1.1, en otra capa.

## Cómo falla

Falla cuando el servidor **revalida la autorización en cada mensaje** —trata cada mensaje como una petición independiente, no como parte de una sesión confiable—. Es la mitigación correcta para el abuso de autorización.

Falla cuando los datos de los mensajes se parametrizan y sanean como cualquier entrada, cerrando la inyección.

Y falla cuando hay un esquema estricto que valida la estructura de cada mensaje, cortando la manipulación de tipos.

## Coste

Medio. Con el socket abierto, editar mensajes es directo —Burp intercepta y edita los mensajes de WebSocket, o se usa un cliente propio—. El trabajo es de reconocimiento: entender el protocolo de mensajes de la aplicación, qué acciones acepta, qué campos, qué llega a un sink. Ese protocolo no está documentado y hay que mapearlo observando el tráfico legítimo.

La inyección hereda el costo del dominio del sink. La autorización por mensaje es barata una vez que se conoce el formato: probar acciones y identificadores ajenos.

## Huella esperada

Silenciosa, y de ahí el `opsec: limpio` — es lo opuesto al secuestro, que se delata en el handshake.

Una vez abierto el socket, los mensajes van por el canal WebSocket, que **ninguna fuente de tráfico del vault inspecciona**: ni [[Log de acceso del servidor web]] ni [[Registro del WAF]] ven el contenido de los mensajes. El payload de inyección, la acción no autorizada, el campo manipulado — todos pasan sin dejar rastro en la telemetría de red.

La única señal está aguas abajo, en el efecto:

- El abuso de autorización deja la marca de [[MOC - Broken access control]] en [[Log de auditoría de la aplicación]] —acción o acceso fuera del rol— y lo cubren [[Acceso a un objeto de otro usuario]] y [[Cambio de privilegio fuera del flujo administrativo]], si el log registra a nivel de acción y no solo el handshake.
- La inyección que llega a un sink deja la huella de ese sink —un proceso hijo, una consulta anómala— aguas abajo del WebSocket.

Es el caso más claro del vault de un **canal no instrumentado**: la recomendación defensiva de mayor retorno no es una regla sino **registrar y auditar los mensajes de WebSocket** como se auditan las peticiones HTTP, sin lo cual el canal es un punto ciego total. Es [[Un log sin identidad es un historial, no una detección]] llevado al canal entero, y queda anotado en [[MOC - WebSocket]].
