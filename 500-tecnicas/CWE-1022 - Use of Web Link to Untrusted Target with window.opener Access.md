---
tipo: tecnica
taxonomia: cwe
identificador: CWE-1022
wstg: WSTG-CLNT-11
tacticas: []
aliases:
  - CWE-1022
  - reverse tabnabbing
  - tabnabbing
  - secuestro de pestaña
tags:
  - dominio/web
---

# CWE-1022 - Use of Web Link to Untrusted Target with window.opener Access

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - Tabnabbing]]; la mecánica y los sinks, en [[Tabnabbing - matriz de referencia]].

## Qué es

Cuando una página abre otra en una pestaña nueva —un enlace con `target="_blank"`, un `window.open()`— la página nueva recibe una referencia a la que la abrió: `window.opener`. Si el enlace no lleva `rel="noopener"`, esa referencia queda viva, y la página abierta puede **navegar la pestaña original** a donde quiera con `window.opener.location = ...`.

El ataque —reverse tabnabbing— aprovecha eso: la víctima clickea un enlace que abre la página del atacante en una pestaña nueva; mientras la mira, el JavaScript del atacante redirige **la pestaña original** —que sigue abierta de fondo— a una copia de phishing del sitio legítimo. Cuando la víctima vuelve a la primera pestaña, ve una página que parece la del sitio en el que confiaba, pidiéndole que se autentique de nuevo.

## Por qué el navegador lo permite

`window.opener` existe para que ventanas del mismo origen se coordinen. El problema es que la referencia se pasa **también a orígenes cruzados**, y aunque un origen cruzado no puede **leer** la pestaña original —eso lo impide el mismo origen—, **sí puede navegarla**: escribir `opener.location` es una de las pocas operaciones cross-origin permitidas. Con eso alcanza para el phishing: no hace falta leer, solo redirigir.

## Por qué es hermano de clickjacking

Los dos son ataques del lado del cliente que abusan cómo el navegador maneja ventanas y marcos, y los dos terminan en engaño de la víctima —clickjacking con un clic disfrazado, tabnabbing con una pestaña cambiada por detrás—. Y comparten la característica que los define frente al resto del vault: **la defensa es prevención, no detección**. El servidor no ve el ataque; lo que hay es impedir que `window.opener` quede accesible.

## Por qué la mitigación es de atributo y cabecera

- **`rel="noopener"`** en todo enlace `target="_blank"` —o `rel="noopener noreferrer"`—. Corta la referencia `window.opener`. Los navegadores modernos lo aplican por defecto a `target="_blank"`, pero no todos y no siempre, y las integraciones viejas lo omiten.
- **`window.open(url, '_blank', 'noopener')`** para las aperturas por JavaScript.
- **`Cross-Origin-Opener-Policy: same-origin`** —COOP—, la defensa de cabecera que aísla el grupo de contexto de navegación y anula `window.opener` entre orígenes.
- **`Referrer-Policy`** para no filtrar además la URL de origen.

## Referencias canónicas

- [CWE-1022](https://cwe.mitre.org/data/definitions/1022.html)
- [CWE-1021](https://cwe.mitre.org/data/definitions/1021.html) — clickjacking, el hermano del lado del cliente
- WSTG-CLNT-11
- OWASP — Reverse Tabnabbing
