---
tipo: tradecraft
clase: "[[CWE-307 - Improper Restriction of Excessive Authentication Attempts]]"
eje: vector
implementacion: "Pares usuario:contraseña de filtraciones ajenas, apostando a la reutilización"
opsec: limpio
telemetria: ["[[Log de autenticación de la aplicación]]"]
requisitos: [corpus-de-credenciales, sin-mfa]
coste: bajo
alternativas: ["[[Autenticación - password spraying]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - credential stuffing
  - reutilización de credenciales
tags:
  - dominio/web
---

# Autenticación - credential stuffing

## Cuándo lo elijo

Cuando existe corpus de credenciales filtradas asociadas al dominio del objetivo. En ese caso gana a [[Autenticación - password spraying]] por dos motivos que se acumulan: la tasa de acierto es mucho mayor —no se adivina, se reutiliza— y **no genera fallos**, así que no dispara nada de lo que está construido para contar rechazos.

Es también el vector que mejor refleja el riesgo real de una organización, porque no depende de ninguna debilidad de su aplicación: depende de que sus empleados hayan usado el mismo par en otro sitio que fue comprometido. Ninguna política de contraseñas propia lo evita.

Si el corpus está vacío, no hay técnica: se vuelve a spraying.

## Por qué funciona

Por la reutilización de contraseñas entre servicios, que es masiva y no va a dejar de serlo mientras la gente tenga que recordar decenas de credenciales.

El detalle que lo separa de todo lo demás del dominio: cuando acierta, **acierta a la primera**. El intento es un acceso exitoso con la credencial correcta desde el primer momento. No hay ráfaga de fallos previa, no hay contador que suba, no hay umbral que se cruce. Para toda la maquinaria defensiva construida alrededor de "muchos fallos seguidos", este ataque no ocurre.

Por eso `opsec: limpio` — y con la misma salvedad que en [[Control de acceso - IDOR]]: no significa indetectable, significa que no hay nada técnicamente anómalo en el evento. La anomalía está en el contexto, no en la petición.

## Cómo falla

- **MFA** — es la defensa. La credencial correcta deja de alcanzar, y contra este vector es la única mitigación que realmente funciona.
- **Verificación contra listas de credenciales filtradas**, al establecer contraseña y de forma periódica. Ataca la causa en vez del síntoma.
- **Detección por origen y por reputación** — un acceso exitoso desde un país nuevo, un proveedor de nube o una IP con antecedentes, contra una cuenta que siempre entra desde el mismo lugar.
- **Las credenciales están viejas** — la contraseña filtrada ya se cambió. La tasa de acierto cae con la antigüedad del corpus.
- **El corpus no corresponde a la organización** — sin filtraciones asociadas al dominio, no hay insumo.

## Coste

Bajo en ejecución: cada par es una petición y una fracción acierta. El costo real está en **conseguir y curar el corpus**, que es trabajo de fuentes abiertas y no técnico.

## Un límite que es sobre todo legal

> [!danger] El insumo son credenciales de personas reales
> Los corpus de filtraciones contienen datos personales de gente que no es parte del engagement. Manejarlos tiene implicancias legales que varían por jurisdicción y que no se resuelven con una cláusula genérica en el contrato.
>
> Antes de usarlos: autorización explícita por escrito, alcance limitado al dominio del cliente, y un acuerdo sobre cómo se almacenan y cuándo se destruyen. En muchos engagements la respuesta correcta es demostrar el riesgo con estadística pública en vez de probar las credenciales.

## Huella esperada

La variante más silenciosa del dominio, con diferencia.

- [[Log de autenticación de la aplicación]] registra **accesos exitosos**. No hay fallos, no hay umbral, no hay nada que una regla de fuerza bruta note.
- Lo único anómalo es el contexto del éxito: origen nuevo para esa cuenta, agente de usuario que no coincide con el histórico, muchas cuentas distintas accediendo desde una misma IP en poco tiempo, hora inusual.
- La señal más robusta es esa última: **una IP que autentica con éxito contra muchas cuentas sin relación entre sí**. Ninguna persona hace eso.
- Con el ataque distribuido, la única señal que queda es por cuenta: el cambio de patrón respecto de su propio histórico.

Es el caso que mejor muestra por qué [[Log de autenticación de la aplicación]] necesita el **origen** y el **camino de acceso** además del resultado. Sin esos campos, un ataque exitoso de este tipo es indistinguible de un día normal.
