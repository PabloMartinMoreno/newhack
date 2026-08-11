---
tipo: tradecraft
clase: "[[CWE-79 - Cross-site Scripting]]"
eje: tipo
implementacion: "JS del cliente pasa una source controlada a un sink peligroso"
opsec: limpio
telemetria: ["[[Informe de violación de CSP]]"]
requisitos: [source-controlable, sink-inseguro-en-el-JS]
coste: medio
alternativas: ["[[XSS - reflejado]]", "[[XSS - almacenado]]"]
probado: nunca
contexto: [chrome]
aliases:
  - DOM XSS
  - DOM-based XSS
tags:
  - dominio/web
---

# XSS - DOM-based

## Cuándo lo elijo

Cuando la inyección **no está en el HTML del servidor** sino en cómo el JavaScript del cliente procesa datos. El payload viaja en algo que el servidor nunca ve —el fragmento `#...`, un `postMessage`— y ejecuta porque el JS lo pasa a un sink peligroso.

La señal: el payload no aparece en el HTML de la respuesta (View Source limpio) pero sí ejecuta. O aparece en el DOM renderizado pero no en el código fuente.

## Por qué funciona

Una **source** controlable por el atacante (`location.hash`, `location.search`, `document.referrer`, `postMessage`) fluye, sin sanitizar, hasta un **sink** que ejecuta o interpreta strings como código o markup (`innerHTML`, `eval`, `document.write`, `location`). Todo ocurre en el navegador; el backend no participa. Ver el mapa completo en [[XSS sources y sinks - matriz de referencia]].

## Cómo falla

- **La source no llega al sink sin pasar por sanitización** — si hay `encodeURIComponent`/DOMPurify en el medio, se corta.
- **El sink no es explotable** con la source disponible (p. ej. `textContent` en vez de `innerHTML`).
- **Trusted Types** (CSP moderno) que prohíbe asignar strings a sinks peligrosos.
- Rastrear el flujo source→sink en JS minificado es trabajoso: es el costo real.

## Coste

Medio, pero por **descubrimiento**, no por explotación. Encontrar el flujo requiere leer el JS del cliente (DevTools, breakpoints en los sinks). Una vez identificado, el payload es directo.

## Huella esperada

`opsec: limpio` por una razón concreta: como el payload viaja en el fragmento `#` —que **no se envía al servidor**— o en un `postMessage`, **no queda nada en los logs del backend**. Es el único tipo de XSS invisible al [[Log de acceso del servidor web]]. Solo se detecta del lado cliente o por violaciones de CSP.

Payloads por sink: [[XSS sources y sinks - matriz de referencia]]. Qué hacer con la ejecución: [[XSS impacto - matriz de referencia]].
