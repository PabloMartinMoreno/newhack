---
tipo: tradecraft
clase: "[[CWE-1021 - Improper Restriction of Rendered UI Layers or Frames]]"
eje: interacción
implementacion: "Encuadrar el objetivo en un marco transparente y alinear un botón sensible bajo un señuelo que la víctima clickea"
opsec: limpio
telemetria: ["[[Log de acceso del servidor web]]"]
requisitos: [objetivo-encuadrable, acción-sensible-de-un-clic]
coste: bajo
alternativas: ["[[Clickjacking - relleno por arrastre y multipaso]]", "[[CSRF - token ausente o no ligado]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - clickjacking clásico
  - one-click clickjacking
tags:
  - dominio/web
---

# Clickjacking - un clic sobre acción sensible

## Cuándo lo elijo

Es el caso base del dominio y el primero a probar. Se reconoce cuando el objetivo **se puede encuadrar** —no manda `X-Frame-Options` ni `frame-ancestors`— y tiene una acción sensible que se ejecuta con **un solo clic**: borrar la cuenta, cambiar el correo, autorizar un pago, aprobar un consentimiento de OAuth.

Se confirma cargando el objetivo en un `iframe` propio y viendo si aparece. Si el encuadre está bloqueado, la rama se cierra —o se intenta el bypass de [[Clickjacking - encuadre - matriz de referencia]]—. Si la acción necesita varios pasos o arrastrar, la rama es [[Clickjacking - relleno por arrastre y multipaso]].

## Por qué funciona

El navegador de la víctima carga el objetivo en el marco **con su sesión** —las cookies viajan como en cualquier carga—, así que el botón encuadrado, si se lo clickea, ejecuta la acción autenticada. El atacante:

1. Pone el objetivo en un `iframe` con **opacidad cero** —invisible— sobre su página.
2. Debajo, un señuelo llamativo alineado con el botón sensible del objetivo: "Reclamá tu premio", un video, un juego.
3. La víctima ve el señuelo y clickea; el clic atraviesa al marco invisible y cae en el botón del objetivo.

El CSS de la superposición y la alineación del señuelo están en [[Clickjacking - superposición - matriz de referencia]]. La parte fina es **alinear** el señuelo con el botón, que se ajusta con `position` y `opacity` —a veces se sube la opacidad del marco mientras se calibra y se baja a cero al final—.

Es primo de [[CSRF - token ausente o no ligado]], y tiene una ventaja sobre él: **sortea las defensas de CSRF**. El clic genera la petición real del objetivo, con su token anti-CSRF válido incluido, así que un formulario protegido contra CSRF sigue cayendo. Lo que se abusa no es la petición sino el clic que la origina.

## Cómo falla

Falla cuando el objetivo manda `X-Frame-Options: DENY`/`SAMEORIGIN` o `Content-Security-Policy: frame-ancestors`, que le dicen al navegador que no lo cargue en un marco ajeno. Es la mitigación correcta y la que va en el informe.

Falla contra acciones que exigen **reautenticación** —la contraseña actual, un segundo factor— antes de ejecutarse: el clic solo no alcanza. Es la misma defensa que sobrevive a un XSS en el mismo origen.

Y depende de una **víctima autenticada que clickee** en la página del atacante, el mismo techo de severidad que [[MOC - CSRF]]: hay que reflejarlo en el informe en vez de venderlo como toma de cuenta directa.

## Coste

Bajo. Encuadrar y superponer es una página HTML de pocas líneas —Burp Clickbandit la genera automáticamente a partir de la acción objetivo—. La calibración de la alineación son unos minutos.

El costo real es de reconocimiento: encontrar la acción de un clic que valga la pena. Un botón de "eliminar cuenta" sin confirmación es crítico; uno de "cambiar tema" es informativo. La misma vulnerabilidad, severidades incomparables, como en CSRF.

## Huella esperada

Es la cara azul más particular del vault, y por eso el `opsec: limpio`: **el servidor casi no ve el ataque**.

La acción que resulta del clic es una petición legítima del usuario autenticado —el mismo problema que CSRF—, así que en [[Log de auditoría de la aplicación]] aparece como una acción normal de la víctima. Lo único distinto es que la carga del marco lleva un `Referer` y un `Sec-Fetch-Dest: iframe` de la página del atacante, visible en [[Log de acceso del servidor web]] si se registran esas cabeceras — pero es ruidoso, porque encuadrar un sitio también es legítimo.

Es el primer dominio del vault cuya cara azul es **puramente preventiva**: no hay una detección fiable, hay una cabecera que impide el ataque. La recomendación defensiva no es una regla sino `frame-ancestors`. Se cruza con [[Ausencia de alertas no es ausencia de ataque]] en su forma más pura: acá no se puede detectar de forma fiable, solo prevenir. Anotado en [[MOC - Clickjacking]].
