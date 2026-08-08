---
tipo: zettel
relacionadas: ["[[Intérprete de comandos como hijo del servidor web]]", "[[Payload de inyección en parámetros de la URL]]", "[[Archivo ejecutable nuevo en la raíz web]]"]
aliases:
  - efecto contra firma
  - pirámide del dolor
tags: []
---

# Detectar el efecto sobrevive a la evasión

## Idea

Una detección puede anclarse en **cómo se ve** un ataque o en **qué produce**. La primera se rompe cuando el atacante cambia el disfraz; la segunda solo se rompe si cambia lo que quiere lograr.

Los objetivos no cambian: si alguien busca ejecución de comandos, en algún momento **nace un proceso**. Puede escribir el comando de mil formas; no puede conseguir el efecto sin el efecto.

## Por qué importa

Es el criterio para decidir dónde poner una regla, y explica de antemano cuánto va a durar.

Un ejemplo del vault que lo muestra completo: [[Payload de inyección en parámetros de la URL]] busca cadenas como `UNION SELECT` en la URL. La evade **cualquiera** que sepa lo que hace —comentarios intercalados, codificación, mayúsculas alternadas— y también quien no sepa nada, simplemente mandando el payload por POST. Lleva `fidelidad: baja` escrita en el frontmatter y su propia nota dice que no se despliega para alertar.

En cambio [[Intérprete de comandos como hijo del servidor web]] no mira el comando: mira que el servidor web sea padre de una shell. Toda la matriz de evasión de comandos es irrelevante contra ella.

El caso más claro es [[Archivo ejecutable nuevo en la raíz web]]: **una sola regla cubre seis técnicas** —webshell, subida, LFI a RCE, `INTO OUTFILE`, gopher a Redis, canal ciego— que no comparten ni payload ni vector. Comparten el efecto, y por eso una condición las alcanza a todas.

## La escala completa

De más fácil a más caro de cambiar para el atacante:

```
hash del archivo        cambia recompilando
dirección IP            cambia alquilando otra
nombre de dominio       cambia registrando otro
cadena en el payload    cambia codificando
herramienta             cambia usando otra
comportamiento          NO cambia sin cambiar el objetivo
```

Es la idea que se conoce como *pirámide del dolor*: cuanto más abajo ancla la detección, más barato le sale al atacante esquivarla.

## Consecuencias

- **Las firmas no son inútiles, son de otro uso.** Sirven para cazar hacia atrás sobre una ventana histórica, no para alertar. Con eso son valiosas y baratas.
- **Una regla de efecto cubre técnicas que no existían cuando se escribió.** Pasó dos veces en este vault: las reglas de proceso hijo y de cambio de privilegio detectaron el dominio de deserialización sin que hiciera falta escribir nada nuevo.
- **La contrapartida es el ruido.** Los efectos también los producen operaciones legítimas, así que las reglas de efecto necesitan exclusiones cuidadas. Por eso todas las de este vault tienen su sección de falsos positivos con lo específico de cada aplicación.

## Fuente

La idea de la pirámide es de David Bianco. El resto, destilado de escribir las detecciones de este vault.
