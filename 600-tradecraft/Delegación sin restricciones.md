---
tipo: tradecraft
clase: "[[T1558 - Steal or Forge Kerberos Tickets]]"
eje: admin-local
implementacion: "Comprometer un host con delegación sin restricciones y forzar a un objetivo valioso a autenticarse para capturar su TGT"
opsec: ruidoso
telemetria: ["[[Windows 4768 - Kerberos TGT requested]]", "[[Windows 4624 - Successful logon]]"]
requisitos: [admin-local-en-un-host-con-delegación-sin-restricciones]
coste: medio
alternativas: ["[[Delegación basada en recursos]]", "[[DCSync]]"]
probado: nunca
contexto: [lab-ad]
aliases:
  - unconstrained delegation
  - delegación irrestricta
tags:
  - dominio/ad
---

# Delegación sin restricciones

## Cuándo lo elijo

Cuando ya tengo administrador local en un host —o control de una cuenta de máquina— y la enumeración muestra que ese host tiene **delegación sin restricciones** habilitada: el atributo `TRUSTED_FOR_DELEGATION` en `userAccountControl`. Se encuentra con [[AD enumeración - matriz de referencia]] o en BloodHound.

Es una vía a administrador de dominio que no rompe ninguna contraseña. La elijo cuando controlo un servidor con esta configuración y quiero escalar; si el control lo tiene el objeto de destino, la rama es [[Delegación basada en recursos]]; si es hacia SPNs concretos, [[Delegación restringida]].

## Por qué funciona

Un host con delegación sin restricciones **guarda en memoria el TGT completo** de todo el que se autentica a él. El TGT es la llave maestra de esa identidad: con él se piden tickets de servicio para cualquier cosa, como esa persona.

La cadena:

1. Comprometo el host con delegación (admin local).
2. **Fuerzo a un objetivo valioso a autenticarse** a ese host. El objetivo más jugoso es un controlador de dominio: si un DC se autentica, su TGT queda en mi memoria, y con el TGT del DC hago [[DCSync]].
3. Extraigo el TGT capturado de memoria y lo uso.

Forzar la autenticación es la parte activa, y hay coacción para eso: el "printer bug" (`MS-RPRN`), `PetitPotam` (`MS-EFSRPC`), o `MS-DFSNM`, que hacen que un DC se conecte de vuelta a mi host. Los comandos están en [[AD delegaciones - matriz de referencia]].

Es el mismo principio que [[Pass-the-ticket]] —usar un ticket que no es mío— pero la fuente del ticket es la memoria de un host que los acumula por diseño, no un volcado de LSASS puntual.

## Cómo falla

Falla cuando no hay ningún host con delegación sin restricciones —es una configuración vieja y desaconsejada, cada vez más rara—, o cuando los objetos sensibles están marcados como **"cuenta sensible que no puede delegarse"** o en el grupo *Protected Users*, que impide que su TGT se guarde.

Falla si no se puede forzar la autenticación del objetivo: las mitigaciones de coacción (parches de PetitPotam, deshabilitar el spooler) cierran esa vía, y sin la autenticación el TGT valioso nunca llega.

Y falla si no se llega a extraer el TGT antes de que caduque —diez horas por defecto—, aunque la ventana es amplia.

## Coste

Medio. Conseguir admin local en el host de delegación es el prerrequisito y puede ser todo el trabajo. Una vez ahí, forzar la autenticación y extraer el TGT son pocos comandos con Rubeus o mimikatz.

La coacción es ruidosa —genera conexiones y autenticaciones anómalas— y la captura del TGT del DC es un salto grande de privilegio, así que conviene tener claro el objetivo antes de disparar la coacción.

## Huella esperada

Ruidosa, y con señales en Kerberos:

- La coacción hace que el objetivo —a menudo un DC— se **autentique al host del atacante**, lo que deja un [[Windows 4624 - Successful logon]] con un origen inusual y un [[Windows 4768 - Kerberos TGT requested]] del objetivo. Un DC autenticándose a un servidor cualquiera no es normal.
- El uso posterior del TGT capturado para pedir tickets de servicio deja rastro en [[Windows 4769 - Kerberos service ticket requested]].

La detección natural es la anomalía de que una cuenta de alto valor se autentique a un host con delegación, y la implementa [[Cuenta de alto valor autenticándose a host con delegación]]: una intersección de dos listas de activos —los hosts con `TRUSTED_FOR_DELEGATION` y las cuentas sensibles— sobre el `4624`. Su fidelidad depende del inventario, no de un campo del evento, así que es tan buena como las listas que la alimentan. Cuando la coacción usa NTLM, además la cruza [[Autenticación NTLM donde el dominio usa Kerberos]]. La rama cierra así su ciclo rojo↔azul, con la salvedad de que la regla es de línea base.
