---
tipo: procedimiento
fase: mantenimiento-del-vault
visibilidad: publica
creado: 2026-08-05
aliases:
  - Ciclo de validación
  - El ciclo
tags: []
---

# Validación de tradecraft en laboratorio

El ciclo que cierra el vault. Un vault con cincuenta de estas vueltas vale más que uno con mil notas leídas.

## Cuándo se ejecuta

- Cuando [[Consultas del vault]] § *Backlog de revalidación* devuelve una variante con `probado` de más de seis meses.
- Cuando se incorpora tradecraft nuevo desde una fuente.
- Cuando cambia el contexto defensivo relevante (versión de EDR, parche, configuración de Sysmon).

## Precondiciones

- Laboratorio con el `contexto:` que se quiere declarar. Si se prueba en un Windows sin EDR, el `contexto:` dice eso y nada más.
- Telemetría del laboratorio recolectándose de verdad. Sin eso el paso 2 es adivinanza.

## Pasos

1. **Ejecutar la variante** en el laboratorio, tal como está descrita en la nota.
2. **Observar qué artefactos aparecieron.** No qué debería haber aparecido: qué apareció. Este es el paso que la gente saltea y es el único que agrega información nueva.
3. **Actualizar `telemetria:`** con lo observado, no con lo supuesto. Crear la nota del artefacto en `550-telemetria/` si no existía.
4. **Escribir o ajustar la detección** en `650-detecciones/` sobre el artefacto observado.
5. **Actualizar `opsec:` y `probado:`** de la variante, y `contexto:` con el entorno exacto de la prueba.

## Criterio de salida

Cada vuelta deja **tres notas modificadas y una arista nueva**. Si terminaste con una sola nota tocada, no cerraste el ciclo: probaste algo y no lo registraste.

## Qué registrar

- Fecha exacta en `probado:` / `validada:`.
- Versión de EDR/SO en `contexto:` — "win11" sin build no sirve dentro de un año.
- Si la variante falló: no se borra la nota, se marca `opsec: quemado` y se anota **qué** la mató en § Cómo falla. El fracaso es el dato más valioso del ciclo.
