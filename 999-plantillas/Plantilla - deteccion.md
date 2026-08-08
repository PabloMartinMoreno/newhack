---
tipo: deteccion
tecnicas: []
telemetria: []
forma: evento
ventana: 
estado: idea
fidelidad: 
logica: 
validada: 
aliases: []
tags: []
---

%%
forma: evento | correlacion | agregado | invariante
  evento      un solo registro en aislamiento
  correlacion dos o más registros que hay que unir
  agregado    función sobre una ventana: tasa, cardinalidad, proporción
  invariante  condición que nunca debería violarse sobre una secuencia
ventana: obligatoria si forma es agregado o invariante — "5m", "1h", "por sesión"
estado: idea | borrador | produccion | retirada
fidelidad: alta | media | baja
logica: sigma | kql | spl | eql | yara | suricata
Sigma expresa bien evento; correlacion e invariante piden el lenguaje del SIEM.
No incluir detecciones propietarias de un empleador: son de la organización, no tuyas.
%%

## Qué detecta

Comportamiento observable, no herramienta.

## Lógica

```yaml

```

## Falsos positivos conocidos

## Evasiones conocidas

Enlazar la variante de tradecraft que la evade — si existe, esta regla ya fue puesta a prueba.

## Cómo se prueba

Variante concreta de `600-tradecraft/` que la dispara, y en qué laboratorio.

Para `agregado`: un disparador único no valida nada. Hace falta volumen y una línea base.
