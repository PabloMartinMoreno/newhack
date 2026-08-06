---
tipo: tradecraft
clase: "[[CWE-89 - SQL Injection]]"
eje: canal-de-extraccion
implementacion: "Condición booleana leída por la diferencia visible en la respuesta"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]"]
requisitos: [respuesta-diferencial, sin-salida-reflejada, sin-error-visible]
coste: medio
alternativas: ["[[SQLi - canal basado en errores]]", "[[SQLi - canal temporal ciego]]"]
probado: 2026-08-06
contexto: [mysql8]
aliases:
  - SQLi boolean blind
  - boolean-based blind
tags:
  - dominio/web
---

# SQLi - canal booleano ciego

## Cuándo lo elijo

Cuando no hay salida reflejada ni error visible, pero la respuesta **cambia de forma observable** según si una condición es verdadera o falsa: un texto que aparece o no, un largo distinto, un `200` vs `500`. Anteúltimo del árbol de [[MOC - SQL injection]], antes del temporal.

Se prefiere al temporal siempre que exista la diferencia: no depende del reloj, así que es más rápido y estable.

## Por qué funciona

La respuesta de la aplicación es un oráculo de un bit. `AND 1=1` deja la página normal; `AND 1=2` la cambia. Reemplazando `1=1` por `substring(password,1,1)='a'` se lee la base carácter por carácter, preguntando por comparación. Ver [[La latencia como canal de datos]] — misma idea, otro reloj.

## Cómo falla

- **La diferencia no es estable** — si la página varía por otras razones (avisos, contadores), el oráculo miente. Hay que fijar una marca confiable.
- **Rate limiting** — el ataque necesita cientos de peticiones.
- **WAF** que normaliza o bloquea.
- **No hay ninguna diferencia** — entonces no es booleano: se baja a temporal.

## Coste

Medio: aproximadamente un bit por petición, igual que el temporal, pero **sin la espera**. Con búsqueda binaria son ~7 peticiones por carácter. Más barato que el temporal, más caro que UNION o error-based.

## Huella esperada

- Ráfaga de peticiones al mismo parámetro con payloads casi idénticos que solo cambian el carácter comparado.
- Alternancia de dos tamaños de respuesta — la firma del oráculo.

Payloads en [[SQLi ciego - matriz de referencia]].
