---
tipo: tradecraft
clase: "[[CWE-918 - Server-Side Request Forgery]]"
eje: retorno
implementacion: "La respuesta del destino interno vuelve dentro de la respuesta HTTP"
opsec: ruidoso
telemetria: ["[[Conexión saliente del servidor de aplicación]]", "[[Log de acceso del servidor web]]"]
requisitos: [url-controlada, respuesta-reflejada]
coste: bajo
alternativas: ["[[SSRF - canal ciego]]"]
probado: nunca
contexto: [php8-linux]
aliases:
  - SSRF básico
  - basic SSRF
tags:
  - dominio/web
---

# SSRF - canal directo

## Cuándo lo elijo

Siempre primero, si existe. Es el caso feliz del árbol de [[MOC - SSRF]]: la aplicación trae una URL y **muestra lo que trajo** —una previsualización de enlace, un importador de datos, un validador de feed, un conversor de documentos—. Esa respuesta reflejada convierte al servidor en un proxy que se puede leer.

Antes de dar por ciego un SSRF hay que agotar las formas parciales de retorno: un mensaje de error que cita el cuerpo de la respuesta, un código de estado distinto, un tamaño de respuesta distinto, o un tiempo distinto. Cualquiera de esas convierte medio dominio en semiciego, que es mucho mejor que ciego.

## Por qué funciona

La aplicación ya está devolviendo el contenido que trae; solo estaba trayendo el contenido equivocado. No hay que construir ningún canal de salida: se reusa el que la app abrió sola, igual que en [[Command injection - canal directo]].

Lo que vuelve valioso a este canal no es leer una página externa —eso ya se podía hacer desde el navegador— sino leer lo que **solo el servidor alcanza**: `127.0.0.1`, la red interna, y el servicio de metadatos de la nube. La posición de red es el activo, no la petición.

## Cómo falla

- **La respuesta se parsea antes de mostrarse.** Si la app espera JSON y descarta lo que no lo sea, el contenido del destino interno se pierde en el camino. A veces se recupera pidiendo un endpoint interno que sí devuelva el formato esperado.
- **Solo se muestra un fragmento** — un título, una miniatura, un `og:image`. Hay canal, pero de pocos bytes por petición.
- **El cliente HTTP no sigue redirecciones** — corta la vía de bypass más simple.
- **Solo se permiten `http` y `https`** — cierra `file://` y `gopher://`, y con ellos la lectura local y [[SSRF - gopher a servicio interno]].
- **Lista blanca de dominios bien implementada** — validada después de resolver y de seguir redirecciones. Es la única defensa que aguanta; ver [[SSRF evasión - matriz de referencia]] para lo que sí se rompe.
- **Egress y tráfico interno segmentados** — hay SSRF y no hay nada alcanzable. Sigue siendo un hallazgo, con severidad mucho menor.

## Coste

El más bajo del dominio: una petición por destino, respuesta completa. Permite explorar la red interna de forma interactiva, casi como si se tuviera un navegador dentro del perímetro.

## Huella esperada

- [[Conexión saliente del servidor de aplicación]] hacia destinos que la aplicación nunca contacta. El indicador no es la conexión: es que el destino no está en la lista blanca de lo habitual.
- Conexiones a `127.0.0.1` o a rangos internos **no aparecen en telemetría de red perimetral**. Ese es el punto ciego que hace obligatoria la telemetría de host o de flujo interno.
- [[Log de acceso del servidor web]] tiene la URL del destino solo si viajó por GET, y solo si el parámetro no está codificado dos veces.
- Del otro lado: el **servicio interno alcanzado** también registra la petición, y ahí el origen es la IP del servidor de aplicación. Correlacionar ambos lados es la detección de mayor fidelidad del dominio.

Los destinos que vale la pena probar están en [[SSRF destinos - matriz de referencia]]; dónde suele nacer el SSRF, en [[SSRF superficies - matriz de referencia]].
