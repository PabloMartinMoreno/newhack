---
tipo: meta
aliases:
  - sondeo de caché
  - cache buster
  - detectar caché
tags:
  - meta/referencia
  - dominio/web
---

# Web cache - matriz de sondeo

> [!info] Referencia pura, no un zettel
> Detectar la caché, medir qué guarda y encontrar el hueco, sin envenenar a nadie. Las entradas y payloads están en [[Web cache entradas sin clave - matriz de referencia]]; el criterio, en [[MOC - Web cache]].

> [!danger] Sondear mal envenena a usuarios reales
> Una respuesta envenenada se sirve a **todos** los que pidan ese recurso hasta que expira. Usar siempre un **cache buster** —un parámetro único— mientras se prueba, de modo que solo se toque una entrada propia. Solo envenenar la entrada real con un payload inocuo y de forma acordada.

## 0. El cache buster

Un parámetro único que aísla las pruebas en su propia entrada de caché:

`?cb=1234` · `?fresh=aleatorio` · `?utm_source=xyz`

Cambiarlo en cada prueba da una entrada limpia cada vez. Sin él, la primera prueba envenena la entrada que pide todo el mundo.

## 1. ¿Hay caché, y qué guarda?

Mirar las cabeceras de respuesta:

```sh
curl -sI 'https://objetivo.com/?cb=1' | grep -iE 'cache|age|x-cache|cf-|via|x-served'
```

| Cabecera | Qué dice |
|---|---|
| `X-Cache: hit` / `miss` | Si vino de caché. La más directa |
| `Age: N` | Segundos que lleva guardada. `> 0` = cacheada |
| `Cache-Control` | Qué pidió el servidor: `public`, `max-age`, `private`, `no-store` |
| `X-Cache-Hits: N` | Cuántas veces se sirvió de caché |
| `CF-Cache-Status` | Cloudflare |
| `Via`, `X-Served-By` | Hay un intermediario (Varnish, Fastly, CDN) |

Confirmar la cacheabilidad: pedir dos veces con el mismo cache buster. Si la segunda trae `Age` mayor o `X-Cache: hit`, se cachea.

## 2. Mapear la clave de caché

Qué entra en la clave y qué no. Se cambia una parte de la petición y se mira si la respuesta viene de la misma entrada:

| Prueba | Si la respuesta es la misma entrada |
|---|---|
| Cambiar un parámetro `?x=1` → `?x=2` | El parámetro **no** está en la clave |
| Cambiar el `Host` | El host no está en la clave (raro) |
| Agregar una cabecera cualquiera | Las cabeceras no están en la clave (lo normal) |
| Cambiar mayúsculas de la ruta | La caché normaliza mayúsculas |
| Agregar `//` o `/./` a la ruta | La caché normaliza la ruta |

Lo que **no** está en la clave y **sí** cambia la respuesta es el hueco del envenenamiento. Ver [[Web cache - envenenamiento por entrada sin clave]].

## 3. Buscar entradas sin clave que se reflejen

Con el cache buster puesto, mandar cabezeras candidatas con un valor canario y buscar el canario en la respuesta:

```
X-Forwarded-Host: canario.com
X-Forwarded-Scheme: nothttps
X-Host: canario.com
X-Forwarded-Server: canario.com
X-Original-URL: /canario
```

Si `canario` aparece en la respuesta —en un enlace, una redirección, una etiqueta—, esa cabecera es sin clave y se refleja: es explotable. El catálogo completo está en [[Web cache entradas sin clave - matriz de referencia]].

Automatizar con **Param Miner** (extensión de Burp): descubre cabeceras y parámetros sin clave probando cientos.

## 4. Medir la ventana

Antes de envenenar la entrada real hay que saber cuánto dura y qué la refresca:

| Dato | Cómo |
|---|---|
| Tiempo de vida | El `max-age` de `Cache-Control`, o medir cuándo `Age` vuelve a cero |
| Momento de guardado | Cachea en el primer `miss`: la primera petición sin buster tras expirar |
| Qué la purga | Probar `PURGE`, o esperar el vencimiento |

Envenenar justo después de que la entrada expira maximiza el tiempo servido. Es información operativa que decide el impacto real.

## 5. Sondeo del engaño de caché

Para [[Web cache - engaño de caché]], la dirección opuesta. Se prueba con la propia cuenta:

1. Autenticado, pedir `https://objetivo.com/cuenta/perfil.css` (u otra página privada con sufijo estático).
2. Ver si devuelve la página privada —el servidor ignoró el sufijo— y si la respuesta trae señales de cacheo (`X-Cache`, `Age`).
3. Cerrar sesión o desde otra sesión, pedir la misma URL.
4. Si vuelven los datos privados, la caché guardó lo personalizado: confirmado, sin tocar a nadie.

Sufijos a probar en el paso 1: en [[Web cache entradas sin clave - matriz de referencia]] § confusión de ruta.

## 6. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| Ninguna cabecera de caché | Puede no haber caché, o no exponerla. Probar dos peticiones y comparar `Age` |
| El canario no se refleja con ninguna cabecera | No hay entrada sin clave reflejada. Probar el catálogo entero antes de descartar |
| Se refleja pero no se cachea | La respuesta con esa cabecera trae `Cache-Control: no-store`. Buscar otra ruta |
| El payload queda en la clave | La entrada sí está en la clave. Ir a [[Web cache - manipulación de la clave]] |
| Envenené y no se sirve a la segunda petición | El buster sigue puesto, o la entrada ya expiró. Revisar la ventana |
| El engaño devuelve `404` con el sufijo | El servidor no ignora el sufijo. Probar otro delimitador |
| El engaño no cachea la página privada | La caché mira el `Content-Type`, no la extensión. Buena mitigación |

## Relacionadas

[[MOC - Web cache]] · [[Web cache entradas sin clave - matriz de referencia]] · [[CWE-349 - Acceptance of Extraneous Untrusted Data With Trusted Data]]
