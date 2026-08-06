---
tipo: zettel
relacionadas: ["[[SQLi - canal temporal ciego]]"]
visibilidad: publica
creado: 2026-08-05
aliases: []
tags: []
---

# La latencia como canal de datos

## Idea

Cuando un sistema no devuelve el contenido de una operación pero sí **cuándo** responde, el tiempo es un canal de datos de un bit por observación. Cualquier primitiva que permita ejecutar condicionalmente algo lento convierte una condición booleana interna en información observable desde afuera.

## Por qué importa

Es la razón por la que "el sistema no devuelve nada" nunca significa "no hay extracción posible". La misma idea reaparece en contextos que no comparten nada más entre sí:

- SQLi temporal ciego: `IF(condición, SLEEP(5), 0)`.
- Comparación de contraseñas no constante en tiempo.
- Enumeración de usuarios por diferencia de tiempo entre un fallo temprano y un hash completo.
- Canales encubiertos por tiempo entre paquetes.
- Ataques de caché por diferencia de acceso.

Todas son la misma idea con distinto reloj.

## Consecuencias

- **Del lado rojo**: el canal temporal es siempre el último recurso por coste — un bit por petición contra los miles de bits que da una extracción directa. Ver [[SQLi - canal temporal ciego]].
- **Del lado azul**: la firma no está en el payload sino en la **distribución** de latencias. Una distribución bimodal en un endpoint es sospechosa aunque cada petición sea individualmente inocente. Eso implica que la detección vive en agregación, no en coincidencia de patrones.
- **Del lado defensivo de diseño**: la mitigación no es esconder el tiempo, es hacerlo constante.

## Fuente

Destilado de trabajo propio, no de una fuente única.
