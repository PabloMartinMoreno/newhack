---
tipo: tecnica
taxonomia: cwe
identificador: CWE-352
wstg: WSTG-SESS-05
tacticas: []
aliases:
  - CWE-352
  - CSRF
  - falsificación de petición en sitio cruzado
  - XSRF
tags:
  - dominio/web
---

# CWE-352 - Cross-Site Request Forgery

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - CSRF]]; las variantes en `600-tradecraft/`; los payloads en [[CSRF entrega - matriz de referencia]].

## Qué es

La aplicación no distingue una petición que el usuario **quiso** hacer de una que su navegador hizo porque otra página se lo pidió. El navegador adjunta las cookies de sesión a toda petición dirigida al dominio, sin importar quién la originó; si el servidor solo mira la cookie, una página del atacante puede accionar en nombre de la víctima.

El atacante no ve la respuesta. Ejecuta una acción a ciegas.

## Por qué es distinta del resto del vault

En casi todos los demás dominios se rompe algo: un parser, un intérprete, una comparación. Acá **no se rompe nada**. La petición es sintácticamente perfecta, la sesión es legítima, la respuesta es `200`, y el registro del servidor la ve idéntica a cualquier otra.

Es el mismo problema conceptual que [[CWE-862 - Missing Authorization]]: lo único fuera de lugar es la intención detrás de la petición, y la intención no viaja en el protocolo. Por eso la defensa no puede ser validar la entrada — hay que agregar al protocolo una prueba de que la petición nació en la propia aplicación.

## Las tres pruebas posibles, y qué prueba cada una

| Defensa | Qué demuestra | Qué no cubre |
|---|---|---|
| Token sincronizador | Que quien manda la petición pudo **leer** una página de la aplicación | Nada, si el token no se liga a la sesión |
| `SameSite` en la cookie | Que la navegación no vino de otro sitio | Subdominios, y navegación de nivel superior con `Lax` |
| `Origin` / `Referer` | De qué origen partió la petición | Peticiones sin esas cabeceras |

La primera es la única que es una defensa por diseño; las otras dos son propiedades del navegador de las que la aplicación depende. Esa distinción es la que ordena todo el dominio: una defensa se rompe encontrando un fallo de implementación, las otras dos se rompen encontrando un caso que el navegador trata distinto.

## Por qué sigue existiendo con `SameSite` por defecto

Desde 2020 los navegadores tratan una cookie sin atributo como `SameSite=Lax`, y eso mató la mayor parte del CSRF clásico por POST. Quedaron vivos cuatro casos, y son los que ocupan el dominio:

1. Acciones que aceptan **`GET`** — `Lax` permite la navegación de nivel superior.
2. Cookies con **`SameSite=None`** explícito, que abundan porque las necesita cualquier integración de terceros.
3. Peticiones desde un **subdominio o sitio hermano**, que para `SameSite` no son "otro sitio".
4. Aplicaciones que **no dependen de cookies** sino de una cabecera de autorización, donde `SameSite` no aplica y la defensa vuelve a ser el token.

Dar el dominio por muerto es el error caro: lo que cambió es dónde está, no si está.

## Referencias canónicas

- [CWE-352](https://cwe.mitre.org/data/definitions/352.html)
- WSTG-SESS-05
- OWASP Top 10 — A01 Broken Access Control
