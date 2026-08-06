---
tipo: tradecraft
clase: "[[CWE-89 - SQL Injection]]"
eje: canal-de-extraccion
implementacion: "UNION SELECT anexa filas propias al resultado que la aplicación ya muestra"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]"]
requisitos: [salida-reflejada, cantidad-de-columnas-conocida, tipos-compatibles]
coste: bajo
alternativas: ["[[SQLi - canal basado en errores]]", "[[SQLi - canal booleano ciego]]"]
probado: 2026-08-05
contexto: [mysql8]
visibilidad: publica
creado: 2026-08-05
aliases:
  - SQLi UNION
  - union-based
tags:
  - dominio/web
---

# SQLi - canal UNION

## Cuándo lo elijo

Cuando la aplicación **muestra en pantalla** el resultado de la consulta y puedo hacer que la mía viaje en el mismo resultado. Es el primero del árbol de [[MOC - SQL injection]] porque es el más barato: una petición devuelve filas enteras, no un bit.

Necesita tres cosas a la vez: salida reflejada, saber cuántas columnas devuelve la consulta original, y que los tipos sean compatibles. Si falta cualquiera, el canal no existe y hay que bajar en el árbol.

Cuando el frontend refleja **una sola fila**, el canal sigue sirviendo: se colapsa todo en un valor con agregación de cadenas. No es una técnica aparte, es la misma con otra forma.

## Por qué funciona

`UNION` concatena el resultado de dos `SELECT` en una sola tabla de salida. Si la aplicación imprime lo que devuelve la consulta, imprime también las filas que agregué — el canal de datos es **la propia respuesta HTML**, sin intermediarios.

Que el motor exponga su catálogo como tablas consultables (`information_schema` y equivalentes) es lo que convierte el canal en enumeración total: la estructura de la base se lee con el mismo `SELECT` que los datos.

## Cómo falla

- **Cantidad de columnas distinta** — el motor rechaza el `UNION` entero. Hay que fijarla primero por incremento o por prueba con marcadores nulos.
- **Tipos incompatibles** en la columna donde inyecto: PostgreSQL y Oracle son estrictos, MySQL tolera.
- **La aplicación solo imprime la primera fila** — se resuelve con agregación, pero si además trunca la longitud, se pierde parte del volcado.
- **`UNION` bloqueado por WAF o lista negra** de palabras clave. Ahí se pasa a evasión o se cambia de canal.
- **La consulta original no es un `SELECT`** (por ejemplo un `INSERT`): no hay resultado que extender.

## Coste

El más bajo de todos los canales: **filas enteras por petición**. Un volcado de credenciales sale en una o dos peticiones, contra las cientos del canal temporal. Por eso es el primero que se intenta.

El costo real está en el ruido, no en el tiempo: los payloads son largos, evidentes en cualquier log y el WAF los tiene firmados desde hace veinte años.

## Huella esperada

- Peticiones con `UNION SELECT` legible en la query string o el cuerpo — queda entero en [[Log de acceso del servidor web]].
- Picos de respuestas anormalmente grandes cuando el volcado sale bien.
- Ráfaga de peticiones al mismo parámetro con longitud creciente durante el conteo de columnas.

Los payloads concretos están en [[SQLi UNION - matriz de referencia]]. El impacto sobre el sistema de archivos es otro eje: ver [[Dialectos SQL - matriz de referencia]].
