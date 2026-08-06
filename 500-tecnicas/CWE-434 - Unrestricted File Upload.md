---
tipo: tecnica
taxonomia: cwe
identificador: CWE-434
wstg: [WSTG-BUSL-09]
tacticas: []
aliases:
  - CWE-434
  - File Upload
  - Unrestricted File Upload
tags:
  - dominio/web
---

# CWE-434 - Unrestricted File Upload

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - File upload]]; las variantes en `600-tradecraft/`; los payloads en las matrices de `900-meta/`.

## Qué es

La aplicación permite subir un archivo sin restringir de forma efectiva su **tipo**, **nombre** o **ubicación**, de modo que el atacante sube algo peligroso: típicamente una webshell que el servidor ejecuta.

## Por qué existe

Porque validar subidas bien es difícil: la extensión, el `Content-Type` y hasta los magic bytes son controlables por el cliente, y cada capa de validación tiene un bypass. La mitigación real es una combinación (lista blanca de extensiones + renombrar + almacenar fuera del webroot + no ejecutar), y basta que falte una para que caiga.

## Ejes que la descomponen

Ver [[MOC - File upload]]. Resumen: validación evadida (extensión/MIME/magic bytes/contenido) × ejecución (¿cae y corre en el webroot?) × payload (webshell/polyglot/SVG-XSS) × impacto.

## Se encadena con file inclusion

Cuando el archivo subido **no se ejecuta** donde cae (fuera del webroot, o con extensión inofensiva), se combina con [[LFI - inclusión local]]: se incluye el archivo subido y ejecuta. Ver [[MOC - File inclusion]].

## Referencias canónicas

- [CWE-434](https://cwe.mitre.org/data/definitions/434.html)
- WSTG-BUSL-09 (Test Upload of Malicious Files)
- [[@portswigger-path-traversal-labs]]
