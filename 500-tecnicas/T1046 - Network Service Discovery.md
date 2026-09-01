---
tipo: tecnica
taxonomia: attack
identificador: T1046
tacticas: [discovery]
aliases:
  - T1046
  - Network Service Discovery
  - escaneo de puertos
  - port scanning
tags:
  - dominio/red
---

# T1046 - Network Service Discovery

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - Reconocimiento de red]]; la sintaxis, en [[Nmap - matriz de referencia]].

## Qué es

Averiguar qué servicios escuchan en un host o en un rango: qué puertos están abiertos, qué corre en ellos y en qué versión.

## Por qué es la fase que condiciona todas las demás

Porque define el conjunto de lo posible. Un puerto que no se encontró es un ataque que no se va a intentar, y el error más caro del reconocimiento no es el falso positivo sino el **falso negativo**: los mil puertos por defecto dejan afuera los sesenta y cuatro mil restantes, y ahí es donde suele estar el panel interno que nadie registró.

La contracara es que el escaneo **no explota nada**. Es hacer preguntas que la pila TCP/IP está obligada a contestar; el conocimiento sale de las reglas del protocolo, no de un fallo. Ver [[TCP - respuestas a segmentos inesperados]].

## Por qué la fidelidad de su detección es baja por naturaleza

Un intento de conexión aislado es indistinguible de un cliente mal configurado, de un monitor de disponibilidad o de un usuario que se equivocó de puerto. **No hay nada anómalo en una conexión rechazada.** Lo anómalo es la forma del conjunto: muchos destinos, mayoría fallando, en poco tiempo.

Eso obliga a que toda detección del dominio sea `forma: agregado` y arrastra las consecuencias de siempre: hace falta ventana, línea base y volumen. Ver [[La detección vive en el agregado, no en el evento]] y [[Sin línea base no hay anomalía]].

## Dónde se ve y dónde no

Asimetría que conviene tener clara antes de escribir cualquier regla:

- **Desde el host que escanea**, si está instrumentado, se ve bien: proceso más abanico de conexiones salientes.
- **Desde el host escaneado**, casi nada. Un sondeo `SYN` no completa el handshake y por lo tanto no llega a la aplicación: no hay línea en ningún log de servicio.
- **Desde la red**, se vería todo, pero exige telemetría de flujo que la mayoría de los entornos no recolecta ni retiene.

## La mitigación real

No se impide: contestar es el trabajo de la pila. Lo que se hace es **reducir la superficie que el escaneo encuentra** —segmentar, cerrar lo que no tiene que estar expuesto, exigir autenticación antes del banner— y aceptar que el escaneo se detecta por volumen, no por evento.

## Referencias canónicas

- [T1046](https://attack.mitre.org/techniques/T1046/)
- [T1018](https://attack.mitre.org/techniques/T1018/) — descubrimiento de sistemas remotos, el paso anterior
