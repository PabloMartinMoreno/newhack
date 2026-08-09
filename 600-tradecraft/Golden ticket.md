---
tipo: tradecraft
clase: "[[T1558.001 - Golden Ticket]]"
eje: persistencia
implementacion: "Forjar un TGT firmado con el secreto de la cuenta krbtgt"
opsec: requiere-bypass
telemetria: ["[[Windows 4624 - Successful logon]]", "[[Windows 4769 - Kerberos service ticket requested]]"]
requisitos: [secreto-de-la-cuenta-de-firma]
coste: bajo
alternativas: ["[[DCSync]]"]
probado: 2026-08-08
contexto: [lab-ad]
aliases:
  - golden ticket
tags:
  - dominio/ad
---

# Golden ticket

## Cuándo lo elijo

Como **persistencia**, después de haber comprometido el dominio y obtenido el secreto de la cuenta que firma los tickets — típicamente con [[DCSync]]. No es una vía de entrada: es lo que garantiza volver a entrar aunque limpien todo lo demás.

Se usa cuando el objetivo deja de ser "conseguir acceso" y pasa a ser "no perderlo".

## Por qué funciona

Porque Kerberos confía en la firma, no en quién la produjo. Toda su seguridad descansa en que solo el controlador conoce la clave de esa cuenta especial. Con esa clave se firman tickets que dicen cualquier cosa —cualquier usuario, cualquier grupo, cualquier vigencia— y el dominio los acepta. Ver [[T1558.001 - Golden Ticket]].

No es un fallo: es el resultado esperado de que ese secreto se filtre.

## Cómo falla

- **La detección de robo del secreto ocurre antes.** El ticket forjado en sí es difícil de distinguir; lo que se detecta es el [[DCSync]] o el volcado que consiguió la clave. Por eso `requiere-bypass` y no `quemado`: la técnica es sólida, lo que la delata es el paso previo.
- **Vigencias absurdas.** Las herramientas viejas ponían vidas de diez años por defecto, que destacan contra los tickets legítimos. Ajustarlas a valores normales lo vuelve mucho más difícil de ver.
- **Tickets que omiten el paso inicial.** Un ticket forjado se usa directamente para pedir servicios sin haber pedido un ticket inicial primero — una secuencia que no ocurre legítimamente y que se puede correlacionar.
- **La única invalidación real** es rotar el secreto de la cuenta de firma **dos veces**, lo que corta todos los tickets del dominio a la vez.

## Coste

Bajo para fabricar, una vez que se tiene la clave. El costo entero fue conseguir el secreto. Fabricar el siguiente ticket no requiere volver a hablar con nada.

## Huella esperada

Es la persistencia mejor lograda del dominio, y su detección es toda indirecta.

- [[Windows 4769 - Kerberos service ticket requested]] con una petición de ticket de servicio **sin el ticket inicial correspondiente** en la secuencia: un acceso que aparece sin haberse autenticado nunca. Es de forma `invariante` — una secuencia que no debería poder ocurrir.
- [[Windows 4624 - Successful logon]] de una cuenta que puede **no existir o estar deshabilitada**, porque el ticket forjado afirma una identidad que el dominio ya no tiene.
- Vigencias de ticket fuera de lo normal, si el atacante no las ajustó.
- **Nada de esto se ve en el momento del compromiso**, que ya pasó. Se ve cuando el ticket se usa, que es después.

Por eso, del lado azul, se trata como pérdida total: la detección llega tarde por diseño, y la recuperación —rotar dos veces la clave de firma— es disruptiva y hay que hacerla completa, o un ticket sobreviviente reabre todo.
