---
tipo: moc
dominio: web
aliases:
  - MOC request smuggling
tags:
  - dominio/web
---

# MOC - Request smuggling

> [!abstract] Nota de referencia paraguas
> La definición vive en [[CWE-444 - Inconsistent Interpretation of HTTP Requests]]. Detectar la desincronización, en [[Request smuggling - matriz de sondeo]]. Acá vive **la decisión**.

Este dominio es distinto de todos los anteriores en una cosa que ordena todo lo demás: **no ataca la aplicación, ataca la cadena de servidores que hay delante**. No hay entrada que la aplicación evalúe mal; hay dos servidores que miden la misma petición distinto. Por eso afecta a otros usuarios, saltea los controles del frente, y su mitigación es de arquitectura y no de código.

| Eje | Valores |
|---|---|
| Primitiva de desincronización | CL.TE · TE.CL · TE.TE · H2.CL · H2.TE · CL.0 |
| Dónde vive la ambigüedad | HTTP/1.1 · degradación de HTTP/2 · un solo servidor |
| Explotación | saltar el frente · capturar peticiones · envenenar la cola · caché → matriz |
| Alcance | otros usuarios · persistente vía caché |

**La primitiva de desincronización es el eje raíz**, agrupada por dónde vive la ambigüedad. Es lo que hay que elegir y lo que decide todo el trabajo de construcción. La explotación —qué se hace con un desync que funciona— va a matriz, porque es ortogonal a cómo se logró: una vez que hay sobrante controlado, capturar una petición o envenenar la caché se hace igual sea cual sea la primitiva.

## Árbol de decisión — cómo desincronizo

```
¿Cómo habla el cliente con el frente?
├─ HTTP/2, y hay un CDN detrás
│  └─ ¿El frente degrada a HTTP/1.1 y confía en las cabeceras internas?
│     └─ [[Request smuggling - degradación de HTTP2]]   ← PROBAR PRIMERO hoy
│        rinde más: el frente se cree seguro por usar H2 y no normaliza
└─ HTTP/1.1
   ├─ ¿Hay frente y back distintos? (CDN, WAF, proxy inverso)
   │  ├─ Sí → pruebas de tiempo → [[Request smuggling - CL.TE y TE.CL]]
   │  │       si los dos entienden TE, ofuscar (TE.TE)
   │  └─ No → ¿algún endpoint ignora el Content-Length?
   │          └─ CL.0 → [[Request smuggling - desincronización del cliente]]
   └─ ¿Explotable solo desde el navegador de una víctima?
      └─ desync del lado del cliente → misma nota
```

Tres cosas que este orden codifica:

**La degradación de HTTP/2 va primero hoy.** El HTTP/1.1 clásico está cada vez más mitigado, pero la degradación reintroduce el problema en cadenas que se creen seguras por hablar HTTP/2. Es la rama de mayor rendimiento actual, al revés de lo que sugeriría la antigüedad de las técnicas.

**La detección es siempre por tiempo primero.** Las pruebas de confirmación por diferencia de respuesta pueden envenenar la petición de un usuario real. Las de tiempo no dañan a nadie. El orden no es preferencia: es seguridad operativa, y está en un callout de [[Request smuggling - matriz de sondeo]].

**CL.0 y el desync del cliente son la rama sin proxy.** No necesitan dos servidores: un solo servidor que ignora el cuerpo alcanza, y el ataque se dispara desde el navegador de la víctima. Es la variante nueva y la que acerca el dominio a los ataques del lado del cliente.

## Árbol de decisión — tengo un desync, ¿qué consigo?

```
El sobrante controlado se antepone a la siguiente petición
├─ ¿Hay un control solo en el frente? (WAF, autorización en el proxy)
│     → escondé la petición prohibida en el sobrante → saltás el control
├─ ¿Hay un endpoint que almacene y refleje? (comentario, perfil)
│     → capturá la petición de la víctima con su cookie → robo de sesión sin XSS
├─ ¿Podés dejar la cola de respuestas desfasada?
│     → cada usuario recibe la respuesta del anterior → fuga masiva
└─ ¿Hay caché delante?
      → envenenás un recurso → persistente y para todos → [[MOC - Cross-site scripting]]
```

Este segundo árbol es lo que separa un smuggling "confirmado" de uno "grave". La primitiva es media victoria; el impacto va de saltar un control —serio— a envenenar la caché para todos los usuarios —crítico y persistente—. La matriz de explotación los cubre en orden.

## Cheatsheets — entrada directa a las construcciones

| Matriz | Cubre |
|---|---|
| [[Request smuggling - matriz de sondeo]] | Detección por tiempo, confirmación segura, ofuscación de TE, degradación H2, encontrar CL.0 |
| [[Request smuggling - matriz de explotación]] | Saltar el frente, capturar peticiones, envenenar la cola, caché, cadena del lado del cliente |

## Orden de aprendizaje

1. [[CWE-444 - Inconsistent Interpretation of HTTP Requests]] — por qué dos servidores miden la misma petición distinto
2. [[Request smuggling - matriz de sondeo]] — detectar sin romper el tráfico de otros, que acá es una regla de seguridad
3. [[Request smuggling - CL.TE y TE.CL]] — el mecanismo clásico, donde se entiende la idea
4. [[Request smuggling - degradación de HTTP2]] — la variante que rinde hoy
5. [[Request smuggling - desincronización del cliente]] — sin proxy, disparado desde el navegador
6. [[Request smuggling - matriz de explotación]] — qué se hace con el desync, que es donde está el impacto

El punto 2 va antes que las técnicas y no es negociable: es el único dominio del vault donde sondear mal **daña a usuarios reales**, así que la matriz de sondeo con su advertencia se lee antes de tocar nada.

## Relación con otros dominios

- [[MOC - Broken access control]] — saltar el control del frente es control de acceso por otra vía: la autorización estaba en el proxy y el smuggling la esquiva. Cuando el control está solo adelante, este dominio lo anula entero.
- [[MOC - Cross-site scripting]] — el envenenamiento de caché entrega un XSS reflejado a todas las víctimas de una, y la desincronización del cliente logra XSS sin sink de HTML. El smuggling es un vehículo de entrega para XSS que las defensas de XSS no ven.
- [[MOC - Gestión de sesión]] — la captura de peticiones roba la cookie de la víctima sin tocar el navegador ni necesitar CORS. Es otra vía al mismo robo de sesión.
- **Web cache poisoning** — el vecino directo, todavía sin modelar. El smuggling es una de las formas de envenenar la caché; hay otras que no lo necesitan.

## Cara azul

| Variante | Telemetría | Firma |
|---|---|---|
| CL.TE / TE.CL / TE.TE | [[Registro del WAF]] | Petición con `Content-Length` **y** `Transfer-Encoding`, o TE ofuscado |
| Todas las clásicas | [[Log de acceso del servidor web]] | **Desajuste de conteo**: el frente registró N peticiones, el back N+1 |
| Degradación de HTTP/2 | [[Registro del WAF]] | Solo si el WAF inspecciona HTTP/2 — muchos son ciegos |
| CL.0 | [[Log de acceso del servidor web]] | Cuerpo sobre un endpoint que no debería recibirlo |
| Desync del cliente | — | Llega con la sesión de la víctima; casi sin huella |

Tres observaciones que este dominio deja:

**La firma de cabeceras rinde, como en prototype pollution y OGNL.** Una petición con `Content-Length` y `Transfer-Encoding` a la vez viola la especificación y no existe en tráfico legítimo. La cubre [[Registro del WAF]], que ve las cabeceras que [[Log de acceso del servidor web]] no registra. Es el tercer dominio donde detectar por firma paga, por la misma razón: la anomalía no tiene forma legítima.

**El hueco propio del dominio es de correlación entre dos capas.** La señal más fuerte —**el frente contó una cantidad de peticiones y el back contó otra en la misma conexión**— exige unir los registros de dos servidores por identificador de conexión, que ninguna fuente del vault modela. No es hueco de contenido: es que la detección natural es una correlación entre capas, y el esquema de `deteccion` asume una fuente. Es el caso más claro de `forma: correlacion` sobre dos telemetrías distintas, y queda anotado.

**Un WAF que solo entiende HTTP/1.1 es ciego a la degradación de HTTP/2.** Es un punto ciego de fuente, no de regla: la cadena habla H2 al cliente, el WAF mira H1, y la rama que más rinde hoy pasa por debajo. La recomendación de mayor retorno es que el WAF inspeccione el mismo protocolo que habla el frente.

Ninguna detección propia hizo falta escribir, pero por primera vez en la racha no es porque otra regla lo cubra bien: es porque **la detección natural del dominio —el desajuste de conteo entre capas— no cabe en el modelo de una fuente**. Décimo dominio cerrado sin detección nueva, y el que más tensa el esquema.

## Huecos conocidos

- [x] Las seis primitivas de desincronización, agrupadas por dónde vive la ambigüedad
- [x] Sondeo seguro y explotación — dos matrices
- [x] Cara azul de firma — cubierta por el WAF
- [ ] **La detección natural no cabe en el esquema.** El desajuste de conteo entre frente y back es una correlación entre dos fuentes distintas, unidas por identificador de conexión. `deteccion` asume una fuente por regla. Si aparece un segundo caso así —telemetría de dos capas que hay que unir—, revisar el esquema, como se hizo con `forma:`
- [ ] Web cache poisoning como dominio propio: el smuggling es una vía de entrada, hay otras
- [ ] Smuggling sobre HTTP/3 y QUIC, superficie nueva y poco explorada
- [ ] Desincronización por `Connection: keep-alive` mal manejado y por respuestas parciales
