---
tipo: tradecraft
clase: "[[CWE-1336 - Improper Neutralization of Special Elements Used in a Template Engine]]"
eje: capacidad-del-motor
implementacion: "Leer los objetos que la plantilla ya tiene en su contexto, sin salir del motor"
opsec: limpio
telemetria: ["[[Log de acceso del servidor web]]", "[[Log de errores del servidor web]]"]
requisitos: [evaluacion-de-expresiones-confirmada]
coste: bajo
alternativas: ["[[SSTI - escape del entorno restringido]]", "[[SSTI - ejecución directa]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - SSTI sin RCE
  - volcado de contexto
tags:
  - dominio/web
---

# SSTI - lectura sin ejecución

## Cuándo lo elijo

En dos situaciones opuestas, y por eso es la rama que más veces se usa sin darse cuenta.

**Cuando no queda otra**: el motor es sin lógica —Handlebars sin ayudantes peligrosos, Mustache, las plantillas de Django— o el entorno restringido no cedió. No hay ejecución posible y abandonar el hallazgo sería tirar un acceso de lectura al proceso.

**Cuando conviene**: siempre, como primer paso después de confirmar la inyección, antes de intentar cualquier escalada. Cuesta una petición, no lanza excepciones, y muchas veces lo que devuelve —una clave de firma, credenciales de base de datos— vale más que la ejecución que se estaba buscando.

## Por qué funciona

El motor renderiza con un **contexto**: el conjunto de variables que la aplicación le pasó. Ese contexto casi nunca se acota a lo necesario. Suele traer el objeto de configuración entero, el de la petición, el usuario de la sesión, y en varios marcos de trabajo un ayudante que expone las variables de entorno.

Volcar ese contexto no es evadir nada: es pedirle al motor lo que el motor está para hacer. Por eso no genera errores y por eso es la variante limpia del dominio.

Lo que aparece ahí con más frecuencia, en orden de valor:

- **La clave de firma de la aplicación.** Con ella se falsifican sesiones y tokens directamente: el hallazgo deja de ser SSTI y pasa a ser [[Sesión - falsificación de JWT]] o manipulación del objeto de sesión, sin necesidad de ejecutar nada.
- **Credenciales de base de datos y de servicios externos**, que suelen estar en la configuración.
- **Variables de entorno**, que en un contenedor son casi siempre el depósito de secretos.
- **El objeto de petición**, que expone cabeceras internas y a veces la dirección de servicios que no se alcanzan desde afuera — insumo para [[MOC - SSRF]].

Ese primer punto es el que convierte esta rama en una escalada seria: la clave de firma da toma de cuenta administrativa sin tocar el sistema operativo.

## Cómo falla

Falla cuando el contexto está bien acotado y solo trae las dos variables que la plantilla necesita. Pasa en aplicaciones que renderizan plantillas de usuario a propósito y pensaron el problema.

Falla también cuando el motor escapa la salida de forma que los objetos se rindan como texto inútil, o cuando la respuesta trunca antes de mostrar lo interesante. Contra lo segundo se pagina: se pide un atributo por vez en lugar del objeto entero.

Y no falla, pero decepciona, cuando no hay nada valioso en el contexto. Es un resultado válido y hay que reportarlo como lo que es: evaluación de expresiones del lado del servidor, severidad según lo que se haya podido leer.

## Coste

Bajo, el más bajo del dominio. Una o dos peticiones y no hay iteración.

Es también el de mejor relación coste/beneficio, y por eso el MOC lo pone antes de la escalada aunque en la mayoría de los tutoriales aparezca como consuelo. Buscar ejecución antes de mirar el contexto es el error de orden del dominio.

## Huella esperada

Casi ninguna, y es la razón del `opsec: limpio`.

No nace ningún proceso, no sale ninguna conexión, no se lanzan excepciones. Las peticiones llegan a un endpoint que ya recibe entrada de usuario, con respuestas más largas de lo normal — que es lo único observable, y solo si alguien mira el tamaño de la respuesta.

Queda en [[Log de acceso del servidor web]] como tráfico ordinario. **Ninguna detección del vault la ve**, y no es un hueco de contenido: es que no hay artefacto que consumir. Detectarla exigiría inspeccionar el cuerpo de las respuestas buscando material que no debería salir, que es un control de prevención de fuga y no una regla de detección.

Es el mismo tipo de límite que el XXE de lectura local con `file://` en [[MOC - XXE]]: la técnica es silenciosa porque no toca ninguna de las fronteras que las fuentes vigilan.
