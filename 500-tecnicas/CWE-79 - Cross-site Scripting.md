---
tipo: tecnica
taxonomia: cwe
identificador: CWE-79
wstg: [WSTG-INPV-01, WSTG-INPV-02, WSTG-CLNT-01]
tacticas: []
aliases:
  - CWE-79
  - XSS
  - Cross-site Scripting
tags:
  - dominio/web
---

# CWE-79 - Cross-site Scripting

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - Cross-site scripting]]; las variantes en `600-tradecraft/`; los payloads en las matrices de `900-meta/`.

## Qué es

Ejecución de JavaScript controlado por el atacante en el navegador de otra persona, porque la aplicación inserta entrada no confiable en una página **sin neutralizarla para el contexto** donde cae.

## Por qué existe

Porque el navegador no distingue el código que puso el desarrollador del que inyectó el atacante: todo lo que llega dentro de un `<script>`, un handler o un `javascript:` se ejecuta con el origen de la víctima. La mitigación real es **codificar según el contexto de salida** (HTML, atributo, JS, URL) — no un escape genérico.

## Ejes que la descomponen

Ver [[MOC - Cross-site scripting]] para la tabla completa y los árboles. Resumen: tipo (reflejado/almacenado/DOM) × contexto de salida × sink (en DOM) × obstáculo (filtro/CSP) × impacto.

## Por qué no basta con ATT&CK

XSS es cliente, no cae limpio en una técnica de ATT&CK. El identificador canónico es **CWE-79 + WSTG**: `WSTG-INPV-01` (reflejado), `WSTG-INPV-02` (almacenado), `WSTG-CLNT-01` (DOM).

## Referencias canónicas

- [CWE-79](https://cwe.mitre.org/data/definitions/79.html)
- WSTG-INPV-01/02, WSTG-CLNT-01
- [[@portswigger-xss-labs]]
