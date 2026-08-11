---
tipo: tradecraft
clase: "[[CWE-352 - Cross-Site Request Forgery]]"
eje: defensa
implementacion: "Suprimir el Referer, o satisfacer una comparación de cadenas mal escrita"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]", "[[Log de auditoría de la aplicación]]"]
requisitos: [sesion-por-cookie, validacion-por-cabecera]
coste: bajo
alternativas: ["[[CSRF - token ausente o no ligado]]", "[[CSRF - bypass de SameSite]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - bypass de Referer
  - Origin bypass
tags:
  - dominio/web
---

# CSRF - bypass de validación de origen

## Cuándo lo elijo

Cuando las pruebas de token no dieron nada y las respuestas cambian según el `Referer`: la petición sin esa cabecera pasa, o con un valor arbitrario devuelve `403`. Es la señal de que la defensa es la comparación de origen y no un token.

Es una defensa de segunda línea que muchas aplicaciones usan como primera. Se rompe rápido, así que va antes que [[CSRF - bypass de SameSite]] en cuanto se confirma que está.

## Por qué funciona

La comparación se apoya en dos cabeceras que la aplicación no controla, y falla de tres maneras distintas:

**La cabecera se puede suprimir.** `Referer` es opcional y el atacante decide si se manda:

- `<meta name="referrer" content="no-referrer">` en la página del ataque.
- `referrerpolicy="no-referrer"` en el elemento que dispara la petición.
- Una redirección desde `https` a `http`, que borra la cabecera por política del navegador.

Muchas implementaciones hacen `if (referer && !referer.startsWith(...))`: sin la cabecera no entran a validar. Es el mismo fallo estructural que en [[CSRF - token ausente o no ligado]] —validar solo si el dato está— y aparece por la misma razón: al programarlo, la ausencia parecía un caso legítimo.

**La comparación es de subcadena.** Cuando se valida con `contains` o `startsWith` en vez de parsear la URL:

- `https://objetivo.com.atacante.com/` pasa un `startsWith` mal anclado.
- `https://atacante.com/?x=objetivo.com` pasa cualquier `contains`.
- `https://objetivo.com.evil.net/` pasa las dos.

**`Origin` no siempre está.** A diferencia de `Referer`, `Origin` no se puede suprimir con una directiva, pero **no se manda** en las peticiones `GET` de navegación de nivel superior. Una aplicación que valida `Origin` y acepta `GET` para la acción tiene el agujero abierto sin darse cuenta.

## Cómo falla

Falla contra una validación que exige la cabecera —rechaza si falta— y compara el origen ya parseado contra una lista blanca. Son cuatro líneas de código y cierran las tres vías de arriba.

Falla también cuando la aplicación valida `Origin` y solo acepta `POST` para la acción: ahí `Origin` siempre viaja y siempre es el del atacante.

Y no aplica en absoluto si además hay token ligado a la sesión: la validación de origen es entonces defensa en profundidad, y romperla no habilita nada.

## Coste

Bajo. Son tres o cuatro peticiones con la cabecera manipulada a mano y la respuesta se lee del código de estado. Es de las pruebas más rápidas del vault, y por eso vale hacerla incluso cuando se sospecha que va a fallar.

El único coste real aparece al construir la prueba de concepto: suprimir el `Referer` desde una página de verdad exige alojarla, y algunas de las técnicas dependen del navegador que use la víctima.

## Huella esperada

Durante la prueba quedan varias peticiones con `Referer` ausente o extraño contra la misma acción, seguidas de `403`. Esa secuencia en [[Log de acceso del servidor web]] es la parte visible.

El ataque exitoso, en cambio, es una sola petición con `Referer` ausente. Y ahí está la asimetría que conviene anotar: **la ausencia de una cabecera no llama la atención de nadie**. Un `Referer` vacío es normal en marcadores, en clientes de correo y en muchas configuraciones de privacidad, así que la señal sola tiene fidelidad demasiado baja para alertar.

Lo que sí discrimina es la combinación —acción que cambia estado, sin `Referer`, sin la navegación previa en [[Log de auditoría de la aplicación]]— y eso ya es una detección de secuencia, no de evento.
