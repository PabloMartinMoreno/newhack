---
tipo: tradecraft
clase: "[[CWE-434 - Unrestricted File Upload]]"
eje: impacto
implementacion: "Subir un SVG con script; al servirse ejecuta como XSS almacenado"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]", "[[Informe de violación de CSP]]"]
requisitos: [acepta-svg, se-sirve-inline]
coste: bajo
alternativas: ["[[File upload + LFI]]"]
probado: 2026-08-06
contexto: [chrome]
aliases:
  - SVG XSS
  - XSS por SVG
tags:
  - dominio/web
---

# File upload - SVG y XSS almacenado

## Cuándo lo elijo

Cuando la subida acepta imágenes pero **no da RCE** —el archivo no se ejecuta como código en el server— y aun así quiero impacto. Un SVG es XML, y el XML permite `<script>`: si el server lo acepta como imagen y lo sirve inline, el navegador lo ejecuta. Es [[XSS - almacenado]] entregado por la vía de subida.

Aplica cuando el filtro valida "es una imagen" y el SVG pasa (es una imagen válida) pero contiene JS.

## Por qué funciona

El SVG es un formato vectorial basado en XML; soporta `<script>` y handlers como `onload`. Servido con `Content-Type: image/svg+xml` **en el mismo origen** y renderizado inline (no como descarga), el navegador ejecuta ese script con el origen del sitio. La validación "es imagen" no ayuda: el SVG **es** una imagen legítima que además trae código.

## Cómo falla

- **Se sirve como descarga** (`Content-Disposition: attachment`) o con `Content-Type` neutro — no se renderiza, no ejecuta.
- **Se sirve desde un dominio de contenido aparte** (sandbox) — el JS ejecuta en otro origen, sin acceso a la sesión.
- **Reprocesan/rasterizan** el SVG a PNG — destruye el script.
- **CSP** que bloquea inline.

## Coste

Bajo: un solo archivo. El impacto es el de un XSS almacenado — le llega a cada usuario que vea la imagen, sin interacción. Buena vía a un admin que revise imágenes subidas.

## Huella esperada

- El SVG malicioso **en disco** — evidencia persistente.
- Cada víctima que lo carga genera las peticiones salientes del payload XSS.

Payloads en [[File upload - archivos maliciosos - matriz de referencia]]. Qué hacer con la ejecución: [[XSS impacto - matriz de referencia]].
