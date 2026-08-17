---
tipo: tradecraft
clase: "[[CWE-1021 - Improper Restriction of Rendered UI Layers or Frames]]"
eje: interacción
implementacion: "Encadenar varios gestos —arrastrar, rellenar, varios clics— sobre el marco para completar una acción de varios pasos"
opsec: limpio
telemetria: ["[[Log de acceso del servidor web]]", "[[Informe de violación de CSP]]"]
requisitos: [objetivo-encuadrable, acción-de-varios-pasos-o-con-entrada]
coste: medio
alternativas: ["[[Clickjacking - un clic sobre acción sensible]]", "[[XSS - reflejado]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - drag-and-drop clickjacking
  - clickjacking multipaso
  - likejacking
tags:
  - dominio/web
---

# Clickjacking - relleno por arrastre y multipaso

## Cuándo lo elijo

Cuando la acción objetivo **no se completa con un solo clic** —necesita un valor en un campo, varios pasos, o una confirmación—, pero el sitio sigue siendo encuadrable. Es el escalón de mayor control del dominio: en vez de un clic, se orquesta una secuencia de gestos sobre el marco invisible.

Se elige después de [[Clickjacking - un clic sobre acción sensible]] cuando aquella no alcanza porque la acción pide más que un clic. Si el objetivo no se puede encuadrar, ninguna de las dos aplica.

## Por qué funciona

El atacante controla la página que contiene el marco, así que controla el contexto donde ocurren los gestos de la víctima, y encadena varios:

**Relleno por arrastre (drag-and-drop).** El navegador permite arrastrar texto entre orígenes. El atacante pone un texto en su página —"arrastrá esto al recuadro para continuar"— y la víctima lo suelta sobre un campo del marco invisible, rellenándolo con un valor elegido por el atacante. Con eso se llena un campo de correo, un monto, un destinatario, antes de que el clic final envíe.

**Multipaso con precarga.** Si el objetivo acepta valores por la URL —un formulario que se precarga con parámetros—, el atacante carga el marco con los campos ya llenos y solo necesita que la víctima clickee "enviar". El relleno lo hace la URL, el clic lo hace la víctima.

**Entrada por teclado dirigida.** Algunas variantes capturan pulsaciones y las dirigen al marco, aunque el navegador lo dificulta.

La secuencia de gestos y las construcciones están en [[Clickjacking - superposición - matriz de referencia]]. Es más frágil que el clic único porque cada gesto es una oportunidad de que la víctima note algo raro.

**Combinado con otras clases**, es donde más rinde:

- **Entregar un XSS reflejado**: precargar el marco con un payload en un campo que se refleje, y el clic lo dispara — se cruza con [[XSS - reflejado]], usando clickjacking como vector de entrega.
- **Consentimiento de OAuth**: encuadrar la pantalla de autorización de OAuth y hacer que la víctima "acepte" sin saberlo, otorgando acceso a la aplicación del atacante — se cruza con [[MOC - OAuth]].
- **Likejacking**: la variante clásica de redes sociales, un clic que da "me gusta" o comparte.

## Cómo falla

Falla contra las mismas defensas de encuadre que la otra rama —`frame-ancestors`, `X-Frame-Options`—: si no se puede encuadrar, no hay dominio.

Falla cuando la acción de varios pasos incluye una confirmación que no se puede precargar ni arrastrar —un CAPTCHA, un código enviado aparte—.

Y es más frágil que el clic único: cada gesto extra es una chance de que la víctima abandone. Cuantos más pasos, menos fiable.

## Coste

Medio. Orquestar la secuencia de arrastre o precarga es más trabajo que la superposición simple, y calibrar que cada gesto caiga donde debe lleva iteración. La precarga por URL es la más barata cuando el objetivo la permite.

El reconocimiento es entender el flujo de varios pasos del objetivo y qué parte se puede automatizar con precarga o arrastre, dejando a la víctima solo el clic final.

## Huella esperada

La misma que la rama de un clic, y por la misma razón: **el servidor ve acciones legítimas del usuario autenticado**. El relleno por arrastre y la precarga ocurren en el navegador de la víctima; el objetivo solo recibe el envío final, indistinguible de uno real.

- La secuencia queda en [[Log de auditoría de la aplicación]] como una acción normal de la víctima.
- Si la variante entrega un XSS, dispara [[Informe de violación de CSP]] en el navegador de la víctima —la detección de efecto de XSS, sin saber que el vector fue clickjacking—.
- La precarga por URL deja los valores en el `Referer` o en la query de la carga del marco, en [[Log de acceso del servidor web]], pero es ruidoso.

Igual que la otra rama, la cara azul es **preventiva**: `frame-ancestors` impide el encuadre y con él toda la secuencia. No hay detección fiable del multipaso porque cada gesto vive en el cliente. Es el mismo límite de [[Clickjacking - un clic sobre acción sensible]], anotado en [[MOC - Clickjacking]].
