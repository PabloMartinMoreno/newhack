---
tipo: tecnica
taxonomia: cwe
identificador: CWE-98
wstg: [WSTG-ATHZ-01, WSTG-INPV-11, WSTG-INPV-12]
tacticas: []
aliases:
  - CWE-98
  - CWE-22
  - File Inclusion
  - Inclusión de archivos
tags:
  - dominio/web
---

# CWE-98 - File Inclusion

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - File inclusion]]; las variantes en `600-tradecraft/`; los payloads en las matrices de `900-meta/`.

## Qué es

La aplicación arma una ruta de archivo con entrada del usuario y la **incluye, lee o ejecuta** sin restringir a qué archivo apunta. Según qué haga la app con la ruta, el impacto va de leer un archivo arbitrario a ejecutar código.

## Por qué existe

Porque el parámetro que debía elegir entre un conjunto cerrado de archivos (`?page=home`) se pasa directo a `include`/`require`/`file_get_contents` sin validar. En PHP el problema es peor: `include` **ejecuta** lo que incluye, así que leer un archivo con código PHP lo corre.

## Ejes que la descomponen

Ver [[MOC - File inclusion]]. Resumen: tipo (LFI/RFI/path traversal) × wrapper PHP × vía a RCE × obstáculo.

## Dos CWE bajo el mismo dominio

- **CWE-22** — path traversal: leer archivos fuera del directorio previsto (solo lectura).
- **CWE-98** — file inclusion en PHP: la ruta se pasa a `include`/`require`, que ejecuta. LFI (local) y RFI (remoto).

La diferencia práctica: traversal **lee**, inclusion **ejecuta**. Identificador canónico por WSTG: `WSTG-ATHZ-01` (traversal), `WSTG-INPV-11` (LFI), `WSTG-INPV-12` (RFI).

## Se encadena con file upload

El combo clásico: subís un archivo con código pero cae fuera del webroot y no se ejecuta; lo **incluís con LFI** y ejecuta. Ver [[MOC - File upload]] § combo con LFI.

## Referencias canónicas

- [CWE-98](https://cwe.mitre.org/data/definitions/98.html) · [CWE-22](https://cwe.mitre.org/data/definitions/22.html)
- WSTG-ATHZ-01, WSTG-INPV-11/12
- [[@portswigger-path-traversal-labs]]
