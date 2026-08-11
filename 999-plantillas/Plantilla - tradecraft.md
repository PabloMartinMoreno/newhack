---
tipo: tradecraft
clase: "[[]]"
eje: 
implementacion: ""
opsec: 
telemetria: []
requisitos: []
coste: 
alternativas: []
probado: nunca
contexto: []
aliases: []
tags: []
---

%%
opsec: limpio | ruidoso | requiere-bypass | quemado
coste: bajo | medio | alto
probado: nunca hasta que la corras en laboratorio. La fecha significa "funcionó ese día", no "la escribí ese día"
contexto: contra qué entorno hay que probarla — win11-defender, win2019-crowdstrike, ubuntu22-auditd
Regla de filtro: si esto no responde "cuándo lo elijo en vez de la alternativa", es un payload. No va acá.
Ninguna de las cuatro secciones lleva sintaxis. La sintaxis va a la matriz de referencia.
%%

## Cuándo lo elijo

Condiciones que hacen que esta variante sea la correcta, y qué alternativa la reemplaza cuando no se cumplen.

## Por qué funciona

El mecanismo. Qué primitiva del sistema se está abusando.

## Cómo falla

Qué la rompe: controles, condiciones de red, versiones, mitigaciones.

## Coste

Tiempo, peticiones, ruido, privilegios necesarios.

## Huella esperada

Qué emite, y con qué campos observables. Cada artefacto va también en `telemetria:`.
