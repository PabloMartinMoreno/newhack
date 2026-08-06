---
tipo: tradecraft
clase: "[[CWE-434 - Unrestricted File Upload]]"
eje: impacto
implementacion: "Subir un archivo XML (SVG/DOCX) con entidad externa que el parser resuelve"
opsec: requiere-bypass
telemetria: ["[[Log de acceso del servidor web]]", "[[Consulta DNS saliente]]"]
requisitos: [parser-xml-en-el-server, entidades-externas-habilitadas]
coste: medio
alternativas: ["[[File upload - SVG y XSS almacenado]]"]
probado: 2026-08-06
contexto: [php8]
aliases:
  - XXE por archivo
  - XXE via upload
tags:
  - dominio/web
---

# File upload - XXE por archivo

## Cuándo lo elijo

Cuando la app **parsea del lado servidor** un archivo basado en XML que subo —un SVG que rasteriza, un DOCX/XLSX que procesa, un XML que importa— y ese parser resuelve entidades externas. A diferencia del SVG-XSS (que ejecuta en el cliente), acá el ataque es contra el **servidor**: leer archivos, SSRF, exfil.

Es distinto de [[File upload - SVG y XSS almacenado]]: aquel necesita que el SVG se **sirva** a un navegador; este necesita que se **parsee** en el server.

> [!note] XXE es su propio dominio
> Esta nota cubre XXE **por la vía de subida de archivos**. XXE completo (CWE-611: parámetro XML directo, blind XXE, XInclude, SOAP) es un dominio aparte, todavía sin modelar en el vault. Roadmap.

## Por qué funciona

Un parser XML con resolución de entidades externas habilitada procesa `<!ENTITY xxe SYSTEM "file:///etc/passwd">` y sustituye la entidad por el contenido del archivo. Como muchos formatos "de imagen" u "ofimáticos" son XML por dentro (SVG, DOCX = zip de XML), la app los parsea creyendo que valida una imagen o un documento, y ahí resuelve la entidad.

## Cómo falla

- **El parser tiene deshabilitadas las entidades externas** — el default seguro en librerías modernas.
- **No hay parseo server-side** — si el SVG solo se sirve, no se resuelve nada (ahí va SVG-XSS).
- **Sin egress** para la variante out-of-band / blind.
- **Salida no reflejada** — obliga a blind XXE (exfil por DTD externa + OOB), más trabajoso.

## Coste

Medio: hay que identificar qué archivo se parsea y si el parser resuelve entidades. Confirmado eso, la lectura de archivos o el SSRF es directo. Blind XXE (sin salida) sube el costo.

## Huella esperada

- El archivo XML/SVG/DOCX malicioso en disco.
- Si es out-of-band: el server hace una petición saliente a mi DTD/endpoint → [[Consulta DNS saliente]] + conexión desde la IP del server.

Payloads en [[File upload - archivos maliciosos - matriz de referencia]].
