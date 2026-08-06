---
tipo: meta
aliases:
  - DOM XSS sinks
  - sources y sinks
tags:
  - meta/referencia
  - dominio/web
---

# XSS sources y sinks - matriz de referencia

> [!info] Referencia pura, no un zettel
> El mapa de [[XSS - DOM-based]]: qué **source** controla el atacante y qué **sink** ejecuta. La explotación es encontrar un flujo `source → sink` sin sanitización en el medio. `yi``  ` copia el fragmento.

## Sources — lo que controla el atacante

`location.hash`
El fragmento `#...`. **No se envía al servidor** — por eso el DOM XSS por hash no deja rastro en logs.

`location.search` / `location.href`
Query string y URL completa. Sí llega al server, pero el bug es cliente.

`document.referrer`
La URL de donde vino la víctima — controlable armando el enlace desde un sitio propio.

`window.name`
Persiste entre navegaciones; se puede setear desde otra página antes de redirigir.

`postMessage` (`event.data`)
Mensaje de otra ventana/iframe. Explotable si el handler no valida `event.origin`.

`localStorage` / `sessionStorage`
Si otro flujo (o un XSS previo) escribió ahí datos que después se leen a un sink.

## Sinks — lo que ejecuta

Ejecución directa de código:

`eval(x)` / `setTimeout(x)` / `setInterval(x)` / `Function(x)`
Ejecutan el string como JS. Payload directo: `alert(1)`.

`element.innerHTML = x` / `outerHTML` / `insertAdjacentHTML`
Interpretan HTML. `<script>` NO ejecuta acá — usar `<img src=x onerror=alert(1)>`.

`document.write(x)` / `document.writeln(x)`
Escriben HTML crudo al documento. `<script>` sí ejecuta acá si se escribe durante la carga.

`element.setAttribute('href', x)` / `a.href = x` / `location = x`
Navegación: payload `javascript:alert(1)`.

`jQuery: $(x)` / `.html(x)` / `.append(x)`
`$('#'+location.hash)` es un patrón clásico de DOM XSS.

`element.src` (script) / `element.onevent = x`
Cargar un script atacante o asignar un handler.

## Explotación por sink

`innerHTML`  ←  `<img src=x onerror=alert(document.domain)>`
El caso más común. Los `<script>` no corren, los handlers sí.

`document.write`  ←  `<script>alert(document.domain)</script>`
Acá sí corre el script directo.

`eval` / `Function`  ←  `alert(document.domain)`
Sin HTML: es JS puro, se ejecuta tal cual.

`location` / `href`  ←  `javascript:alert(document.domain)`
El esquema `javascript:` ejecuta al navegar.

## Cómo se rastrea

```
1. DevTools → Sources → buscar los sinks: innerHTML, eval, document.write, location
2. Poner breakpoint en el sink
3. Cargar la página con un marcador en la source (#zzq123)
4. Ver si el marcador llega al sink sin pasar por encode/sanitize
5. Si llega crudo → construir el payload según el sink (tabla de arriba)
```

`sources & sinks` de DevTools o extensiones como DOM Invader (Burp) automatizan el paso 1-4.

## Relacionadas

[[XSS - DOM-based]] · [[MOC - Cross-site scripting]] · [[XSS contextos - matriz de referencia]]
