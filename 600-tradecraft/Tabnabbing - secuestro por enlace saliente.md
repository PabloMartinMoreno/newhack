---
tipo: tradecraft
clase: "[[CWE-1022 - Use of Web Link to Untrusted Target with window.opener Access]]"
eje: entrega
implementacion: "Redirigir la pestaña abridora a una copia de phishing desde una página que el objetivo abrió con target=_blank sin noopener"
opsec: limpio
telemetria: ["[[Log de acceso del servidor web]]"]
requisitos: [enlace-saliente-con-target-blank-sin-noopener, destino-influenciable]
coste: bajo
alternativas: ["[[Tabnabbing - enlace plantado en contenido de usuario]]", "[[Clickjacking - un clic sobre acción sensible]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - reverse tabnabbing por enlace
tags:
  - dominio/web
---

# Tabnabbing - secuestro por enlace saliente

## Cuándo lo elijo

Cuando el sitio objetivo tiene enlaces salientes que abren en pestaña nueva —`target="_blank"`— **sin** `rel="noopener"`, y el destino de alguno de esos enlaces es algo que el atacante puede influir: un sitio de terceros, un perfil, un dominio que el atacante controla o puede comprometer. Se reconoce leyendo el HTML: un `<a target="_blank">` sin `rel="noopener"` es la marca.

El objetivo es phishing: cuando la víctima abre ese enlace, la página abierta redirige la pestaña original del objetivo a una copia falsa. Si el enlace lo planta el atacante dentro del sitio —un comentario, un perfil—, la rama es [[Tabnabbing - enlace plantado en contenido de usuario]]; esta es cuando el propio sitio ya enlaza a algo que el atacante controla.

## Por qué funciona

La página abierta recibe `window.opener` y, aunque no pueda leer la pestaña original por ser de otro origen, sí puede navegarla:

```html
<!-- en la página del atacante, que el objetivo abre en pestaña nueva -->
<script>
  if (window.opener) {
    window.opener.location = 'https://phishing-objetivo.com/login';
  }
</script>
```

La secuencia:

1. La víctima está en el sitio objetivo, autenticada.
2. Clickea un enlace `target="_blank"` que lleva a la página del atacante —o a un sitio de terceros que el atacante comprometió—.
3. La página del atacante se abre en una pestaña nueva y ejecuta el `opener.location`.
4. La pestaña original —el sitio objetivo, de fondo— navega a la copia de phishing.
5. La víctima termina de mirar la pestaña nueva, vuelve a la primera, y ve una página que parece el sitio objetivo pidiéndole autenticarse. La URL puede diferir, pero el usuario que volvió a "su" pestaña rara vez la mira.

La copia de phishing hereda la credibilidad de que la víctima **ya estaba** en ese sitio. Es más creíble que un phishing por correo, porque la pestaña no la abrió el atacante: estaba abierta.

## Cómo falla

Falla contra `rel="noopener"` en el enlace —que corta `window.opener`— o contra `Cross-Origin-Opener-Policy: same-origin` en el objetivo, que aísla la ventana. Los navegadores modernos aplican `noopener` por defecto a `target="_blank"`, así que el ataque vive sobre todo en navegadores viejos, en aperturas por `window.open()` sin la opción, y en sitios que fuerzan el comportamiento antiguo.

Falla cuando el sitio no tiene enlaces salientes influenciables: si todos los `target="_blank"` van a destinos fijos y confiables, no hay dónde plantar el redirector.

Y depende de que la víctima **no note** el cambio de URL al volver a la pestaña. Contra un usuario que verifica la barra de direcciones, el phishing se cae —el mismo techo que cualquier ataque de suplantación—.

## Coste

Bajo. La página redirectora es tres líneas. El reconocimiento es leer el HTML del objetivo buscando `target="_blank"` sin `noopener`, y ver si alguno lleva a un destino que se pueda controlar.

El costo real es montar la copia de phishing convincente y, si hace falta, comprometer el sitio de terceros al que el objetivo enlaza. Sin un enlace saliente influenciable, esta rama no arranca.

## Huella esperada

Es cara azul preventiva, igual que [[Clickjacking - un clic sobre acción sensible]], y de ahí el `opsec: limpio`: **el objetivo casi no ve el ataque**.

La navegación de la pestaña original ocurre en el navegador de la víctima. Lo único que el objetivo podría registrar es la salida del usuario —la pestaña dejó de estar en el sitio— y, si la víctima cae, un `Referer` de la página falsa cuando reenvía las credenciales a otro lado; nada de eso es una firma fiable.

Como en clickjacking, no hay detección: hay prevención. La recomendación es `rel="noopener"` en los enlaces salientes y `Cross-Origin-Opener-Policy` en el sitio. Es el segundo dominio del vault de cara azul puramente preventiva, y comparte la conclusión de [[Ausencia de alertas no es ausencia de ataque]]: no hay nada que alertar, hay una puerta que cerrar. Anotado en [[MOC - Tabnabbing]].
