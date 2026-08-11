---
tipo: tradecraft
clase: "[[CWE-307 - Improper Restriction of Excessive Authentication Attempts]]"
eje: vector
implementacion: "Una contraseña probable contra muchas cuentas, para no disparar el bloqueo por cuenta"
opsec: ruidoso
telemetria: ["[[Log de autenticación de la aplicación]]"]
requisitos: [lista-de-cuentas, sin-limite-por-origen]
coste: medio
alternativas: ["[[Autenticación - credential stuffing]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - password spraying
  - rociado de contraseñas
tags:
  - dominio/web
---

# Autenticación - password spraying

## Cuándo lo elijo

Cuando hay una lista de cuentas y un bloqueo por cuenta. Es la respuesta directa a ese control: en vez de muchas contraseñas contra un usuario —que lo bloquea al quinto intento— se prueba **una** contraseña contra muchos usuarios, de modo que ninguna cuenta acumula fallos.

La elección entre esto y [[Autenticación - credential stuffing]] depende de un solo dato: si hay corpus de credenciales filtradas de esa organización. Si lo hay, el stuffing gana por lejos — su tasa de acierto es mucho mayor y no genera fallos. El spraying es la opción cuando no hay corpus y sí hay lista de cuentas.

Prerrequisito casi obligatorio: [[Autenticación - enumeración de usuarios]]. Rociar sobre cuentas inventadas multiplica el ruido sin multiplicar las chances.

## Por qué funciona

Por dos hechos que se combinan mal para el defensor.

**El control está en el eje equivocado.** Contar fallos por cuenta es el reflejo natural y detiene únicamente la fuerza bruta clásica. El spraying reparte los fallos sobre miles de cuentas y cada contador queda en uno. Ver [[CWE-307 - Improper Restriction of Excessive Authentication Attempts]].

**Las contraseñas de una organización se parecen entre sí.** No por casualidad: la política las hace parecerse. Exigir mayúscula, número y símbolo, con cambio cada noventa días, produce de forma predecible el nombre de la estación seguido del año y un signo de admiración. En una población de mil personas, que una sola haya elegido eso es prácticamente seguro — y una sola alcanza.

## Cómo falla

- **Límite por origen**, además del límite por cuenta. Es la mitigación correcta y obliga a distribuir el ataque, lo que lo encarece mucho.
- **MFA bien implementado** — la contraseña correcta deja de alcanzar y todo el vector pasa de crítico a moderado. Es la defensa que de verdad cambia el resultado.
- **Detección por tasa global de fallos** — invisible cuenta por cuenta, evidente en el agregado. Un defensor que mire ese número lo ve enseguida.
- **Política de contraseñas que rompe el patrón** — frases de paso, o verificación contra listas de contraseñas filtradas.
- **Bloqueo por ventana temporal** — si la ventana es larga, hay que espaciar las rondas mucho, y el ataque pasa de horas a días.

## Coste

Medio y sobre todo **lento si se hace bien**. La velocidad es el enemigo: una ronda por ventana de bloqueo, esperando entre rondas. Hacerlo rápido lo vuelve trivial de detectar y puede bloquear cuentas de verdad, lo que además tiene consecuencias para el cliente.

## Un límite operativo

> [!warning] Bloquear cuentas es un incidente, no un hallazgo
> Ir demasiado rápido o probar demasiadas contraseñas por cuenta bloquea usuarios reales y genera llamadas a soporte, gente sin poder trabajar y un incidente que no era el objetivo.
>
> Se acuerda de antemano la ventana, el ritmo y el máximo de intentos por cuenta, y se deja margen respecto del umbral de bloqueo. Cuando el umbral no se conoce, se asume el peor caso.

## Huella esperada

Perfectamente detectable **si alguien mira el agregado**, e invisible si se mira cuenta por cuenta. Esa asimetría es todo el interés de la técnica.

- [[Log de autenticación de la aplicación]] con un fallo por cuenta sobre cientos de cuentas, todos desde el mismo origen o el mismo rango, en una ventana estrecha. Ninguna cuenta llega al umbral y el agregado es inconfundible.
- Distribución temporal regular: las peticiones automatizadas llegan con una periodicidad que las personas no producen.
- Un **éxito** en medio de la ráfaga es el evento crítico: acceso correcto desde el mismo origen que acaba de fallar contra doscientas cuentas.
- Si se distribuye el origen, la señal que queda es la lista de cuentas objetivo — la misma secuencia, en el mismo orden, desde IP distintas.

Las contraseñas que pagan y el cálculo de la ventana están en [[Autenticación - matriz de referencia]] § Contraseñas.
