---
tipo: tecnica
taxonomia: cwe
identificador: CWE-362
wstg: WSTG-BUSL-07
tacticas: []
aliases:
  - CWE-362
  - race condition
  - condición de carrera
  - TOCTOU
tags:
  - dominio/web
---

# CWE-362 - Concurrent Execution using Shared Resource with Improper Synchronization

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - Race conditions]]; disparar la colisión, en [[Race - matriz de disparo]]; dónde buscarlas, en [[Race - superficies y sub-estados]].

## Qué es

La aplicación comprueba algo y después actúa sobre ello en dos pasos, asumiendo que nada cambia en el medio. Si dos peticiones llegan **a la vez**, las dos pasan la comprobación antes de que cualquiera actúe, y las dos actúan. El intervalo entre comprobar y usar —la ventana— es el fallo.

El ejemplo mínimo: una tarjeta de regalo con saldo para un canje. La lógica es "¿tiene saldo? sí → canjear, poner saldo en cero". Con dos peticiones simultáneas, las dos leen "sí tiene saldo" antes de que ninguna lo ponga en cero, y las dos canjean. El saldo se usó dos veces.

## Por qué es distinta del resto del vault

Casi todas las demás clases son sobre **qué** se manda: un payload, un operador, una estructura. Esta es sobre **cuándo**: la petición es perfectamente válida —canjear la tarjeta una vez es legítimo—, y lo único anómalo es que llegan varias en la misma ventana. No hay nada que filtrar en la entrada, porque la entrada no tiene nada de malo.

Eso cambia todo el enfoque:

- **No hay payload.** El "exploit" es la sincronización, no el contenido.
- **La ventana es de milisegundos.** El arte del dominio es hacer que N peticiones lleguen dentro de ella, contra el ruido de la red que las dispersa.
- **La detección es de invariante, no de firma.** Lo que delata el ataque no es una petición sino que un invariante se rompió —el saldo quedó negativo, un token de un solo uso se usó dos veces—.

## Por qué se volvió práctica hace poco

Durante años las condiciones de carrera web se consideraban difíciles de explotar porque el jitter de la red dispersaba las peticiones más que la ventana. Dos cosas lo cambiaron:

- **El ataque de un solo paquete (single-packet attack).** Sobre HTTP/2 se pueden mandar 20-30 peticiones en **un solo paquete TCP**, de modo que llegan al servidor literalmente juntas, eliminando el jitter de la red. Es lo que volvió el dominio explotable de forma fiable.
- **La sincronización por último byte** sobre HTTP/1.1, que retiene el byte final de cada petición y lo suelta a la vez.

Antes de eso el dominio era teórico; ahora es una de las técnicas más productivas contra lógica de negocio.

## Por qué la mitigación es de atomicidad

No se filtra ni se valida: la mitigación es que comprobar y actuar sean **una sola operación indivisible**.

- **Transacciones atómicas** con el bloqueo adecuado en la base de datos.
- **Bloqueo pesimista** sobre el recurso: nadie más lo lee hasta que el primero termina.
- **Restricciones a nivel de datos** —un índice único, un `CHECK` que impida saldo negativo— que la base garantiza aunque la lógica falle.
- **Idempotencia** por token: la segunda petición con el mismo token de operación no hace nada.

## Referencias canónicas

- [CWE-362](https://cwe.mitre.org/data/definitions/362.html)
- [CWE-367](https://cwe.mitre.org/data/definitions/367.html) — TOCTOU, el caso comprobar-luego-usar
- WSTG-BUSL-07
- OWASP — Testing for Race Conditions
