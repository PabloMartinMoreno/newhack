---
tipo: tradecraft
clase: "[[CWE-79 - Cross-site Scripting]]"
eje: obstaculo
implementacion: "El navegador muta HTML sanitizado hasta volverlo ejecutable"
opsec: requiere-bypass
telemetria: []
requisitos: [sanitizador-del-lado-cliente, reparse-del-html]
coste: alto
alternativas: ["[[XSS - DOM-based]]"]
probado: 2026-08-06
contexto: [chrome]
aliases:
  - mXSS
  - mutation XSS
tags:
  - dominio/web
---

# XSS - mutation XSS

## Cuándo lo elijo

Cuando hay un **sanitizador del lado cliente** (DOMPurify y afines) que declara seguro el HTML, pero ese HTML se **vuelve a parsear** después y el navegador lo muta en algo ejecutable. Es el bypass de los sanitizadores, no un tipo de entrega — por eso vive en el eje obstáculo, junto a [[XSS - CSP]].

La señal: el payload pasa la sanitización (no lo bloquean) pero igual ejecuta, o un payload "inerte" cambia de forma al leerlo vía `innerHTML`.

## Por qué funciona

El sanitizador valida el HTML con un parser y lo aprueba. Después la app lo asigna a `innerHTML`, lo que dispara un **segundo parseo** con reglas distintas (namespaces de SVG/MathML, corrección automática de tags mal anidados, decodificación de entidades). Esa diferencia entre "cómo lo vio el sanitizador" y "cómo lo re-arma el navegador" es la mutación: un nodo aparentemente seguro se reescribe como uno que ejecuta.

El caso canónico: contenido dentro de `<svg>`/`<math>` que, al sacarlo de ese contexto en el reparse, cambia de significado y libera un handler.

## Cómo falla

- **Sanitizador actualizado** — DOMPurify parchea las mutaciones conocidas rápido; requiere una mutación no cubierta.
- **No hay reparse** — si el HTML sanitizado se inserta con `textContent` o no se vuelve a tocar, no hay mutación.
- **Trusted Types** que corta la asignación a `innerHTML` de raíz.
- Encontrar una mutación nueva es investigación de parser, no aplicación de payload: por eso `coste: alto`.

## Coste

Alto. Las mutaciones conocidas están parcheadas; las nuevas son trabajo de research sobre discrepancias de parseo. En un engagement real, mXSS aparece cuando el sanitizador es viejo o custom. Contra DOMPurify al día, rara vez.

## Huella esperada

Igual que [[XSS - DOM-based]]: como el bypass ocurre en el cliente al re-parsear, **no deja rastro server-side**. Solo violaciones de CSP si la política atrapa la ejecución.

Mutaciones conocidas en [[XSS evasión - matriz de referencia]] § mXSS.
