---
tipo: tradecraft
clase: "[[CWE-200 - Exposure of Sensitive Information to an Unauthorized Actor]]"
eje: fase
implementacion: "Recuperar el esquema completo por introspección, o reconstruirlo por sugerencia de campos cuando está apagada"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]", "[[Log de auditoría de la aplicación]]"]
requisitos: [endpoint-graphql-alcanzable]
coste: bajo
alternativas: ["[[GraphQL - autorización rota en resolvers]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - introspection query
  - field suggestion
  - clairvoyance
tags:
  - dominio/web
---

# GraphQL - introspección del esquema

## Cuándo lo elijo

Siempre primero. Es el paso de reconocimiento que decide todo el resto del trabajo en GraphQL: sin el esquema, encontrar el resolver sin control de acceso o el argumento que llega a una inyección es adivinar; con el esquema, es leer.

No es un fin en sí mismo —el esquema no son datos de usuario— sino el mapa que hace baratas las otras tres ramas del dominio. Por eso va antes que [[GraphQL - autorización rota en resolvers]], que es a dónde se pasa apenas se tiene el esquema.

## Por qué funciona

GraphQL expone por diseño una consulta especial —introspección— que devuelve el esquema entero: cada tipo, cada campo, cada argumento, cada relación entre tipos. Es una funcionalidad de desarrollo, pensada para que las herramientas de cliente autocompletén; el fallo es dejarla abierta a usuarios no confiables en producción.

La consulta de introspección (`__schema`, `__type`) está en [[GraphQL - matriz de reconocimiento]]. Devuelve, entre otras cosas:

- Los tipos de datos y sus campos, incluidos los que ninguna interfaz de usuario muestra.
- Las mutaciones disponibles, que es la lista de acciones que cambian estado — el objetivo de la rama de autorización.
- Los argumentos de cada campo, que es dónde buscar inyecciones.
- Campos marcados como obsoletos, que suelen ser los peor mantenidos.

**Cuando la introspección está apagada, el esquema se reconstruye igual**, y esto es lo que conviene saber para no dar el dominio por cerrado:

- **Sugerencia de campos.** Muchos servidores, ante un campo mal escrito, responden "¿quisiste decir `usuario`?". Cada corrección confirma un nombre válido. Herramientas como Clairvoyance automatizan la reconstrucción del esquema a partir de esas sugerencias.
- **Fuerza bruta de nombres** contra una lista, viendo cuáles no dan error de campo inexistente.

Por eso la introspección apagada **sube el costo del reconocimiento pero no lo elimina**, y hay que decirlo en el informe: recomendar solo "apagá la introspección" da falsa tranquilidad.

## Cómo falla

Falla, en el sentido de que se encarece, cuando la introspección está deshabilitada y además la sugerencia de campos está apagada. Ahí queda solo la fuerza bruta de nombres, que es lenta y ruidosa.

Falla cuando el endpoint no es alcanzable sin autenticación y no se tiene ninguna credencial — aunque muchas APIs exponen el esquema antes del login.

Y no falla, pero no alcanza, cuando el esquema está protegido pero los datos detrás también: conocer el esquema no habilita nada si cada resolver valida autorización. Ese es el caso bien hecho, y entonces el reconocimiento es solo eso.

## Coste

Bajo con introspección abierta: una petición devuelve todo. Medio con sugerencia de campos: la herramienta reconstruye en minutos u horas según el tamaño. Alto con solo fuerza bruta.

Es de las mejores relaciones costo/valor del vault: una petición que convierte una API opaca en un mapa completo, y que decide dónde apuntar todo el esfuerzo siguiente.

## Huella esperada

Ruidosa y de firma clara, aunque casi nunca vigilada:

- La **consulta de introspección** contiene `__schema` y `__type`, cadenas que no aparecen en el tráfico normal de una aplicación —solo las herramientas de desarrollo las mandan—. Es una firma de alta fidelidad sobre el cuerpo de la petición, que ve [[Registro del WAF]] si inspecciona cuerpos y no [[Log de acceso del servidor web]], que no los registra.
- La **sugerencia de campos** deja una ráfaga de consultas con nombres de campo inexistentes, cada una devolviendo un error de "campo desconocido". Esa ráfaga en [[Log de auditoría de la aplicación]] —muchos errores de esquema desde un origen— es la señal de una reconstrucción en curso, y es de las pocas del dominio que se detecta por volumen sin instrumentar nada especial.

Ninguna detección del vault la implementa, pero la firma de `__schema` es de las más limpias que aparecieron: recomendar alertar sobre consultas de introspección en producción es de mayor retorno que apagarla, porque detecta también los intentos. Anotado en [[MOC - GraphQL]].
