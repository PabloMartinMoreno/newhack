---
tipo: tecnica
taxonomia: cwe
identificador: CWE-918
wstg: WSTG-INPV-19
tacticas: []
aliases:
  - CWE-918
  - SSRF
  - Falsificación de petición del lado del servidor
tags:
  - dominio/web
---

# CWE-918 - Server-Side Request Forgery

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - SSRF]]; las variantes en `600-tradecraft/`; los payloads en las matrices de `900-meta/`.

## Qué es

La aplicación hace una petición de red a un destino que el atacante controla, total o parcialmente. El servidor se convierte en el cliente HTTP del atacante.

## Por qué existe

Porque las aplicaciones modernas necesitan traer cosas por URL —previsualizar un enlace, importar una imagen, llamar a un webhook, renderizar un PDF, validar un feed— y la URL viene del usuario. El error no es hacer la petición: es no acotar **a dónde**.

## Por qué importa más de lo que parece

Un SSRF no vale por la petición: vale por **desde dónde** sale. El servidor está adentro del perímetro, y esa posición le da tres cosas que el atacante no tiene:

- **Alcance de red** — servicios internos sin exposición pública, que casi siempre confían en quien los llama porque asumen que el perímetro filtra.
- **Identidad** — el servidor tiene credenciales de instancia, tokens de servicio y reglas de firewall a su nombre. En la nube, esto es lo que convierte un SSRF en compromiso de la cuenta.
- **Confianza implícita** — muchos servicios internos no autentican en absoluto. La autenticación era el perímetro, y el SSRF acaba de saltarlo.

Por eso la severidad se calcula por destino alcanzable, no por la existencia de la petición.

## Relación con otras clases

- [[CWE-98 - File Inclusion]] — [[RFI - inclusión remota]] **es** un SSRF cuyo resultado, además de traerse, se ejecuta. La diferencia es qué hace la app con la respuesta.
- [[CWE-611 - XML External Entity]] — un parser XML con entidades externas habilitadas es una máquina de SSRF: ver [[File upload - XXE por archivo]].
- **CSRF no es lo mismo, y confundirlos es frecuente.** En CSRF la petición la hace el **navegador de la víctima**, y el atacante aprovecha las cookies de esa víctima. En SSRF la hace el **servidor**, y el atacante aprovecha su posición de red. Distinto actor, distinta defensa: los tokens anti-CSRF no hacen nada acá.

## La mitigación real

Lista **blanca** de destinos, resuelta y validada después de seguir redirecciones, con la conexión atada a la IP ya validada. Todo lo demás falla:

- Lista negra de rangos — hay demasiadas formas de escribir la misma IP; ver [[SSRF evasión - matriz de referencia]].
- Validar la URL antes de pedirla — se rompe con una redirección o con DNS rebinding.
- Filtrar solo por nombre de dominio — un dominio propio puede resolver a `127.0.0.1`.

Complementos que sí ayudan: deshabilitar todo esquema que no sea `http`/`https`, no seguir redirecciones, aislar el componente que hace las peticiones en su propio segmento de red, y exigir IMDSv2 en la nube.

## Ejes que la descomponen

Ver [[MOC - SSRF]] para la tabla completa y los árboles. Resumen: retorno × destino × esquema × bypass del filtro × impacto.

## Referencias canónicas

- [CWE-918](https://cwe.mitre.org/data/definitions/918.html)
- WSTG-INPV-19
