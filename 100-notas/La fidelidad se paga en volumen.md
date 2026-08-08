---
tipo: zettel
relacionadas: ["[[Sin línea base no hay anomalía]]", "[[Petición al servicio de metadatos de instancia]]"]
aliases:
  - falsos positivos y negativos
  - el compromiso del SOC
tags: []
---

# La fidelidad se paga en volumen

## Idea

Toda detección elige entre dos errores: alertar por algo que no era un ataque, o callarse ante uno que sí. Ajustar una regla no elimina el compromiso, lo **mueve**: apretar el umbral baja los falsos positivos y sube los falsos negativos, y al revés.

No existe la regla que detecte todo sin ruido. La pregunta útil no es cuál de los dos errores evitar sino **cuál de los dos podés pagar**.

## Por qué importa

Porque el costo de los dos errores no lo paga la misma persona ni en el mismo momento, y eso deforma las decisiones.

Un falso positivo cuesta **atención humana ahora**: alguien mira una alerta y descarta. Es visible, medible y molesta a diario. Un falso negativo cuesta **un incidente después**: es invisible hasta que ya pasó, y nadie lo atribuye a la regla que faltó.

Esa asimetría empuja siempre en la misma dirección — apretar los umbrales hasta que el equipo deje de quejarse. Y ahí aparece el fracaso real de un SOC, que no es tener malas reglas: es tener **buenas reglas que nadie mira** porque están enterradas en ruido.

## El número que importa

Con una detección de alta fidelidad, la intuición falla feo. Si una regla acierta el 99% de las veces pero el ataque ocurre una vez cada diez mil eventos, la mayoría de sus alertas siguen siendo falsas — porque hay muchísimos más eventos benignos que malignos, y el 1% de un número enorme supera al 99% de uno chiquito.

La consecuencia práctica: **contra eventos raros, "99% de acierto" no alcanza**. Por eso las reglas que valen son las que anclan en algo que casi no ocurre de forma legítima, y no las que aciertan mucho.

[[Petición al servicio de metadatos de instancia]] es el ejemplo: no es fiable porque acierte mucho, sino porque **una aplicación no pide credenciales de instancia en medio de una petición de usuario**. El denominador de eventos legítimos es casi cero.

## Consecuencias

- **La fidelidad se declara, no se supone.** Por eso `fidelidad:` está en el frontmatter de cada detección: obliga a decir qué esperás antes de desplegar.
- **Bajar el ruido cambiando la fuente vale más que ajustar el umbral.** Filtrar procesos hijos por padre baja el volumen uno o dos órdenes de magnitud sin perder nada del ataque.
- **Una regla ruidosa que no se puede afinar hay que retirarla.** Está el estado `retirada` para eso: dejarla activa entrena al equipo a ignorar alertas, que es peor que no tenerla.
- **Fidelidad baja no significa inútil**, significa otro uso: cazar hacia atrás en vez de alertar. Ver [[Detectar el efecto sobrevive a la evasión]].

## Fuente

Destilado propio. El fenómeno del denominador se conoce como falacia de la tasa base.
