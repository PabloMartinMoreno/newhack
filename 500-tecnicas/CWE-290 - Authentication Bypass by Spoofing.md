---
tipo: tecnica
taxonomia: cwe
identificador: CWE-290
wstg: WSTG-ATHN-01
tacticas: []
aliases:
  - CWE-290
  - authentication bypass by spoofing
  - bypass por confianza en cabeceras
tags:
  - dominio/web
---

# CWE-290 - Authentication Bypass by Spoofing

> [!note] Nota paraguas
> Sin contenido operativo. Su uso vía cabeceras vive en [[Host header - bypass de acceso por confianza]]; el reconocimiento, en [[Host header cabeceras de confianza - matriz de referencia]].

## Qué es

La aplicación toma una decisión de seguridad —conceder acceso, saltar autenticación, confiar en un origen— basándose en un dato que el atacante controla y que **parece** venir de una fuente confiable. Spoofear ese dato es suficiente para pasar el control.

El caso canónico en web: la aplicación restringe `/admin` a "peticiones internas" y decide si una petición es interna mirando una cabecera —`X-Forwarded-For: 127.0.0.1`, `Host: localhost`, `X-Real-IP`—. Como esas cabeceras las pone el cliente, el atacante las falsifica y la aplicación lo trata como interno.

## Por qué es la clase del abuso de cabeceras de confianza

Un proxy inverso o un balanceador agregan cabeceras `X-Forwarded-*` para decirle a la aplicación de dónde vino la petición. La aplicación las lee como verdad porque en su modelo mental vienen del proxy. El fallo es que **el atacante también puede ponerlas**, y si la aplicación no distingue las que agregó el proxy de las que trajo el cliente, confía en un dato spoofeado.

Es el mismo patrón que [[CWE-1385 - Missing Origin Validation in WebSockets]] con el `Origin` y que [[CWE-942 - Permissive Cross-domain Policy with Untrusted Domains]] con el reflejo: confiar en un valor que el cliente controla. Acá el valor es una cabecera de reenvío o el `Host`, y la decisión que gobierna es de acceso.

## Por qué la mitigación es no confiar en el cliente

- **No decidir acceso** por cabeceras que el cliente puede poner. La identidad y la autorización van por la sesión, no por `X-Forwarded-For`.
- Si un proxy agrega cabeceras de confianza, que las **sobrescriba** —borrando las que trajo el cliente— antes de reenviar, y que la aplicación solo confíe en las que vienen del proxy conocido.
- Validar el `Host` contra una lista blanca y no usarlo para decisiones de seguridad ni para construir URLs.

## Referencias canónicas

- [CWE-290](https://cwe.mitre.org/data/definitions/290.html)
- [CWE-348](https://cwe.mitre.org/data/definitions/348.html) — Use of Less Trusted Source, la vecina
- WSTG-ATHN-01
- OWASP — Testing for Host Header Injection
