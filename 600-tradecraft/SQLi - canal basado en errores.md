---
tipo: tradecraft
clase: "[[CWE-89 - SQL Injection]]"
eje: canal-de-extraccion
implementacion: "Forzar un error del motor que incluya el dato en el mensaje"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]"]
requisitos: [errores-visibles, salida-no-reflejada]
coste: bajo
alternativas: ["[[SQLi - canal UNION]]", "[[SQLi - canal booleano ciego]]"]
probado: 2026-08-06
contexto: [mysql8]
visibilidad: publica
creado: 2026-08-06
aliases:
  - SQLi error-based
  - error-based
tags:
  - dominio/web
---

# SQLi - canal basado en errores

## Cuándo lo elijo

Cuando la aplicación **no refleja el resultado** de la consulta pero **sí muestra el mensaje de error** del motor. Segundo del árbol de [[MOC - SQL injection]], después de UNION: sigue devolviendo el dato en la respuesta, solo que dentro de un error en vez de en una fila.

Es la salida típica cuando UNION no sirve porque la consulta no imprime filas, pero el `500` del servidor filtra la excepción con el texto adentro.

## Por qué funciona

Ciertas funciones fallan a propósito con un mensaje que **incluye un valor calculado**. `extractvalue('1', concat(0x7e, (SELECT ...)))` intenta parsear como XPath un string que empieza con `~`, falla, y vomita ese string —con tu subconsulta ya evaluada— en el mensaje de error. El error es el canal.

## Cómo falla

- **Errores suprimidos** — si la app muestra una página genérica en vez del mensaje, el canal desaparece: se baja a booleano ciego.
- **Truncamiento** — el mensaje corta a ~32 caracteres. Datos largos salen por partes con `substring`.
- **WAF** que filtra `extractvalue`/`updatexml` por firma.
- **Motor sin la primitiva** — cada motor tiene la suya; ver la matriz.

## Coste

Bajo, como UNION: un dato por petición, en texto claro dentro del error. El ruido es alto — cada intento genera un `500` en los logs.

## Huella esperada

- Ráfaga de respuestas `500` sobre el mismo endpoint — el sello del canal.
- `extractvalue`/`updatexml` legibles en el [[Log de acceso del servidor web]].

Payloads en [[SQLi error-based - matriz de referencia]].
