---
tipo: tradecraft
clase: "[[CWE-770 - Allocation of Resources Without Limits or Throttling]]"
eje: fase
implementacion: "Enviar una consulta profunda, circular o muy ancha que multiplica el trabajo del servidor"
opsec: ruidoso
telemetria: ["[[Log de errores del servidor web]]", "[[Log de acceso del servidor web]]"]
requisitos: [esquema-con-relaciones-circulares, sin-límite-de-profundidad-ni-costo]
coste: bajo
alternativas: ["[[GraphQL - lotes y alias]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - GraphQL DoS
  - query depth attack
  - nested query
tags:
  - dominio/web
---

# GraphQL - denegación por complejidad

## Cuándo lo elijo

Cuando el esquema tiene relaciones circulares —un tipo que referencia a otro que referencia al primero— y el servidor no limita la profundidad ni el costo de las consultas. Se reconoce en el esquema que dio [[GraphQL - introspección del esquema]]: si `Usuario` tiene `publicaciones` y `Publicacion` tiene `autor`, el ciclo está.

Es la rama de menor impacto del dominio —denegación de servicio, no acceso— y la que hay que probar con más cuidado, porque puede tirar el servicio de verdad. Se elige cuando el objetivo es demostrar el riesgo de disponibilidad, no robar datos.

## Por qué funciona

GraphQL le da al cliente el control de la forma de la consulta, y sin límites eso incluye el control de cuánto trabajo hace el servidor. Dos mecanismos, en [[GraphQL - matriz de explotación]]:

- **Profundidad circular.** Siguiendo el ciclo `Usuario → publicaciones → autor → publicaciones → autor…`, cada nivel multiplica los objetos a resolver. Diez o quince niveles generan una explosión combinatoria que consume memoria y CPU, y a menudo dispara una avalancha de consultas a la base de datos.
- **Amplitud con alias.** Pedir un campo caro —uno que hace un cálculo o una consulta pesada— cientos de veces con alias distintos en una sola petición. Se cruza con [[GraphQL - lotes y alias]] en el mecanismo, pero acá el objetivo es agotar el servidor, no un control de tasa.

El daño es desproporcionado respecto del tamaño de la petición: unas líneas de consulta contra minutos de CPU o una caída. Por eso es `CWE-770` —recursos sin límite— y no una inyección: la consulta es válida, solo es carísima.

## Cómo falla

Falla contra un **límite de profundidad** o un **análisis de costo** que rechaza la consulta antes de ejecutarla. Es la mitigación correcta y la más común en servidores GraphQL maduros, que traen esos límites de fábrica.

Falla cuando hay tiempo máximo de ejecución y paginación obligatoria: aunque la consulta sea profunda, se corta antes de hacer daño.

Y falla, felizmente, cuando el esquema no tiene ciclos ni campos caros — aunque eso es raro en un grafo real.

## Coste

Bajo de construir, **alto de probar con responsabilidad**. La consulta es trivial de armar a partir del ciclo del esquema. El problema es el opuesto de casi todo el vault: acá el riesgo no es que no funcione, es que funcione **demasiado** y tire el servicio de un cliente real.

> [!danger] Esto puede tirar producción
> Una consulta de complejidad no acotada puede agotar el servidor y dejar la aplicación caída para todos, no como efecto lateral sino como el efecto mismo. En un objetivo real se prueba con **profundidad creciente y medida** —empezar en tres niveles, subir de a uno, mirar el tiempo de respuesta— y se para al primer signo de carga, sin llegar a la caída. Demostrar el riesgo no es causarlo. Acordar la ventana antes.

## Huella esperada

La más visible del dominio por efecto, no por firma:

- El servidor bajo carga deja **tiempos de respuesta que se disparan** y a menudo `500`/`503` en [[Log de acceso del servidor web]] y errores de tiempo agotado o de memoria en [[Log de errores del servidor web]]. Es la señal de efecto: la disponibilidad cae y eso se ve en cualquier monitoreo, sin instrumentar GraphQL.
- La consulta en sí es **profunda y repetitiva** de forma característica —el mismo campo anidado muchas veces—, una firma sobre el cuerpo que [[Registro del WAF]] podría ver si mide profundidad, cosa que casi ninguno hace.

A diferencia de las otras ramas de GraphQL, esta se detecta bien **por efecto** con el monitoreo de disponibilidad que ya existe en cualquier operación seria: un pico de latencia y errores correlacionado con una petición grande a `/graphql`. No hace falta una regla nueva ni instrumentación especial, y por eso es la cara azul más cubierta del dominio. Lo que el monitoreo de disponibilidad no dice es **cuál** consulta lo causó — para eso hace falta registrar el costo por consulta, anotado como mejora en [[MOC - GraphQL]].
