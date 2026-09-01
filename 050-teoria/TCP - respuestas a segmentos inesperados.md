---
tipo: teoria
habilita: ["[[Escaneo - sondeo SYN de puertos TCP]]", "[[Escaneo - sondeos de bandera anómala]]", "[[Escaneo - sondeo de puertos UDP]]"]
relacionadas: ["[[TCP - establecimiento de la conexión]]", "[[ICMP - el canal de error de IP]]"]
aliases:
  - RST behaviour
  - scan types
tags: []
---

# TCP - respuestas a segmentos inesperados

## Qué dice la especificación

El handshake describe qué pasa cuando **todo sale bien**. La parte que se usa para escanear es la otra: qué está obligado a responder un host ante un segmento que no encaja en ninguna conexión suya. El RFC lo define por estado, y de esas reglas sale **cada tipo de escaneo que existe**.

| Estado del puerto | Llega `SYN` | Llega `ACK` suelto | Llega `FIN`, sin banderas, o `FIN+PSH+URG` |
|---|---|---|---|
| Cerrado | `RST` | `RST` | `RST` |
| Abierto (`LISTEN`) | `SYN-ACK` | `RST` | **Silencio** |

Dos reglas explican toda la tabla:

- **Puerto cerrado: contestar `RST` a cualquier cosa** que no sea un `RST` (contestar un `RST` con otro daría un bucle). El host no distingue entre sondeos: nadie escucha, y lo dice.
- **Puerto abierto: descartar en silencio** un segmento sin `SYN`, sin `ACK` y sin `RST`. No pertenece a ninguna conexión establecida y no inicia ninguna, así que no hay nada que responder.

La consecuencia es contraintuitiva y es el corazón de media docena de escaneos: para un sondeo de bandera anómala, **el silencio significa abierto y la respuesta significa cerrado**. La lógica queda invertida respecto del sondeo `SYN`.

El caso del `ACK` suelto es distinto de los otros dos: devuelve `RST` en los dos estados, así que **no dice nada sobre el puerto**. Lo que informa es si el `RST` volvió — es decir, si algo en el camino filtró. Mapea el firewall, no el servicio.

En UDP no hay nada de esto porque no hay conexión ni banderas. Un puerto cerrado se delata por [[ICMP - el canal de error de IP]] `tipo 3 código 3`; uno abierto contesta si la aplicación quiere, y si no quiere, calla. Silencio es ambiguo por diseño.

## Dónde el estándar deja lugar

En que **muchas pilas no cumplen la segunda regla**. Windows, buena parte del equipamiento de red y varios sistemas embebidos responden `RST` también con el puerto abierto. No es un bug con consecuencias: es un desvío deliberado y viejo, y arruina exactamente los escaneos que dependen del silencio — contra esos hosts todo da *cerrado* y el resultado es inservible.

El resto de lo que decide un escaneo tampoco está en el RFC:

- **Si el `RST` sale del host o lo genera un firewall** en su nombre, y si en cambio se descarta sin más. Es la diferencia entre *cerrado* y *filtrado*.
- **La limitación de tasa de errores ICMP**, que es lo que vuelve lento el sondeo UDP: hay que esperar a que el destino tenga permitido volver a quejarse.
- **Si el estado se guarda.** Un firewall sin estado deja pasar el `ACK` suelto; uno con estado lo descarta por no pertenecer a ninguna conexión. Esa diferencia *es* el resultado del sondeo por `ACK`.

## Qué habilita

- **El sondeo `SYN`** lee la tabla en su primera columna: `SYN-ACK` abierto, `RST` cerrado, silencio filtrado → [[Escaneo - sondeo SYN de puertos TCP]].
- **Los sondeos de bandera anómala** leen la tercera y viven de la inversión, con la trampa de las pilas que no cumplen → [[Escaneo - sondeos de bandera anómala]].
- **El sondeo UDP** no lee ninguna: depende enteramente de ICMP y de su limitación de tasa, que es de dónde sale su coste → [[Escaneo - sondeo de puertos UDP]].

## Cómo se ve en la práctica

Nada de esto llega a la aplicación. Un sondeo `SYN` que nunca completa el handshake **no produce un `accept()`**, así que el servidor web no registra absolutamente nada; el sondeo de bandera anómala ni siquiera toca la máquina de estados de la conexión. Lo que sí lo ve es la pila y lo que esté delante: el firewall registra el intento, y en un host instrumentado [[Sysmon EID 3 - NetworkConnect]] ve la conexión saliente **del que escanea**, no del escaneado.

De ahí la asimetría que ordena la cara azul del dominio: **el escaneo se detecta mucho mejor en el atacante que en la víctima**, siempre que el atacante esté corriendo desde un host que se esté vigilando.

## Fuente

RFC 9293 §3.10.7 (Segment Arrives), que consolida las reglas por estado de RFC 793. El desvío de las pilas que responden `RST` con el puerto abierto está documentado desde los primeros trabajos sobre escaneo y sigue vigente.
