---
tipo: tecnica
taxonomia: cwe
identificador: CWE-349
wstg: WSTG-INPV-17
tacticas: []
aliases:
  - CWE-349
  - web cache poisoning
  - envenenamiento de caché
  - unkeyed input
tags:
  - dominio/web
---

# CWE-349 - Acceptance of Extraneous Untrusted Data With Trusted Data

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - Web cache]]; sondear la caché, en [[Web cache - matriz de sondeo]]; las entradas sin clave, en [[Web cache entradas sin clave - matriz de referencia]].

## Qué es

Una caché web guarda una respuesta y la reparte a todos los que pidan lo mismo. Para saber qué es "lo mismo" usa una **clave de caché**: normalmente el método, el host y la ruta. Lo que no entra en la clave —una cabecera, un parámetro, una cookie— es **sin clave**: no cambia qué entrada se guarda o se sirve, pero **sí** puede cambiar el contenido de la respuesta.

El envenenamiento explota esa brecha: se encuentra una entrada sin clave que influye en la respuesta, se le mete un payload, y la respuesta envenenada queda guardada. A partir de ahí la caché la sirve a **todos** los que pidan esa página, sin que ninguno haya mandado el payload.

## Por qué el nombre de la CWE describe el fallo

"Aceptación de datos externos no confiables junto con datos confiables" es exactamente la mecánica: la respuesta cacheada mezcla lo que sí está en la clave —confiable, lo que identifica el recurso— con lo que no —la entrada sin clave que el atacante controló—. La caché trata a las dos como parte del mismo recurso, y ahí está el error.

## Por qué amplifica en vez de crear

El envenenamiento rara vez es una vulnerabilidad sola: es un **multiplicador**. Lo que se cachea suele ser el resultado de otra clase —un XSS reflejado, una redirección abierta, una importación de script— que sin la caché afectaría solo a quien mande el payload. La caché lo convierte en un ataque a todos los usuarios y persistente:

| Lo que se cachea | Se vuelve |
|---|---|
| Un XSS reflejado en una cabecera sin clave | XSS almacenado, servido a todos — [[MOC - Cross-site scripting]] |
| Una redirección que refleja `X-Forwarded-Host` | Redirección abierta masiva — [[CWE-601 - URL Redirection to Untrusted Site]] |
| Una etiqueta de script con host sin clave | Importación de JavaScript del atacante |
| Una respuesta de error grande o rota | Denegación de servicio del recurso |

Por eso la severidad depende de dos cosas a la vez: qué entrada sin clave se encontró, y qué se puede reflejar con ella.

## Por qué la mitigación es de configuración

No se filtra entrada: la petición envenenadora es válida. La mitigación es alinear la clave de caché con lo que de verdad afecta la respuesta:

- **No cachear** respuestas que dependan de cabeceras que no están en la clave.
- **Incluir en la clave** toda entrada que influya en el contenido, o dejar de reflejarla.
- Desactivar el soporte de cabeceras que la aplicación no usa —`X-Forwarded-Host`, `X-Original-URL`— que los frameworks aceptan por defecto.

## Referencias canónicas

- [CWE-349](https://cwe.mitre.org/data/definitions/349.html)
- WSTG-INPV-17
- OWASP — Web Cache Poisoning
