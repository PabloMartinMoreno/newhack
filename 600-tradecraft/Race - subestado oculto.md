---
tipo: tradecraft
clase: "[[CWE-362 - Concurrent Execution using Shared Resource with Improper Synchronization]]"
eje: tipo-de-ventana
implementacion: "Empujar la máquina de estados a un subestado transitorio que no debería ser alcanzable, con peticiones concurrentes a un solo endpoint"
opsec: ruidoso
telemetria: ["[[Log de auditoría de la aplicación]]", "[[Log de acceso del servidor web]]"]
requisitos: [endpoint-con-máquina-de-estados-y-pasos-intermedios]
coste: alto
alternativas: ["[[Race - superación de límite]]", "[[Race - colisión entre endpoints]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - single-endpoint race
  - subestado oculto
  - hidden multi-step
tags:
  - dominio/web
---

# Race - subestado oculto

## Cuándo lo elijo

Cuando un solo endpoint esconde una **máquina de estados** con pasos intermedios que la lógica asume que se recorren en orden, y peticiones concurrentes contra ese endpoint fuerzan un subestado transitorio que no debería ser alcanzable. No es superar un límite ni cruzar dos operaciones: es que **una operación que parece atómica en realidad no lo es**, y colisionar contra sí misma la parte.

Se elige cuando la superación de límite no aplica —no hay un contador obvio— pero la operación hace varias cosas internas que se pueden desincronizar: un registro que valida y crea, un pago que reserva y confirma, un proceso que marca y ejecuta.

## Por qué funciona

Una operación "atómica" desde afuera suele ser varios pasos adentro, y algunos dejan subestados que ninguna interfaz expone. Golpear el mismo endpoint muchas veces a la vez hace que unas peticiones vean el subestado de otras:

- **Registro que valida-luego-crea.** Dos registros del mismo usuario a la vez pasan la validación de "no existe" antes de que ninguno cree, y crean dos cuentas con el mismo identificador — o una cuenta en un estado a medio construir, sin el paso de seguridad que debía seguir.
- **Aplicar un token de un solo uso** que se marca usado después de actuar: varias peticiones actúan antes del marcado.
- **Un proceso de varios pasos** —crear objeto, asignar dueño, aplicar permisos por defecto— donde colisionar deja el objeto sin el paso de permisos, accesible.

Es la variante conceptualmente más difícil porque el subestado no se ve: hay que **inferir** que existe por cómo se comporta la operación bajo carga concurrente. La "construcción parcial" —un objeto que queda a medio crear y es usable en ese estado— es el caso emblemático y el que más sorprende, porque el estado no aparece en ningún flujo normal.

La sincronización es la de siempre —ataque de un solo paquete, [[Race - matriz de disparo]]— pero el reconocimiento es de comportamiento: se dispara la ráfaga y se observa qué queda inconsistente, en vez de apuntar a un límite conocido.

## Cómo falla

Falla contra atomicidad real de la operación completa, no solo de la escritura final: si los pasos internos están dentro de una transacción o un bloqueo, no hay subestado alcanzable.

Falla contra restricciones de datos que rechazan el estado inconsistente —un índice único que impide el doble registro— aunque la ventana exista.

Y falla, muy seguido, porque el subestado que se imaginó no existe: es la rama con más hipótesis que no dan, y hay que aceptar que a menudo no hay nada que colisionar.

## Coste

Alto. El reconocimiento es el más especulativo del dominio: no hay un límite visible que atacar, hay que sospechar que una operación tiene pasos internos desincronizables y confirmarlo por comportamiento. Muchas hipótesis no dan, y hay que fijar presupuesto.

La sincronización, una vez que se sospecha el subestado, es la misma plantilla de Turbo Intruder de las otras ramas — el trabajo está antes, en imaginar dónde está la costura.

## Huella esperada

La misma estructura defensiva que el resto del dominio, con el agregado más fuerte de las tres ramas:

- La ráfaga contra un solo endpoint es **idéntica y simultánea**, como en [[Race - superación de límite]], así que el agregado por cadencia la ve igual de bien: veinte registros del mismo usuario en el mismo milisegundo no es tráfico legítimo.
- La confirmación es de **invariante**, y acá la más vistosa: dos cuentas con el mismo identificador único, un objeto sin sus permisos por defecto, un token de un solo uso con dos efectos. Un estado que las restricciones de datos deberían haber impedido y no impidieron. `forma: invariante` sobre [[Log de auditoría de la aplicación]].

Refuerza la conclusión del dominio: **la firma no sirve —cada petición es válida—, el agregado ayuda cuando la ráfaga es idéntica, y el invariante es lo único que confirma**. Las tres ramas convergen en que la detección aprovechable es comprobar que un estado imposible ocurrió. Es el argumento más fuerte del vault a favor de `forma: invariante`, y queda anotado en [[MOC - Race conditions]] junto con los candidatos de detección.
