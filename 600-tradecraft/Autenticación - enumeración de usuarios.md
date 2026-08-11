---
tipo: tradecraft
clase: "[[CWE-204 - Observable Response Discrepancy]]"
eje: fase
implementacion: "Distinguir cuentas existentes por diferencia de mensaje, tiempo o comportamiento"
opsec: ruidoso
telemetria: ["[[Log de autenticación de la aplicación]]", "[[Log de acceso del servidor web]]"]
requisitos: [respuesta-diferencial, lista-de-candidatos]
coste: bajo
alternativas: ["[[Autenticación - abuso de recuperación de contraseña]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - enumeración de cuentas
tags:
  - dominio/web
---

# Autenticación - enumeración de usuarios

## Cuándo lo elijo

Siempre primero en este dominio, y no por su impacto propio —que es bajo— sino porque **multiplica todo lo que viene después**. Es el paso que convierte [[Autenticación - password spraying]] de un disparo a ciegas en un ataque dirigido.

La aritmética justifica el orden: probar una contraseña contra diez mil direcciones inventadas son diez mil peticiones fallidas y un ruido enorme; contra doscientas cuentas confirmadas son doscientas peticiones que pasan por debajo de casi cualquier umbral. La enumeración compra sigilo, no solo información.

Se prueba en **todos** los puntos que tocan la lista de cuentas, no solo en el acceso: alcanza con que uno filtre. Registro, recuperación e invitaciones fallan más seguido que el formulario de acceso, porque son los que nadie revisó.

## Por qué funciona

La aplicación tiene que hacer cosas distintas según la cuenta exista o no, y hacer cosas distintas lleva tiempos distintos y produce respuestas distintas. Ocultar esa diferencia es trabajo deliberado que hay que hacer en cada endpoint.

El oráculo por **tiempo** es el que sobrevive a las correcciones parciales, y por una razón que es casi una ironía: si la cuenta no existe, la aplicación responde de inmediato; si existe, calcula el hash de la contraseña antes de rechazarla. El hash es lento **a propósito**, porque así se defiende de quien lo robe. Esa lentitud deliberada es la fuga. Ver [[La latencia como canal de datos]].

## Cómo falla

- **Respuestas idénticas y tiempo constante** — la mitigación correcta, que exige calcular un hash falso cuando la cuenta no existe. Cuando está bien hecha, cierra el vector.
- **El ruido de red tapa la diferencia de tiempo** — con diferencias de decenas de milisegundos hacen falta varias mediciones por candidato y estadística, no una comparación simple.
- **Control de ritmo o CAPTCHA en el endpoint** — encarece la enumeración masiva. Suele haber otro endpoint sin protección.
- **Lista de candidatos mala** — sin nombres reales de la organización no hay a quién enumerar. El trabajo previo es de fuentes abiertas, no técnico.
- **Respuestas neutras por diseño** — "si la cuenta existe, te escribimos" es correcto y frecuente en flujos de recuperación modernos.

## Coste

Bajo por candidato y **alto en volumen**: la lista se recorre entera. El oráculo por tiempo es varias veces más caro que el de mensaje, porque cada candidato necesita repeticiones para promediar.

## Huella esperada

Es de las variantes más visibles del vault, y no tiene forma sigilosa: hay que preguntar una vez por cada candidato.

- [[Log de autenticación de la aplicación]] con una ráfaga de fallos contra **cuentas mayormente inexistentes**. Ese detalle es la firma que la distingue de un ataque de credenciales: acá la mayoría de los objetivos no existen, y eso solo se ve si el registro guarda el **motivo** del fallo.
- [[Log de acceso del servidor web]] con muchas peticiones al mismo endpoint desde un origen, con tiempos regulares.
- En el oráculo por tiempo, además: **varias peticiones idénticas por candidato**, que es un patrón que ningún usuario produce.

La detección de mayor retorno acá no mira un evento: mira la proporción de fallos por cuenta inexistente en una ventana. Un pico en esa proporción es enumeración y casi nada más.

Los oráculos concretos y los endpoints a revisar están en [[Autenticación - matriz de referencia]] § Enumeración.
