---
tipo: moc
dominio: web
aliases:
  - MOC WebSocket
  - seguridad de WebSocket
tags:
  - dominio/web
---

# MOC - WebSocket

> [!abstract] Nota de referencia paraguas
> Detectar el socket y probar el origen, en [[WebSocket - matriz de reconocimiento]]. Acá vive **la decisión**.

WebSocket es una tecnología de transporte, no una vulnerabilidad, así que —como [[MOC - GraphQL]]— cada nota cuelga de su clase real. Lo que lo hace un dominio y no una nota suelta es que abre **dos superficies que el resto del vault no cubre**: el handshake, que es un CSRF con defensas propias, y el canal de mensajes, que casi ninguna fuente inspecciona.

| Fase | `clase:` | Nota |
|---|---|---|
| Secuestrar el handshake | `CWE-1385` | [[WebSocket - secuestro entre sitios]] |
| Abusar el canal ya abierto | `CWE-862` | [[WebSocket - confianza del canal]] |
| Inyección por mensaje | la del sink | matriz — el canal es el vector |

`CWE-1385` es nueva —la falta de validación de origen del handshake— y es la única específica del dominio. La confianza del canal reusa `CWE-862`, y la inyección por mensaje **no genera nota**: la clase es la del sink, el WebSocket solo la transporta, mismo criterio que la inyección por argumento en [[MOC - GraphQL]] y la subida en [[File upload - XXE por archivo]].

| Eje | Valores |
|---|---|
| Superficie | el handshake · el canal de mensajes |
| Fase | secuestro (cruzado) · abuso (canal propio) |
| Impacto | lectura/escritura autenticada · autz por mensaje · inyección · XSS reenviado |

**La superficie es el eje**: el handshake y el canal son dos problemas distintos con defensas y telemetría distintas. El handshake se ataca de forma cruzada y se ve; el canal se abusa desde adentro y es ciego.

## Árbol de decisión — handshake o canal

```
¿Hay WebSocket?  → [[WebSocket - matriz de reconocimiento]] § 1
└─ Sí — ¿el socket se autentica por cookie?
   │
   ├─ Sí — ¿el handshake valida el Origin?
   │  ├─ No → [[WebSocket - secuestro entre sitios]]   ← PRIMERO, canal bidireccional autenticado
   │  └─ Sí, laxo → bypass de cadena → misma nota, vía [[CORS bypass de origen - matriz de referencia]]
   │
   └─ Con el socket abierto (propio o secuestrado), ¿el servidor confía en los mensajes?
      → [[WebSocket - confianza del canal]]
         ├─ ¿Revalida autz por mensaje?      No → IDOR / escalada por el canal
         ├─ ¿Los datos llegan a un sink?      → inyección, la clase del sink
         └─ ¿Valida tipos y estructura?       No → manipulación / mass assignment
```

Tres cosas que este orden codifica:

**El secuestro va primero porque es el de mayor impacto y el más específico.** Un handshake sin validación de origen da un canal bidireccional autenticado con la sesión de la víctima —lectura y escritura, no CSRF a ciegas—. Es la prueba de apertura y la que define el dominio.

**El secuestro se ve; el abuso del canal no.** El handshake es una petición HTTP con `Origin`, así que se detecta. Los mensajes van por el socket, que las fuentes no inspeccionan. Esa asimetría de visibilidad es la que ordena la cara azul y la que hace del canal el punto ciego del dominio.

**La inyección por mensaje es un vector, no una clase.** Un payload en un mensaje llega a un sink; la clase es la de ese sink. El agravante propio de WebSocket es que **el WAF es ciego al mensaje**: lo que bloquearía en HTTP pasa por el socket.

## Árbol de decisión — qué consigo por superficie

```
¿Qué superficie caí?
├─ Handshake sin validar (CSWSH)
│  └─ canal bidireccional con la sesión de la víctima
│     ├─ leer sus mensajes/datos privados → fuga
│     └─ enviar acciones en su nombre → como [[MOC - CORS]] pero lectura+escritura
├─ Canal — autz no revalidada
│  └─ acceso o acción ajena → [[MOC - Broken access control]]
├─ Canal — inyección
│  └─ la clase del sink: SQLi, NoSQL, command, y el XSS reenviado a otros clientes
└─ Canal — XSS entrante en el cliente
      → el onmessage inserta sin sanear → [[XSS - DOM-based]] con fuente WebSocket
```

## Cheatsheets — entrada directa

| Matriz | Cubre |
|---|---|
| [[WebSocket - matriz de reconocimiento]] | Detectar el socket, anatomía del handshake, probar el origen, PoC de CSWSH, herramientas, mapear el protocolo |
| [[WebSocket - matriz de manipulación]] | Autz por mensaje, inyección por sink, manipulación de estructura, repetición, XSS entrante |

## Orden de aprendizaje

1. [[CWE-1385 - Missing Origin Validation in WebSockets]] — por qué el handshake es un CSRF con defensas propias
2. [[WebSocket - matriz de reconocimiento]] — detectar y probar el origen va primero
3. [[WebSocket - secuestro entre sitios]] — la superficie del handshake, el impacto mayor
4. [[WebSocket - confianza del canal]] — la superficie del canal, y por qué es ciega

## Relación con otros dominios

- [[MOC - CSRF]] — el secuestro es CSRF sobre el handshake, y era el hueco declarado en aquel MOC: no hay control previo de CORS ni `SameSite` que valga sobre el handshake. Comparte familia (`CWE-352` → `CWE-1385`) pero el impacto es mayor porque el canal queda bidireccional.
- [[MOC - CORS]] — el impacto real —leer respuestas autenticadas de forma cruzada— es el de CORS, no el del CSRF ciego. Y el bypass de un `Origin` laxo reusa [[CORS bypass de origen - matriz de referencia]]: comparar un origen falla igual en las dos capas.
- [[MOC - GraphQL]] — el mismo patrón "el canal es un vector, la clase es del sink" para la inyección por mensaje, y el mismo problema de una capa que las fuentes no instrumentan bien.
- [[MOC - Broken access control]] — la autz no revalidada por mensaje es `CWE-862` sobre el canal; el método de prueba es [[Control de acceso - matriz de pruebas]].
- [[MOC - Race conditions]] — los mensajes de un socket llegan rápido y sin jitter, así que la repetición de un mensaje con efecto se cruza con las carreras.

## Cara azul

| Variante | Telemetría | Firma |
|---|---|---|
| Secuestro (CSWSH) | [[Log de acceso del servidor web]] · [[Registro del WAF]] | Handshake `Upgrade: websocket` con `Origin` externo |
| Confianza del canal — autz | [[Log de auditoría de la aplicación]] | Acción o acceso ajeno — si se audita a nivel de mensaje |
| Confianza del canal — inyección | — | El WAF no ve los mensajes; solo el efecto aguas abajo |

La observación que parte en dos la cara azul, y es la de visibilidad:

**El handshake se ve, el canal es ciego.** El secuestro deja una firma escribible y de fuente disponible: un handshake de WebSocket con `Origin` fuera de la lista blanca no ocurre en tráfico legítimo, y el `Origin` del handshake se registra como en cualquier petición HTTP. Es análogo a la firma de [[CORS - reflejo del origen con credenciales]] y, como aquella, candidato a detección propia — de los pocos huecos recientes que es de trabajo y no de fuente.

El canal, en cambio, es el punto ciego más completo del vault. Una vez abierto el socket, **ninguna fuente de tráfico inspecciona los mensajes**: ni el log de acceso ni el WAF ven la acción no autorizada, el payload de inyección o el precio manipulado. La inyección solo se detecta por su efecto aguas abajo —un proceso hijo, una consulta anómala—; el abuso de autz solo por el invariante en el log de auditoría, si se audita a nivel de mensaje. La recomendación de mayor retorno no es una regla sino **auditar los mensajes de WebSocket como se auditan las peticiones HTTP**. Es [[Un log sin identidad es un historial, no una detección]] llevado a un canal entero, no a un campo.

Décimo quinto dominio cerrado sin detección nueva. Un candidato escribible: la firma del `Origin` externo en el handshake.

## Huecos conocidos

- [x] Las dos superficies — handshake y canal
- [x] CSWSH con su CWE propia, y la inyección como vector
- [x] Reconocimiento y manipulación — dos matrices
- [x] Cara azul del handshake — firma escribible sobre el `Origin`
- [ ] **El canal de mensajes no se instrumenta.** Ninguna fuente ve los mensajes de un socket abierto. La recomendación es auditarlos como peticiones HTTP; sin eso, punto ciego total. Hueco de fuente, el más amplio del vault
- [ ] `socket.io` y otras bibliotecas con framing y reconexión propios — el origen se prueba igual, el protocolo de mensajes cambia
- [ ] WebSocket sobre HTTP/2 y WebTransport sobre HTTP/3 como superficie más nueva
