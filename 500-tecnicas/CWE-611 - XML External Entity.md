---
tipo: tecnica
taxonomia: cwe
identificador: CWE-611
wstg: WSTG-INPV-07
tacticas: []
aliases:
  - CWE-611
  - XXE
  - Entidad externa XML
tags:
  - dominio/web
---

# CWE-611 - XML External Entity

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - XXE]]; las variantes en `600-tradecraft/`; los payloads en las matrices de `900-meta/`.

## Qué es

El parser de XML resuelve **entidades externas** declaradas en el documento que recibe. Una entidad es un marcador que el parser reemplaza por contenido; si ese contenido puede venir de una URL o de una ruta del sistema de archivos, quien controla el XML controla qué se lee y a dónde se conecta el servidor.

## Por qué existe

No es un fallo de implementación: es una **función documentada de la especificación de XML**, que nació como formato de documentos con inclusiones por referencia. Que resolver entidades externas sea peligroso no fue un descuido, fue un cambio de contexto — el formato pasó de describir documentos a transportar datos entre servicios, y la característica se quedó.

Por eso la vulnerabilidad aparece donde nadie la busca: en el parser por defecto de una biblioteca vieja, no en código que alguien escribió mal.

## Las tres piezas que hay que distinguir

El dominio se vuelve confuso si se mezclan, y son cosas distintas:

- **Entidad general externa** — `&nombre;` en el cuerpo del documento. Es la forma clásica, y solo sirve si el valor termina reflejado en la respuesta.
- **Entidad de parámetro** — `%nombre;` dentro de la DTD. No aparece en el cuerpo, pero permite construir otras entidades dinámicamente. Es lo que hace posible la exfiltración fuera de banda y por error, y por eso es la pieza que convierte un XXE ciego en explotable.
- **XInclude** — no es una entidad. Es otro mecanismo, de otra especificación, que pide un recurso externo. Importa porque **funciona sin declarar un DOCTYPE**, que es justo lo que queda cuando la aplicación inserta la entrada del usuario dentro de un XML propio.

## Qué se obtiene

Lectura de archivos del servidor y, casi siempre, [[CWE-918 - Server-Side Request Forgery]]: un parser con entidades externas habilitadas es una máquina de hacer peticiones desde adentro del perímetro. En la práctica el segundo impacto suele valer más que el primero.

RCE es posible pero raro, y depende de módulos poco habituales. Denegación de servicio por expansión recursiva de entidades es trivial de lograr y casi siempre está fuera de alcance: rompe el servicio.

## La mitigación real

Deshabilitar el procesamiento de DTD en el parser. Una línea de configuración por biblioteca, y cierra la clase entera — entidades, DTD externa y expansión recursiva de una sola vez.

Los parsers modernos ya vienen así, y esa es la razón por la que el XXE aparece cada vez más en **componentes viejos** que en código nuevo: bibliotecas antiguas, servicios SOAP heredados, procesadores de documentos de oficina y de SVG.

Si el DTD tiene que quedar habilitado, deshabilitar al menos las entidades externas y la resolución de DTD externa. Filtrar la cadena `<!ENTITY` no es una mitigación: hay demasiadas codificaciones.

## Ejes que la descomponen

Ver [[MOC - XXE]] para la tabla completa y los árboles. Resumen: canal × mecanismo × obstáculo × impacto.

## Referencias canónicas

- [CWE-611](https://cwe.mitre.org/data/definitions/611.html)
- [CWE-776](https://cwe.mitre.org/data/definitions/776.html) — expansión recursiva de entidades
- WSTG-INPV-07
