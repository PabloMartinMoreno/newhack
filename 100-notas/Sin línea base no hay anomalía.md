---
tipo: zettel
relacionadas: ["[[Barrido de puertos internos desde el servidor de aplicación]]", "[[Ráfaga de errores del servidor desde un mismo origen]]"]
aliases:
  - línea base
  - baseline
tags: []
---

# Sin línea base no hay anomalía

## Idea

"Anómalo" no es una propiedad de un evento: es una **comparación**. Decir que algo es anormal exige saber qué es normal, y eso solo se sabe midiéndolo.

Una regla con un umbral inventado no detecta anomalías. Detecta el número que alguien escribió, y ese número o deja pasar todo o alerta por todo.

## Por qué importa

Es el trabajo que separa una regla que existe de una regla que funciona, y es el que casi nadie hace porque es aburrido: mirar tráfico normal durante días antes de escribir nada.

Los umbrales de las detecciones de este vault —`total > 20`, `cuentas > 15`, `p95 > p50 * 10`— son **puntos de partida, no valores**. Están puestos para que la consulta se pueda leer, y cada uno hay que derivarlo del entorno donde se despliega.

El mismo número da resultados opuestos en dos lugares:

- Cincuenta conexiones internas en cinco minutos: **normal** en una aplicación con descubrimiento de servicios, **un barrido** en una que habla con tres destinos fijos.
- Veinte accesos fallidos desde una IP: **normal** detrás de un NAT corporativo, **un ataque** desde una IP residencial.
- Un pico de errores del servidor: **un despliegue roto** si afecta a todos los orígenes, **reconocimiento** si viene de uno.

Ese último es el patrón general: la línea base no solo da el umbral, **da la dimensión por la que hay que agrupar**.

## Consecuencias

- **Las reglas de forma `agregado` no se validan con un disparo.** Confirmar que disparan es fácil; saber que no ahogan en falsos positivos requiere el entorno real. Por eso ninguna llega a `estado: produccion` desde un laboratorio.
- **Un umbral copiado de internet es un umbral inventado.** Sirve para entender la forma de la regla, no para desplegarla.
- **Cambiar la aplicación invalida la línea base.** Un despliegue que agrega un servicio nuevo cambia lo normal, y las reglas calibradas contra lo anterior empiezan a mentir sin avisar.
- **La ausencia de línea base se disfraza de detección funcionando.** Una regla que nunca dispara parece bien calibrada y puede estar simplemente ciega.

## Cómo se construye

1. Recolectar sin alertar, con la aplicación en operación normal.
2. Mirar la **distribución**, no el promedio: casi todo lo interesante vive en los percentiles altos.
3. Fijar el umbral por encima del máximo observado sin ataque, no por encima del promedio.
4. Volver a medir después de cada cambio grande del sistema.

## Fuente

Destilado de escribir las detecciones de este vault, todas las cuales lo necesitan y ninguna lo tiene todavía.
