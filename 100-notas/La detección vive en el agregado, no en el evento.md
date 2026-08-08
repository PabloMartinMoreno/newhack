---
tipo: zettel
relacionadas: ["[[Fallos de acceso contra cuentas inexistentes]]", "[[Esquema de frontmatter]]"]
aliases:
  - reglas sobre ventana
tags: []
---

# La detección vive en el agregado, no en el evento

## Idea

Muchos ataques están hechos **enteramente de eventos legítimos**. Cada petición es válida, cada sesión real, cada respuesta correcta. Lo anómalo no está en ningún evento: está en su **cantidad, su proporción, su orden o su relación**.

Una regla que mira un evento por vez no puede ver nada de eso. No porque esté mal escrita: porque la información no está ahí.

## Por qué importa

Es la diferencia entre poder escribir una detección y no poder.

Un intento de acceso fallido no es nada. Cien fallos contra cien cuentas distintas desde un origen es un rociado de contraseñas. **Ningún fallo individual es sospechoso**, y el conjunto es inequívoco.

Peor todavía: la defensa clásica de autenticación cuenta fallos **por cuenta**, y el rociado reparte uno por cuenta. Cada contador queda en uno y nada dispara. El ataque es invisible cuenta por cuenta y evidente en el agregado — ver [[Fallos de acceso contra cuentas inexistentes]].

Y hay ataques que ni siquiera producen fallos: la reutilización de credenciales filtradas **acierta a la primera**. Toda la maquinaria construida sobre "muchos intentos fallidos seguidos" no lo ve, y hay que mirar los **éxitos** anómalos.

## Las cuatro formas

Cuando esto apareció por cuarta vez en este vault, se agregó `forma:` al esquema de las detecciones:

| Forma | Qué evalúa | Ejemplo |
|---|---|---|
| `evento` | un registro en aislamiento | un `sh` hijo de `php-fpm` |
| `correlacion` | dos o más registros que hay que unir | el actor no es el dueño del objeto |
| `agregado` | una función sobre una ventana | proporción de fallos contra cuentas inexistentes |
| `invariante` | una condición sobre una secuencia | actividad de sesión después de su cierre |

No es una clasificación decorativa: **cambia el lenguaje** —Sigma expresa bien `evento` y no llega a `correlacion` ni `invariante`—, **cambia el coste** —una ventana necesita estado— y **cambia cómo se valida**.

## Consecuencias

- **Un disparo valida una regla de `evento` y no dice nada de una de `agregado`.** Es el error de validación más común: se confirma que la regla dispara y se despliega sin saber cuánto dispara sin ataque.
- **Las de `agregado` necesitan línea base.** Ver [[Sin línea base no hay anomalía]].
- **Si la herramienta solo expresa reglas de evento, hay ataques que no se pueden escribir.** Esa limitación es de la herramienta, no del analista, y conviene reconocerla en vez de forzar una regla mala.
- **La agrupación es tan importante como el umbral.** Agrupar por IP y agrupar por sesión detectan cosas distintas; un atacante distribuido evade la primera y no la segunda.

## Fuente

Destilado de escribir las detecciones de este vault. Cuatro dominios seguidos lo pidieron antes de que se agregara el campo.
