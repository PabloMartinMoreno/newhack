---
tipo: zettel
relacionadas: ["[[Validación de tradecraft en laboratorio]]", "[[Esquema de frontmatter]]"]
aliases:
  - ciclo de vida de una regla
  - por qué existe el campo estado
tags: []
---

# Toda detección es una hipótesis con fecha de vencimiento

## Idea

Una regla afirma algo sobre el mundo: *si ocurre X, probablemente hubo un ataque*. Eso es una **hipótesis**, no un hecho — y como toda hipótesis, se puede falsar: por un falso positivo que muestra que X ocurre legítimamente, o por una evasión que muestra que el ataque puede ocurrir sin X.

Y además caduca. El sistema que vigila cambia, el atacante aprende, la biblioteca se actualiza. Una regla escrita hace dos años y nunca revisada no es una regla vigente: es una regla vieja que nadie miró.

## Por qué importa

Porque una detección desplegada y olvidada **da cobertura aparente**. Aparece en el inventario, cuenta en la métrica, y puede llevar meses sin poder disparar. Nadie se entera, porque el silencio de una regla rota se ve igual que el de una que funciona — ver [[Ausencia de alertas no es ausencia de ataque]].

Es exactamente el mismo problema que el conocimiento ofensivo caducado, y por eso este vault trata a los dos lados igual: `probado:` en el tradecraft y `validada:` en las detecciones existen por la misma razón.

## El ciclo

```
idea        escrita, nunca ejecutada contra nada
borrador    disparó en laboratorio; sin calibrar contra ruido real
produccion  calibrada en el entorno real, con su línea base
retirada    ya no vale — evadida, obsoleta, o insalvablemente ruidosa
```

Las 16 detecciones de este vault están en `idea`. Eso no es un defecto de registro: **es lo que son**. Ninguna se ejecutó todavía, y el campo vacío lo dice.

`retirada` importa tanto como los otros tres. Una regla que no se puede afinar hay que sacarla: dejarla activa entrena al equipo a ignorar alertas, que hace más daño que no tenerla.

## Consecuencias

- **Una regla sin fecha de validación es una regla sin evidencia.** El campo vacío es información, no un descuido.
- **La evasión conocida es parte de la regla.** Por eso todas las de este vault tienen esa sección: sin ella no se sabe qué significa su silencio.
- **Los cambios del sistema invalidan reglas en silencio.** Un despliegue que renombra un servicio o cambia un formato de log puede romper una regla sin que nada falle visiblemente.
- **Falsar una regla propia es un buen resultado.** Descubrir que una detección se evade fácil enseña más que confirmarla, y es la misma lógica que hace del fracaso el dato más valioso en [[Validación de tradecraft en laboratorio]].

## Fuente

Destilado propio, por simetría con el ciclo de revalidación del lado rojo de este vault.
