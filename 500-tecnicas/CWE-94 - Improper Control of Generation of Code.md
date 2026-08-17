---
tipo: tecnica
taxonomia: cwe
identificador: CWE-94
wstg: WSTG-INPV-15
tacticas: []
aliases:
  - CWE-94
  - code injection
  - XSLT injection
  - inyección de código
tags:
  - dominio/web
---

# CWE-94 - Improper Control of Generation of Code

> [!note] Nota paraguas
> Sin contenido operativo. Su uso en XSLT vive en [[MOC - XSLT injection]]; identificar el procesador, en [[XSLT - matriz de identificación]]; los payloads, en [[XSLT payloads - matriz de referencia]].

## Qué es

La aplicación genera código —o una estructura que un motor va a evaluar como código— mezclando entrada del usuario sin separarla de la lógica. El atacante aporta directivas que el motor ejecuta con los privilegios de la aplicación. Es la clase amplia de la que cuelgan las inyecciones que terminan en ejecución cuando el "sink" es un evaluador, no un intérprete de consultas.

## Por qué es la clase de la inyección de XSLT

XSLT es un lenguaje de **transformación**: toma un documento XML y una hoja de estilo con instrucciones, y produce una salida. Esas instrucciones son código —bucles, condiciones, llamadas a funciones—. Si la aplicación construye la hoja de estilo con entrada del usuario, o transforma un documento que el atacante controla, el atacante escribe instrucciones XSLT que el procesador ejecuta.

Es primo de [[CWE-1336 - Improper Neutralization of Special Elements Used in a Template Engine]] (SSTI): los dos son inyección en un lenguaje de plantilla/transformación evaluado del lado del servidor. La diferencia es que XSLT opera sobre XML y su capacidad depende del **procesador** —libxslt, Xalan, Saxon, el de .NET— y de si tiene habilitadas las funciones de extensión.

## Qué se consigue, según el procesador

| Capacidad | Cómo | Cruza con |
|---|---|---|
| Divulgación de versión | `system-property('xsl:vendor')` | reconocimiento |
| Lectura de archivos | `document()`, `unparsed-text()` | [[MOC - XXE]] |
| SSRF | `document('http://interno')` | [[MOC - SSRF]] |
| Ejecución de código | funciones de extensión (`php:function`, Java, .NET) | [[MOC - Command injection]] |

La ejecución de código es la capacidad más grave y la que hace a XSLT peligroso: varios procesadores permiten llamar funciones del lenguaje anfitrión —PHP, Java, .NET— desde la hoja de estilo, y eso es RCE directo si están habilitadas.

## Por qué la mitigación es acotar el procesador

- **No construir hojas de estilo con entrada del usuario** ni transformar documentos no confiables sin restringir el procesador.
- **Deshabilitar las funciones de extensión** —el acceso al lenguaje anfitrión— en el procesador. Es lo que corta la ejecución.
- **Deshabilitar `document()` y el acceso a recursos externos**, que cierra la lectura de archivos y el SSRF.
- Usar un procesador en modo restringido y validar la entrada.

## Referencias canónicas

- [CWE-94](https://cwe.mitre.org/data/definitions/94.html)
- [CWE-1336](https://cwe.mitre.org/data/definitions/1336.html) — SSTI, el primo por mecanismo
- WSTG-INPV-15
- OWASP — Testing for XSLT Injection
