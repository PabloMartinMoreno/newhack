---
tipo: tradecraft
clase: "[[CWE-1022 - Use of Web Link to Untrusted Target with window.opener Access]]"
eje: entrega
implementacion: "Plantar un enlace en contenido de usuario que se renderiza con target=_blank sin noopener, para tabnabbear a quienes lo clickean"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]", "[[Log de auditoría de la aplicación]]"]
requisitos: [contenido-de-usuario-que-renderiza-enlaces-con-target-blank-sin-noopener]
coste: bajo
alternativas: ["[[Tabnabbing - secuestro por enlace saliente]]", "[[XSS - almacenado]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - stored tabnabbing
  - tabnabbing en UGC
tags:
  - dominio/web
---

# Tabnabbing - enlace plantado en contenido de usuario

## Cuándo lo elijo

Cuando el sitio **renderiza enlaces de contenido de usuario** —comentarios, perfiles, mensajes, markdown, biografías— y los emite con `target="_blank"` **sin** `rel="noopener"`. El atacante planta un enlace propio, y cualquier usuario que lo clickee queda expuesto al secuestro de su pestaña.

Es la variante "almacenada" del dominio, análoga a [[XSS - almacenado]]: el atacante deja el enlace una vez y las víctimas llegan solas. Se elige cuando el sitio deja publicar enlaces; si el propio sitio ya enlaza a algo controlable, la rama es [[Tabnabbing - secuestro por enlace saliente]].

## Por qué funciona

Muchos sitios abren los enlaces de contenido de usuario en pestaña nueva —para no sacar al usuario del sitio— y lo hacen con `target="_blank"`. Si el renderizador no agrega `rel="noopener"` —un olvido común, sobre todo en conversores de markdown viejos—, cada enlace publicado hereda el acceso a `window.opener`.

El atacante publica un enlace a su página redirectora:

```
Miren este artículo: https://pagina-del-atacante.com/articulo
```

Que el sitio renderiza como:

```html
<a href="https://pagina-del-atacante.com/articulo" target="_blank">...</a>
```

Cualquier usuario que lo clickee abre la página del atacante, que ejecuta `window.opener.location = 'phishing'` y le cambia la pestaña del sitio legítimo por una copia. La víctima estaba **en el sitio de confianza** cuando clickeó, así que el phishing es especialmente creíble.

La ventaja sobre la rama de enlace saliente es que no depende de que el sitio ya enlace a algo controlable: el atacante **crea** el enlace. La ventaja sobre [[XSS - almacenado]] es que funciona aunque el sitio sanee el HTML correctamente —no hace falta inyectar script, solo un enlace legítimo—, así que pasa filtros que detienen el XSS.

## Cómo falla

Falla cuando el renderizador agrega `rel="noopener"` a los enlaces de contenido de usuario —lo correcto, y lo que hacen los conversores de markdown modernos—.

Falla contra `Cross-Origin-Opener-Policy: same-origin` en el sitio, que anula `window.opener` sin importar el enlace.

Falla cuando el sitio no abre los enlaces de usuario en pestaña nueva —sin `target="_blank"` no hay `opener`— o cuando el navegador de la víctima aplica `noopener` por defecto.

Y comparte el techo de la otra rama: depende de que la víctima no note el cambio de URL al volver.

## Coste

Bajo, el más bajo del dominio. Publicar un enlace es gratis, y una vez plantado las víctimas llegan solas. El reconocimiento es publicar un enlace de prueba y mirar el HTML renderizado: si sale `target="_blank"` sin `rel="noopener"`, está.

El costo es la copia de phishing, igual que la otra rama.

## Huella esperada

A diferencia de la rama de enlace saliente, esta **sí deja algo en el sitio**: el enlace plantado queda almacenado en el contenido, visible en [[Log de auditoría de la aplicación]] como una publicación del atacante. Un enlace externo en un comentario no es anómalo por sí solo, pero el contenido publicado es un rastro que la otra rama no tiene.

El secuestro en sí, en cambio, ocurre en el navegador de cada víctima y el sitio no lo ve —igual que toda la familia—. La única detección posible sería del lado del renderizador: **una auditoría del HTML generado buscando `target="_blank"` sin `rel="noopener"`**, que es prevención en tiempo de desarrollo, no detección en producción.

Sigue siendo un dominio de cara azul preventiva: la defensa es que el renderizador agregue `noopener` y que el sitio mande COOP. Lo único que lo diferencia de [[Tabnabbing - secuestro por enlace saliente]] es que acá queda el enlace almacenado como evidencia de que alguien lo intentó. Anotado en [[MOC - Tabnabbing]].
