---
tipo: tradecraft
clase: "[[T1046 - Network Service Discovery]]"
eje: sondeo
implementacion: "Enviar segmentos sin SYN —FIN, sin banderas, FIN+PSH+URG, o ACK suelto— y clasificar por la ausencia o presencia de RST"
opsec: ruidoso
telemetria: ["[[Sysmon EID 3 - NetworkConnect]]", "[[Sysmon EID 1 - ProcessCreate]]"]
requisitos: [raw-sockets, root-o-administrador, pila-que-cumpla-el-rfc]
coste: medio
alternativas: ["[[Escaneo - sondeo SYN de puertos TCP]]"]
probado: nunca
contexto: [lab-linux, firewall-sin-estado]
aliases:
  - FIN scan
  - NULL scan
  - Xmas scan
  - ACK scan
tags:
  - dominio/red
---

# Escaneo - sondeos de bandera anómala

## Cuándo lo elijo

Casi nunca para saber si un puerto está abierto, y bastante seguido para saber **qué hay en el camino**. Son dos usos distintos que conviene no mezclar:

- **`FIN`, sin banderas y `FIN+PSH+URG`** clasifican puertos con la lógica invertida: el silencio es abierto. Sólo tiene sentido contra pilas que cumplan el RFC —en la práctica, no Windows— y su ventaja histórica era atravesar filtros que sólo miraban el `SYN`. Ese caso es cada vez más raro.
- **`ACK` suelto** no clasifica puertos en absoluto: devuelve `RST` esté abierto o cerrado. Lo que informa es si el `RST` volvió, y con eso se **mapea el firewall**: qué puertos deja pasar y si guarda estado. Es el uso que sigue rindiendo hoy.

La decisión práctica: si quiero estado de puertos, uso `SYN`; si quiero entender el filtro que tengo delante antes de insistir, uso `ACK`.

## Por qué funciona

Por la asimetría que impone el RFC y que está en [[TCP - respuestas a segmentos inesperados]]: un puerto cerrado contesta `RST` a cualquier cosa, y uno abierto **descarta en silencio** lo que no lleva `SYN`, `ACK` ni `RST`. De ahí la inversión.

El `ACK` funciona por otro motivo: un firewall sin estado no tiene forma de saber que ese `ACK` no pertenece a ninguna conexión y lo deja pasar; uno con estado lo descarta. La diferencia entre las dos conductas es, literalmente, el resultado del sondeo.

## Cómo falla

De la peor manera posible: **devolviendo resultados que parecen buenos**. Contra una pila que responde `RST` con el puerto abierto —Windows y buena parte del equipamiento de red—, todo aparece como cerrado y no hay nada en la salida que avise que la premisa no se cumple. Antes de creerle a un escaneo de estos hay que confirmar por otra vía que el objetivo no es de esa familia.

El segundo modo de falla es de mérito ajeno: cualquier IDS moderno tiene firma para un paquete sin banderas o con `FIN+PSH+URG`, porque no existe tráfico legítimo con esa forma. La reputación de sigilosos es de los años noventa; hoy son **más** detectables que un `SYN`, no menos.

## Coste

Medio, y mal pagado en el uso de clasificación: mismo tiempo que un `SYN` para un resultado que hay que validar aparte. En el uso de mapeo de firewall el rendimiento es alto, porque contesta una pregunta —¿esto tiene estado?— que ningún otro sondeo del dominio contesta.
