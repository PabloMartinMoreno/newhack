---
tipo: meta
aliases:
  - JavaScript deobfuscation
  - deofuscación de JS
  - deobfuscar JavaScript
tags:
  - meta/referencia
  - dominio/web
---

# JavaScript deobfuscation - matriz de referencia

> [!info] Referencia pura, no un zettel
> Volver legible el JS minificado/ofuscado para **extraer lo que esconde**: endpoints de API, claves, parámetros, feature flags, y los sinks del lado cliente. Técnica de recon web; el criterio de fase, en [[MOC - Reconocimiento web]]. **No es** ingeniería reversa de binarios (Ghidra/IDA) — eso está fuera del alcance del vault; acá es análisis de código cliente que ya descargaste.
> Encaja después de [[Crawling web - matriz de referencia]] (que **encuentra** los `.js`) y alimenta su § Extraer de JavaScript y a [[XSS - DOM-based]] (sources/sinks del DOM).

`HOST` es el objetivo de ejemplo. El análisis es **offline** sobre el JS ya bajado: cero ruido al objetivo.

> [!tip] Paso 0 — buscar el sourcemap
> Antes de deobfuscar nada: pedir `archivo.js.map`. Si existe, reconstruye el **código fuente original** con nombres y comentarios — no hace falta deobfuscar. Webpack/Vite suelen dejarlos en prod por error. Herramientas: `unwebpack-sourcemap`, o devtools los aplica solo.

## Reconocer el tipo de ofuscación

| Síntoma | Tipo | Cómo se ataca |
|---|---|---|
| Una sola línea, nombres cortos (`a`,`b`), sin espacios | minificado | reindentar (beautify) |
| `eval(function(p,a,c,k,e,d){...})` | packed (Dean Edwards) | unpackear (de4js, o reemplazar `eval` por `console.log`) |
| Arrays `_0x1a2b=[...]` y llamadas `_0x1a2b(0x3)` | string-array (obfuscator.io) | de4js, o análisis dinámico |
| Cadenas en `\x68\x65` o base64 dentro del código | encoding | decodificar (CyberChef, `atob`) |
| Saltos raros, `while(true){switch...}` | control-flow flattening | análisis **dinámico** (estático no rinde) |

## Herramientas

| Herramienta | Para qué |
|---|---|
| js-beautify / prettier | reindentar minificado a algo leíble |
| devtools `{ }` (pretty-print) | lo mismo en el navegador, con breakpoints |
| de4js | deobfuscador web: unpack, string-array, decodificado |
| CyberChef | decodificar cadenas sueltas (base64/hex/charcode/rot) |
| Babel / AST | casos duros: transformar el árbol de sintaxis con reglas propias |
| devtools (dinámico) | breakpoints, `debugger`, watch y console para ver valores en runtime |

## De estático a dinámico

Cuando el estático se traba (control-flow flattening, cadenas armadas en runtime), el atajo es **ejecutarlo y mirar**: breakpoint en la función sospechosa, o reemplazar el `eval`/constructor final por `console.log` para volcar el string ya desofuscado. En una SPA, la consola del navegador con el JS pausado suele resolver en minutos lo que el estático no.

## Qué buscar una vez legible

- Endpoints y rutas de API que no aparecen en el HTML → suma superficie; se cruzan con [[Crawling web - matriz de referencia]] § Extraer de JavaScript.
- Claves/tokens hardcodeados → como en [[Google dorking - matriz de referencia]] y [[GitHub dorking - matriz de referencia]], pero acá servidos por la propia app.
- Parámetros y feature flags ocultos → parámetros para fuzzear.
- `sources` y `sinks` del DOM (`location`, `innerHTML`, `eval`) → [[XSS - DOM-based]].
- Comentarios y nombres de variables que revelan lógica de negocio o validación cliente (que se bypassa server-side).

## Errores / notas

| Síntoma | Causa | Salida |
|---|---|---|
| Beautify no alcanza, sigue ilegible | está ofuscado, no solo minificado | de4js / dinámico, no solo prettier |
| `debugger` en bucle traba el navegador | anti-debugging | "Deactivate breakpoints" o "Never pause here" en devtools |
| Cadenas siguen sin sentido tras unpack | se arman en runtime | dinámico: logear después de que se construyen |
| Nombres siguen como `_0x...` | renombrado no reversible | no es bloqueante: seguir el flujo, no los nombres |

> [!warning] Ofuscación no es seguridad
> Todo lo que corre en el cliente es visible; ofuscar solo sube el costo de leerlo. Un secreto en el JS **es** un secreto expuesto, esté ofuscado o no.
