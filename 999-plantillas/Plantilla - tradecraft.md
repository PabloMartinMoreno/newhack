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
probado: 
contexto: []
visibilidad: privada
creado: {{date}}
aliases: []
tags: []
---

%%
opsec: limpio | ruidoso | requiere-bypass | quemado
coste: bajo | medio | alto
contexto: dónde se probó — win11-defender, win2019-crowdstrike, ubuntu22-auditd
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
