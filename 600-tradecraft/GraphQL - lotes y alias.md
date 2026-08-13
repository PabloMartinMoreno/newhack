---
tipo: tradecraft
clase: "[[CWE-307 - Improper Restriction of Excessive Authentication Attempts]]"
eje: fase
implementacion: "Meter cientos de operaciones en una sola petición con alias o lotes, para saltar los límites por petición"
opsec: ruidoso
telemetria: ["[[Log de autenticación de la aplicación]]", "[[Log de acceso del servidor web]]"]
requisitos: [servidor-que-acepta-alias-o-lotes, límite-de-tasa-por-petición]
coste: bajo
alternativas: ["[[Autenticación - password spraying]]", "[[GraphQL - denegación por complejidad]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - GraphQL batching
  - alias brute force
  - 2FA bypass por lotes
tags:
  - dominio/web
---

# GraphQL - lotes y alias

## Cuándo lo elijo

Cuando hay un control de tasa o de intentos que cuenta **por petición HTTP** —login, código de segundo factor, cupón, voto— y el servidor GraphQL acepta varias operaciones en un solo mensaje. Se reconoce probando si una consulta con dos campos aliasados devuelve los dos resultados: si lo hace, el límite por petición se puede pulverizar.

Es la rama que convierte un control de fuerza bruta razonable en inútil. Se elige contra cualquier endpoint que limite por número de peticiones en vez de por número de intentos.

## Por qué funciona

GraphQL permite pedir el mismo campo muchas veces en una consulta usando **alias** —nombres distintos para el mismo campo— y, en muchos servidores, mandar **varias operaciones en un lote** (un array de consultas). Las dos cosas hacen que una sola petición HTTP contenga cientos de operaciones independientes.

El control de tasa clásico cuenta peticiones: "cinco intentos de login por minuto por IP". Si mil intentos entran en **una** petición, ese control ve una petición y deja pasar los mil:

```graphql
{
  a: login(user:"admin", pass:"1234")  { token }
  b: login(user:"admin", pass:"1235")  { token }
  c: login(user:"admin", pass:"1236")  { token }
  # … cientos más
}
```

Los objetivos donde más rinde:

- **Código de segundo factor.** Un OTP de seis dígitos son un millón de combinaciones; sin límite efectivo, se agotan. Es el caso emblemático y el de mayor impacto — convierte el 2FA en decoración.
- **Contraseña**, cuando hay un usuario conocido y el límite es por petición.
- **Cualquier acción con cupo**: un voto por cuenta, un cupón por usuario, se disparan en lote.

La falta de límite sobre cuántas operaciones entran en una petición es la misma clase que habilita la denegación de [[GraphQL - denegación por complejidad]] —`CWE-770`—; acá el recurso que se agota no es el servidor sino el control de tasa, y por eso la `clase:` de esta nota es la de fuerza bruta, `CWE-307`.

## Cómo falla

Falla contra un límite que cuenta **operaciones**, no peticiones: si el servidor rechaza consultas con más de N operaciones o más de N alias del mismo campo, el ataque se corta. Es la mitigación correcta y la que va en el informe — limitar por petición es lo que crea el agujero.

Falla cuando el servidor no soporta lotes ni permite alias sobre el campo sensible, que algunos deshabilitan justamente por esto.

Y falla cuando el control de tasa está aguas arriba contando por conexión o por token de acción de un solo uso —un OTP que se invalida al primer intento fallido no se puede fuerza-brutear por lotes.

## Coste

Bajo. Una vez confirmado que los alias funcionan, construir la consulta con cientos de intentos es trivial y una herramienta la genera. El OTP de seis dígitos se agota en pocas peticiones de gran tamaño.

El coste es de reconocimiento previo: confirmar que el alias devuelve resultados independientes, y encontrar el nombre exacto de la mutación de login o de verificación — que la introspección de [[GraphQL - introspección del esquema]] ya dio.

## Huella esperada

Ruidosa en volumen de intentos pero **engañosamente silenciosa en volumen de peticiones**, y ahí está lo interesante del dominio para el defensor:

- [[Log de autenticación de la aplicación]] registra **cientos de intentos de login fallidos** si registra a nivel de operación. Esa ráfaga la ve [[Accesos exitosos contra muchas cuentas desde un origen]] y las reglas de fuerza bruta — **pero solo si el log cuenta operaciones, no peticiones**.
- [[Log de acceso del servidor web]] ve **una sola petición**, o muy pocas. Un defensor que mire el log de acceso —lo habitual— no ve ninguna anomalía de volumen: es una petición grande, no mil chicas.

Ese desfase es la lección del dominio: **el mismo error que habilita el ataque lo esconde de la telemetría de tráfico**. El control cuenta peticiones y las peticiones son pocas; la señal real está a nivel de operación, en el log de autenticación, y solo si ese log se instrumentó por intento y no por request. Es una variante del hueco de [[Un log sin identidad es un historial, no una detección]]: la unidad de conteo equivocada vuelve invisible lo que debería saltar. Anotado en [[MOC - GraphQL]].
