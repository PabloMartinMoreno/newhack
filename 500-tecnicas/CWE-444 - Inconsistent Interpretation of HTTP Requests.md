---
tipo: tecnica
taxonomia: cwe
identificador: CWE-444
wstg: WSTG-INPV-15
tacticas: []
aliases:
  - CWE-444
  - HTTP request smuggling
  - request smuggling
  - desincronización HTTP
tags:
  - dominio/web
---

# CWE-444 - Inconsistent Interpretation of HTTP Requests

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - Request smuggling]]; detectar la desincronización, en [[Request smuggling - matriz de sondeo]]; explotarla, en [[Request smuggling - matriz de explotación]].

## Qué es

Casi ninguna aplicación web habla directo con el cliente: hay una cadena de servidores —un balanceador, un proxy inverso, un CDN, un WAF— por delante del servidor de aplicación. Todos leen la misma petición, y el ataque explota que **dos de ellos determinen dónde termina esa petición de forma distinta**.

Si el servidor de adelante cree que la petición termina en un punto y el de atrás cree que termina en otro, lo que sobra —lo que el de adelante consideró parte de esta petición y el de atrás no— queda al principio de **la siguiente petición**. El atacante controla ese sobrante, y con él antepone datos a la petición de otra persona.

## De qué depende el largo, y por qué se puede desincronizar

HTTP/1.1 tiene dos formas de decir dónde termina el cuerpo, y ese es el origen de todo:

- **`Content-Length`** — un número de bytes.
- **`Transfer-Encoding: chunked`** — el cuerpo llega en trozos con su tamaño, y termina con un trozo de tamaño cero.

Si una petición trae las dos y cada servidor de la cadena prioriza una distinta —o si una de las dos se ofusca para que un servidor la vea y el otro no—, los dos leen largos diferentes. La especificación dice qué hacer, pero los servidores no coinciden, y esa discrepancia es la vulnerabilidad.

HTTP/2 lo resolvía —lleva el largo en el propio protocolo— pero introdujo un problema nuevo: cuando el servidor de adelante habla HTTP/2 con el cliente y **lo degrada a HTTP/1.1** para hablar con el de atrás, tiene que reconstruir las cabeceras de largo, y si lo hace mal reaparece la ambigüedad.

## Por qué es de las más graves de la web

El ataque no toca la aplicación: toca la **infraestructura compartida**, y por eso su alcance es distinto de todo lo demás del vault:

- Afecta a **otros usuarios**, no solo al atacante. Se antepone a la petición de la víctima, se roba su sesión, se le sirve una respuesta que no pidió.
- **Saltea los controles del frente.** Un WAF o una regla de autorización en el proxy solo ven la petición como la interpretan ellos; lo escondido en el sobrante llega al back sin pasar por ese control.
- Es **persistente** cuando se combina con caché: una respuesta envenenada queda servida a todos.

## Por qué la mitigación es de arquitectura

No se filtra ni se valida entrada, porque la petición maliciosa es sintácticamente válida — el problema es que es válida de **dos maneras**. La mitigación es estructural:

- Usar **HTTP/2 de extremo a extremo**, sin degradar al back.
- Que el servidor de adelante **normalice** las peticiones ambiguas —rechazar las que traen `Content-Length` y `Transfer-Encoding` a la vez— antes de reenviarlas.
- Que front y back sean el mismo software con la misma interpretación, lo que en la práctica casi nunca ocurre.

## Referencias canónicas

- [CWE-444](https://cwe.mitre.org/data/definitions/444.html)
- WSTG-INPV-15
- RFC 7230 § 3.3.3 — precedencia de `Transfer-Encoding` sobre `Content-Length`
- RFC 9113 — HTTP/2, y el problema de la degradación
