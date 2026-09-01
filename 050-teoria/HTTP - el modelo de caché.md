---
tipo: teoria
habilita: ["[[Web cache - envenenamiento por entrada sin clave]]", "[[Web cache - engaño de caché]]", "[[Web cache - manipulación de la clave]]", "[[CWE-524 - Use of Cache Containing Sensitive Information]]"]
relacionadas: ["[[HTTP - el modelo de conexión]]"]
aliases:
  - cache key
  - HTTP caching
tags: []
---

# HTTP - el modelo de caché

## Qué dice la especificación

Una caché guarda una respuesta y la sirve a peticiones posteriores sin consultar al origen. Para eso necesita responder dos preguntas, y el protocolo las separa:

- **¿Esta petición es la misma que aquella?** Se decide por la **clave de caché**: método, esquema, host y ruta, más lo que `Vary` agregue. Todo lo que no entra en la clave es invisible para la caché aunque cambie la respuesta.
- **¿La respuesta sigue sirviendo?** Se decide por frescura: `Cache-Control`, `max-age`, `Expires`, validadores como `ETag`.

`Cache-Control: private` restringe el almacenamiento a la caché del navegador; `public` lo habilita en las compartidas. La distinción entre **caché privada y compartida** es la que decide si el daño alcanza a un usuario o a todos.

## Dónde el estándar deja lugar

La clave de caché es donde el estándar prácticamente se calla. Cada CDN e implementación decide qué normaliza y qué ignora:

- Cabeceras que **cambian la respuesta y no están en la clave** — `X-Forwarded-Host`, `X-Original-URL`, cabeceras propias de la aplicación.
- Partes de la URL que se descartan al armar la clave: parámetros de query, el fragmento, la extensión, los delimitadores que cada parser interpreta distinto.
- Discrepancia entre **qué considera un archivo estático la caché** y qué considera una ruta dinámica la aplicación. La caché ve `/perfil/foto.css` y decide guardar; la aplicación ignora el sufijo y devuelve el perfil de quien preguntó.

## Qué habilita

Los dos ataques del dominio son la misma discrepancia leída en direcciones opuestas:

- **Envenenamiento** — el atacante mete algo suyo en una respuesta que la caché guardará para otros, usando una entrada que la clave no cubre → [[Web cache - envenenamiento por entrada sin clave]] y [[Web cache - manipulación de la clave]].
- **Engaño** — el atacante logra que la caché guarde una respuesta privada de la víctima como si fuera estática, y después la lee → [[Web cache - engaño de caché]].

La consecuencia que ordena todo el dominio: **la caché convierte un efecto de una petición en un efecto persistente sobre terceros**. Es el multiplicador de alcance de cualquier otro bug de la cadena.

## Cómo se ve en la práctica

`X-Cache: hit/miss`, `Age` y `CF-Cache-Status` dicen si una respuesta salió de la caché, y son la base de todo sondeo del dominio. Del lado azul valen para lo mismo: un `hit` sobre una URL con parámetros que nadie más usa, o un `Age` alto en una ruta autenticada, son observables sin ver el payload.

## Fuente

RFC 9111 (HTTP Caching). La clave de caché, que es donde vive el ataque, es comportamiento de implementación y no está normada — ver [[Web cache - matriz de sondeo]].
