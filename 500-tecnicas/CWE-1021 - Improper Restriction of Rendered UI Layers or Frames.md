---
tipo: tecnica
taxonomia: cwe
identificador: CWE-1021
wstg: WSTG-CLNT-09
tacticas: []
aliases:
  - CWE-1021
  - clickjacking
  - UI redressing
  - secuestro de clic
tags:
  - dominio/web
---

# CWE-1021 - Improper Restriction of Rendered UI Layers or Frames

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - Clickjacking]]; encuadrar el objetivo, en [[Clickjacking - encuadre - matriz de referencia]]; la superposición, en [[Clickjacking - superposición - matriz de referencia]].

## Qué es

La aplicación permite que otra página la **incruste en un marco** (`iframe`). El atacante carga el sitio objetivo en un marco transparente, lo pone encima de su propia página con un señuelo debajo —"hacé clic para ganar"—, y alinea el señuelo con un botón sensible del objetivo. La víctima cree que hace clic en el señuelo; en realidad hace clic en el botón del objetivo, con su sesión activa.

Es engaño de la interfaz —UI redressing—: el clic es real y autenticado, pero la víctima no sabe qué está clickeando.

## Por qué es distinto del resto del vault

Casi todos los demás dominios atacan el **servidor**: un payload, una consulta, una petición. Clickjacking ataca la **percepción del usuario**. El objetivo no procesa nada malicioso —la petición que resulta del clic es perfectamente legítima—; lo que se manipula es qué cree la víctima que está haciendo.

Consecuencias que ordenan el dominio:

- **No hay payload en el servidor.** El objetivo recibe un clic normal de un usuario autenticado.
- **La víctima es el objetivo, no el servidor.** El ataque vive en la página del atacante.
- **La defensa es prevención, no detección.** No hay nada que detectar en el servidor de forma fiable; lo que hay es impedir el encuadre.

## Por qué es primo de CSRF

Los dos hacen que la víctima **ejecute una acción que no quiso**. La diferencia es el mecanismo: [[CWE-352 - Cross-Site Request Forgery]] **falsifica la petición**; clickjacking **engaña el clic** que la genera. Por eso las dos apuntan a las mismas acciones —cambiar el correo, autorizar un pago, aprobar un consentimiento de OAuth— y comparten el techo de severidad: dependen de una víctima autenticada que interactúe.

La diferencia práctica es que clickjacking sortea las defensas de CSRF: el token anti-CSRF viaja en la petición real que el clic genera, así que está presente y válido. Un formulario protegido contra CSRF sigue siendo vulnerable a clickjacking.

## Por qué la mitigación es de cabecera

No se filtra entrada: la mitigación es **impedir que el sitio se cargue en un marco ajeno**.

- **`Content-Security-Policy: frame-ancestors`** con la lista de orígenes permitidos —o `'none'`—. Es la defensa moderna y la que hay que recomendar.
- **`X-Frame-Options: DENY`** o `SAMEORIGIN`, la defensa vieja, todavía útil por compatibilidad.
- Los **frame-busters** por JavaScript —código que detecta el marco y rompe— son la defensa más débil: se anulan con el atributo `sandbox` del marco.

## Referencias canónicas

- [CWE-1021](https://cwe.mitre.org/data/definitions/1021.html)
- [CWE-352](https://cwe.mitre.org/data/definitions/352.html) — CSRF, el primo
- WSTG-CLNT-09
- OWASP — Clickjacking Defense Cheat Sheet
