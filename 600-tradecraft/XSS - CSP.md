---
tipo: tradecraft
clase: "[[CWE-79 - Cross-site Scripting]]"
eje: obstaculo
implementacion: "Ejecutar pese a una Content-Security-Policy, o esquivarla"
opsec: requiere-bypass
telemetria: ["[[Informe de violación de CSP]]"]
requisitos: [csp-con-debilidad]
coste: alto
alternativas: []
probado: nunca
contexto: [chrome]
aliases:
  - Content Security Policy
  - CSP bypass
tags:
  - dominio/web
---

# XSS - CSP

## Cuándo lo elijo

No es un tipo de XSS: es **el obstáculo** que define el XSS moderno. Cuando ya tengo inyección pero el navegador no ejecuta el payload, casi siempre es una `Content-Security-Policy`. Esta nota es el criterio para leer la política y decidir si tiene un hueco; los payloads viven en [[XSS bypass de CSP - matriz de referencia]].

Primero se lee el header `Content-Security-Policy` de la respuesta y se busca la debilidad. Sin debilidad, la inyección puede ser real y aun así no explotable.

## Por qué funciona

El bypass funciona cuando la política es **permisiva o mal armada**. CSP restringe de dónde se puede cargar y ejecutar script; se saltea por sus grietas:

- `unsafe-inline` presente → los handlers y `<script>` inline ejecutan: no hay CSP efectivo para XSS.
- Un dominio permitido en `script-src` que **hostea un gadget** (JSONP, una librería con `eval`, un endpoint que refleja).
- `strict-dynamic` con un script confiable que carga más scripts de forma abusable.
- `nonce` reutilizado o predecible.
- Falta `object-src 'none'` / `base-uri` → inyección vía `<base>` o `<object>`.

## Cómo falla

- **CSP estricta y bien armada** — `script-src 'nonce-aleatorio' 'strict-dynamic'; object-src 'none'; base-uri 'none'` sin dominios con gadgets: no hay por dónde. La inyección queda como hallazgo sin impacto de ejecución.
- **El gadget no existe** en los dominios permitidos.
- El `nonce` es realmente aleatorio por respuesta.

## Coste

Alto. A diferencia de un XSS sin CSP —payload directo—, acá el trabajo es de **análisis**: leer la política, enumerar los dominios permitidos, buscar gadgets conocidos (`csp-evaluator` de Google ayuda a encontrar la debilidad). Muchas CSP no se saltean, y eso es un resultado válido: reportás la inyección con impacto limitado.

## Huella esperada

- Si la CSP tiene `report-uri`/`report-to`, cada intento bloqueado genera un **reporte de violación de CSP** — la telemetría azul propia del XSS moderno (pendiente de nota en `550-telemetria/`).
- El payload en el [[Log de acceso del servidor web]] si viajó por la request.

Payloads de bypass en [[XSS bypass de CSP - matriz de referencia]].
