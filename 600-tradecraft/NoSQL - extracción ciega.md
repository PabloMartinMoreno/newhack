---
tipo: tradecraft
clase: "[[CWE-943 - Improper Neutralization of Special Elements in Data Query Logic]]"
eje: familia
implementacion: "Extraer datos carácter por carácter con $regex u operadores de comparación, leyendo un oráculo booleano o temporal"
opsec: ruidoso
telemetria: ["[[Registro del WAF]]", "[[Log de acceso del servidor web]]"]
requisitos: [inyección-de-operador-confirmada, un-oráculo-observable]
coste: alto
alternativas: ["[[NoSQL - inyección de operador]]", "[[SQLi - canal booleano ciego]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - NoSQL blind
  - regex extraction
  - $regex char by char
tags:
  - dominio/web
---

# NoSQL - extracción ciega

## Cuándo lo elijo

Cuando [[NoSQL - inyección de operador]] confirmó que se puede inyectar pero la respuesta **no devuelve los datos** —solo cambia entre dos estados, o cambia el tiempo de respuesta—. Es el paralelo exacto de [[SQLi - canal booleano ciego]] en NoSQL, y se elige por la misma razón: hay inyección, no hay salida directa, y hay que inferir.

Se llega acá desde el salto de operador cuando el objetivo pasa de "entrar" a "sacar datos" —una contraseña, un token, un campo oculto— y esos datos no se reflejan.

## Por qué funciona

`$regex` convierte cualquier campo en un oráculo. Una consulta que devuelve un estado distinto según si un campo **coincide con un patrón** permite preguntar por el dato carácter por carácter:

```
{"user": "admin", "pass": {"$regex": "^a"}}   → ¿la contraseña empieza con 'a'?
{"user": "admin", "pass": {"$regex": "^b"}}   → ¿con 'b'?
```

El estado de la respuesta —login exitoso o no, un `200` contra un `403`, un contenido presente o ausente— es el oráculo booleano. Se itera el patrón: fijado el primer carácter, se prueba el segundo (`^aa`, `^ab`…), y así hasta reconstruir el campo entero.

Los operadores de comparación dan otros oráculos:

- `$gt` / `$lt` — búsqueda binaria sobre valores, más rápida que probar carácter por carácter para datos numéricos.
- `$regex` con anclas y clases —`^a.{5}$` para la longitud, `[a-m]` para bisecar el alfabeto— afina la extracción.

Cuando no hay oráculo booleano —la respuesta es idéntica siempre— queda el **canal temporal**, con `$where` y un bucle que retarda: es más lento y se cruza con [[NoSQL - inyección de JavaScript]] porque necesita evaluar código. Las construcciones de los tres oráculos están en [[NoSQL extracción ciega - matriz de referencia]].

## Cómo falla

Falla contra el forzado de tipo, igual que la rama de operador: sin poder inyectar el `$regex`, no hay oráculo.

Falla cuando la respuesta no tiene ningún estado observable —ni contenido, ni código, ni tiempo—, que es raro pero posible. Ahí no hay canal y la extracción no avanza.

Y se encarece hasta lo impráctico cuando cada consulta es lenta o hay límite de tasa: la extracción ciega son cientos o miles de peticiones, y un control de tasa efectivo la vuelve inviable en tiempo razonable.

## Coste

Alto, el más alto del dominio. Extraer un campo de veinte caracteres del alfabeto completo son cientos de peticiones aun con búsqueda binaria, y el canal temporal multiplica el tiempo. Es trabajo de herramienta —`nosqlmap` o un script propio—, no manual.

Conviene medir antes de lanzarlo: cuánto tarda cada consulta, si hay límite de tasa, cuánto dato hay que sacar. Si el objetivo es solo confirmar la inyección, el salto de operador ya lo hizo y no hace falta la extracción; esta rama es para cuando el dato importa.

## Huella esperada

La rama más ruidosa del dominio por volumen, y la que mejor se detecta **por agregado**:

- Cientos o miles de consultas casi idénticas, variando un patrón `$regex`, desde un mismo origen en poco tiempo. Es una firma de volumen clarísima —el mismo endpoint, el mismo tamaño, diferencias mínimas—, y la ve [[Log de acceso del servidor web]] aunque no registre el cuerpo, porque el **patrón de repetición** está en el volumen y la cadencia, no en el contenido.
- [[Registro del WAF]] ve además los `$regex` en el cuerpo, la misma firma de clave `$` que la rama de operador pero repetida.

Es el caso del dominio donde la detección por `forma: agregado` rinde sin instrumentar el cuerpo: la tasa de consultas casi idénticas contra un endpoint de login o de búsqueda es anómala por sí sola, como la fuerza bruta de [[Fallos de acceso contra cuentas inexistentes]]. La diferencia con aquella es que acá los intentos pueden ser todos "exitosos" a nivel HTTP —`200` cada uno—, así que la señal no es el fallo sino la **repetición con variación mínima**. Anotado como candidato de detección en [[MOC - NoSQL injection]].
