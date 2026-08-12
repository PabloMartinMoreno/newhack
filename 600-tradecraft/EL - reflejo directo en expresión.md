---
tipo: tradecraft
clase: "[[CWE-917 - Expression Language Injection]]"
eje: superficie
implementacion: "Inyectar en un punto donde la entrada se concatena dentro de una expresión que el motor evalúa y devuelve"
opsec: ruidoso
telemetria: ["[[Proceso hijo del servidor web]]", "[[Log de errores del servidor web]]"]
requisitos: [entrada-concatenada-en-una-expresion, resultado-reflejado]
coste: bajo
alternativas: ["[[EL - evaluación indirecta y ciega]]", "[[EL - OGNL en el framework]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - SpEL reflejado
  - Thymeleaf expression injection
tags:
  - dominio/web
---

# EL - reflejo directo en expresión

## Cuándo lo elijo

Cuando la entrada se evalúa y el resultado vuelve en la respuesta, igual que en SSTI: `${7*7}` devuelve `49`. Es el caso más fácil de confirmar del dominio y el que se prueba primero.

En Java aparece sobre todo en dos lugares: una expresión de Thymeleaf construida con entrada —el patrón `__${...}__::`—, o un fragmento de vista de Spring que concatena un parámetro dentro de una expresión SpEL. Se distingue de un SSTI de plantilla clásica porque el motor es de Java, lo que se confirma con la matriz.

Si el resultado **no** vuelve —la evaluación es indirecta—, la rama es [[EL - evaluación indirecta y ciega]]. Si la entrada la evalúa el framework por diseño, [[EL - OGNL en el framework]].

## Por qué funciona

El motor de expresiones recibe una cadena que incluye lo que puso el atacante y la evalúa completa. Como SpEL, OGNL y MVEL pueden instanciar clases y llamar métodos de Java arbitrarios, la expresión llega directo a `Runtime.exec`:

- SpEL: `T(java.lang.Runtime).getRuntime().exec(...)`
- OGNL: `@java.lang.Runtime@getRuntime().exec(...)`
- MVEL: `Runtime.getRuntime().exec(...)`

No hay que trepar ningún grafo de objetos como en el escape de un entorno restringido de Jinja2: los lenguajes de expresión de Java exponen el acceso al sistema como parte del lenguaje. El payload es el que está en la documentación del motor, y por eso identificar bien el motor es lo único que importa antes de tirarlo. Los payloads por motor están en [[EL injection payloads - matriz de referencia]].

La única complicación es cerrar el contexto de la expresión original cuando la entrada cae dentro de una ya empezada, igual que la ruptura del contexto en [[MOC - Command injection]]: a veces hay que cerrar un `}` o un `]` antes de la propia. La matriz lo cubre.

## Cómo falla

Falla cuando el motor corre con un sandbox activo —SpEL permite un `EvaluationContext` restringido, OGNL tiene un `MemberAccess` que se puede cerrar—. Ahí el `T(...)` o el `@...@` se rechazan y hay que escapar la restricción, que en Java es más difícil que en las plantillas y a veces no se logra. Las vías de escape están en la matriz de payloads.

Falla cuando la entrada no llega realmente al evaluador sino que se escapa antes: no todo `${...}` en una respuesta significa evaluación del lado del servidor. La prueba aritmética lo confirma antes de invertir.

Y falla contra frameworks parcheados que dejaron de evaluar entrada en ese punto — la historia del dominio es una sucesión de esos parches.

## Coste

Bajo. Confirmada la evaluación y el motor, son dos peticiones: una de prueba y una de objetivo. El payload sale de la matriz.

El coste está antes, en identificar el motor, y ahí conviene ser sistemático con [[EL injection - matriz de identificación]] en vez de tirar payloads de motores equivocados, que es lo que llena el registro de errores.

## Huella esperada

La rama más visible del dominio, por la misma razón que casi todas las de ejecución: **nace un proceso hijo del servidor web**, que es la relación en la que ancla [[Intérprete de comandos como hijo del servidor web]]. Esa detección lo ve sin saber que hubo EL de por medio, igual que ve command injection, SSTI y deserialización.

Antes de eso queda el reconocimiento, y es abundante: los payloads de motores equivocados lanzan excepciones de EL —`SpelEvaluationException`, `OgnlException`— que caen en [[Log de errores del servidor web]] con la traza. Una ráfaga de esas excepciones desde un mismo origen es reconocimiento de EL en curso, y precede al intento que funciona. Es la misma asimetría que en SSTI y en deserialización: lo fallido es más visible que lo exitoso, y esa es la ventana de detección real.
